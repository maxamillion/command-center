//! One-use message grants prevent retries, stale endpoints, and process replacement.
use crate::{ApiError, AppState};
use axum::{
    Json,
    extract::{Path, Query, State},
    http::StatusCode,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::HashMap,
    sync::Arc,
    time::{Duration, Instant},
};
use std::{collections::HashSet, io::Write, path::PathBuf};
use tokio::sync::Mutex;

#[derive(Default)]
pub(crate) struct Agents {
    grants: Mutex<HashMap<String, Grant>>,
    approvals: Mutex<HashMap<String, ApprovalGrant>>,
    submitted: Mutex<HashSet<String>>,
    submitted_path: Option<PathBuf>,
}
impl Agents {
    pub fn new(path: Option<PathBuf>) -> anyhow::Result<Self> {
        let submitted: HashSet<String> = match &path {
            Some(p) if p.exists() => {
                anyhow::ensure!(
                    p.metadata()?.len() <= 1024 * 1024,
                    "Approval ledger too large"
                );
                serde_json::from_slice(&std::fs::read(p)?)?
            }
            _ => HashSet::new(),
        };
        anyhow::ensure!(
            submitted.len() <= 4096
                && submitted
                    .iter()
                    .all(|s| s.len() == 64 && s.bytes().all(|b| b.is_ascii_hexdigit())),
            "Invalid approval ledger"
        );
        Ok(Self {
            submitted: Mutex::new(submitted),
            submitted_path: path,
            ..Self::default()
        })
    }
    async fn save_submitted(&self, submitted: &HashSet<String>) -> Result<(), ApiError> {
        let Some(path) = self.submitted_path.clone() else {
            return Ok(());
        };
        let bytes = serde_json::to_vec(submitted).map_err(anyhow::Error::from)?;
        tokio::task::spawn_blocking(move || -> anyhow::Result<()> {
            let parent = path
                .parent()
                .filter(|p| !p.as_os_str().is_empty())
                .unwrap_or_else(|| std::path::Path::new("."));
            let mut temporary = tempfile::NamedTempFile::new_in(parent)?;
            temporary.write_all(&bytes)?;
            temporary.as_file().sync_all()?;
            temporary.persist(&path)?;
            std::fs::File::open(parent)?.sync_all()?;
            Ok(())
        })
        .await
        .map_err(anyhow::Error::from)??;
        Ok(())
    }
}
pub(crate) struct Grant {
    pub(crate) host: String,
    pub(crate) target: Target,
    pub(crate) provider: String,
    pub(crate) identity: String,
    pub(crate) screen: String,
    at: Instant,
    used: bool,
}
#[derive(Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Target {
    pub(crate) session: String,
    pub(crate) window: String,
    pub(crate) pane: String,
    pub(crate) connection_revision: String,
    pub(crate) conversation: Option<String>,
    pub(crate) before: Option<u64>,
    pub(crate) history_cursor: Option<String>,
    pub(crate) history_view: Option<String>,
    pub(crate) known_version: Option<String>,
    pub(crate) known_branch: Option<String>,
}
impl Target {
    pub(crate) fn request(&self) -> Value {
        json!({"session":self.session,"window":self.window,"pane":self.pane,
               "conversation":self.conversation,"before":self.before,"history_cursor":self.history_cursor,"history_view":self.history_view,"known_version":self.known_version,"known_branch":self.known_branch,"action":"details"})
    }
    pub(crate) fn is_latest(&self) -> bool {
        self.before.is_none() && self.history_cursor.is_none()
    }
}
pub(crate) fn result(value: Value) -> Result<Value, ApiError> {
    if let Some(error) = value.get("error").and_then(Value::as_str) {
        return Err(ApiError(
            StatusCode::from_u16(value["status"].as_u64().unwrap_or(502) as u16)
                .unwrap_or(StatusCode::BAD_GATEWAY),
            error.into(),
        ));
    }
    value
        .get("ok")
        .cloned()
        .ok_or_else(|| ApiError(StatusCode::BAD_GATEWAY, "Invalid agent response".into()))
}

const CAPABILITY_NAMES: [&str; 11] = [
    "process_observation",
    "project_history",
    "current_session_linkage",
    "verified_phase",
    "ordinary_message_submission",
    "acceptance_confirmation",
    "native_approval",
    "launch",
    "resume",
    "restart",
    "close_agent",
];

