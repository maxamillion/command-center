//! Durable attention metadata only: no messages or terminal contents are copied.
use crate::{
    ApiError, AppState,
    config::Host,
    queue::{Activity, AgentState},
};
use axum::{Json, extract::State as AxumState, http::StatusCode};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{collections::HashMap, io::Write, path::PathBuf, sync::Arc};
use tokio::sync::Mutex;

fn hash(value: impl AsRef<[u8]>) -> String {
    format!("{:x}", Sha256::digest(value.as_ref()))
}
pub(crate) fn scope(host: &Host, session: &str, window: &str, pane: &str) -> (String, String) {
    let endpoint = if host.ssh_jump.is_some() {
        hash(
            serde_json::to_vec(&(
                &host.id,
                &host.ssh,
                &host.socket,
                &host.ssh_config,
                &host.ssh_jump,
            ))
            .unwrap(),
        )
    } else {
        // Preserve existing read/approval identities for direct connections.
        hash(serde_json::to_vec(&(&host.id, &host.ssh, &host.socket, &host.ssh_config)).unwrap())
    };
    let agent = agent_scope(&endpoint, session, window, pane);
    (endpoint, agent)
}
pub(crate) fn agent_scope(endpoint: &str, session: &str, window: &str, pane: &str) -> String {
    hash(format!("{endpoint}/{session}/{window}/{pane}"))
}
#[derive(Clone, Default, Deserialize, Serialize, PartialEq)]
struct Data {
    agents: HashMap<String, Agent>,
    conversations: HashMap<String, Conversation>,
}
#[derive(Clone, Default, Deserialize, Serialize, PartialEq)]
struct Agent {
    instance: String,
    revision: u64,
    phase: Option<AgentState>,
    ready_transition: Option<String>,
    finished: u64,
    finished_read: u64,
    approval: u64,
    approval_read: u64,
    approval_open: bool,
    conversation: Option<String>,
    watch: Option<String>,
    version: Option<String>,
    conversations: Vec<String>,
}
#[derive(Clone, Default, Deserialize, Serialize, PartialEq)]
struct Conversation {
    #[serde(default)]
    history_id: Option<String>,
    latest: Option<String>,
    read: Option<String>,
    version: String,
    #[serde(default)]
    mtime_ns: u64,
    #[serde(default)]
    position: u64,
    #[serde(default)]
    source_id: Option<String>,
    #[serde(default)]
    session_id: Option<String>,
    #[serde(default)]
    reply_order_key: Option<String>,
}
#[derive(Clone, Deserialize)]
pub(crate) struct Reply {
    conversation: String,
    version: String,
    cursor: Option<String>,
    #[serde(default)]
    unchanged: bool,
    #[serde(default)]
    mtime_ns: u64,
    #[serde(default)]
    position: u64,
    #[serde(default)]
    source_id: Option<String>,
    #[serde(default)]
    session_id: Option<String>,
    #[serde(default)]
    reply_order_key: Option<String>,
    #[serde(default)]
    reset: bool,
}
#[derive(Clone, Debug, Default, Serialize)]
pub(crate) struct View {
    pub key: String,
    pub instance: String,
    pub revision: u64,
    pub finished: bool,
    pub new_approval: bool,
    pub unread_reply: bool,
    pub needs_attention: bool,
    pub conversation: Option<String>,
    pub reply_cursor: Option<String>,
    pub history_id: Option<String>,
}
impl View {
    pub fn unread(&self) -> bool {
        self.finished || self.new_approval || self.unread_reply
    }
}
pub(crate) struct Attention {
    data: Mutex<Data>,
    path: Option<PathBuf>,
}
impl Attention {
    pub fn new(path: Option<PathBuf>) -> anyhow::Result<Self> {
        let data = match &path {
            Some(path) if path.exists() => {
                anyhow::ensure!(
                    std::fs::metadata(path)?.len() <= 16 * 1024 * 1024,
                    "attention metadata exceeds limit"
                );
                serde_json::from_slice(&std::fs::read(path)?)?
            }
            _ => Data::default(),
        };
        Ok(Self {
            data: Mutex::new(data),
            path,
        })
    }
    async fn save(&self, data: &Data) -> Result<(), ApiError> {
        let Some(path) = self.path.clone() else {
            return Ok(());
        };
        let bytes = serde_json::to_vec(data)
            .map_err(|e| ApiError(StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        if bytes.len() > 16 * 1024 * 1024 {
            return Err(ApiError(
                StatusCode::TOO_MANY_REQUESTS,
                "Attention metadata exceeds limit".into(),
            ));
        }
        tokio::task::spawn_blocking(move || -> std::io::Result<()> {
            let parent = path
                .parent()
                .filter(|p| !p.as_os_str().is_empty())
                .unwrap_or_else(|| std::path::Path::new("."));
            let mut file = tempfile::NamedTempFile::new_in(parent)?;
            file.write_all(&bytes)?;
            file.as_file().sync_all()?;
            file.persist(path).map_err(|e| e.error)?;
            Ok(())
        })
        .await
        .map_err(|e| ApiError(StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
        .map_err(|e| {
            ApiError(
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Could not save attention metadata: {e}"),
            )
        })
    }
    pub async fn observation_args(
        &self,
        key: &str,
    ) -> (Option<String>, Option<String>, Option<String>) {
        let data = self.data.lock().await;
        let Some(agent) = data.agents.get(key) else {
            return (None, None, None);
        };
        let order = agent
            .conversation
            .as_ref()
            .and_then(|conversation| data.conversations.get(conversation))
            .filter(|conversation| agent.watch.as_deref() == conversation.history_id.as_deref())
            .and_then(|conversation| conversation.reply_order_key.clone());
        (agent.watch.clone(), agent.version.clone(), order)
    }
    pub async fn observe(
        &self,
        scope: (&str, &str),
        instance: Option<&str>,
        activity: &Activity,
        reply: Option<Reply>,
        active: bool,
        watch: Option<&str>,
    ) -> Result<View, ApiError> {
        let (key, endpoint) = scope;
        let mut stored = self.data.lock().await;
        let mut data = stored.clone();
        if !data.agents.contains_key(key) && data.agents.len() >= 4096 {
            return Err(ApiError(
                StatusCode::TOO_MANY_REQUESTS,
                "Attention metadata is full".into(),
            ));
        }
        let agent = data.agents.entry(key.into()).or_default();
        if let Some(instance) = instance.filter(|s| !s.is_empty())
            && agent.instance != instance
        {
            *agent = Agent {
                instance: instance.into(),
                ..Agent::default()
            };
        }
        match activity.state {
            AgentState::Working => {
                agent.phase = Some(AgentState::Working);
            }
            AgentState::Ready => {
                if agent.phase == Some(AgentState::Working)
                    || (agent.phase == Some(AgentState::Ready)
                        && agent.ready_transition.is_some()
                        && activity.transition.is_some()
                        && agent.ready_transition != activity.transition)
                {
                    agent.revision += 1;
                    agent.finished = agent.revision;
                }
                agent.phase = Some(AgentState::Ready);
                agent.ready_transition = activity.transition.clone();
            }
            _ => {}
        }
        if activity.state == AgentState::Approval && !agent.approval_open {
            agent.revision += 1;
            agent.approval = agent.revision;
            agent.approval_open = true;
        } else if matches!(activity.state, AgentState::Working | AgentState::Ready) {
            agent.approval_open = false;
            agent.approval_read = agent.approval;
        }
        let mut selected = None;
        let mut displayed_cursor = None;
        if let Some(reply) = reply {
            if reply.conversation.len() > 1024
                || reply
                    .source_id
                    .as_ref()
                    .is_some_and(|value| value.is_empty() || value.len() > 256)
                || reply
                    .session_id
                    .as_ref()
                    .is_some_and(|value| value.is_empty() || value.len() > 512)
                || reply
                    .reply_order_key
                    .as_ref()
                    .is_some_and(|value| value.is_empty() || value.len() > 512)
            {
                return Err(ApiError(
                    StatusCode::BAD_GATEWAY,
                    "Invalid agent history cursor metadata".into(),
                ));
            }
            let conversation_key = hash(format!("{endpoint}/{}", reply.conversation));
            if !data.conversations.contains_key(&conversation_key)
                && data.conversations.len() >= 4096
            {
                return Err(ApiError(
                    StatusCode::TOO_MANY_REQUESTS,
                    "Conversation read metadata is full".into(),
                ));
            }
            let first = !data.conversations.contains_key(&conversation_key);
            let conversation = data
                .conversations
                .entry(conversation_key.clone())
                .or_default();
            conversation.history_id = Some(reply.conversation.clone());
            let source_changed = conversation
                .source_id
                .as_ref()
                .zip(reply.source_id.as_ref())
                .is_some_and(|(old, new)| old != new);
            let session_changed = conversation
                .session_id
                .as_ref()
                .zip(reply.session_id.as_ref())
                .is_some_and(|(old, new)| old != new);
            displayed_cursor = Some(if reply.unchanged {
                if conversation.version == reply.version {
                    conversation.latest.clone()
                } else {
                    None
                }
            } else {
                reply.cursor.clone()
            });
            if !reply.unchanged {
                let same_order_changed = reply
                    .reply_order_key
                    .as_ref()
                    .zip(conversation.reply_order_key.as_ref())
                    .is_some_and(|(incoming, current)| {
                        incoming == current && reply.cursor != conversation.latest
                    });
                let reset = reply.reset || source_changed || session_changed || same_order_changed;
                let current_order = conversation
                    .reply_order_key
                    .clone()
                    .or_else(|| Some(format!("{:020}:000000", conversation.position)));
                let order_is_older = reply
                    .reply_order_key
                    .as_ref()
                    .zip(current_order.as_ref())
                    .is_some_and(|(incoming, current)| incoming < current && !reset);
                if (first || !order_is_older)
                    && (first
                        || reset
                        || reply
                            .reply_order_key
                            .as_ref()
                            .zip(current_order.as_ref())
                            .is_some_and(|(incoming, current)| incoming > current)
                        || reply
                            .reply_order_key
                            .as_ref()
                            .zip(current_order.as_ref())
                            .is_some_and(|(incoming, current)| incoming == current)
                            && reply.cursor == conversation.latest
                        || reply.reply_order_key.is_none()
                            && (reply.mtime_ns, reply.position)
                                >= (conversation.mtime_ns, conversation.position))
                {
                    if reply.cursor.is_some() || reset {
                        conversation.latest = reply.cursor.clone();
                    }
                    conversation.position = reply.position;
                    conversation.mtime_ns = reply.mtime_ns;
                    conversation.version = reply.version.clone();
                    if reset || first {
                        conversation.read = conversation.latest.clone();
                    }
                    if reset || reply.reply_order_key.is_some() {
                        conversation.reply_order_key = reply.reply_order_key.clone();
                    }
                    if reply.source_id.is_some() {
                        conversation.source_id = reply.source_id.clone();
                    }
                    if reply.session_id.is_some() {
                        conversation.session_id = reply.session_id.clone();
                    }
                }
            }
            if !agent.conversations.contains(&conversation_key) {
                if agent.conversations.len() >= 20 {
                    agent.conversations.remove(0);
                }
                agent.conversations.push(conversation_key.clone());
            }
            if active || agent.conversation.is_none() {
                agent.conversation = Some(conversation_key.clone());
            }
            if agent.conversation.as_ref() == Some(&conversation_key) {
                agent.version = Some(conversation.version.clone());
            }
            selected = Some(conversation_key);
        }
        if let Some(watch) = watch {
            agent.watch = Some(watch.into());
        }
        let mut view = Self::view_in(&data, key, selected.as_deref());
        if let Some(cursor) = displayed_cursor {
            view.reply_cursor = cursor;
        }
        if data != *stored {
            self.save(&data).await?;
            *stored = data;
        }
        Ok(view)
    }
    fn view_in(data: &Data, key: &str, selected: Option<&str>) -> View {
        let Some(agent) = data.agents.get(key) else {
            return View {
                key: key.into(),
                ..View::default()
            };
        };
        let conversation = selected
            .map(str::to_owned)
            .or_else(|| agent.conversation.clone());
        let reply = conversation
            .as_ref()
            .and_then(|key| data.conversations.get(key));
        View {
            key: key.into(),
            instance: agent.instance.clone(),
            revision: agent.revision,
            finished: agent.finished > agent.finished_read,
            new_approval: agent.approval > agent.approval_read,
            unread_reply: reply.is_some_and(|c| c.latest != c.read),
            needs_attention: agent.approval_open
                || agent.finished > agent.finished_read
                || agent.approval > agent.approval_read
                || reply.is_some_and(|c| c.latest != c.read),
            conversation,
            reply_cursor: reply.and_then(|r| r.latest.clone()),
            history_id: reply.and_then(|r| r.history_id.clone()),
        }
    }
    pub async fn view(&self, key: &str) -> View {
        Self::view_in(&*self.data.lock().await, key, None)
    }
    async fn read(&self, request: Read) -> Result<View, ApiError> {
        let mut stored = self.data.lock().await;
        let mut data = stored.clone();
        let agent = data.agents.get_mut(&request.key).ok_or_else(|| {
            ApiError(
                StatusCode::NOT_FOUND,
                "Agent attention state no longer exists".into(),
            )
        })?;
        if agent.instance != request.instance {
            return Err(ApiError(
                StatusCode::CONFLICT,
                "Agent process changed; reopen the conversation".into(),
            ));
        }
        if request.revision > agent.revision {
            return Err(ApiError(
                StatusCode::CONFLICT,
                "Read marker is newer than the observed agent".into(),
            ));
        }
        if request
            .conversation
            .as_ref()
            .is_some_and(|c| !agent.conversations.contains(c))
        {
            return Err(ApiError(
                StatusCode::CONFLICT,
                "Conversation does not belong to this observed agent".into(),
            ));
        }
        agent.finished_read = agent
            .finished_read
            .max(agent.finished.min(request.revision));
        agent.approval_read = agent
            .approval_read
            .max(agent.approval.min(request.revision));
        if let Some(key) = &request.conversation
            && let Some(reply) = data.conversations.get_mut(key)
            && reply.latest == request.reply_cursor
        {
            reply.read = reply.latest.clone();
        }
        self.save(&data).await?;
        *stored = data;
        Ok(Self::view_in(
            &stored,
            &request.key,
            request.conversation.as_deref(),
        ))
    }
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Read {
    key: String,
    instance: String,
    revision: u64,
    conversation: Option<String>,
    reply_cursor: Option<String>,
}
pub(crate) async fn read(
    AxumState(state): AxumState<Arc<AppState>>,
    Json(request): Json<Read>,
) -> Result<Json<View>, ApiError> {
    Ok(Json(state.attention.read(request).await?))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn direct_host_identity_is_compatible_and_jump_routes_are_distinct() {
        let mut host: Host = serde_json::from_value(
            serde_json::json!({"id":"test","name":"Test","ssh":"user@target"}),
        )
        .unwrap();
        let direct = scope(&host, "$0", "@0", "%0");
        assert_eq!(
            direct.0,
            "863d55dbf4fd6a458fd3d94c299c4f3a1a65ffaa48f0433b2d6a401fca600f08"
        );
        host.name = "Renamed".into();
        assert_eq!(scope(&host, "$0", "@0", "%0"), direct);
        host.ssh_jump = Some("jump-a".into());
        let routed = scope(&host, "$0", "@0", "%0");
        assert_ne!(routed, direct);
        host.ssh_jump = Some("jump-b".into());
        assert_ne!(scope(&host, "$0", "@0", "%0"), routed);
    }

    fn activity(state: &str, transition: &str) -> Activity {
        serde_json::from_value(serde_json::json!({"state":state,"source":"fixture","reason":"test","evidence_at":100,"observed_at":100,"transition":transition})).unwrap()
    }
    fn reply(cursor: &str) -> Option<Reply> {
        Some(Reply {
            conversation: "thread".into(),
            version: cursor.into(),
            cursor: Some(cursor.into()),
            unchanged: false,
            mtime_ns: match cursor {
                "old" => 1,
                "new" => 2,
                _ => 3,
            },
            position: 0,
            source_id: None,
            session_id: None,
            reply_order_key: None,
            reset: false,
        })
    }
    fn opaque_reply(cursor: &str, order: &str, reset: bool) -> Option<Reply> {
        Some(Reply {
            conversation: "thread".into(),
            version: format!("revision-{cursor}"),
            cursor: Some(cursor.into()),
            unchanged: false,
            mtime_ns: 0,
            position: 0,
            source_id: Some("store-opaque".into()),
            session_id: Some("native-session".into()),
            reply_order_key: Some(order.into()),
            reset,
        })
    }
    fn read(view: &View) -> Read {
        Read {
            key: view.key.clone(),
            instance: view.instance.clone(),
            revision: view.revision,
            conversation: view.conversation.clone(),
            reply_cursor: view.reply_cursor.clone(),
        }
    }
    #[tokio::test]
    async fn first_history_is_read_and_old_ack_cannot_clear_new_events() {
        let store = Attention::new(None).unwrap();
        let baseline = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("ready", "one"),
                reply("old"),
                true,
                None,
            )
            .await
            .unwrap();
        assert!(!baseline.unread());
        assert_eq!(baseline.history_id.as_deref(), Some("thread"));
        store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("working", "two"),
                reply("old"),
                true,
                None,
            )
            .await
            .unwrap();
        let shown = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("ready", "three"),
                reply("new"),
                true,
                None,
            )
            .await
            .unwrap();
        assert!(shown.finished && shown.unread_reply);
        let newer = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("ready", "four"),
                reply("newer"),
                true,
                None,
            )
            .await
            .unwrap();
        let late = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("unknown", "late"),
                reply("new"),
                true,
                None,
            )
            .await
            .unwrap();
        assert_eq!(store.view("agent").await.reply_cursor, Some("newer".into()));
        assert_eq!(late.reply_cursor, Some("new".into()));
        store.read(read(&shown)).await.unwrap();
        let still = store.view("agent").await;
        assert!(still.finished && still.unread_reply);
        store.read(read(&late)).await.unwrap();
        assert!(store.view("agent").await.unread_reply);
        store.read(read(&newer)).await.unwrap();
        assert!(!store.view("agent").await.unread());
        let approval = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("approval", "five"),
                reply("newer"),
                true,
                None,
            )
            .await
            .unwrap();
        assert!(approval.new_approval);
        let seen = store.read(read(&approval)).await.unwrap();
        assert!(!seen.new_approval && seen.needs_attention);
    }

    #[tokio::test]
    async fn opaque_reply_order_resets_reinsertions_and_rejects_stale_acknowledgements() {
        let store = Attention::new(None).unwrap();
        let order_one = "00000000000000000001:000000";
        let order_two = "00000000000000000002:000000";
        let order_three = "00000000000000000003:000000";
        let baseline = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("unknown", "none"),
                opaque_reply("original", order_two, false),
                true,
                None,
            )
            .await
            .unwrap();
        assert!(!baseline.unread());
        let reset = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("unknown", "none"),
                opaque_reply("reinserted-old-row", order_one, true),
                true,
                None,
            )
            .await
            .unwrap();
        assert!(!reset.unread());
        let new_reply = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("unknown", "none"),
                opaque_reply("new-reply", order_three, false),
                true,
                None,
            )
            .await
            .unwrap();
        assert!(new_reply.unread_reply);
        let stale = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("unknown", "none"),
                opaque_reply("stale", order_two, false),
                true,
                None,
            )
            .await
            .unwrap();
        assert!(stale.unread_reply);
        store.read(read(&baseline)).await.unwrap();
        assert!(store.view("agent").await.unread_reply);
    }

    #[tokio::test]
    async fn a_revision_refresh_with_the_same_reply_cursor_is_not_unread() {
        let store = Attention::new(None).unwrap();
        let order = "00000000000000000001:000000";
        let baseline = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("unknown", "none"),
                opaque_reply("same-reply", order, false),
                true,
                None,
            )
            .await
            .unwrap();
        let refreshed = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("unknown", "none"),
                opaque_reply("same-reply", order, false),
                true,
                None,
            )
            .await
            .unwrap();
        assert!(!baseline.unread());
        assert!(!refreshed.unread());
    }
    #[tokio::test]
    async fn metadata_survives_restart_and_isolated_processes_cannot_share_read_markers() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("attention.json");
        let store = Attention::new(Some(path.clone())).unwrap();
        store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("ready", "one"),
                reply("old"),
                true,
                None,
            )
            .await
            .unwrap();
        let unread = store
            .observe(
                ("agent", "host"),
                Some("process"),
                &activity("ready", "two"),
                reply("new"),
                true,
                None,
            )
            .await
            .unwrap();
        drop(store);
        let store = Attention::new(Some(path)).unwrap();
        assert!(store.view("agent").await.unread_reply);
        let other = store
            .observe(
                ("other", "other-host"),
                Some("other-process"),
                &activity("ready", "one"),
                reply("new"),
                true,
                None,
            )
            .await
            .unwrap();
        let mut wrong = read(&other);
        wrong.conversation = unread.conversation.clone();
        assert_eq!(store.read(wrong).await.unwrap_err().0, StatusCode::CONFLICT);
        store
            .observe(
                ("agent", "host"),
                Some("replacement"),
                &activity("ready", "three"),
                reply("new"),
                true,
                None,
            )
            .await
            .unwrap();
        assert_eq!(
            store.read(read(&unread)).await.unwrap_err().0,
            StatusCode::CONFLICT
        );
        assert!(!store.view("agent").await.finished);
    }
}