pub(crate) fn capability_available(provider: &str, capability: &str) -> bool {
    let established = matches!(provider, "codex" | "claude" | "pi");
    if !CAPABILITY_NAMES.contains(&capability) {
        return false;
    }
    if provider == "goose" {
        return matches!(
            capability,
            "process_observation" | "project_history" | "close_agent"
        );
    }
    if !established {
        return false;
    }
    !(provider == "pi" && capability == "native_approval")
}

fn capability_reason(provider: &str, capability: &str) -> &'static str {
    match (provider, capability) {
        ("pi", "native_approval") => "Pi dialogs must be handled in the terminal.",
        ("goose", "process_observation") => {
            "Goose process observation is available; session linkage and lifecycle evidence are not."
        }
        ("goose", "project_history") => {
            "Goose project history is read-only and is not linked to the running process."
        }
        ("goose", "current_session_linkage") => {
            "The native Goose CLI does not expose verified current-session identity."
        }
        ("goose", "verified_phase") => {
            "No authoritative native Goose lifecycle evidence is available."
        }
        ("goose", "ordinary_message_submission") => {
            "Guarded Goose message submission is not available. Respond in the terminal."
        }
        ("goose", "acceptance_confirmation") => "Native Goose input acceptance cannot be verified.",
        ("goose", "native_approval") => "Goose approvals must be handled in the terminal.",
        ("goose", "launch") => "Goose launch support is not implemented yet.",
        ("goose", "resume") => "Exact Goose conversation ownership is not available.",
        ("goose", "restart") => "Exact Goose conversation ownership is not available.",
        ("goose", "close_agent") => {
            "Goose Close agent is available after an exact process and topology review."
        }
        _ => "This provider capability is unavailable.",
    }
}

pub(crate) fn capability_payload(provider: &str) -> Value {
    let mut values = serde_json::Map::new();
    for name in CAPABILITY_NAMES {
        let available = capability_available(provider, name);
        values.insert(
            name.to_owned(),
            json!({
                "available": available,
                "reason": if available { Value::Null } else { json!(capability_reason(provider, name)) },
            }),
        );
    }
    Value::Object(values)
}

pub(crate) fn require_capability(provider: &str, capability: &str) -> Result<(), ApiError> {
    if !matches!(provider, "codex" | "claude" | "pi" | "goose") {
        return Err(ApiError(
            StatusCode::BAD_REQUEST,
            "Unsupported agent provider".into(),
        ));
    }
    if !CAPABILITY_NAMES.contains(&capability) {
        return Err(ApiError(
            StatusCode::INTERNAL_SERVER_ERROR,
            "Unknown agent capability".into(),
        ));
    }
    if capability_available(provider, capability) {
        Ok(())
    } else {
        Err(ApiError(
            StatusCode::CONFLICT,
            capability_reason(provider, capability).into(),
        ))
    }
}

pub(crate) async fn conversation(
    State(state): State<Arc<AppState>>,
    Path(host): Path<String>,
    Query(target): Query<Target>,
) -> Result<Json<Value>, ApiError> {
    if target
        .history_cursor
        .as_ref()
        .is_some_and(|cursor| cursor.len() > 1024)
        || target
            .history_view
            .as_ref()
            .is_some_and(|cursor| cursor.len() > 1024)
        || (target.history_cursor.is_some() && target.before.is_some())
        || (target.history_view.is_some()
            && (target.history_cursor.is_some() || target.before.is_some()))
    {
        return Err(ApiError(
            StatusCode::BAD_REQUEST,
            "Invalid history paging cursor".into(),
        ));
    }
    let _slot = state.file_slots.try_acquire().map_err(|_| {
        ApiError(
            StatusCode::TOO_MANY_REQUESTS,
            "Agent/file operations busy; retry shortly".into(),
        )
    })?;
    let machine = state.registry.get(&host).await?;
    if machine.connection_revision != target.connection_revision {
        return Err(ApiError(
            StatusCode::CONFLICT,
            "Machine changed; refresh the agent list".into(),
        ));
    }
    let (endpoint, attention_key) = crate::attention::scope(
        &machine.config,
        &target.session,
        &target.window,
        &target.pane,
    );
    let (watch, version, order) = state.attention.observation_args(&attention_key).await;
    let mut request = target.request();
    request["known_reply_version"] = json!(version);
    if target.conversation.is_none() || target.conversation == watch {
        request["known_reply_order_key"] = json!(order);
    }
    let mut value = result(machine.transport.agent_request(request).await?)?;
    if state.registry.get(&host).await?.connection_revision != target.connection_revision {
        return Err(ApiError(
            StatusCode::CONFLICT,
            "Machine changed during observation".into(),
        ));
    }
    let activity = crate::queue::Activity::from_value(
        &value["activity"],
        value["context"].as_str().unwrap_or(""),
    );
    let provider = value["provider"]
        .as_str()
        .ok_or_else(|| ApiError(StatusCode::BAD_GATEWAY, "Agent provider unavailable".into()))?
        .to_owned();
    value["capabilities"] = capability_payload(&provider);
    if !capability_available(&provider, "ordinary_message_submission")
        || !capability_available(&provider, "acceptance_confirmation")
    {
        value["send_available"] = json!(false);
        let name = if capability_available(&provider, "ordinary_message_submission") {
            "acceptance_confirmation"
        } else {
            "ordinary_message_submission"
        };
        value["send_reason"] = value["capabilities"][name]["reason"].clone();
    }
    let attention =
        !value["approval"].is_null() || activity.state == crate::queue::AgentState::Approval;
    if target.is_latest() {
        let reply = crate::attention::parse_reply(&value["reply"]);
        let view = state
            .attention
            .observe(
                (&attention_key, &endpoint),
                value["instance"].as_str(),
                &activity,
                reply,
                false,
                target.conversation.as_deref(),
            )
            .await?;
        value["read_state"] = json!(view);
        if provider == "goose" && value["reply"]["displayed"] != true {
            // Observing a reply for attention does not mean it was rendered in
            // the selected bounded history view. Never acknowledge unseen text.
            value["read_state"]["reply_cursor"] = Value::Null;
        }
    }
    if let Some(observation) = value
        .as_object_mut()
        .and_then(|v| v.remove("_outbox_observation"))
    {
        let scope = format!(
            "{attention_key}/{}",
            value["instance"].as_str().unwrap_or("")
        );
        value["outbox_entries"] =
            json!(crate::outbox::history_receipts(&state, scope, &observation).await?);
    }
    if let Some(messages) = value["messages"].as_array_mut() {
        for message in messages {
            if let Some(object) = message.as_object_mut() {
                object.remove("legacy_position");
            }
        }
    }
    value["card"] = json!(
        crate::agent_cards::view(
            &state,
            attention_key.clone(),
            value["instance"].as_str().unwrap_or("").to_owned()
        )
        .await?
    );
    value["activity"] = json!(activity);
    value["attention"] = json!(attention);
    if attention {
        value["send_available"] = json!(false);
        value["send_reason"] = json!(
            "Approval prompt detected. Respond in the terminal before sending a new message."
        );
    } else if value["send_available"] != true && !value["send_reason"].is_string() {
        value["send_reason"] = json!(
            "Live process verification unavailable or pane is in copy mode. Use Open terminal."
        );
    }
    crate::questions::enrich(&state, &host, &target, &attention_key, &mut value).await?;
    if !capability_available(&provider, "native_approval") {
        value["approval"] = Value::Null;
    }
    if !value["approval"].is_null() && target.is_latest() {
        let mut grants = state.agents.approvals.lock().await;
        grants.retain(|_, g| g.grant.at.elapsed() < Duration::from_secs(120));
        if grants.len() < 512 {
            let token = uuid::Uuid::new_v4().to_string();
            let approval_id = value["approval"]["id"].as_str().unwrap_or("").to_owned();
            let claim = format!(
                "{:x}",
                Sha256::digest(
                    format!(
                        "{attention_key}/{}/{approval_id}",
                        value["instance"].as_str().unwrap_or("")
                    )
                    .as_bytes()
                )
            );
            let submitted = state.agents.submitted.lock().await.contains(&claim);
            value["approval"]["submitted"] = json!(submitted);
            if !submitted {
                grants.insert(
                    token.clone(),
                    ApprovalGrant {
                        grant: Grant {
                            host: host.clone(),
                            target: target.clone(),
                            provider: provider.clone(),
                            identity: value["instance"].as_str().unwrap_or("").into(),
                            screen: value["screen"].as_str().unwrap_or("").into(),
                            at: Instant::now(),
                            used: false,
                        },
                        approval_id,
                        claim,
                        choices: value["approval"]["choices"]
                            .as_array()
                            .unwrap()
                            .iter()
                            .filter_map(|c| c["id"].as_str().map(str::to_owned))
                            .collect(),
                    },
                );
                value["approval"]["token"] = json!(token);
            }
        }
        value["send_reason"] = json!("Review the tool request below and choose a response.");
    }
    if let Some(choices) = value
        .get_mut("approval")
        .and_then(|a| a.get_mut("choices"))
        .and_then(Value::as_array_mut)
    {
        for choice in choices {
            choice.as_object_mut().unwrap().remove("key");
        }
    }
    if value["send_available"] == true
        && capability_available(&provider, "ordinary_message_submission")
        && capability_available(&provider, "acceptance_confirmation")
        && target.is_latest()
    {
        // A durable send may follow only a process-linked conversation, never a
        // project-history selection. Native identity survives backend restart.
        let mut target = target;
        target.conversation = if value["association"] == "process" {
            value["selected"].as_str().map(str::to_owned)
        } else {
            None
        };
        let mut grants = state.agents.grants.lock().await;
        grants.retain(|_, g| g.at.elapsed() < Duration::from_secs(120));
        if grants.len() >= 512 {
            return Err(ApiError(
                StatusCode::TOO_MANY_REQUESTS,
                "Too many active message drafts; try again shortly".into(),
            ));
        }
        let token = uuid::Uuid::new_v4().to_string();
        grants.insert(
            token.clone(),
            Grant {
                host,
                target,
                provider,
                identity: value["instance"].as_str().unwrap_or("").into(),
                screen: value["screen"].as_str().unwrap_or("").into(),
                at: Instant::now(),
                used: false,
            },
        );
        value["message_token"] = json!(token);
    }
    // Screen fingerprints are internal to the grant, not response capabilities.
    value.as_object_mut().unwrap().remove("screen");
    Ok(Json(value))
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Message {
    token: String,
    text: String,
    id: Option<String>,
    attachments: Option<Vec<crate::attachments::Source>>,
}
pub(crate) async fn message(
    State(state): State<Arc<AppState>>,
    Path(host): Path<String>,
    Json(message): Json<Message>,
) -> Result<Json<Value>, ApiError> {
    if message.text.trim().is_empty()
        || message.text.len() > 12000
        || message
            .text
            .chars()
            .any(|c| c.is_control() && c != '\n' && c != '\t')
    {
        return Err(ApiError(
            StatusCode::BAD_REQUEST,
            "Message must be 1–12000 UTF-8 bytes without control characters".into(),
        ));
    }
    if let Some(id) = message.id {
        return crate::outbox::enqueue(
            state,
            host,
            id,
            message.token,
            message.text,
            message.attachments,
        )
        .await;
    }
    if message.attachments.is_some() {
        return Err(ApiError(
            StatusCode::BAD_REQUEST,
            "Attachments require a durable message UUID".into(),
        ));
    }
    let _slot = state.file_slots.try_acquire().map_err(|_| {
        ApiError(
            StatusCode::TOO_MANY_REQUESTS,
            "Agent/file operations busy; retry shortly".into(),
        )
    })?;
    // Consume before transport IO. A timeout or backend restart must never replay input.
    let (target, provider, identity, screen) = {
        let mut grants = state.agents.grants.lock().await;
        let grant = grants.get_mut(&message.token).ok_or_else(|| {
            ApiError(
                StatusCode::GONE,
                "Message authorization expired. Refresh and review before sending.".into(),
            )
        })?;
        if grant.host != host || grant.used || grant.at.elapsed() >= Duration::from_secs(120) {
            return Err(ApiError(
                StatusCode::GONE,
                "Message authorization expired or already used. Do not retry an uncertain send."
                    .into(),
            ));
        }
        require_capability(&grant.provider, "ordinary_message_submission")?;
        require_capability(&grant.provider, "acceptance_confirmation")?;
        grant.used = true;
        (
            grant.target.clone(),
            grant.provider.clone(),
            grant.identity.clone(),
            grant.screen.clone(),
        )
    };
    require_capability(&provider, "ordinary_message_submission")?;
    let machine = state.registry.get(&host).await?;
    if machine.connection_revision != target.connection_revision {
        return Err(ApiError(
            StatusCode::CONFLICT,
            "Machine changed; message was not sent".into(),
        ));
    }
    // Serialize explicit sends with endpoint edits/file writes on this connection.
    let _guard = machine.file_writes.lock().await;
    if state.registry.get(&host).await?.connection_revision != target.connection_revision {
        return Err(ApiError(
            StatusCode::CONFLICT,
            "Machine changed; message was not sent".into(),
        ));
    }
    let mut request = target.request();
    request["action"] = json!("send");
    request["identity"] = json!(identity);
    request["screen"] = json!(screen);
    request["text"] = json!(message.text);
    let response = result(machine.transport.agent_request(request).await?)?;
    Ok(Json(response))
}

pub(crate) async fn claim_message(
    state: &AppState,
    host: &str,
    token: &str,
) -> Result<Grant, ApiError> {
    let mut grants = state.agents.grants.lock().await;
    let g = grants.get_mut(token).ok_or_else(|| {
        ApiError(
            StatusCode::GONE,
            "Message authorization expired. Refresh and review.".into(),
        )
    })?;
    if g.host != host || g.used || g.at.elapsed() >= Duration::from_secs(120) {
        return Err(ApiError(
            StatusCode::GONE,
            "Message authorization expired or already used. Check the outbox before trying again."
                .into(),
        ));
    }
    require_capability(&g.provider, "ordinary_message_submission")?;
    require_capability(&g.provider, "acceptance_confirmation")?;
    g.used = true;
    Ok(Grant {
        host: g.host.clone(),
        target: g.target.clone(),
        provider: g.provider.clone(),
        identity: g.identity.clone(),
        screen: g.screen.clone(),
        at: g.at,
        used: true,
    })
}

struct ApprovalGrant {
    grant: Grant,
    approval_id: String,
    claim: String,
    choices: Vec<String>,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Decision {
    token: String,
    choice: String,
}
pub(crate) async fn approval(
    State(state): State<Arc<AppState>>,
    Path(host): Path<String>,
    Json(decision): Json<Decision>,
) -> Result<Json<Value>, ApiError> {
    let _slot = state.file_slots.try_acquire().map_err(|_| {
        ApiError(
            StatusCode::TOO_MANY_REQUESTS,
            "Agent operations busy".into(),
        )
    })?;
    let (target, provider, identity, screen, approval_id, claim) = {
        let mut grants = state.agents.approvals.lock().await;
        let g = grants.get_mut(&decision.token).ok_or_else(|| {
            ApiError(
                StatusCode::GONE,
                "Approval authorization expired; refresh and review".into(),
            )
        })?;
        if g.grant.host != host || g.grant.used || g.grant.at.elapsed() >= Duration::from_secs(120)
        {
            return Err(ApiError(
                StatusCode::GONE,
                "Approval authorization expired or already used".into(),
            ));
        }
        if !g.choices.contains(&decision.choice) {
            return Err(ApiError(
                StatusCode::BAD_REQUEST,
                "Unknown approval choice".into(),
            ));
        }
        require_capability(&g.grant.provider, "native_approval")?;
        g.grant.used = true;
        (
            g.grant.target.clone(),
            g.grant.provider.clone(),
            g.grant.identity.clone(),
            g.grant.screen.clone(),
            g.approval_id.clone(),
            g.claim.clone(),
        )
    };
    require_capability(&provider, "native_approval")?;
    let machine = state.registry.get(&host).await?;
    let _guard = machine.file_writes.lock().await;
    if state.registry.get(&host).await?.connection_revision != target.connection_revision {
        return Err(ApiError(
            StatusCode::CONFLICT,
            "Machine changed; decision was not sent".into(),
        ));
    }
    // Claim the prompt, not just this browser's token. Retain uncertain deliveries.
    {
        let mut submitted = state.agents.submitted.lock().await;
        if submitted.len() >= 4096 || !submitted.insert(claim.clone()) {
            return Err(ApiError(StatusCode::GONE, "This prompt already has a submitted decision, or approval capacity is exhausted. Check the agent.".into()));
        }
        // Persist before transport IO, so restart cannot enable uncertain replays.
        state.agents.save_submitted(&submitted).await?;
    }
    let mut request = target.request();
    request["action"] = json!("approval");
    request["identity"] = json!(identity);
    request["screen"] = json!(screen);
    request["approval_id"] = json!(approval_id);
    request["choice"] = json!(decision.choice);
    let response = result(machine.transport.agent_request(request).await?);
    if let Err(ApiError(status, _)) = &response
        && (*status == StatusCode::CONFLICT || *status == StatusCode::BAD_REQUEST)
    {
        let mut submitted = state.agents.submitted.lock().await;
        submitted.remove(&claim);
        state.agents.save_submitted(&submitted).await?;
    }
    Ok(Json(response?))
}

#[cfg(test)]
mod capability_tests {
    use super::*;

    #[test]
    fn python_and_rust_capability_contracts_agree_exhaustively() {
        use std::io::Write;
        use std::process::{Command, Stdio};
        let mut child = Command::new("python3")
            .args([
                "-c",
                r#"
import sys,json
ns={'__name__':'cc_capability_contract'}
exec(compile(sys.stdin.read(),'<helper>','exec'),ns)
result={}
for provider in ns['PROVIDER_CAPABILITIES']:
    result[provider]=ns['capability_payload'](provider)
    for name,capability in result[provider].items():
        try:
            ns['require_capability'](provider,name)
            assert capability['available']
        except ns['Failure'] as error:
            assert not capability['available'] and error.status==409
print(json.dumps(result))
"#,
            ])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        child
            .stdin
            .take()
            .unwrap()
            .write_all(include_bytes!("agent_remote.py"))
            .unwrap();
        let output = child.wait_with_output().unwrap();
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        let payload: Value = serde_json::from_slice(&output.stdout).unwrap();
        assert_eq!(payload.as_object().unwrap().len(), 4);
        for provider in ["codex", "claude", "pi", "goose"] {
            let capabilities = payload[provider].as_object().unwrap();
            assert_eq!(capabilities.len(), CAPABILITY_NAMES.len());
            for name in CAPABILITY_NAMES {
                let available = capability_available(provider, name);
                assert_eq!(
                    capabilities[name]["available"], available,
                    "{provider}/{name}"
                );
                assert_eq!(require_capability(provider, name).is_ok(), available);
                if available {
                    assert!(capabilities[name]["reason"].is_null());
                } else {
                    assert!(
                        capabilities[name]["reason"]
                            .as_str()
                            .is_some_and(|s| !s.is_empty())
                    );
                }
            }
        }
    }

    #[test]
    fn goose_history_is_read_only_and_only_reviewed_close_is_available() {
        for capability in [
            "current_session_linkage",
            "verified_phase",
            "ordinary_message_submission",
            "acceptance_confirmation",
            "native_approval",
            "launch",
            "resume",
            "restart",
        ] {
            assert!(!capability_available("goose", capability));
            let value = capability_payload("goose");
            assert_eq!(value[capability]["available"], false);
            assert!(
                value[capability]["reason"]
                    .as_str()
                    .is_some_and(|s| !s.is_empty())
            );
            assert_eq!(
                require_capability("goose", capability).unwrap_err().0,
                StatusCode::CONFLICT
            );
        }
        assert!(capability_available("goose", "process_observation"));
        assert!(capability_available("goose", "project_history"));
        let value = capability_payload("goose");
        assert_eq!(value["process_observation"]["available"], true);
        assert!(value["process_observation"]["reason"].is_null());
        assert_eq!(value["project_history"]["available"], true);
        assert!(capability_available("goose", "close_agent"));
        assert_eq!(value["close_agent"]["available"], true);
        assert!(value["close_agent"]["reason"].is_null());
        require_capability("goose", "close_agent").unwrap();
        assert!(value["project_history"]["reason"].is_null());
    }

    #[test]
    fn existing_provider_capabilities_preserve_supported_actions() {
        for provider in ["codex", "claude", "pi"] {
            assert!(capability_available(
                provider,
                "ordinary_message_submission"
            ));
            assert!(capability_available(provider, "acceptance_confirmation"));
            assert!(capability_available(provider, "launch"));
            assert!(capability_available(provider, "restart"));
        }
        assert!(capability_available("claude", "native_approval"));
        assert!(!capability_available("pi", "native_approval"));
        assert_eq!(
            require_capability("other", "launch").unwrap_err().0,
            StatusCode::BAD_REQUEST
        );
    }
}
