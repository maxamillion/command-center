"""Bounded local/SSH agent observation and explicit human-directed tmux input.
No installation, daemon, contents in logs, or arbitrary log path from clients.
"""
import hashlib
import base64
import shutil
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import sys
import uuid
import time
from datetime import datetime
from datetime import timezone

# Adding a provider requires an explicit audit of each provider-specific path;
# unsupported values must not inherit the Claude fallbacks below.
PROVIDER_NAMES = {
    'codex': frozenset(('codex',)),
    'claude': frozenset(('claude',)),
    'pi': frozenset(('pi', 'pi-coding-agent')),
    'goose': frozenset(('goose', 'goose-cli')),
}
AGENT_PROVIDERS = frozenset(PROVIDER_NAMES)
CAPABILITY_NAMES = (
    'process_observation', 'project_history', 'current_session_linkage',
    'verified_phase', 'ordinary_message_submission', 'acceptance_confirmation',
    'native_approval', 'launch', 'resume', 'restart', 'close_agent',
)
_ESTABLISHED_CAPABILITIES = frozenset(CAPABILITY_NAMES) - frozenset(('native_approval',))
_GOOSE_CAPABILITIES = frozenset(('process_observation','project_history','close_agent'))
PROVIDER_CAPABILITIES = {
    'codex': frozenset(CAPABILITY_NAMES),
    'claude': frozenset(CAPABILITY_NAMES),
    'pi': _ESTABLISHED_CAPABILITIES,
    # Goose project history is a persisted read-only projection. The other
    # capabilities remain disabled until separate native contracts prove them.
    'goose': _GOOSE_CAPABILITIES,
}

class Failure(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message

def fail(status, message):
    raise Failure(status, message)

def require_provider(value):
    if not isinstance(value, str) or value not in AGENT_PROVIDERS:
        fail(400, 'Unsupported agent provider')
    return value

def provider_from_names(names):
    for kind, aliases in PROVIDER_NAMES.items():
        if any(name in aliases for name in names):
            return kind
    return None

def capability_reason(provider, capability):
    return {
        ('pi', 'native_approval'): 'Pi dialogs must be handled in the terminal.',
        ('goose', 'process_observation'): 'Goose process observation is available; session linkage and lifecycle evidence are not.',
        ('goose', 'project_history'): 'Goose project history is read-only, unlinked history from the configured project.',
        ('goose', 'current_session_linkage'): 'The native Goose CLI does not expose verified current-session identity.',
        ('goose', 'verified_phase'): 'No authoritative native Goose lifecycle evidence is available.',
        ('goose', 'ordinary_message_submission'): 'Guarded Goose message submission is not available. Respond in the terminal.',
        ('goose', 'acceptance_confirmation'): 'Native Goose input acceptance cannot be verified.',
        ('goose', 'native_approval'): 'Goose approvals must be handled in the terminal.',
        ('goose', 'launch'): 'Goose launch support is not implemented yet.',
        ('goose', 'resume'): 'Exact Goose conversation ownership is not available.',
        ('goose', 'restart'): 'Exact Goose conversation ownership is not available.',
        ('goose', 'close_agent'): 'Goose Close agent is available after an exact process and topology review.',
    }.get((provider, capability), 'This provider capability is unavailable.')

def capability_available(provider, capability):
    return capability in PROVIDER_CAPABILITIES.get(provider, ())

def require_capability(provider, capability):
    if not isinstance(provider, str) or provider not in PROVIDER_CAPABILITIES:
        fail(400, 'Unsupported agent provider')
    if not isinstance(capability, str) or capability not in CAPABILITY_NAMES:
        fail(500, 'Unknown agent capability')
    if not capability_available(provider, capability):
        fail(409, capability_reason(provider, capability))

def capability_payload(provider):
    if not isinstance(provider, str) or provider not in PROVIDER_CAPABILITIES:
        fail(400, 'Unsupported agent provider')
    return {name: dict(available=capability_available(provider, name),
                       reason=None if capability_available(provider, name) else capability_reason(provider, name))
            for name in CAPABILITY_NAMES}

def tmux(request, *args, input=None):
    command = ['tmux', '-u']
    if request.get('socket'):
        command += ['-S', request['socket']]
    env = dict(os.environ)
    env.pop('TMUX', None)
    env.pop('TMUX_PANE', None)
    result = subprocess.run(command + list(args), input=input, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, timeout=8)
    if result.returncode:
        fail(409, 'Tmux target is unavailable; refresh the agent')
    return result.stdout.decode('utf-8', errors='replace')

def proc(pid):
    base = Path('/proc') / str(pid)
    raw = (base / 'stat').read_text()
    fields = raw[raw.rindex(')') + 2:].split()
    return base, fields[19], int(fields[5])  # starttime and terminal foreground group

def process_info(pid):
    base=Path('/proc')/str(pid)
    fields=(base/'stat').read_text().rsplit(')',1)[1].split()
    return dict(pid=int(pid),base=base,start=fields[19],parent=int(fields[1]),group=int(fields[2]),tty=int(fields[4]),foreground=int(fields[5]))


def process_argv(base):
    with (base/'cmdline').open('rb') as source:
        raw=source.read(65537)
    if len(raw)>65536 or not raw.endswith(b'\0'):
        return []
    try:
        return [part.decode(errors='strict') for part in raw[:-1].split(b'\0')]
    except UnicodeError:
        return []


def _parse_cli_options(args, boolean_options, value_options, repeatable=()):
    values={}
    aliases={canonical:canonical for canonical in value_options}
    aliases.update({alias:canonical for canonical,shorts in value_options.items() for alias in shorts})
    bool_aliases={canonical:canonical for canonical in boolean_options}
    bool_aliases.update({alias:canonical for canonical,shorts in boolean_options.items() for alias in shorts})
    repeatable=set(repeatable)
    i=0
    while i<len(args):
        token=args[i]
        if token in ('--','-') or not token.startswith('-') or token in ('--help','-h'):
            return None
        inline=None
        if token.startswith('--'):
            option,equals,inline=token.partition('=')
            inline=inline if equals else None
        else:
            option=token[:2]
            suffix=token[2:]
            if suffix:
                inline=suffix
        canonical=bool_aliases.get(option)
        if canonical is not None:
            if inline is not None or canonical in values:
                return None
            values[canonical]=True
            i+=1
            continue
        canonical=aliases.get(option)
        if canonical is None:
            return None
        if canonical in values and canonical not in repeatable:
            return None
        if inline is None:
            i+=1
            if i>=len(args) or args[i].startswith('-') and not (canonical=='--instructions' and args[i]=='-'):
                return None
            inline=args[i]
        if canonical in repeatable:
            values.setdefault(canonical,[]).append(inline)
        else:
            values[canonical]=inline
        i+=1
    return values


_SESSION_BOOLEAN_OPTIONS={
    '--resume':('-r',), '--fork':(), '--edit':(), '--history':(), '--debug':(),
    '--no-profile':(),
}
_SESSION_VALUE_OPTIONS={
    '--name':('-n',), '--session-id':('--id',), '--path':(), '--system':(),
    '--max-tool-repetitions':(), '--max-turns':(), '--container':(),
    '--with-extension':(), '--with-streamable-http-extension':(), '--with-builtin':(),
    '--provider':(), '--model':(),
}
_RUN_BOOLEAN_OPTIONS={
    '--interactive':('-s',), '--no-session':(), '--resume':('-r',), '--stats':(),
    '--debug':(), '--no-profile':(), '--quiet':('-q',), '--explain':(),
    '--render-recipe':(),
}
_RUN_VALUE_OPTIONS={
    '--instructions':('-i',), '--text':('-t',), '--recipe':(), '--system':(),
    '--params':(), '--sub-recipe':(), '--name':('-n',), '--session-id':('--id',),
    '--path':(), '--max-tool-repetitions':(), '--max-turns':(), '--container':(),
    '--with-extension':(), '--with-streamable-http-extension':(), '--with-builtin':(),
    '--provider':(), '--model':(), '--output-format':(), '--scheduled-job-id':(),
}


def goose_invocation(argv):
    """Return a bounded interactive mode for supported native Goose CLI forms."""
    if not argv or os.path.basename(argv[0]).lower() not in ('goose','goose-cli'):
        return None
    args=argv[1:]
    if not args:
        return None
    if args[0] in ('session','s'):
        options=_parse_cli_options(args[1:],_SESSION_BOOLEAN_OPTIONS,_SESSION_VALUE_OPTIONS,
                                   ('--with-extension','--with-streamable-http-extension','--with-builtin'))
        if options is None:
            return None
        identifiers=sum(name in options for name in ('--name','--session-id','--path'))
        if identifiers>1 or ('--session-id' in options and '--resume' not in options):
            return None
        if any(name in options for name in ('--fork','--edit','--history')) and '--resume' not in options:
            return None
        return 'session'
    if args[0]=='run':
        options=_parse_cli_options(args[1:],_RUN_BOOLEAN_OPTIONS,_RUN_VALUE_OPTIONS,
                                   ('--params','--sub-recipe','--with-extension',
                                    '--with-streamable-http-extension','--with-builtin'))
        if options is None or '--interactive' not in options:
            return None
        identifiers=sum(name in options for name in ('--name','--session-id','--path'))
        inputs=sum(name in options for name in ('--instructions','--text','--recipe'))
        if identifiers>1 or inputs>1:
            return None
        if '--session-id' in options and '--resume' not in options:
            return None
        if '--no-session' in options and any(name in options for name in ('--resume','--name','--path')):
            return None
        if '--scheduled-job-id' in options or '--explain' in options or '--render-recipe' in options:
            return None
        if '--recipe' in options and '--system' in options:
            return None
        return 'run-interactive'
    return None


def goose_data_dir(env, platform=None, home=None):
    """Resolve Goose's native data directory from path-only process settings."""
    platform=platform or sys.platform
    if platform.startswith('win'):
        from pathlib import PureWindowsPath
        path_type=PureWindowsPath
    else:
        from pathlib import PurePosixPath
        path_type=PurePosixPath
    home_path=path_type(home) if home else path_type(env.get('HOME',''))
    if not str(home_path) or not home_path.is_absolute():
        home_path=path_type(Path.home().as_posix())
    root=path_type(env.get('GOOSE_PATH_ROOT',''))
    if root.is_absolute():
        return root/'data'
    if platform.startswith('win'):
        appdata=path_type(env.get('APPDATA',''))
        if not appdata.is_absolute():
            appdata=home_path/'AppData'/'Roaming'
        return appdata/'Block'/'goose'/'data'
    if platform=='darwin':
        return home_path/'Library'/'Application Support'/'Block'/'goose'
    xdg=path_type(env.get('XDG_DATA_HOME',''))
    base=xdg if xdg.is_absolute() else home_path/'.local'/'share'
    return base/'goose'


def goose_data_identity(path):
    canonical=os.path.realpath(str(path))
    try:
        info=os.stat(canonical)
        store=os.stat(os.path.join(canonical,'sessions','sessions.db'))
        identity=f'{canonical}:{info.st_dev}:{info.st_ino}:store:{store.st_dev}:{store.st_ino}'
    except FileNotFoundError:
        try:
            info=os.stat(canonical)
            identity=f'{canonical}:{info.st_dev}:{info.st_ino}:store:missing'
        except OSError:
            identity=f'{canonical}:missing:store:missing'
    except OSError:
        identity=f'{canonical}:missing'
    return hashlib.sha256(('goose-data-v1:'+identity).encode()).hexdigest()


GOOSE_STORE_SCHEMA_VERSION = 17
GOOSE_STORE_MAX_QUERY_SECONDS = 0.25
GOOSE_STORE_MAX_TOTAL_SECONDS = 1.0
GOOSE_STORE_MAX_QUERY_STEPS = 1200
GOOSE_STORE_MAX_SESSIONS = 20
GOOSE_STORE_MAX_MESSAGES = 100
GOOSE_STORE_MAX_ACTIVITY_ROWS = 2000
GOOSE_STORE_MAX_ACTIVITY_BYTES = 2 * 1024 * 1024
GOOSE_STORE_MAX_ACTIVITY_EVENTS = 5000
GOOSE_STORE_MAX_HISTORY_PAGES = 5
GOOSE_STORE_MAX_HISTORY_ROWS = GOOSE_STORE_MAX_MESSAGES * GOOSE_STORE_MAX_HISTORY_PAGES
GOOSE_STORE_MAX_HISTORY_BYTES = 2 * 1024 * 1024
GOOSE_STORE_MAX_CELL_BYTES = 128 * 1024
GOOSE_STORE_MAX_PAGE_BYTES = 512 * 1024
GOOSE_STORE_MAX_WAL_BYTES = 256 * 1024 * 1024
GOOSE_STORE_MAX_SHM_BYTES = 64 * 1024 * 1024


def _goose_file_identity(path, *, required=True):
    try:
        info=os.lstat(path)
    except FileNotFoundError:
        if required: fail(409,'Goose session store is unavailable')
        return None
    except OSError:
        fail(409,'Goose session store is unavailable')
    if (stat.S_ISLNK(info.st_mode) or info.st_uid!=os.geteuid()
            or info.st_mode & 0o022):
        fail(409,'Goose session store path is unsafe')
    if not stat.S_ISREG(info.st_mode):
        fail(409,'Goose session store is unavailable')
    return (info.st_dev,info.st_ino,info.st_mode & 0o170000)


def _goose_text_is_bounded(value,limit,nullable=False):
    if value is None: return nullable
    if not isinstance(value,str) or len(value)>limit or '\0' in value: return False
    try: value.encode('utf-8')
    except UnicodeError: return False
    return True


class GooseSessionStore:
    """Read schema-17 Goose history without initializing or mutating its store."""
    _SCHEMA_COLUMNS={
        'schema_version':frozenset(('version',)),
        'sessions':frozenset(('id','name','session_type','working_dir','created_at',
                              'updated_at','archived_at','schedule_id')),
        'messages':frozenset(('id','message_id','session_id','role','content_json',
                              'created_timestamp','metadata_json')),
    }

    def __init__(self,observation):
        self.root=Path(os.path.realpath(observation.get('storage_root','')))
        self.expected_identity=observation.get('storage_identity')
        self.cwd=observation.get('cwd')
        self.path=self.root/'sessions'/'sessions.db'
        self.connection=None
        self._opened_at=0.0
        self._deadline=0.0
        self._steps=0
        self._identity=None
        self._directories=None
        self._sidecars={}

    def _path_state(self):
        try:
            root_info=os.stat(self.root)
            sessions_path=self.root/'sessions'
            sessions_info=os.lstat(sessions_path)
        except OSError:
            fail(409,'Goose session store is unavailable')
        if (not stat.S_ISDIR(root_info.st_mode) or root_info.st_uid!=os.geteuid()
                or root_info.st_mode & 0o022 or stat.S_ISLNK(sessions_info.st_mode)
                or not stat.S_ISDIR(sessions_info.st_mode) or sessions_info.st_uid!=os.geteuid()
                or sessions_info.st_mode & 0o022):
            fail(409,'Goose session store path is unsafe')
        db_identity=_goose_file_identity(self.path)
        self._directories=(root_info.st_dev,root_info.st_ino,
                           sessions_info.st_dev,sessions_info.st_ino)
        return (db_identity,self._directories)

    def _check_identity(self):
        if (not isinstance(self.expected_identity,str)
                or not re.fullmatch(r'[0-9a-f]{64}',self.expected_identity)
                or goose_data_identity(self.root)!=self.expected_identity):
            fail(409,'Goose session store changed; refresh the agent')
        current=self._path_state()
        if current!=self._identity:
            fail(409,'Goose session store changed; refresh the agent')
        for suffix,identity in self._sidecars.items():
            path=Path(str(self.path)+suffix)
            if _goose_file_identity(path,required=False)!=identity:
                fail(409,'Goose session store changed; refresh the agent')

    def _progress(self):
        self._steps+=1
        if (self._steps>GOOSE_STORE_MAX_QUERY_STEPS
                or time.monotonic()>self._deadline
                or time.monotonic()-self._opened_at>GOOSE_STORE_MAX_TOTAL_SECONDS):
            return 1
        return 0

    def _query(self,sql,parameters=()):
        if self.connection is None: fail(409,'Goose session store is unavailable')
        self._steps=0
        self._deadline=min(time.monotonic()+GOOSE_STORE_MAX_QUERY_SECONDS,
                           self._opened_at+GOOSE_STORE_MAX_TOTAL_SECONDS)
        try:
            rows=self.connection.execute(sql,parameters).fetchall()
        except (sqlite3.Error,UnicodeError,ValueError,OverflowError):
            fail(409,'Goose session store is busy, corrupt or outside the read budget')
        self._check_identity()
        return rows

    def __enter__(self):
        try:
            if (not self.root.is_absolute() or not _goose_text_is_bounded(self.cwd,4096)
                    or not os.path.isabs(self.cwd)):
                fail(409,'Goose session store is unavailable')
            if not isinstance(self.expected_identity,str) or goose_data_identity(self.root)!=self.expected_identity:
                fail(409,'Goose session store changed; refresh the agent')
            self._identity=self._path_state()
            with self.path.open('rb') as source:
                header=source.read(100)
            if len(header)<100 or header[:16]!=b'SQLite format 3\0' or header[18:20] not in (b'\x01\x01',b'\x02\x02'):
                fail(409,'Goose session store is corrupt or unsupported')
            wal_mode=header[18:20]==b'\x02\x02'
            for suffix in ('-wal','-shm','-journal'):
                sidecar=Path(str(self.path)+suffix)
                self._sidecars[suffix]=_goose_file_identity(sidecar,required=False)
                if self._sidecars[suffix] is not None:
                    try: sidecar_size=os.stat(sidecar).st_size
                    except OSError: fail(409,'Goose session store changed; refresh the agent')
                    limit=(GOOSE_STORE_MAX_WAL_BYTES if suffix=='-wal'
                           else GOOSE_STORE_MAX_SHM_BYTES if suffix=='-shm' else 0)
                    if suffix=='-journal' or sidecar_size>limit:
                        fail(409,'Goose journal state is unavailable for a safe read')
            if wal_mode:
                if not self._sidecars['-wal'] or not self._sidecars['-shm'] or self._sidecars['-journal']:
                    fail(409,'Goose WAL state is unavailable for a safe read')
            elif any(self._sidecars.values()):
                fail(409,'Goose journal state is unavailable for a safe read')
            if goose_data_identity(self.root)!=self.expected_identity:
                fail(409,'Goose session store changed; refresh the agent')
            uri=self.path.as_uri()+'?mode=ro'
            self.connection=sqlite3.connect(uri,uri=True,timeout=.1,isolation_level=None)
            self.connection.enable_load_extension(False)
            if hasattr(self.connection,'setlimit'):
                limits=(('SQLITE_LIMIT_LENGTH',GOOSE_STORE_MAX_CELL_BYTES),
                        ('SQLITE_LIMIT_SQL_LENGTH',8192),('SQLITE_LIMIT_COLUMN',32),
                        ('SQLITE_LIMIT_ATTACHED',0))
                for name,value in limits:
                    if hasattr(sqlite3,name): self.connection.setlimit(getattr(sqlite3,name),value)
            self.connection.execute('PRAGMA query_only=ON')
            self.connection.execute('PRAGMA trusted_schema=OFF')
            self.connection.execute('PRAGMA busy_timeout=100')
            self.connection.set_progress_handler(self._progress,1000)
            self._opened_at=time.monotonic()
            self.connection.execute('BEGIN')
            self._verify_schema()
            self._check_identity()
            return self
        except Failure:
            self.close()
            raise
        except (OSError,sqlite3.Error,ValueError,TypeError):
            self.close()
            fail(409,'Goose session store is unavailable or unsupported')

    def _verify_schema(self):
        objects=self._query(
            "SELECT type,name,sql FROM sqlite_schema "
            "WHERE name IN ('schema_version','sessions','messages')")
        if (len(objects)!=3 or any(row[0]!='table' or row[1] not in self._SCHEMA_COLUMNS
                or not isinstance(row[2],str) or len(row[2])>8192
                or re.match(r'(?is)^\s*CREATE\s+VIRTUAL\s+TABLE\b',row[2]) for row in objects)):
            fail(409,'Goose session store schema is unsupported')
        for table,required in self._SCHEMA_COLUMNS.items():
            columns=self._query(f'PRAGMA table_info("{table}")')
            names={row[1] for row in columns if len(row)>1 and isinstance(row[1],str)}
            if not required.issubset(names):
                fail(409,'Goose session store schema is unsupported')
        versions=self._query('SELECT version FROM schema_version LIMIT 2')
        if (len(versions)!=1 or isinstance(versions[0][0],bool)
                or not isinstance(versions[0][0],int)
                or versions[0][0]!=GOOSE_STORE_SCHEMA_VERSION):
            fail(409,'Goose session store schema is unsupported')

    def _eligible_session(self,session_id):
        rows=self._query(
            "SELECT id,session_type,working_dir,schedule_id FROM sessions WHERE id=? LIMIT 2",
            (session_id,))
        if len(rows)!=1:
            fail(409,'Goose conversation is no longer available')
        row=rows[0]
        if (not _goose_text_is_bounded(row[0],256) or row[0]!=session_id or row[1]!='user'
                or row[3] is not None or not _goose_text_is_bounded(row[2],4096)
                or not os.path.isabs(row[2])
                or os.path.normcase(os.path.realpath(row[2]))!=os.path.normcase(os.path.realpath(self.cwd))):
            fail(409,'Goose conversation is not an available project session')
        return row

    def sessions(self):
        rows=self._query(
            "SELECT id,name,session_type,working_dir,created_at,updated_at,archived_at,schedule_id "
            "FROM sessions WHERE working_dir=? AND session_type='user' AND schedule_id IS NULL "
            "ORDER BY rowid DESC LIMIT ?",
            (self.cwd,GOOSE_STORE_MAX_SESSIONS+1))
        candidates=[]
        limited=len(rows)>GOOSE_STORE_MAX_SESSIONS
        for row in rows[:GOOSE_STORE_MAX_SESSIONS]:
            (session_id,name,session_type,working_dir,created_at,updated_at,archived_at,schedule_id)=row
            if (not _goose_text_is_bounded(session_id,256) or not session_id
                    or session_type!='user' or schedule_id is not None
                    or not _goose_text_is_bounded(working_dir,4096)
                    or not os.path.isabs(working_dir)
                    or os.path.normcase(os.path.realpath(working_dir))!=os.path.normcase(os.path.realpath(self.cwd))
                    or not _goose_text_is_bounded(name,512,nullable=True)
                    or not _goose_text_is_bounded(created_at,64)
                    or not _goose_text_is_bounded(updated_at,64)
                    or not _goose_text_is_bounded(archived_at,64,nullable=True)):
                limited=True
                continue
            ident=hashlib.sha256(('cc-goose-session-v1:'+self.expected_identity+':'+session_id).encode()).hexdigest()
            candidates.append(dict(id=ident,session=session_id,name=name,created_at=created_at,
                                   updated_at=updated_at,archived=archived_at is not None,linked=False))
        return dict(conversations=candidates,limited=limited,store_identity=self.expected_identity)

    def messages(self,session_id,before=None):
        if not _goose_text_is_bounded(session_id,256) or not session_id:
            fail(400,'Invalid Goose conversation')
        self._eligible_session(session_id)
        parameters=[session_id]
        clause=''
        if before is not None:
            if (not isinstance(before,(list,tuple)) or len(before)!=2
                    or any(not isinstance(value,str) or not value.isascii() or not value.isdecimal() for value in before)):
                fail(400,'Invalid Goose history cursor')
            timestamp,message_id=map(int,before)
            if timestamp>2**63-1 or message_id>2**63-1 or message_id<1:
                fail(400,'Invalid Goose history cursor')
            clause=' AND (created_timestamp < ? OR (created_timestamp = ? AND id < ?))'
            parameters.extend((timestamp,timestamp,message_id))
        parameters.append(GOOSE_STORE_MAX_MESSAGES+1)
        rows=self._query(
            'SELECT id,message_id,session_id,role,content_json,created_timestamp,metadata_json '
            'FROM messages WHERE session_id=?'+clause+
            ' ORDER BY created_timestamp DESC,id DESC LIMIT ?',parameters)
        messages=[]
        budget=GOOSE_STORE_MAX_PAGE_BYTES
        source_bytes=0
        fingerprint=hashlib.sha256(b'goose-source-page-v1\0')
        limited=len(rows)>GOOSE_STORE_MAX_MESSAGES
        selected=rows[:GOOSE_STORE_MAX_MESSAGES]
        for row in selected:
            (row_id,message_id,owner,role,content_json,created_timestamp,metadata_json)=row
            try:
                encoded=json.dumps(row,separators=(',',':'),ensure_ascii=True).encode('ascii')
            except (TypeError,ValueError,UnicodeError,RecursionError):
                encoded=repr(row).encode('utf-8','replace')
                limited=True
            source_bytes+=len(encoded)
            fingerprint.update(len(encoded).to_bytes(4,'big'))
            fingerprint.update(encoded)
            if (not isinstance(row_id,int) or isinstance(row_id,bool) or row_id<1 or row_id>2**63-1
                    or owner!=session_id or role not in ('user','assistant')
                    or not isinstance(created_timestamp,int) or isinstance(created_timestamp,bool)
                    or created_timestamp<0 or created_timestamp>2**63-1
                    or not _goose_text_is_bounded(message_id,256,nullable=True)
                    or not isinstance(content_json,str) or not isinstance(metadata_json,(str,type(None)))):
                limited=True
                continue
            try:
                content_size=len(content_json.encode('utf-8'))
                metadata_size=len(metadata_json.encode('utf-8')) if metadata_json is not None else 0
            except UnicodeError:
                limited=True
                continue
            if (content_size>GOOSE_STORE_MAX_CELL_BYTES//2 or metadata_size>16*1024
                    or content_size+metadata_size>budget):
                limited=True
                continue
            try:
                content=json.loads(content_json)
                metadata=json.loads(metadata_json) if metadata_json else {}
            except (ValueError,UnicodeError,RecursionError):
                limited=True
                continue
            if (not isinstance(content,list) or len(content)>1024 or not isinstance(metadata,dict)
                    or any(not isinstance(block,dict) or not isinstance(block.get('type'),str)
                           or len(block['type'])>64 for block in content)):
                limited=True
                continue
            user_visible=metadata.get('userVisible')
            if not isinstance(user_visible,bool): user_visible=None
            messages.append(dict(id=str(row_id),message_id=message_id,role=role,
                                 created_timestamp=str(created_timestamp),content=content,
                                 user_visible=user_visible,
                                 turn_context=metadata.get('turnContext') is True,
                                 compaction_summary=metadata.get('compactionSummary') is True))
            budget-=content_size+metadata_size
        older=None
        if len(rows)>GOOSE_STORE_MAX_MESSAGES and selected:
            oldest=selected[-1]
            if isinstance(oldest[0],int) and isinstance(oldest[5],int):
                older=(str(oldest[5]),str(oldest[0]))
        messages.reverse()
        return dict(messages=messages,older=older,limited=limited,store_identity=self.expected_identity,
                    fingerprint=fingerprint.hexdigest(),source_bytes=source_bytes)

    def history_window_fingerprint(self,session_id):
        """Fingerprint every source row a client may load across the bounded page window."""
        self._eligible_session(session_id)
        self._steps=0
        self._deadline=min(time.monotonic()+GOOSE_STORE_MAX_QUERY_SECONDS,
                           self._opened_at+GOOSE_STORE_MAX_TOTAL_SECONDS)
        fingerprint=hashlib.sha256(b'goose-history-window-v1\0')
        source_bytes=0
        try:
            cursor=self.connection.execute(
                'SELECT id,message_id,session_id,role,content_json,created_timestamp,metadata_json '
                'FROM messages WHERE session_id=? ORDER BY created_timestamp DESC,id DESC LIMIT ?',
                (session_id,GOOSE_STORE_MAX_HISTORY_ROWS))
            while True:
                row=cursor.fetchone()
                if row is None: break
                try: encoded=json.dumps(row,separators=(',',':'),ensure_ascii=True).encode('ascii')
                except (TypeError,ValueError,UnicodeError,RecursionError):
                    encoded=repr(row).encode('utf-8','replace')
                source_bytes+=len(encoded)
                if source_bytes>GOOSE_STORE_MAX_HISTORY_BYTES or time.monotonic()>self._deadline:
                    cursor.close()
                    return dict(complete=False,fingerprint=None,source_bytes=source_bytes)
                fingerprint.update(len(encoded).to_bytes(4,'big'));fingerprint.update(encoded)
            cursor.close()
            self._check_identity()
            return dict(complete=True,fingerprint=fingerprint.hexdigest(),source_bytes=source_bytes)
        except (sqlite3.Error,UnicodeError,ValueError,OverflowError):
            return dict(complete=False,fingerprint=None,source_bytes=source_bytes)

    def activity_occurrences(self,session_id,wanted):
        """Pair bounded visible-page tool calls with persisted results by ID and occurrence."""
        if not wanted: return dict(complete=True,calls={},results={})
        self._eligible_session(session_id)
        self._steps=0
        self._deadline=min(time.monotonic()+GOOSE_STORE_MAX_QUERY_SECONDS,
                           self._opened_at+GOOSE_STORE_MAX_TOTAL_SECONDS)
        try:
            cursor=self.connection.execute(
                'SELECT id,role,content_json,created_timestamp,metadata_json FROM messages '
                'WHERE session_id=? ORDER BY created_timestamp,id LIMIT ?',
                (session_id,GOOSE_STORE_MAX_ACTIVITY_ROWS+1))
            request_counts={};response_counts={};wanted_calls={};results={}
            scanned=0;source_bytes=0;event_count=0;complete=True
            while True:
                row=cursor.fetchone()
                if row is None: break
                scanned+=1
                if scanned>GOOSE_STORE_MAX_ACTIVITY_ROWS:
                    complete=False;break
                row_id,role,content_json,created_timestamp,metadata_json=row
                if (not isinstance(row_id,int) or row_id<1 or role not in ('user','assistant')
                        or not isinstance(content_json,str) or not isinstance(metadata_json,(str,type(None)))):
                    complete=False;break
                try:
                    source_bytes+=len(content_json.encode('utf-8'))+(len(metadata_json.encode('utf-8')) if metadata_json else 0)
                    if source_bytes>GOOSE_STORE_MAX_ACTIVITY_BYTES:
                        complete=False;break
                    content=json.loads(content_json);metadata=json.loads(metadata_json) if metadata_json else {}
                except (ValueError,UnicodeError,RecursionError):
                    complete=False;break
                if not isinstance(content,list) or len(content)>1024 or not isinstance(metadata,dict):
                    complete=False;break
                visible=(metadata.get('userVisible') is True
                         and metadata.get('turnContext') is not True
                         and metadata.get('compactionSummary') is not True)
                for index,block in enumerate(content):
                    if not isinstance(block,dict): continue
                    category=block.get('type')
                    if category not in ('toolRequest','toolResponse'): continue
                    block_visible=goose_block_audience_visible(block)
                    source_id=block.get('id')
                    if source_id is not None and (not isinstance(source_id,str) or not source_id or len(source_id)>256):
                        continue
                    event_count+=1
                    if event_count>GOOSE_STORE_MAX_ACTIVITY_EVENTS:
                        complete=False;break
                    counts=request_counts if category=='toolRequest' else response_counts
                    occurrence=counts.get(source_id,0);counts[source_id]=occurrence+1
                    location=(row_id,index)
                    if category=='toolRequest' and location in wanted and visible and block_visible and role=='assistant':
                        wanted_calls[location]=(source_id,occurrence)
                    elif category=='toolResponse' and visible and block_visible and role=='user':
                        pair=(source_id,occurrence)
                        if pair in wanted_calls.values():
                            results[pair]=(block,created_timestamp)
                if not complete: break
                if time.monotonic()>self._deadline or time.monotonic()-self._opened_at>GOOSE_STORE_MAX_TOTAL_SECONDS:
                    complete=False;break
            cursor.close()
            self._check_identity()
            if not complete:
                return dict(complete=False,calls={},results={})
            return dict(complete=True,calls=wanted_calls,results=results)
        except (sqlite3.Error,UnicodeError,ValueError,OverflowError):
            return dict(complete=False,calls={},results={})

    def reply_row(self,session_id,order_key):
        match=re.fullmatch(r'([0-9]{20}):([0-9]{20}):[0-9]{6}',order_key or '')
        if not match: return None
        timestamp,row_id=map(int,match.groups())
        rows=self._query('SELECT message_id,role,created_timestamp,metadata_json,content_json FROM messages WHERE session_id=? AND id=? LIMIT 2',
                         (session_id,row_id))
        if len(rows)!=1: return None
        message_id,role,stored_timestamp,metadata_json,content_json=rows[0]
        if (stored_timestamp!=timestamp or role!='assistant' or not isinstance(metadata_json,(str,type(None)))
                or not isinstance(content_json,str)): return None
        try:
            metadata=json.loads(metadata_json) if metadata_json else {}
            content=json.loads(content_json)
        except (ValueError,UnicodeError,RecursionError): return None
        if (not isinstance(metadata,dict) or metadata.get('userVisible') is not True
                or metadata.get('turnContext') is True or metadata.get('compactionSummary') is True): return None
        return dict(message_id=message_id,content=content)

    def verify_current(self):
        self._check_identity()

    def close(self):
        if self.connection is not None:
            try: self.connection.close()
            except sqlite3.Error: pass
            self.connection=None

    def __exit__(self,exception_type,exception,_traceback):
        try:
            if exception_type is None: self.verify_current()
        finally:
            self.close()
        return False


def goose_store_sessions(observation):
    require_provider(observation.get('kind'))
    if observation['kind']!='goose': fail(400,'Unsupported agent provider')
    with GooseSessionStore(observation) as store:
        return store.sessions()


def goose_store_messages(observation,session_id,before=None):
    require_provider(observation.get('kind'))
    if observation['kind']!='goose': fail(400,'Unsupported agent provider')
    with GooseSessionStore(observation) as store:
        return store.messages(session_id,before)


def goose_block_audience_visible(block):
    annotations=block.get('annotations') if isinstance(block,dict) else None
    if not isinstance(annotations,dict) or 'audience' not in annotations:
        return True
    audience=annotations.get('audience')
    return isinstance(audience,list) and 'user' in audience and all(value in ('user','assistant') for value in audience)


def goose_message_time(value):
    try:
        timestamp=int(value)
        if timestamp<0 or timestamp>253402300799: return ''
        return datetime.fromtimestamp(timestamp,timezone.utc).isoformat().replace('+00:00','Z')
    except (TypeError,ValueError,OverflowError,OSError):
        return ''


def goose_order_key(timestamp,row_id,block=0):
    return f'{timestamp:020d}:{row_id:020d}:{max(0,block):06d}'


def goose_row_visible(row):
    return (row.get('user_visible') is True and not row.get('turn_context')
            and not row.get('compaction_summary'))


def goose_chat_text(row):
    pieces=[];first_order=0
    for index,block in enumerate(row.get('content',[])[:1024]):
        if not isinstance(block,dict) or not goose_block_audience_visible(block): continue
        kind=block.get('type')
        if kind=='text' and isinstance(block.get('text'),str):
            if block['text']:
                if not pieces: first_order=index
                pieces.append(block['text'])
        elif kind in ('image','document'):
            if not pieces: first_order=index
            pieces.append('[Image omitted]' if kind=='image' else '[Document omitted]')
    text='\n'.join(pieces)
    return text,first_order


def goose_result_content(value):
    if isinstance(value,list): content=value
    elif isinstance(value,dict) and isinstance(value.get('content'),list): content=value['content']
    else: return '',False
    parts=[]
    for block in content[:32]:
        if not isinstance(block,dict) or not goose_block_audience_visible(block): continue
        kind=block.get('type')
        if kind=='text' and isinstance(block.get('text'),str): parts.append(block['text'])
        elif kind=='image': parts.append('[Image omitted]')
        elif kind=='audio': parts.append('[Audio omitted]')
        elif kind in ('resource','resource_link'): parts.append('[Resource omitted]')
    return '\n'.join(parts),False


def goose_tool_result(block):
    wrapper=block.get('toolResult')
    error=False;output=''
    if isinstance(wrapper,dict) and wrapper.get('status')=='error':
        error=True
        value=wrapper.get('error')
        output=value if isinstance(value,str) else ''
    else:
        value=wrapper.get('value') if isinstance(wrapper,dict) and wrapper.get('status')=='success' else wrapper
        if isinstance(value,dict) and value.get('isError') is True: error=True
        output,_=goose_result_content(value)
    return ('error' if error else 'completed'),output


def goose_tool_request(block):
    wrapper=block.get('toolCall')
    if isinstance(wrapper,dict) and wrapper.get('status')=='error':
        value=wrapper.get('error')
        return 'Tool call','',(value[:12001] if isinstance(value,str) and value else '')
    value=wrapper.get('value') if isinstance(wrapper,dict) and wrapper.get('status')=='success' else wrapper
    if not isinstance(value,dict): return 'Tool call','', ''
    name=value.get('name')
    title=name[:160] if isinstance(name,str) and name else 'Tool call'
    arguments=value.get('arguments')
    if not isinstance(arguments,(dict,list,str)): return title,'',''
    try: rendered=arguments if isinstance(arguments,str) else json.dumps(arguments,ensure_ascii=True,indent=2)
    except (TypeError,ValueError,RecursionError): return title,'',''
    return title,rendered[:4000],rendered[4000:]


def goose_activity_entries(rows,occurrences,conversation_id):
    entries=[];limited=not occurrences.get('complete',False)
    result_by_pair=occurrences.get('results',{}) if occurrences.get('complete') else {}
    for row in rows:
        if not goose_row_visible(row): continue
        row_id=int(row['id']);timestamp=goose_message_time(row['created_timestamp'])
        for index,block in enumerate(row['content'][:1024]):
            if not isinstance(block,dict) or not goose_block_audience_visible(block): continue
            category=block.get('type')
            if category=='thinking' and row.get('role')=='assistant':
                text=block.get('thinking')
                if isinstance(text,str) and text.strip():
                    entries.append(dict(id=f'goose-activity:{conversation_id}:{row_id}:{index}',order=index,
                                        order_key=goose_order_key(int(row['created_timestamp']),row_id,index),timestamp=timestamp,
                                        kind='thinking',title='Thinking',text=text[:12000],truncated=len(text)>12000,status='recorded'))
            elif category=='toolRequest' and row.get('role')=='assistant':
                location=(row_id,index);pair=occurrences.get('calls',{}).get(location)
                title,arguments,overflow=goose_tool_request(block)
                status='pending';output='';output_truncated=False
                if overflow:
                    status='error';output=overflow[:12000];output_truncated=len(overflow)>12000
                elif pair in result_by_pair:
                    status,raw_output=goose_tool_result(result_by_pair[pair][0]);output=raw_output[:12000]
                    output_truncated=len(raw_output)>12000
                entry=dict(id=f'goose-activity:{conversation_id}:{row_id}:{index}',order=index,
                           order_key=goose_order_key(int(row['created_timestamp']),row_id,index),timestamp=timestamp,
                           kind='tool',title=title,arguments=arguments,status=status,
                           truncated=len(arguments)>4000 or output_truncated)
                if output: entry['output']=output
                entries.append(entry)
    entries.sort(key=lambda entry:(entry['order_key'],entry['order']))
    if len(entries)>100: limited=True;entries=entries[-100:]
    budget=256000
    for index,entry in enumerate(entries):
        allowance=budget//max(1,len(entries)-index);shortened=entry.get('truncated',False)
        for key in ('text','arguments','output'):
            value=entry.get(key,'');take=min(len(value),allowance)
            entry[key]=value[:take];allowance-=take;budget-=take;shortened=shortened or take<len(value)
        entry['truncated']=shortened
    return entries,limited


def goose_history_store_id(observation,chosen):
    return hashlib.sha256(('goose-history-v1:'+str(observation.get('storage_identity'))+':'+chosen['session']).encode()).hexdigest()


def goose_history_revision(store_id,fingerprint):
    return hashlib.sha256(f'goose-revision-v1:{store_id}:{fingerprint}'.encode()).hexdigest()


def encode_goose_history_cursor(store_id,chosen,revision,pages,before):
    payload=dict(v=1,provider='goose',store=store_id,conversation=chosen['id'],session=chosen['session'],
                 revision=revision,pages=pages,before=before)
    raw=json.dumps(payload,separators=(',',':'),sort_keys=True).encode()
    token='cc-history-v1.'+base64.urlsafe_b64encode(raw).decode().rstrip('=')
    if len(token)>1024: fail(500,'Goose history cursor exceeded its limit')
    return token


def decode_goose_history_cursor(token,store_id,chosen):
    if not isinstance(token,str) or len(token)>1024 or not token.startswith('cc-history-v1.'):
        fail(400,'Invalid history cursor')
    encoded=token[len('cc-history-v1.'):]
    try:
        raw=base64.b64decode(encoded+'='*((-len(encoded))%4),altchars=b'-_',validate=True)
        payload=json.loads(raw)
    except (ValueError,UnicodeError): fail(400,'Invalid history cursor')
    if not isinstance(payload,dict) or set(payload)!={'v','provider','store','conversation','session','revision','pages','before'} or payload.get('v')!=1:
        fail(400,'Invalid history cursor')
    if (payload.get('provider')!='goose' or payload.get('store')!=store_id
            or payload.get('conversation')!=chosen.get('id') or payload.get('session')!=chosen.get('session')):
        fail(409,'History cursor belongs to another source; reload the latest history')
    pages=payload.get('pages');before=payload.get('before')
    if (not isinstance(pages,list) or not 1<=len(pages)<GOOSE_STORE_MAX_HISTORY_PAGES
            or not isinstance(payload.get('revision'),str) or not re.fullmatch(r'[0-9a-f]{64}',payload['revision'])):
        fail(400,'Invalid history cursor')
    for page in pages:
        if not isinstance(page,dict) or set(page)!={'before','fingerprint'} or not re.fullmatch(r'[0-9a-f]{64}',str(page.get('fingerprint',''))):
            fail(400,'Invalid history cursor')
        marker=page.get('before')
        if marker is not None and (not isinstance(marker,list) or len(marker)!=2 or any(not isinstance(value,str) or not value.isascii() or not value.isdecimal() for value in marker)):
            fail(400,'Invalid history cursor')
    if not isinstance(before,list) or len(before)!=2 or any(not isinstance(value,str) or not value.isascii() or not value.isdecimal() for value in before):
        fail(400,'Invalid history cursor')
    if any(int(value)>2**63-1 for value in before): fail(400,'Invalid history cursor')
    return payload


def goose_history_page(observation,chosen,request):
    require_capability('goose','project_history')
    if request.get('before') is not None: fail(400,'Goose history requires an opaque cursor')
    session_id=chosen.get('session')
    if not _goose_text_is_bounded(session_id,256) or not session_id: fail(409,'Goose conversation is unavailable')
    store_id=goose_history_store_id(observation,chosen)
    with GooseSessionStore(observation) as store:
        latest=store.messages(session_id)
        window=store.history_window_fingerprint(session_id)
        revision_source=window['fingerprint'] if window['complete'] else 'partial:'+latest['fingerprint']
        revision=goose_history_revision(store_id,revision_source)
        token=request.get('history_cursor')
        reset=False
        loaded=[]
        page_specs=[]
        current=latest
        if token is not None:
            cursor=decode_goose_history_cursor(token,store_id,chosen)
            verified=[]
            changed=cursor['revision']!=revision or cursor['pages'][0].get('before') is not None or cursor['pages'][0]['fingerprint']!=latest['fingerprint']
            for page_spec in cursor['pages']:
                if changed: break
                snapshot=latest if page_spec.get('before') is None else store.messages(session_id,page_spec['before'])
                if snapshot['fingerprint']!=page_spec['fingerprint']:
                    changed=True;break
                verified.append(snapshot)
            if (not changed and (not verified or list(verified[-1].get('older') or ())!=cursor['before'])):
                changed=True
            if changed:
                reset=True;current=latest;loaded=[latest];page_specs=[dict(before=None,fingerprint=latest['fingerprint'])]
            else:
                current=store.messages(session_id,cursor['before'])
                loaded=verified+[current]
                page_specs=[dict(before=page.get('before'),fingerprint=page['fingerprint']) for page in cursor['pages']]
                page_specs.append(dict(before=cursor['before'],fingerprint=current['fingerprint']))
        else:
            loaded=[latest];page_specs=[dict(before=None,fingerprint=latest['fingerprint'])]

        loaded_bytes=sum(page.get('source_bytes',0) for page in loaded)
        raw_rows=[row for page in loaded for row in page['messages']]
        wanted=set()
        for row in raw_rows:
            if goose_row_visible(row) and row.get('role')=='assistant':
                for index,block in enumerate(row['content'][:1024]):
                    if isinstance(block,dict) and block.get('type')=='toolRequest' and goose_block_audience_visible(block):
                        wanted.add((int(row['id']),index))
        occurrences=store.activity_occurrences(session_id,wanted)
        activities,activity_limited=goose_activity_entries(raw_rows,occurrences,chosen['id'])
        messages=[]
        message_budget=512000
        for row in current['messages']:
            if message_budget<=0: break
            if not goose_row_visible(row): continue
            text,order=goose_chat_text(row)
            if not text.strip(): continue
            row_id=int(row['id']);timestamp=int(row['created_timestamp'])
            allowance=message_budget
            shown=text[:min(16000,allowance)]
            message_budget-=len(shown)
            digest=hashlib.sha256(f"goose-message-v1:{store_id}:{row_id}:{row['role']}:{text}".encode()).hexdigest()
            message=dict(id=f'goose-message:{chosen["id"]}:{row_id}',cursor=digest,
                         role=row['role'],text=shown,truncated=len(shown)<len(text),
                         order=order,order_key=goose_order_key(timestamp,row_id,order),
                         reply_order_key=goose_order_key(timestamp,row_id),timestamp=goose_message_time(timestamp))
            messages.append(message)
            if message_budget<=0: break

        page_limited=(any(page.get('limited') for page in loaded) or activity_limited
                      or loaded_bytes>GOOSE_STORE_MAX_HISTORY_BYTES or not window['complete'])
        next_cursor=None
        if (window['complete'] and current.get('older') is not None and len(page_specs)<GOOSE_STORE_MAX_HISTORY_PAGES
                and loaded_bytes<GOOSE_STORE_MAX_HISTORY_BYTES):
            next_cursor=encode_goose_history_cursor(store_id,chosen,revision,page_specs,current['older'])
        notice=None
        if reset: notice='Goose history changed while paging; the latest page was reloaded.'
        elif activity_limited: notice='Some Goose activity could not be paired safely within the bounded history scan.'
        elif page_limited: notice='Some Goose history was omitted to keep this view bounded.'
        elif len(page_specs)>=GOOSE_STORE_MAX_HISTORY_PAGES and current.get('older') is not None:
            notice='Older Goose history is limited to five pages.'

        if token is None and request.get('known_version') is not None and request.get('known_version')!=revision:
            reset=True
            notice='Goose history changed; the latest persisted page was reloaded.'
        unchanged=bool(token is None and request.get('known_version')==revision and not reset)
        if unchanged: messages=[];activities=[]
        reply=goose_reply_observation(observation,chosen,request.get('known_reply_version'),
                                      request.get('known_reply_order_key'),latest,store)
        return dict(messages=messages,activities=activities,activity_limited=activity_limited,
                    limited=page_limited,history_version=revision,history_reset=reset,
                    history_notice=notice,history_unchanged=unchanged,
                    history_page=dict(protocol='cc.history.v1',store_id=store_id,session_id=session_id,
                                      revision=revision,reset=reset,next_cursor=next_cursor),
                    reply=reply)


def goose_reply_observation(observation,chosen,known_version=None,known_order=None,page=None,store=None):
    if not chosen: return None
    if store is None:
        with GooseSessionStore(observation) as opened:
            page=page or opened.messages(chosen['session'])
            return goose_reply_observation(observation,chosen,known_version,known_order,page,opened)
    if page is None: page=store.messages(chosen['session'])
    store_id=goose_history_store_id(observation,chosen)
    version=goose_history_revision(store_id,page['fingerprint'])
    result=dict(conversation=chosen['id'],session_id=chosen['session'],source_id=store_id,
                version=version,cursor=None,order_key=None,reply_order_key=None,
                reset=False,unchanged=False,mtime_ns=0,position=0)
    rows=[row for row in page['messages'] if row.get('role')=='assistant' and goose_row_visible(row)
          and goose_chat_text(row)[0].strip()]
    latest=rows[-1] if rows else None
    if latest:
        timestamp=int(latest['created_timestamp']);row_id=int(latest['id'])
        order=goose_order_key(timestamp,row_id)
        message_id=latest.get('message_id')
        result['order_key']=goose_order_key(timestamp,row_id,0)
        result['reply_order_key']=order
        if isinstance(message_id,str) and message_id and len(message_id)<=256:
            result['cursor']=hashlib.sha256(f'goose-reply-v1:{store_id}:{chosen["session"]}:{message_id}'.encode()).hexdigest()
    result['unchanged']=known_version==version
    if not result['unchanged'] and known_order:
        if latest is None or result['reply_order_key'] is None or result['reply_order_key']<known_order:
            result['reset']=True
        elif result['reply_order_key']>known_order:
            previous=store.reply_row(chosen['session'],known_order)
            previous_text=goose_chat_text(dict(content=previous['content']))[0] if previous and isinstance(previous.get('content'),list) else ''
            current_text=goose_chat_text(latest)[0]
            if (previous is None or previous.get('message_id')==latest.get('message_id')
                    or previous_text and previous_text==current_text):
                result['reset']=True
    return result


def is_goose_process(base):
    try:
        command=(base/'comm').read_text().strip().lower()
        argv=process_argv(base)
        return command in ('goose','goose-cli') or bool(argv and os.path.basename(argv[0]).lower() in ('goose','goose-cli'))
    except (OSError,IndexError):
        return False


def process_kind(base):
    command=(base/'comm').read_text().strip().lower()
    argv=process_argv(base)
    executable=os.path.basename(argv[0]).lower() if argv else ''
    kind=provider_from_names((command,executable))
    if kind=='goose':
        return kind if goose_invocation(argv) else None
    return kind


def foreground_agent(pid):
    pane=process_info(pid)
    if pane['foreground']<=0 or not pane['tty']: return None
    leader=process_info(pane['foreground'])
    if leader['tty']!=pane['tty'] or leader['group']!=leader['pid']: return None
    ancestor=leader
    for _ in range(32):
        if ancestor['pid']==pane['pid']: break
        if ancestor['parent']<=1: return None
        ancestor=process_info(ancestor['parent'])
    else: fail(413,'Foreground ancestry exceeds the discovery bound')
    import stat
    terminal=os.stat(pane['base']/'fd/0')
    if not stat.S_ISCHR(terminal.st_mode): return None
    kind=process_kind(leader['base'])
    if kind: candidate=leader
    else:
        if is_goose_process(leader['base']): return None
        pending=[leader];visited=set();candidates=[]
        while pending:
            current=pending.pop(0)
            if current['pid'] in visited: continue
            visited.add(current['pid'])
            if len(visited)>32: fail(413,'Foreground process tree exceeds the discovery bound')
            if current['group']!=leader['pid'] or current['tty']!=pane['tty']: continue
            current_kind=process_kind(current['base'])
            if current_kind:
                stdin=os.stat(current['base']/'fd/0')
                if stat.S_ISCHR(stdin.st_mode) and stdin.st_rdev==terminal.st_rdev: candidates.append((current,current_kind))
                continue  # A CLI's delegated children are not separate pane agents.
            if is_goose_process(current['base']): return None
            for child in (current['base']/'task'/str(current['pid'])/'children').read_text().split()[:33]:
                try: child_info=process_info(int(child))
                except (OSError,ValueError): continue
                if child_info['parent']==current['pid']: pending.append(child_info)
        if len(candidates)!=1: return None
        candidate,kind=candidates[0]
    candidate_stdin=os.stat(candidate['base']/'fd/0')
    if not stat.S_ISCHR(candidate_stdin.st_mode) or candidate_stdin.st_rdev!=terminal.st_rdev: return None
    fresh_pane=process_info(pid);fresh_leader=process_info(leader['pid']);fresh_agent=process_info(candidate['pid'])
    if (fresh_pane['start']!=pane['start'] or fresh_pane['foreground']!=leader['pid']
        or fresh_leader['start']!=leader['start'] or fresh_agent['start']!=candidate['start']
        or fresh_agent['group']!=leader['pid'] or fresh_agent['tty']!=pane['tty']
        or process_kind(fresh_agent['base'])!=kind): return None
    mode=goose_invocation(process_argv(candidate['base'])) if kind=='goose' else None
    fresh_mode=goose_invocation(process_argv(fresh_agent['base'])) if kind=='goose' else None
    if mode!=fresh_mode: return None
    return pane,leader,candidate,kind,mode


def discover_agents(request):
    rows=tmux(request,'list-panes','-a','-F','#{pane_id}\t#{pane_pid}\t#{pane_dead}').splitlines()
    seen=set();agents=[];limited=False
    for row in rows:
        fields=row.split('\t')
        if len(fields)!=3 or fields[0] in seen or fields[2]!='0': continue
        seen.add(fields[0])
        if len(seen)>256: limited=True;break
        try:
            resolved=foreground_agent(int(fields[1]))
            if resolved: agents.append(dict(pane=fields[0],provider=resolved[3]))
        except Failure: limited=True
        except (OSError,ValueError,IndexError): pass
    return dict(agents=agents,limited=limited)


def observe(request):
    for name, prefix in [('session', '$'), ('window', '@'), ('pane', '%')]:
        if not re.fullmatch(re.escape(prefix) + r'\d+', request.get(name, '')):
            fail(400, 'Invalid agent target')
    session, window, pane = (request[k] for k in ['session', 'window', 'pane'])
    members = tmux(request, 'list-panes', '-s', '-t', session, '-F', '#{window_id}\t#{pane_id}').splitlines()
    if window + '\t' + pane not in members:
        fail(409, 'Agent pane is no longer in this session/window')
    target = f'{session}:{window}.{pane}'
    info = tmux(request, 'display-message', '-p', '-t', target,
                '#{pane_pid}\t#{pane_current_command}\t#{pane_dead}\t#{pane_in_mode}').strip().split('\t')
    if len(info) != 4 or info[2] != '0':
        fail(409, 'Agent pane has exited')
    command = info[1].lower()
    kind = provider_from_names((command,))
    captured = tmux(request, 'capture-pane', '-p', '-t', target, '-S', '-40')
    text = captured[-48000:]
    identity, agent_base, args, env = None, None, [], {}
    try:
        resolved=foreground_agent(int(info[0]))
        if not resolved: fail(409,'No unique supported agent owns this foreground terminal')
        pane_process,leader,agent_process,kind,mode=resolved
        start=pane_process['start'];foreground=leader['pid'];agent_start=agent_process['start'];agent_base=agent_process['base']
        argv=(agent_base/'cmdline').read_bytes().decode(errors='replace').split('\0')
        args = argv
        # Read only allowlisted provider/environment identity metadata. Never return environments.
        for value in (agent_base / 'environ').read_bytes().decode(errors='replace').split('\0'):
            key, _, val = value.partition('=')
            if key in ('VIRTUAL_ENV', 'CODEX_HOME', 'CLAUDE_CONFIG_DIR', 'CC_LAUNCH_ID', 'PI_CODING_AGENT_DIR', 'PI_CODING_AGENT_SESSION_DIR', 'CC_RESTART_ID',
                       'GOOSE_PATH_ROOT', 'XDG_DATA_HOME', 'APPDATA', 'HOME'):
                env[key] = val
        boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        basis=f'{boot}:{info[0]}:{start}:{foreground}:{agent_start}:{kind}'
        if agent_process['pid']!=foreground: basis+=f":wrapped:{agent_process['pid']}:{leader['start']}"
        storage_root=None
        storage_identity=None
        if kind=='goose':
            storage_root=str(goose_data_dir(env))
            storage_identity=goose_data_identity(storage_root)
            basis+=f':goose-mode:{mode}:storage:{storage_identity}'
        identity = hashlib.sha256(basis.encode()).hexdigest()
        cwd = os.path.realpath(agent_base / 'cwd')
    except (OSError, ValueError, IndexError):
        if not kind: fail(409,'No process-backed agent association is available')
        cwd = tmux(request, 'display-message', '-p', '-t', target, '#{pane_current_path}').rstrip('\n')
    return dict(target=target, socket=request.get("socket"), kind=kind, identity=identity, base=agent_base, args=args,
                env=env, storage_root=storage_root if kind=='goose' else None,
                storage_identity=storage_identity if kind=='goose' else None,
                cwd=cwd, context=text, visible=tmux(request, 'capture-pane', '-p', '-t', target, '-S', '0'), in_mode=info[3] != '0',
                screen=hashlib.sha256(captured.encode()).hexdigest())

def approval_menu(observation):
    """Recognize live provider approval menus, never scrollback or arbitrary questions.
    Only single advertised shortcuts (Codex) or numbered Claude choices are sent.
    There is deliberately no trailing Enter or navigation sequence.
    """
    if not observation.get('identity') or observation.get('in_mode'):
        return None
    visible = observation.get('visible', '').rstrip()
    if len(visible) > 48000:
        return None
    lines = visible.splitlines()
    footer = next((i for i in range(len(lines)-1, -1, -1)
                   if re.search(r'(?i)esc(?:ape)? to (?:cancel|decline|interrupt)|enter to confirm', lines[i])), None)
    if footer is None or any(line.strip() for line in lines[footer+1:]):
        return None
    rows = []
    for i, line in enumerate(lines[:footer]):
        match = re.fullmatch(r'\s*([›❯>])?\s*([1-9])[.)]\s+(.+?)\s*', line)
        if match:
            rows.append([i, match.group(1), match.group(2), match.group(3)])
    if not 2 <= len(rows) <= 6 or [r[2] for r in rows] != [str(i+1) for i in range(len(rows))]:
        return None
    if sum(bool(r[1]) for r in rows) != 1:
        return None
    # Require an approval-specific question, not an ask-user selection menu.
    prefix = '\n'.join(lines[:rows[0][0]])
    questions = re.findall(r'(?im)^.*(?:would you like|do you want|allow|approve|permission)[^\n]*\?.*$', prefix)
    if not questions or not re.search(r'(?i)run|command|change|edit|write|read|access|permission|proceed|allow|apply|execute', questions[-1]):
        return None
    choices = []
    for index, (line_index, _, number, label) in enumerate(rows):
        end = rows[index+1][0] if index+1 < len(rows) else footer
        continuation = [line.strip() for line in lines[line_index+1:end] if line.strip()]
        label = ' '.join([label, *continuation])
        if not re.match(r'(?i)^(yes|no|allow|deny|approve|reject|cancel)\b', label):
            return None
        shortcut = re.search(r'\(([a-z]|esc)\)$', label)
        if observation['kind'] == 'codex':
            if not shortcut:
                return None  # customized/unsupported bindings must not be guessed
            key = shortcut.group(1)
        elif observation['kind'] == 'claude':
            key = number
        else:
            return None
        choices.append(dict(id=number, label=label, key=key))
    if not any(re.match(r'(?i)^(no|deny|reject|cancel)\b', c['label']) for c in choices):
        return None
    return dict(id=hashlib.sha256(visible.encode()).hexdigest(), title=questions[-1].strip(),
                context=visible, choices=choices)

def input_question(observation):
    """Claude AskUserQuestion observation; capabilities are issued separately.

    Require its live footer, checked-question heading and actual numbered menu.
    This must not broaden approval_menu's allow/deny grammar or key mapping.
    """
    if observation.get('kind') != 'claude' or not observation.get('identity') or observation.get('in_mode'):
        return None
    visible = observation.get('visible', '').rstrip()
    if not visible or len(visible) > 48000:
        return None
    lines = visible.splitlines()
    if not re.fullmatch(r'\s*Enter to select\s*·\s*↑/↓ to navigate(?:\s*·\s*ctrl\+g to edit in [^\n]{1,100})?\s*·\s*Esc to cancel\s*', lines[-1]):
        return None
    headings = [i for i,line in enumerate(lines) if re.match(r'^\s*[☐☑]\s+\S', line)]
    if not headings:
        return None
    start = headings[-1]
    rows = []
    for i,line in enumerate(lines[start+1:-1], start+1):
        match = re.fullmatch(r'\s*([›❯>])?\s*([1-9])[.)]\s+(.+?)\s*', line)
        if match:
            rows.append((i, match.group(1), match.group(2), match.group(3)))
    if (not 2 <= len(rows) <= 9 or sum(bool(r[1]) for r in rows) != 1
            or [r[2] for r in rows] != [str(i+1) for i in range(len(rows))]
            or not any(re.fullmatch(r'Type something\.?', r[3]) for r in rows)):
        return None
    question = ' '.join(line.strip().lstrip('│┃').strip() for line in lines[start+1:rows[0][0]] if line.strip())
    if not question or '?' not in question or len(question) > 4000:
        return None
    context = '\n'.join(lines[start:])
    if len(context) > 12000:
        return None
    options=[]
    for index,(line,marker,number,label) in enumerate(rows):
        end=rows[index+1][0] if index+1<len(rows) else len(lines)-1
        description=[]
        for continuation in lines[line+1:end]:
            if re.fullmatch(r'\s*[─━═]{10,}\s*',continuation): break
            if continuation.strip():description.append(continuation.strip())
        options.append(dict(id=number,label=label,description=' '.join(description)))
    other=[r for r in options if re.fullmatch(r'Type something\.?',r['label'])]
    selected=next(r[2] for r in rows if r[1])
    choices=[r for r in options if r['label'] not in ('Type something.','Type something','Chat about this')]
    supported=(len(headings)==1 and len(other)==1 and other[0]['label']=='Type something.'
               and len(re.findall(r'[☐☑]',lines[start]))==1 and 'Submit' not in lines[start]
               and 1<=len(choices)<=6 and selected in [c['id'] for c in choices]+[other[0]['id']])
    # Cursor navigation must not produce a fresh claim after uncertain input.
    semantic=json.dumps(dict(title=question,header=lines[start].strip(),options=options),sort_keys=True,ensure_ascii=False)
    return dict(id=hashlib.sha256(semantic.encode()).hexdigest(),title=question,context=context,
                choices=choices,text_available=supported, supported=supported,
                selected=selected,other=other[0]['id'] if len(other)==1 else None)

def question_waiting_id(observation, chosen):
    """Owned native waiting transition; independent of deferred transcript IO."""
    try:
        home=provider_home(observation);base=observation['base']
        roots=process_sessions(observation,home,follow_continuations=False)
        current=process_sessions(observation,home)
        if len(current)!=1 or chosen.get('session') not in current:return None
        with (home/'sessions'/f'{base.name}.json').open('rb') as source:
            raw=source.read(65537)
        if len(raw)>65536:return None
        record=json.loads(raw)
        if (record.get('status')!='waiting' or record.get('sessionId') not in roots
                or record.get('pid')!=int(base.name) or str(record.get('procStart'))!=proc(int(base.name))[1]):return None
        stamp=event_time(record.get('statusUpdatedAt'));updated=event_time(record.get('updatedAt'));started=event_time(record.get('startedAt'));now=int(time.time())
        if (stamp is None or stamp<0 or stamp>now+30 or (started is not None and stamp<started)
                or updated is None or updated<stamp or updated>now+30):return None
        return hashlib.sha256(json.dumps(['native-waiting',record['sessionId'],record['statusUpdatedAt']],separators=(',',':')).encode()).hexdigest()
    except (OSError,ValueError,KeyError,TypeError,IndexError):return None

def question_request_id(observation, menu, candidates=None):
    """Require a verified native waiting transition or pending question call.

    Native request identity distinguishes repeated identical questions. Plain
    terminal-looking output alone never becomes an answer capability.
    """
    if not menu or not menu.get('supported') or observation.get('base') is None:
        return None
    candidates=conversations(observation) if candidates is None else candidates
    linked=[c for c in candidates if c.get('linked')]
    if len(linked)!=1:
        return None
    chosen=linked[0]
    waiting=question_waiting_id(observation,chosen)
    if waiting:return waiting
    try:
        page=history(chosen['path'],'claude')
        entries=[e for e in page.get('activities',[]) if e.get('kind')=='tool' and e.get('title')=='AskUserQuestion' and e.get('status')=='pending']
        if len(entries)!=1:return None
        entry=entries[0]
        with open(chosen['path'],'rb') as source:
            source.seek(entry['position']);raw=source.readline(65537)
        if len(raw)>65536 or not raw.endswith(b'\n'):return None
        record=json.loads(raw)
        if record.get('isMeta') or record.get('isSidechain') or record.get('sessionId')!=chosen.get('session') or record.get('type')!='assistant':return None
        message=record.get('message',{})
        if message.get('role')!='assistant':return None
        block=message['content'][entry['order']]
        questions=block.get('input',{}).get('questions',[])
        if block.get('type')!='tool_use' or block.get('name')!='AskUserQuestion' or not isinstance(block.get('id'),str) or not 1<=len(block['id'])<=256 or len(questions)!=1:return None
        asked=questions[0]
        if ' '.join(str(asked.get('question','')).split())!=' '.join(menu['title'].split()):return None
        if asked.get('multiSelect') or [option.get('label') for option in asked.get('options',[])]!=[option['label'] for option in menu['choices']]:return None
        return hashlib.sha256((chosen['id']+'/'+block['id']).encode()).hexdigest()
    except (OSError,ValueError,KeyError,TypeError,IndexError):return None

def active_message_state(observation):
    state=provider_activity(observation)
    return state if state.get('state') in ('ready','working') and state.get('source') in ('pi_bridge','claude_registry','claude_events','codex_events') else None

def message_input_guard(observation, state=None):
    state=active_message_state(observation) if state is None else state
    if not state: return None
    if observation['kind']!='pi' or state['state']!='working': return observation['screen']
    # Pi's empty native editor has a changing Working spinner in its top border.
    # Bind the empty editor, width and cwd footer, not tool output/spinner/usage.
    # A nonempty editor or unfamiliar layout is not safe for automatic busy input.
    lines=observation.get('visible','').splitlines()
    borders=[i for i in range(max(0,len(lines)-12),len(lines)) if sum(c in '─━═' for c in lines[i])>=10]
    if len(borders)<2: return None
    top,bottom=borders[-2:]
    footer=[line.strip() for line in lines[bottom+1:] if line.strip()]
    if (not re.fullmatch(r'\s*[─━═]{10,}\s*',lines[bottom]) or top+1>=bottom
            or any(line.strip() for line in lines[top+1:bottom])
            or not 1<=len(footer)<=3 or not footer[0].startswith(('~/','/'))): return None
    return 'pi-editor:'+hashlib.sha256(json.dumps([observation['cwd'],lines[bottom],footer[0]]).encode()).hexdigest()

def verify_active_message(request, observation):
    state=active_message_state(observation)
    if not state: fail(409,'Agent is no longer verified Ready or Working; no message was pasted')
    linked=[c for c in conversations(observation) if c.get('linked')]
    expected=request.get('conversation')
    if expected is not None:
        if len(linked)!=1 or linked[0]['id']!=expected: fail(409,'Conversation changed; no message was pasted')
    elif not request.get('pending_pi_session') or pi_pending_session(observation)!=request['pending_pi_session']:
        fail(409,'No original conversation identity; no message was pasted')
    return state

def head_records(path):
    try:
        with open(path, 'rb') as f:
            data = f.read(256 * 1024)
        for line in data.splitlines():
            try:
                value = json.loads(line)
                if isinstance(value, dict):
                    yield value
            except (ValueError, UnicodeError):
                continue
    except OSError:
        return

def metadata(path, kind):
    require_provider(kind)
    require_capability(kind, 'project_history')
    for record in head_records(path):
        if kind == 'pi' and record.get('type') == 'session':
            version = record.get('version', 1)
            if isinstance(version, int) and not isinstance(version, bool) and 1 <= version <= 3:
                return record.get('cwd'), record.get('id'), record.get('timestamp', '')
            return None, None, ''
        if kind == 'codex' and record.get('type') == 'session_meta':
            payload = record.get('payload', {})
            if not isinstance(payload, dict): return None, None, ''
            source = payload.get('source')
            # Owned writer locks also include Codex's guardian/subagent threads.
            # Explicit provider provenance excludes these sidechains; never pick
            # one by recency, cwd, or a child's inherited session_id.
            if (isinstance(source, dict) and 'subagent' in source
                    or source == 'subagent'
                    or payload.get('thread_source') in ('guardian_review', 'subagent')):
                return None, None, ''
            return payload.get('cwd'), payload.get('id'), payload.get('timestamp', record.get('timestamp', ''))
        if kind == 'claude' and record.get('cwd') and record.get('sessionId') and not record.get('isSidechain'):
            return record['cwd'], record['sessionId'], record.get('timestamp', '')
    if kind=='claude':
        # Continued sessions can begin with a huge api-request record. Their
        # first message metadata may be outside the bounded header read.
        try:
            for record in bounded_events(path) or []:
                if (record.get('cwd') and record.get('sessionId')==Path(path).stem
                        and not record.get('isSidechain')):
                    return record['cwd'],record['sessionId'],record.get('timestamp','')
        except OSError: pass
    return None, None, ''

def codex_registered_session(observation, home):
    """Explicit registration by a tool of this live CLI; never infer from cwd."""
    import stat
    base = observation.get('base')
    if base is None: return None
    try:
        pid = int(base.name)
        _, start, _ = proc(pid)
        path = home / 'command-center-sessions' / f'{pid}.json'
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as source:
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077 or info.st_size > 4096: return None
            record = json.loads(source.read(4097))
        if not isinstance(record, dict): return None
        session = record.get('session_id')
        if (record.get('schema') != 1 or record.get('pid') != pid or record.get('proc_start') != start
                or record.get('boot_id') != Path('/proc/sys/kernel/random/boot_id').read_text().strip()
                or record.get('tmux_pane') != observation.get('target', '').rsplit('.', 1)[-1]
                or not isinstance(record.get('cwd'), str)
                or os.path.realpath(record['cwd']) != os.path.realpath(observation.get('cwd', ''))
                or not isinstance(session, str) or not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', session)
                or proc(pid)[1] != start): return None
        return session
    except (OSError, ValueError, TypeError, IndexError): return None

def claude_project(home, cwd):
    return home / 'projects' / re.sub(r'[^a-zA-Z0-9]', '-', cwd)


def bounded_events(path, limit=512*1024):
    with open(path,'rb') as source:
        size=os.fstat(source.fileno()).st_size;source.seek(max(0,size-limit))
        if size>limit: source.readline(limit)
        data=source.read(limit)
    if data and not data.endswith(b'\n'): return None
    records=[]
    for line in data.splitlines():
        try:
            record=json.loads(line)
            if isinstance(record,dict): records.append(record)
        except (ValueError,UnicodeError): pass
    return records


def claude_session_path(home, cwd, session):
    # UUID is supplied only by process evidence, never by a project-history guess.
    if not isinstance(session,str) or not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}',session): return None
    root=(home/'projects').resolve()
    if not root.is_relative_to(home.resolve()): return None
    def verified(path):
        try:
            if path.is_symlink(): return None
            resolved=path.resolve(strict=True)
            if resolved.parent.parent!=root or not resolved.is_file(): return None
            log_cwd,log_session,_=metadata(resolved,'claude')
            return resolved if log_session==session and isinstance(log_cwd,str) and os.path.isabs(log_cwd) else None
        except OSError: return None
    direct=claude_project(home,cwd)/(session+'.jsonl')
    if direct.exists() or direct.is_symlink(): return verified(direct)
    matches=set()
    try:
        for index,directory in enumerate(root.iterdir()):
            if index>=2000: return None
            path=directory/(session+'.jsonl')
            if path.is_file():
                candidate=verified(path)
                if candidate: matches.add(candidate)
                if len(matches)>1: return None
    except OSError: return None
    return next(iter(matches),None)


def claude_current_session(home, cwd, session):
    """Follow only explicit provider continuation edges from a verified PID registry."""
    initial=claude_session_path(home,cwd,session)
    if initial is None:
        direct=claude_project(home,cwd)/(session+'.jsonl')
        return None if direct.exists() or direct.is_symlink() else session
    directory=initial.parent;visited=set()
    for hop in range(9):
        if session in visited: return None
        visited.add(session);path=directory/(session+'.jsonl')
        if not path.exists(): return session if hop==0 else None
        if path.resolve().parent!=directory: return None
        try: records=bounded_events(path)
        except OSError: return None
        if records is None: return None
        edges=[]
        for record in records:
            if record.get('type')!='continued-in' or record.get('isSidechain') or record.get('sessionId')!=session: continue
            target=record.get('continuedInSessionId');stamp=event_time(record.get('timestamp'))
            if (not isinstance(target,str) or not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}',target)
                    or stamp is None or stamp<0 or stamp>int(time.time())+30): return None
            edges.append(target)
        if not edges: return session
        if len(set(edges))!=1: return None
        child=directory/(edges[0]+'.jsonl')
        if not child.exists() or child.resolve().parent!=directory: return None
        child_cwd,child_session,_=metadata(child,'claude')
        if child_session!=edges[0] or not isinstance(child_cwd,str) or not os.path.isabs(child_cwd): return None
        session=edges[0]
    return None


def claude_tmux_matches(recorded, target, socket=None):
    if not isinstance(recorded,str) or not isinstance(target,str):return False
    if recorded in (target, target.lstrip('$')):return True
    # CC viewers link the original window: the physical window/pane IDs remain
    # unchanged even after a temporary viewer session is removed/recreated.
    # This is used only alongside the verified foreground PID/start/domain/cwd.
    original=re.fullmatch(r'\$[0-9]+:(@[0-9]+\.%[0-9]+)',target)
    viewer=re.fullmatch(r'cc-view-[0-9a-f]{32}:(@[0-9]+\.%[0-9]+)',recorded)
    if original and viewer and original[1]==viewer[1]: return True
    # Native Claude can persist its session's literal name instead of $ID.
    # Resolve exact current membership on this socket; a matching suffix alone
    # must never link a different session, a renamed alias or another server.
    named=re.fullmatch(r'([^:\x00-\x1f\x7f]{1,240}):(@[0-9]+\.%[0-9]+)',recorded)
    if not original or not named or named[2]!=original[1]: return False
    try:
        members=tmux({'socket':socket},'list-panes','-s','-t','='+named[1]+':','-F','#{session_id}:#{window_id}.#{pane_id}')
        return len(members)<=262144 and target in members.splitlines()[:2048]
    except (Failure,OSError,subprocess.SubprocessError): return False

def process_sessions(observation, home, follow_continuations=True):
    """Provider state must match live PID/start identity, never cwd alone."""
    require_provider(observation.get('kind'))
    base = observation.get('base')
    if base is None:
        return set()
    try:
        pid = int(base.name)
        _, start, _ = proc(pid)
    except (OSError, ValueError, IndexError):
        return set()
    sessions = set()
    if observation['kind'] == 'codex':
        registered = codex_registered_session(observation, home)
        # The runtime-provided session supersedes incidental startup/other-thread writers.
        if registered: return {registered}
    if observation['kind'] == 'claude':
        try:
            path = home / 'sessions' / f'{pid}.json'
            with path.open('rb') as source:
                record = json.loads(source.read(65537))
            if not isinstance(record, dict):
                return set()
            # PID reuse, namespace collisions, stale session files and another
            # tmux target must not make an old transcript appear current.
            domain = record.get('pidDomain', '')
            if domain:
                machine_id = Path('/etc/machine-id').read_text().strip()
                expected = f'linux:{machine_id}:{os.readlink(base / "ns/pid")}'
                if domain != expected:
                    return set()
            session = record.get('sessionId', '')
            if (record.get('pid') == pid and str(record.get('procStart')) == start
                    and claude_tmux_matches(record.get('tmux'), observation['target'], observation.get('socket'))
                    and os.path.realpath(record.get('cwd', '')) == os.path.realpath(observation['cwd'])
                    and re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', session)):
                if follow_continuations:
                    session=claude_current_session(home,observation['cwd'],session)
                if session: sessions.add(session)
        except (OSError, ValueError, TypeError):
            pass
    else:
        try:
            for fd in list((base / 'fd').iterdir())[:256]:
                try:
                    path = Path(os.readlink(fd))
                    if path.parent.resolve() != (home / 'thread-writer-locks').resolve():
                        continue
                    session = path.stem
                    if not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', session):
                        continue
                    # Opening a lock file isn't enough: require a write lock
                    # owned by this process in the kernel's fdinfo record.
                    locks = (base / 'fdinfo' / fd.name).read_text().splitlines()
                    if any(re.search(r'\bWRITE\s+' + str(pid) + r'\s', line) for line in locks if line.startswith('lock:')):
                        sessions.add(session)
                except OSError:
                    pass
        except OSError:
            pass
        if observation.get('env', {}).get('CC_LAUNCH_ID'):
            pending=[(base,start,0)]; visited=0
            while pending and visited<32:
                parent,parent_start,depth=pending.pop()
                if depth>=3: continue
                try:
                    if proc(int(parent.name))[1]!=parent_start: continue
                    children=(parent/'task'/parent.name/'children').read_text().split()[:32]
                except OSError: continue
                for child in children:
                    if visited>=32: break
                    visited+=1
                    try:
                        child_base,child_start,_=proc(int(child))
                        fields=(child_base/'stat').read_text().rsplit(')',1)[1].split()
                        if fields[1]!=parent.name: continue
                        for fd in list((child_base/'fd').iterdir())[:256]:
                            try:
                                path=Path(os.readlink(fd))
                                if path.parent.resolve()!=(home/'thread-writer-locks').resolve(): continue
                                session=path.stem
                                if not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}',session): continue
                                locks=(child_base/'fdinfo'/fd.name).read_text().splitlines()
                                if any(re.search(r'\bWRITE\s+'+child+r'\s',line) for line in locks if line.startswith('lock:')):
                                    if proc(int(child))[1]==child_start and proc(int(parent.name))[1]==parent_start:
                                        sessions.add(session)
                            except OSError: continue
                        pending.append((child_base,child_start,depth+1))
                    except (OSError,ValueError,IndexError): continue
    try:
        if proc(pid)[1] != start:
            return set()
    except (OSError, ValueError, IndexError):
        return set()
    return sessions

def pi_home(observation):
    path = Path(observation.get('env', {}).get('PI_CODING_AGENT_DIR', Path.home()/'.pi/agent')).expanduser()
    return path if path.is_absolute() else Path(observation['cwd'])/path

def pi_bridge(observation):
    if '_pi_bridge' in observation: return observation['_pi_bridge']
    observation['_pi_bridge'] = None
    base = observation.get('base')
    if not observation.get('identity') or base is None: return None
    try:
        import stat
        pid=int(base.name); _,start,_=proc(pid)
        path=pi_home(observation)/'command-center-status'/f'{pid}.json'
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as source:
            info=os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.geteuid() or info.st_mode&0o077 or info.st_size>16384: return None
            record=json.loads(source.read(16385))
        now=time.time();stamp=record.get('updated_at')
        if (record.get('schema')!=1 or record.get('pid')!=pid or record.get('proc_start')!=start
            or record.get('boot_id')!=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
            or not isinstance(stamp,(float,int)) or isinstance(stamp,bool) or not now-30<=stamp<=now+5
            or os.path.realpath(record.get('cwd',''))!=os.path.realpath(observation['cwd'])
            or record.get('tmux_pane')!=observation['target'].rsplit('.',1)[-1]
            or record.get('state') not in ('unknown','working','ready','waiting')
            or not isinstance(record.get('transition'),str) or not re.fullmatch(r'[0-9a-f-]{36}',record['transition'])
            or not isinstance(record.get('session_id'),str) or not re.fullmatch(r'[0-9a-fA-F-]{36}',record['session_id'])
            or (record.get('session_file') is not None and (not isinstance(record['session_file'],str) or not os.path.isabs(record['session_file']) or len(record['session_file'])>4096))
            or (record.get('leaf_id') is not None and (not isinstance(record['leaf_id'],str) or len(record['leaf_id'])>200))
            or proc(pid)[1]!=start): return None
        observation['_pi_bridge']=record
        return record
    except (OSError,ValueError,TypeError,AttributeError,IndexError): return None

def pi_pending_session(observation):
    if observation.get('kind') != 'pi': return None
    bridge = pi_bridge(observation)
    if not bridge or bridge.get('leaf_id') is not None: return None
    path = bridge.get('session_file')
    if path:
        try: os.lstat(path)
        except FileNotFoundError: pass
        except OSError: return None
        else: return None  # Existing/unreadable/invalid logs are not empty sessions.
    return bridge['session_id']


def pi_conversations(observation):
    if require_provider(observation.get('kind')) != 'pi': fail(400, 'Unsupported agent provider')
    import itertools
    home = pi_home(observation)
    cwd = observation['cwd']
    custom = observation.get('env', {}).get('PI_CODING_AGENT_SESSION_DIR')
    explicit_files = set()
    explicit_ids = set()
    bridge = pi_bridge(observation)
    if bridge and bridge.get('session_file'): explicit_files.add(str(Path(bridge['session_file']).resolve()))
    args = observation.get('args', [])
    session_dir = None
    for index, arg in enumerate(args):
        flag, separator, inline = arg.partition('=')
        value = inline if separator else args[index+1] if index+1 < len(args) else ''
        if flag == '--session-dir' and value: session_dir = value
        if not bridge and flag in ('--session', '--session-id') and value:
            if flag == '--session' and (value.endswith('.jsonl') or '/' in value):
                path = Path(value).expanduser()
                explicit_files.add(str((path if path.is_absolute() else Path(cwd)/path).resolve()))
            else: explicit_ids.add(value)
    custom = session_dir or custom
    roots = []
    if custom:
        directory = Path(custom).expanduser()
        if not directory.is_absolute(): directory = Path(cwd)/directory
        roots.append(directory)
    else:
        encoded = '--' + re.sub(r'[/\\:]', '-', cwd.lstrip('/\\')) + '--'
        roots.append(home/'sessions'/encoded)
    paths = [Path(path) for path in explicit_files]
    for directory in roots:
        if directory.is_dir():
            paths += sorted(itertools.islice(directory.glob('*.jsonl'),2000),key=lambda p:p.stat().st_mtime,reverse=True)[:100]
    candidates=[];seen=set()
    for path in paths:
        try:
            path = path.resolve(strict=True)
            if str(path) in seen or not path.is_file(): continue
            if str(path) not in explicit_files and not any(path.is_relative_to(root.resolve()) for root in roots): continue
            seen.add(str(path))
            log_cwd,session,timestamp=metadata(path,'pi')
            if not isinstance(session,str) or not session or len(session)>200 or not log_cwd or os.path.realpath(log_cwd)!=os.path.realpath(cwd): continue
            linked=(str(path) in explicit_files and (not bridge or session==bridge['session_id'])) or session in explicit_ids
            candidate=dict(id=hashlib.sha256(str(path).encode()).hexdigest(),path=str(path),session=session,timestamp=timestamp,linked=linked)
            if bridge and linked: candidate['leaf_id']=bridge.get('leaf_id')
            candidates.append(candidate)
        except OSError: continue
    return candidates[:20]

def pi_dialog(observation):
    return bool(re.search(r'(?i)enter\s+to\s+(?:confirm|select|accept)|(?:↑|↓|arrow keys).*?(?:select|navigate)',observation.get('visible','')[-12000:]))

def native_input_dialog(observation):
    # Selection/extension dialogs are not a native backlog capability.
    return pi_dialog(observation)

def input_hash(text):
    return hashlib.sha256(text.replace('\r\n','\n').strip().encode()).hexdigest()


def native_input_hash(text, kind):
    # Claude's long-paste transport wraps the entire input. Normalize only a
    # complete single wrapper with matching IDs, never arbitrary embedded tags.
    # Keep displayed text/cursors literal; receipt matching still requires the
    # original verified process, same log inode, post-submit offset and one use.
    if kind == 'claude':
        normalized = text.replace('\r\n', '\n').strip()
        wrapped = re.fullmatch(r'<pasted_content id="([0-9a-f]{4,64})">\n([\s\S]*)\n</pasted_content id="\1">', normalized)
        if wrapped and '<pasted_content' not in wrapped[2] and '</pasted_content' not in wrapped[2]:
            return input_hash(wrapped[2])
    return input_hash(text)


def codex_internal_user(payload):
    # Native Codex records explicitly distinguish injected content from user.text.
    # Never classify XML-looking text alone, or discard ambiguous/mixed records.
    if not isinstance(payload, dict) or payload.get('type') != 'message' or payload.get('role') != 'user': return False
    metadata = payload.get('internal_chat_message_metadata_passthrough')
    if not isinstance(metadata, dict): return False
    kinds = metadata.get('content_item_kinds')
    origins = metadata.get('content_item_metadata')
    content = payload.get('content')
    if (not isinstance(kinds, list) or not kinds or len(kinds) > 64
        or not isinstance(content, list) or len(content) != len(kinds)): return False
    internal = ('generic.turn_aborted', 'environments.environment_context')
    if not all(isinstance(kind, str) and kind in internal for kind in kinds): return False
    if 'content_item_metadata' not in metadata:
        # New native environment envelopes omit this optional provenance array.
        # Accept only the observed single environment kind and generated native
        # message/turn envelope, never XML text alone or contradictory metadata.
        identifier=r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}'
        created=metadata.get('create_time')
        return (kinds==['environments.environment_context']
                and isinstance(content[0],dict) and content[0].get('type')=='input_text'
                and isinstance(content[0].get('text'),str)
                and isinstance(payload.get('id'),str) and re.fullmatch('msg_'+identifier,payload['id']) is not None
                and isinstance(metadata.get('turn_id'),str) and re.fullmatch(identifier,metadata['turn_id']) is not None
                and isinstance(created,(int,float)) and not isinstance(created,bool) and 0<created<1e12)
    return (isinstance(origins,list) and len(origins)==len(kinds)
            and all(isinstance(origin, dict) and isinstance(origin.get('provenance'), dict)
                    and origin['provenance'].get('type') == 'harness' for origin in origins))


def claude_internal_user(record):
    # Newer Claude logs store provider notifications/summaries as user records,
    # without isMeta. Trust explicit origin metadata, never XML-looking text.
    if record.get('type') != 'user': return False
    origin = record.get('origin')
    return (record.get('isCompactSummary') is True
            or record.get('promptSource') == 'system'
            or record.get('turnOrigin') == 'task_notification'
            or (isinstance(origin, dict) and origin.get('kind') == 'task-notification'))


def background_task_id(value):
    if not isinstance(value,dict): return None
    identifier=value.get('backgroundTaskId') or (value.get('agentId') if value.get('isAsync') is True else None)
    return identifier if isinstance(identifier,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,100}',identifier) else None


def native_task_notice(record):
    origin=record.get('origin')
    if (record.get('type')!='user' or record.get('isSidechain')
        or not (record.get('turnOrigin')=='task_notification' or record.get('promptSource')=='system'
                or isinstance(origin,dict) and origin.get('kind')=='task-notification')): return None
    message=record.get('message')
    if not isinstance(message,dict): return None
    text=message_text(message.get('content')).strip()
    if len(text)>64000 or not text.startswith('<task-notification>') or '<!' in text: return None
    end=text.find('</task-notification>')
    if end<0: return None
    import xml.etree.ElementTree as ET
    try: root=ET.fromstring(text[:end+len('</task-notification>')])
    except ET.ParseError: return None
    def field(name):
        values=root.findall(name)
        return values[0].text or '' if len(values)==1 and not list(values[0]) else ''
    identifier=field('task-id');state=field('status');summary=field('summary')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',identifier): return None
    states={'completed':'completed','failed':'failed','killed':'cancelled','cancelled':'cancelled','running':'running','in_progress':'running'}
    if not state or len(state)>40: return None
    state=states.get(state,'unverified')
    # Claude explicitly reports a subagent yielding while its child work runs.
    if state=='completed' and 'is waiting on its own background work' in summary: state='waiting'
    return dict(id=identifier,state=state,summary=summary[:500],call_id=field('tool-use-id'))


def fold_background_tasks(records, session, now):
    calls={};tasks={}
    for record in records:
        if record.get('isSidechain') or record.get('sessionId') not in (None,session): continue
        stamp=event_time(record.get('timestamp'))
        if stamp is None or stamp<0 or stamp>now+30: continue
        notice=native_task_notice(record)
        if notice:
            old=tasks.get(notice['id'])
            if old and old['updated_at']>stamp: continue
            call=calls.get(notice['call_id'],{})
            task=old or dict(id=notice['id'],title=call.get('title') or notice['summary'][:160] or 'Background task',started_at=call.get('started_at'))
            task.update(state=notice['state'],summary=notice['summary'],updated_at=stamp)
            if notice['state'] in ('completed','failed','cancelled'): task['finished_at']=stamp
            else: task.pop('finished_at',None)
            tasks[notice['id']]=task
            continue
        if record.get('isMeta') or claude_internal_user(record): continue
        message=record.get('message',{});content=message.get('content',[]) if isinstance(message,dict) else []
        if not isinstance(content,list): continue
        for block in content[:64]:
            if not isinstance(block,dict): continue
            if message.get('role')=='assistant' and block.get('type')=='tool_use' and block.get('name') in ('Bash','Agent','Task'):
                arguments=block.get('input',{});identifier=block.get('id')
                if not isinstance(arguments,dict) or not isinstance(identifier,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,200}',identifier): continue
                title=arguments.get('description')
                calls[identifier]=dict(title=title[:160] if isinstance(title,str) and title.strip() else 'Background '+block['name'],started_at=stamp,requested=arguments.get('run_in_background') is True)
            elif message.get('role')=='user' and block.get('type')=='tool_result':
                call=calls.get(block.get('tool_use_id'),{})
                results=[b for b in content if isinstance(b,dict) and b.get('type')=='tool_result']
                identifier=background_task_id(record.get('toolUseResult')) if len(results)==1 else None
                if not identifier and call.get('requested'):
                    text=activity_text(block.get('content'),2000)
                    match=re.search(r'^Command running in background with ID: ([A-Za-z0-9_-]{1,100})(?:[.\s]|$)',text,re.M)
                    if match: identifier=match[1]
                if not identifier or block.get('is_error'): continue
                old=tasks.get(identifier)
                if old and (old['updated_at']>=stamp or old['state'] in ('completed','failed','cancelled')): continue
                tasks[identifier]=dict(id=identifier,title=call.get('title','Background task'),started_at=call.get('started_at'),updated_at=stamp,state='running',summary='Started in background; completion has not been reported.')
    for task in tasks.values():
        if task['state'] in ('running','waiting') and now-task['updated_at']>900:
            task['state']='unverified';task['summary']='No recent task completion/status evidence. '+task['summary']
    values=sorted(tasks.values(),key=lambda t:(t['state'] in ('completed','failed','cancelled'),-t['updated_at']))
    return values[:8],len(values)>8


def observed_background_tasks(observation, chosen):
    if observation['kind']!='claude' or not chosen or not chosen.get('linked'): return None
    now=int(time.time());result=dict(source='claude_tasks',observed_at=now,conversation=chosen['id'],tasks=[],limited=False,unavailable=False)
    try:
        info=os.stat(chosen['path']);records=bounded_events(chosen['path'])
        if records is None: result.update(unavailable=True,limited=True);return result
        tasks,limited=fold_background_tasks(records,chosen['session'],now)
        result.update(tasks=tasks,limited=limited or info.st_size>512*1024)
    except OSError: result.update(unavailable=True,limited=True)
    return result


def message_order(content):
    if not isinstance(content,list): return -1
    return next((index for index,block in enumerate(content) if isinstance(block,dict) and block.get('type') in ('text','input_text','output_text') and isinstance(block.get('text'),str) and block['text'].strip()),-1)

def legacy_order_key(position, order=0):
    # Fixed-width ASCII keeps file offsets sortable without making the browser
    # interpret a display ID as a number. Native providers supply their own
    # lexically sortable key under the same API contract.
    return f'{position:020d}:{max(0, order):06d}'


def activity_text(value, limit=12000):
    if isinstance(value, str): return value[:limit]
    if isinstance(value, list):
        return '\n'.join(block.get('text', '')[:limit] for block in value[:32]
                         if isinstance(block, dict) and block.get('type') in ('text', 'output_text', 'summary_text') and isinstance(block.get('text'), str))[:limit]
    return ''


def history_activities(records, kind, floor=0):
    """Read only provider-visible blocks; never signatures, encrypted reasoning or hidden context."""
    require_provider(kind)
    require_capability(kind, 'project_history')
    entries, calls = [], {}
    def add(offset, order, timestamp, category, title, text='', call_id=None):
        entry = dict(id=f'activity:{offset}:{order}', position=offset, order=order,
                     order_key=legacy_order_key(offset, order), timestamp=timestamp,
                     kind=category, title=title[:160], text=text[:12000], truncated=len(text)>12000, status='recorded' if category=='thinking' else 'pending')
        entries.append(entry)
        if isinstance(call_id, str) and call_id and len(call_id)<=256: calls[call_id]=entry
        return entry
    def finish(call_id, output, error=False, metadata=None):
        if not isinstance(call_id, str) or call_id not in calls: return
        entry=calls[call_id]; entry['status']='error' if error else 'completed'; entry['output']=activity_text(output,12001); entry['truncated']=entry.get('truncated',False) or len(entry['output'])>12000; entry['output']=entry['output'][:12000]
        identifier=background_task_id(metadata)
        if not identifier and entry.get('background_requested'):
            match=re.search(r'^Command running in background with ID: ([A-Za-z0-9_-]{1,100})(?:[.\s]|$)',entry['output'],re.M)
            if match: identifier=match[1]
        if identifier and not error: entry['status']='background';entry['background_task_id']=identifier
    for offset, record in records:
        if record.get('isMeta') or record.get('isSidechain'): continue
        timestamp=record.get('timestamp','')
        if kind=='codex':
            payload=record.get('payload',{})
            if not isinstance(payload,dict) or record.get('type')!='response_item': continue
            category=payload.get('type')
            if category=='reasoning':
                # Only the exported summary, never content/encrypted_content.
                summary=activity_text(payload.get('summary'))
                add(offset,0,timestamp,'thinking','Thinking',summary or 'No readable summary was recorded.')
            elif category in ('function_call','custom_tool_call'):
                arguments=payload.get('arguments') if category=='function_call' else payload.get('input')
                entry=add(offset,0,timestamp,'tool',str(payload.get('name') or 'Tool call'),call_id=payload.get('call_id'))
                entry['arguments']=(arguments[:4000] if isinstance(arguments,str) else '')
                entry['truncated']=isinstance(arguments,str) and len(arguments)>4000
            elif category in ('function_call_output','custom_tool_call_output'):
                finish(payload.get('call_id'),payload.get('output'))
            continue
        if kind=='pi':
            if record.get('type')!='message': continue
            message=record.get('message',{})
        else:
            if record.get('type') not in ('assistant','user'): continue
            message=record.get('message',{})
        if not isinstance(message,dict): continue
        role=message.get('role')
        if kind=='pi' and role=='toolResult':
            finish(message.get('toolCallId'),message.get('content'),message.get('isError') is True)
            continue
        content=message.get('content')
        if not isinstance(content,list): continue
        for order,block in enumerate(content[:64]):
            if not isinstance(block,dict): continue
            category=block.get('type')
            if role=='assistant' and category=='thinking':
                text=block.get('thinking')
                if isinstance(text,str) and text.strip(): add(offset,order,timestamp,'thinking','Thinking',text)
            elif role=='assistant' and category in ('tool_use','toolCall'):
                entry=add(offset,order,timestamp,'tool',str(block.get('name') or 'Tool call'),call_id=block.get('id'))
                arguments=block.get('input') if category=='tool_use' else block.get('arguments')
                if kind=='claude' and isinstance(arguments,dict): entry['background_requested']=arguments.get('run_in_background') is True
                if isinstance(arguments,(dict,list,str)):
                    rendered=json.dumps(arguments,ensure_ascii=True,indent=2) if not isinstance(arguments,str) else arguments
                    entry['arguments']=rendered[:4000]; entry['truncated']=len(rendered)>4000
            elif role=='user' and category=='tool_result':
                finish(block.get('tool_use_id'),block.get('content'),block.get('is_error') is True,record.get('toolUseResult') if kind=='claude' and sum(isinstance(b,dict) and b.get('type')=='tool_result' for b in content)==1 else None)
    # Keep existing message pagination and reply/read cursors unchanged. Activity
    # is supplementary, bounded, and explicitly reports omissions on busy pages.
    entries=[entry for entry in entries if entry['position']>=floor]
    limited=len(entries)>100
    entries=entries[-100:]
    budget=256000
    for index,entry in enumerate(entries):
        allowance=budget//max(1,len(entries)-index)
        shortened=entry.get('truncated',False)
        for key in ('text','arguments','output'):
            text=entry.get(key,''); take=min(len(text),allowance)
            entry[key]=text[:take]; allowance-=take; budget-=take; shortened=shortened or take<len(text)
        entry['truncated']=shortened
    return entries, limited


def pi_history(path, before=None, known_branch=None, active_leaf=False, include_activity=True):
    # Reconstruct only the latest persisted branch. Never concatenate abandoned
    # branches, custom/hidden records or system prompts. Activity uses this same branch.
    limit=8*1024*1024
    header=next((r for r in head_records(path) if r.get('type')=='session'),{})
    version=header.get('version',1)
    if not isinstance(version,int) or isinstance(version,bool) or version not in (1,2,3): fail(415,'Unsupported pi session version')
    with open(path,'rb') as source:
        end=os.fstat(source.fileno()).st_size;start=max(0,end-limit);source.seek(start)
        if start: source.readline(limit)
        entries=[]
        while source.tell()<end and len(entries)<50000:
            offset=source.tell();line=source.readline(min(limit,end-offset))
            if not line.endswith(b'\n'): continue
            try: record=json.loads(line)
            except (ValueError,UnicodeError): continue
            if not isinstance(record,dict) or record.get('type')=='session': continue
            if version==1:
                record=dict(record,id=str(offset),parentId=entries[-1][1]['id'] if entries else None)
            if not isinstance(record.get('id'),str) or len(record['id'])>200: continue
            if record.get('parentId') is not None and not isinstance(record.get('parentId'),str): continue
            entries.append((offset,record))
    by_id={record['id']:(offset,record) for offset,record in entries}
    if len(by_id)!=len(entries): fail(409,'Pi history has duplicate entry identities')
    branch=(entries[-1][1]['id'] if entries else None) if active_leaf is False else active_leaf
    selected=[];visited=set();cursor=branch
    while cursor is not None and cursor in by_id:
        if cursor in visited: fail(409,'Pi history has a cyclic branch')
        visited.add(cursor);entry=by_id[cursor];selected.append(entry);cursor=entry[1].get('parentId')
    selected.reverse()
    reset=bool(known_branch and known_branch not in visited)
    if before is not None and reset: fail(409,'Pi branch changed; reload latest history before loading older messages')
    messages=[]; commands=[]
    for offset,record in selected:
        if before is not None and offset>=int(before): continue
        if record.get('type')!='message': continue
        message=record.get('message',{})
        if (isinstance(message,dict) and message.get('role')=='bashExecution'
                and isinstance(message.get('command'),str)
                and isinstance(message.get('excludeFromContext'),bool)):
            prefix='!!' if message['excludeFromContext'] else '!'
            commands.append(dict(position=offset,digest=input_hash(prefix+message['command'])))
        if not isinstance(message,dict) or message.get('role') not in ('user','assistant'): continue
        text=message_text(message.get('content'))
        if not text.strip(): continue
        order=message_order(message.get('content'))
        messages.append(dict(id=str(offset),legacy_position=offset,cursor=hashlib.sha256(f'{offset}:{text}'.encode()).hexdigest(),role=message['role'],input_hash=input_hash(text) if message['role']=='user' else None,
                             text=text[:16000],truncated=len(text)>16000,order=order,order_key=legacy_order_key(offset,order),reply_order_key=legacy_order_key(offset),timestamp=record.get('timestamp','')))
    page=messages[-100:];budget=512000
    for index,message in enumerate(page):
        original=len(message['text']);allowance=budget//(len(page)-index);message['text']=message['text'][:allowance]
        message['truncated']=message['truncated'] or original>allowance;budget-=len(message['text'])
    notice='Showing the latest persisted pi branch; older ancestry is outside the bounded history window.' if cursor is not None or start or len(entries)>=50000 else None
    activity_records=[(offset,record) for offset,record in selected if before is None or offset<int(before)]
    activities, activity_limited = history_activities(activity_records, 'pi', page[0].get('legacy_position',0) if len(messages)>100 else 0) if include_activity else ([],False)
    return dict(messages=page,commands=commands[-100:],activities=activities,activity_limited=activity_limited,older_cursor=page[0].get('legacy_position',0) if len(messages)>100 else (activities[0]['position'] if activity_limited and not page else None),history_branch=branch,
                history_reset=reset,history_notice=notice,limited=bool(notice or len(messages)>100))

def conversations(observation):
    require_provider(observation.get('kind'))
    if not capability_available(observation['kind'], 'project_history'):
        return []
    if observation['kind'] == 'pi': return pi_conversations(observation)
    if observation['kind'] == 'goose':
        try:
            store=goose_store_sessions(observation)
            return [dict(id=row['id'],session=row['session'],name=row.get('name'),
                         timestamp=row.get('updated_at'),created_at=row.get('created_at'),
                         updated_at=row.get('updated_at'),archived=row.get('archived',False),
                         linked=False) for row in store['conversations']]
        except Failure as error:
            observation['history_error']=error.message
            return []
    kind, cwd, env = observation['kind'], observation['cwd'], observation['env']
    home = Path(env.get('CODEX_HOME', Path.home() / '.codex') if kind == 'codex' else env.get('CLAUDE_CONFIG_DIR', Path.home() / '.claude'))
    paths, linked = [], set()
    # An open rollout or explicit resume/session argument is a strong association.
    base = observation['base']
    if base is not None:
        try:
            for fd in list((base / 'fd').iterdir())[:256]:
                try:
                    p = Path(os.readlink(fd))
                    if p.suffix == '.jsonl' and p.is_relative_to(home):
                        paths.append(p); linked.add(str(p))
                except OSError:
                    pass
        except OSError:
            pass
    registered = codex_registered_session(observation, home) if kind == 'codex' else None
    explicit = {registered} if registered else process_sessions(observation, home)
    args = observation['args']
    if not registered and (kind!='claude' or not explicit):
        for i, arg in enumerate(args[:-1]):
            if arg in ('resume', '--resume', '--session-id', '-r') and re.fullmatch(r'[0-9a-fA-F-]{36}', args[i+1]):
                session=claude_current_session(home,cwd,args[i+1]) if kind=='claude' else args[i+1]
                if session: explicit.add(session)
    if kind == 'codex':
        for db in sorted(home.glob('state*.sqlite'), reverse=True)[:2]:
            try:
                with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True, timeout=.2) as conn:
                    for session in explicit:
                        paths += [Path(r[0]) for r in conn.execute('SELECT rollout_path FROM threads WHERE id = ? AND cwd = ?', (session, cwd))]
                    paths += [Path(r[0]) for r in conn.execute('SELECT rollout_path FROM threads WHERE cwd = ? AND archived = 0 ORDER BY updated_at DESC LIMIT 20', (cwd,))]
                break
            except sqlite3.Error:
                pass
        if not paths:
            # Bounded fallback for older CLI versions without a thread database.
            import itertools
            paths = sorted(itertools.islice((home / 'sessions').glob('*/*/*/*.jsonl'), 4000), key=lambda p: p.stat().st_mtime, reverse=True)[:100]
    else:
        project = re.sub(r'[^a-zA-Z0-9]', '-', cwd)
        directory = home / 'projects' / project
        for session in explicit:
            resolved=claude_session_path(home,cwd,session)
            if resolved: paths.append(resolved)
        if directory.is_dir():
            paths += [directory / f'{session}.jsonl' for session in explicit if (directory / f'{session}.jsonl').is_file()]
            import itertools
            paths += sorted(itertools.islice(directory.glob('*.jsonl'), 2000), key=lambda p: p.stat().st_mtime, reverse=True)[:100]
    candidates, seen = [], set()
    for path in paths:
        try:
            path = path.resolve(strict=True)
            if not path.is_relative_to(home.resolve()) or str(path) in seen or not path.is_file():
                continue
            seen.add(str(path))
            log_cwd, session, timestamp = metadata(path, kind)
            if not log_cwd or (os.path.realpath(log_cwd) != os.path.realpath(cwd) and not (kind=='claude' and session in explicit)):
                continue
            candidates.append(dict(id=hashlib.sha256(str(path).encode()).hexdigest(), path=str(path),
                                   session=session, timestamp=timestamp, linked=session == registered if registered else str(path) in linked or session in explicit))
        except OSError:
            continue
    return candidates[:20]

def provider_home(observation):
    require_provider(observation.get('kind'))
    require_capability(observation['kind'], 'project_history')
    if observation['kind'] == 'pi': return pi_home(observation)
    env = observation['env']
    return Path(env.get('CODEX_HOME', Path.home() / '.codex') if observation['kind'] == 'codex'
                else env.get('CLAUDE_CONFIG_DIR', Path.home() / '.claude'))

def state_result(state, source, reason, evidence_at=None, transition=None):
    return dict(state=state, source=source, reason=reason, evidence_at=evidence_at,
                observed_at=int(time.time()), transition=transition)

def event_time(value):
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return int(value / 1000 if value > 100000000000 else value)
        if isinstance(value, str):
            stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if stamp.tzinfo is not None:
                return int(stamp.timestamp())
    except (ValueError, OverflowError):
        pass
    return None

def codex_tail_activity(data, now):
    """Replay a complete bounded window; None means a root anchor is missing."""
    turn, current, stamp, event = None, None, None, None
    for line in data.splitlines():
        try:
            record = json.loads(line)
        except (ValueError, UnicodeError):
            continue
        if not isinstance(record, dict) or record.get('type') != 'event_msg': continue
        payload = record.get('payload')
        if not isinstance(payload, dict): continue
        kind, ident = payload.get('type'), payload.get('turn_id')
        # Long-running turns can produce tools for hours. Only progress
        # explicitly scoped to the already verified root turn refreshes it;
        # child items, token counts and arbitrary log writes cannot.
        if kind == 'item_completed' and current == 'working' and ident == turn:
            progress = event_time(record.get('timestamp'))
            if progress is not None and stamp is not None and stamp <= progress <= now + 30:
                stamp, event = progress, 'item_completed'
            continue
        if kind not in ('task_started', 'task_complete', 'turn_aborted') or not isinstance(ident, str) or not ident: continue
        if payload.get('root_turn_id') and payload['root_turn_id'] != ident: continue
        if kind != 'task_started' and turn is not None and turn != ident: continue
        turn = ident
        stamp = event_time(record.get('timestamp'))
        current = 'working' if kind == 'task_started' else 'ready'
        event = kind
    if not current:
        return None
    if stamp is None or stamp > now + 30 or stamp < 0:
        return state_result('unknown', 'codex_events', 'Provider event has an invalid timestamp')
    if current == 'working' and now - stamp > 900:
        return state_result('unknown', 'codex_events', 'Working evidence is older than 15 minutes', stamp)
    return state_result(current, 'codex_events', f'Codex reported {event}', stamp, hashlib.sha256(f'{turn}:{event}:{stamp}'.encode()).hexdigest())

def codex_activity(path, now):
    """Adaptive bounded root lookup; recent root progress refreshes long turns."""
    try:
        with open(path, 'rb') as source:
            end=os.fstat(source.fileno()).st_size
            for limit in (512*1024, 2*1024*1024, 8*1024*1024):
                start=max(0,end-limit);source.seek(start);data=source.read(end-start)
                if data and not data.endswith(b'\n'):
                    return state_result('unknown','codex_events','Provider update is incomplete')
                if start:
                    # Discard only the initial partial record inside this budget.
                    _,separator,data=data.partition(b'\n')
                    if not separator: data=b''
                result=codex_tail_activity(data,now)
                if result is not None: return result
                if start==0: break
        return state_result('unknown','codex_events','No root turn transition within the bounded 8 MiB status window')
    except (OSError, ValueError):
        return state_result('unknown', 'codex_events', 'Process-linked event log is unavailable')


def claude_log_activity(path, session, now):
    try: records=bounded_events(path)
    except OSError: return state_result('unknown','claude_events','Process-linked Claude event log is unavailable')
    if records is None: return state_result('unknown','claude_events','Claude event update is incomplete')
    state,stamp,event=None,None,None
    background={r.get('id') for r in records if r.get('type')=='api-request' and r.get('querySource') not in (None,'repl_main_thread') and isinstance(r.get('id'),str)}
    for record in records:
        if record.get('sessionId')!=session or record.get('isSidechain') or record.get('isMeta'): continue
        if record.get('serverClassifierRequest') is True or (isinstance(record.get('requestRef'),str) and record['requestRef'] in background): continue
        kind=record.get('type');message=record.get('message',{})
        transition=None
        if kind=='api-request' and record.get('querySource')=='repl_main_thread': transition='working'
        elif kind=='user' and isinstance(message,dict) and message.get('role')=='user': transition='working'
        elif kind=='assistant' and isinstance(message,dict) and message.get('role')=='assistant':
            stop=message.get('stop_reason')
            if stop in ('end_turn','stop_sequence'): transition='ready'
            elif stop=='tool_use': transition='working'
        if transition is None: continue
        timestamp=event_time(record.get('timestamp'))
        if timestamp is None or timestamp<0 or timestamp>now+30: return state_result('unknown','claude_events','Claude event timestamp is invalid')
        if stamp is not None and timestamp<stamp: continue
        state,stamp,event=transition,timestamp,str(record.get('uuid') or record.get('id') or kind)
    if state is None: return state_result('unknown','claude_events','No foreground Claude turn evidence in the bounded log tail')
    if state=='working' and now-stamp>900: return state_result('unknown','claude_events','Claude turn evidence is older than 15 minutes',stamp)
    return state_result(state,'claude_events','Claude reported '+('turn completion' if state=='ready' else 'foreground turn activity'),stamp,hashlib.sha256(f'{session}:{event}:{stamp}:{state}'.encode()).hexdigest())


def provider_activity(observation, candidates=None):
    require_provider(observation.get('kind'))
    if not capability_available(observation['kind'], 'verified_phase'):
        return state_result('unknown', 'none', capability_reason(observation['kind'], 'verified_phase'))
    menu = approval_menu(observation)
    if menu:
        return state_result('approval', 'terminal_prompt', 'Recognized live approval menu; explicit human decision required', int(time.time()), menu['id'])
    question = input_question(observation)
    if question:
        anchor=question_request_id(observation,question,candidates)
        transition=hashlib.sha256((question['id']+'/'+anchor).encode()).hexdigest() if anchor else question['id']
        return state_result('approval', 'terminal_question', question['title'], int(time.time()), transition)
    if not observation.get('identity') or observation.get('base') is None:
        return state_result('unknown', 'none', 'Live agent process could not be verified')
    if observation['kind'] == 'pi':
        bridge=pi_bridge(observation)
        if bridge:
            state={'working':'working','ready':'ready','waiting':'approval','unknown':'unknown'}[bridge['state']]
            reason='Pi is waiting for input in an extension dialog. Respond in the terminal.' if bridge['state']=='waiting' else 'Native pi bridge reports '+bridge['state']
            return state_result(state,'pi_bridge',reason,int(bridge['updated_at']),bridge['transition'])
        return state_result('unknown', 'pi_session', 'Pi status bridge is absent or stale; live activity is unverified. Install the bridge and run /reload when idle.')
    home = provider_home(observation)
    if observation['kind'] == 'claude':
        linked = process_sessions(observation, home, follow_continuations=False)
        try:
            base = observation['base']
            with (home / 'sessions' / f'{base.name}.json').open('rb') as source:
                record = json.loads(source.read(65537))
            if (not isinstance(record, dict) or record.get('sessionId') not in linked
                    or record.get('pid') != int(base.name) or str(record.get('procStart')) != proc(int(base.name))[1]):
                return state_result('unknown', 'none', 'No valid process-linked status record')
            stamp = event_time(record.get('statusUpdatedAt'))
            started = event_time(record.get('startedAt'))
            updated = event_time(record.get('updatedAt'))
            now = int(time.time())
            if (stamp is None or stamp < 0 or stamp > now + 30 or
                    (started is not None and stamp < started) or
                    (updated is not None and (updated < stamp or updated > now + 30))):
                return state_result('unknown', 'claude_registry', 'Provider status timestamp is invalid')
            current=process_sessions(observation,home)
            if len(current)!=1:
                return state_result('unknown','claude_events','Claude session continuation cannot be verified')
            active=next(iter(current))
            path=claude_session_path(home,observation['cwd'],active)
            events=claude_log_activity(path,active,now) if path else state_result('unknown','claude_events','No verified native session log is available')
            if events['reason'] in ('Claude event timestamp is invalid','Claude event update is incomplete'): return events
            # Root turn events supersede an older registry transition. Registry
            # updatedAt is only freshness, never a new phase transition.
            if events['state']!='unknown' and (active!=record['sessionId'] or events['evidence_at']>=stamp): return events
            if active!=record['sessionId']:
                return events
            value = record.get('status')
            # Claude derives shell from idle foreground plus background shell work.
            # Background liveness/completion stays in the separate task snapshot.
            state = {'idle':'ready', 'shell':'ready', 'working':'working', 'busy':'working', 'running':'working',
                     'waiting_for_approval':'approval', 'waiting_for_permission':'approval', 'waiting':'approval'}.get(value)
            if state is None:
                return state_result('unknown', 'claude_registry', 'Provider status is not recognized', stamp)
            if state == 'working' and now - max(stamp, updated or stamp) > 900:
                return state_result('unknown', 'claude_registry', 'Working evidence is older than 15 minutes', stamp)
            evidence=max(stamp,updated or stamp) if state=='working' else stamp
            if value == 'waiting':
                return state_result('approval', 'claude_input', 'Claude reports waiting for user input; respond in the terminal', stamp, hashlib.sha256(f"{record['sessionId']}:{record['statusUpdatedAt']}:waiting".encode()).hexdigest())
            reason = 'Claude foreground is idle; background shell work reported' if value=='shell' else f'Claude reports {value}'
            return state_result(state, 'claude_registry', reason, evidence, hashlib.sha256(f"{record['sessionId']}:{record['statusUpdatedAt']}:{value}".encode()).hexdigest())
        except (OSError, ValueError, TypeError, IndexError):
            return state_result('unknown', 'none', 'No valid process-linked status record')
    candidates = conversations(observation) if candidates is None else candidates
    linked = [c for c in candidates if c['linked']]
    if len(linked) != 1:
        return state_result('unknown', 'none', 'No unique process-linked conversation for turn status')
    return codex_activity(linked[0]['path'], int(time.time()))

def message_text(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ''
    return '\n'.join(c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') in ('text', 'input_text', 'output_text') and isinstance(c.get('text'), str))

def history(path, kind, before=None, known_branch=None, active_leaf=False, include_activity=True):
    require_provider(kind)
    require_capability(kind, 'project_history')
    if kind == 'pi': return pi_history(path,before,known_branch,active_leaf,include_activity)
    # Read only a tail/page, never a growing multi-GB transcript into memory.
    with open(path, 'rb') as source:
        end = os.fstat(source.fileno()).st_size
        if before is not None:
            end = min(end, max(0, int(before)))
        start = max(0, end - 4 * 1024 * 1024)
        source.seek(start)
        if start:
            source.readline(4 * 1024 * 1024)
        records = []
        while source.tell() < end:
            offset = source.tell()
            line = source.readline(min(end - offset, 4 * 1024 * 1024))
            if not line.endswith(b'\n'):
                continue  # unfinished append; retry on next refresh
            try:
                record = json.loads(line)
                if isinstance(record, dict): records.append((offset, record))
            except (ValueError, UnicodeError):
                pass
    messages, events = [], []
    for offset, record in records:
        if kind == 'codex':
            payload = record.get('payload', {})
            if not isinstance(payload, dict): continue
            if record.get('type') == 'response_item' and payload.get('type') == 'message':
                if codex_internal_user(payload): continue
                role, text = payload.get('role'), message_text(payload.get('content'))
            elif record.get('type') == 'event_msg' and payload.get('type') in ('user_message', 'agent_message'):
                role = 'user' if payload['type'] == 'user_message' else 'assistant'
                text = payload.get('message', '')
                if isinstance(text, str) and text:
                    events.append((offset, dict(id=str(offset), legacy_position=offset, cursor=hashlib.sha256(f'{offset}:{text}'.encode()).hexdigest(), role=role, input_hash=input_hash(text) if role=='user' else None, text=text[:16000], truncated=len(text)>16000, order_key=legacy_order_key(offset), reply_order_key=legacy_order_key(offset), timestamp=record.get('timestamp', ''))))
                continue
            else: continue
        else:
            if record.get('type') not in ('user', 'assistant') or record.get('isMeta') or record.get('isSidechain') or claude_internal_user(record): continue
            payload = record.get('message', {})
            if not isinstance(payload, dict): continue
            role, text = payload.get('role'), message_text(payload.get('content'))
        if role not in ('user', 'assistant') or not text.strip(): continue
        order=message_order(payload.get('content'))
        messages.append((offset, dict(id=str(offset), legacy_position=offset, cursor=hashlib.sha256(f'{offset}:{text}'.encode()).hexdigest(), role=role, input_hash=native_input_hash(text,kind) if role=='user' else None, text=text[:16000], truncated=len(text)>16000, order=order, order_key=legacy_order_key(offset,order), reply_order_key=legacy_order_key(offset), timestamp=record.get('timestamp', ''))))
    if not messages: messages = events
    page = messages[-100:]
    budget = 512000
    for index, (_, message) in enumerate(page):
        original = len(message['text'])
        allowance = budget // (len(page) - index)
        message['text'] = message['text'][:allowance]
        message['truncated'] = message['truncated'] or original > allowance
        budget -= len(message['text'])
    cursor = page[0][0] if len(messages) > 100 else records[0][0] if start and records else start
    activities, activity_limited = history_activities(records, kind, page[0][0] if len(messages)>100 else 0) if include_activity else ([],False)
    if activity_limited and not page: cursor=activities[0]['position']
    return dict(messages=[m for _, m in page], activities=activities, activity_limited=activity_limited, older_cursor=cursor if cursor > 0 else None,
                limited=start > 0 or len(messages) > 100 or activity_limited)

def transcript_version(chosen):
    info = os.stat(chosen['path'])
    version = hashlib.sha256(f"{chosen['id']}:{info.st_dev}:{info.st_ino}:{info.st_size}:{info.st_mtime_ns}".encode()).hexdigest()
    if 'leaf_id' in chosen: version=hashlib.sha256((version+':'+json.dumps(chosen['leaf_id'])).encode()).hexdigest()
    return info, version

def history_store_id(chosen):
    info=os.stat(chosen['path'])
    return hashlib.sha256(f'file-v1:{info.st_dev}:{info.st_ino}'.encode()).hexdigest()

def encode_history_cursor(kind, chosen, revision, before):
    payload=dict(v=1,provider=kind,store=history_store_id(chosen),conversation=chosen['id'],
                 revision=revision,before=str(before),branch=chosen.get('leaf_id'))
    raw=json.dumps(payload,separators=(',',':'),sort_keys=True).encode()
    return 'cc-history-v1.'+base64.urlsafe_b64encode(raw).decode().rstrip('=')

def decode_history_cursor(token, kind, chosen, revision):
    if not isinstance(token,str) or len(token)>1024 or not token.startswith('cc-history-v1.'):
        fail(400,'Invalid history cursor')
    encoded=token[len('cc-history-v1.'):]
    try:
        raw=base64.b64decode(encoded+'='*((-len(encoded))%4),altchars=b'-_',validate=True)
        payload=json.loads(raw)
    except (ValueError,UnicodeError):
        fail(400,'Invalid history cursor')
    if not isinstance(payload,dict) or set(payload)!={'v','provider','store','conversation','revision','before','branch'} or payload.get('v')!=1:
        fail(400,'Invalid history cursor')
    if (payload.get('provider')!=kind or payload.get('store')!=history_store_id(chosen)
        or payload.get('conversation')!=chosen.get('id')):
        fail(409,'History cursor belongs to another source; reload the latest history')
    if payload.get('branch')!=chosen.get('leaf_id') or payload.get('revision')!=revision:
        return None,True
    before=payload.get('before')
    if not isinstance(before,str) or not before.isascii() or not before.isdecimal() or (len(before)>1 and before.startswith('0')):
        fail(400,'Invalid history cursor')
    position=int(before)
    if position>os.stat(chosen['path']).st_size:
        return None,True
    return position,False

def reply_observation(chosen, kind, known_version=None, known_order=None, page=None):
    require_provider(kind)
    require_capability(kind, 'project_history')
    if not chosen: return None
    info, version = transcript_version(chosen)
    result = dict(conversation=chosen['id'], session_id=chosen.get('session',chosen['id']),
                  source_id=history_store_id(chosen), version=version, cursor=None, order_key=None,
                  reply_order_key=None, reset=False, unchanged=False, mtime_ns=info.st_mtime_ns, position=0)
    if version == known_version:
        result['unchanged'] = True
        return result
    page = history(chosen['path'], kind, active_leaf=chosen.get('leaf_id',False), include_activity=False) if page is None else page
    latest = next((m for m in reversed(page['messages']) if m['role'] == 'assistant'), None)
    if latest:
        result['position'] = latest.get('legacy_position',0)
        result['order_key'] = latest.get('order_key')
        result['reply_order_key'] = latest.get('reply_order_key')
        result['cursor'] = hashlib.sha256(f"{info.st_dev}:{info.st_ino}:{latest['cursor']}".encode()).hexdigest()
    changed = known_version is not None and known_version != version
    moved_back = (known_order is not None and latest is not None
                  and isinstance(latest.get('reply_order_key'), str)
                  and latest['reply_order_key'] < known_order)
    result['reset']=bool(page.get('history_reset') or changed and (latest is None or moved_back))
    return result

def project_directory(value):
    if not isinstance(value, str) or not value or len(value) > 4096 or any(ord(c) < 32 for c in value):
        fail(400, 'Invalid project directory')
    path = Path(os.path.expanduser(value))
    if not path.is_absolute(): fail(400, 'Use an absolute directory or ~/path')
    try: path = path.resolve(strict=True)
    except OSError: fail(404, 'Project directory not found')
    if not path.is_dir() or not os.access(path, os.R_OK | os.X_OK): fail(400, 'Project directory is unavailable')
    info=path.stat()
    return str(path), f'{info.st_dev}:{info.st_ino}'

def python_venv(project, value):
    if value is None or value == '': return None, None
    if not isinstance(value,str) or len(value.encode())>4096 or any(ord(c)<32 or 127<=ord(c)<160 for c in value):
        fail(400,'Python venv must be a literal directory path')
    try:
        root=Path(value).expanduser()
        if not root.is_absolute(): root=Path(project)/root
        root=root.resolve(strict=True)
        cfg=root/'pyvenv.cfg'; binary=root/'bin'/'python'
        if not root.is_dir() or not cfg.is_file() or cfg.stat().st_size>65536 or not binary.is_file() or not os.access(binary,os.X_OK):
            fail(400,'Python venv needs pyvenv.cfg and an executable bin/python')
        identities=[]
        for item in (root,root/'bin',cfg,binary):
            info=item.stat();identities.append([str(item.resolve()),info.st_dev,info.st_ino,info.st_mtime_ns,info.st_size])
        return str(root), hashlib.sha256(json.dumps(identities).encode()).hexdigest()
    except (OSError,ValueError,RuntimeError): fail(400,'Python venv is unavailable; check its directory')

def launch_executable(kind):
    require_capability(kind, 'launch')
    require_provider(kind)
    search = os.environ.get('PATH', '') + os.pathsep + str(Path.home()/'.local/bin') + os.pathsep + str(Path.home()/'.cargo/bin') + ':/usr/local/bin'
    executable=shutil.which(kind, path=search)
    if not executable: fail(404, f'{kind} is not installed on this machine or is not executable')
    executable=os.path.abspath(executable)
    info=os.stat(executable)
    return executable, f'{info.st_dev}:{info.st_ino}:{info.st_size}:{info.st_mtime_ns}', search

def launch_candidates(path, kind):
    require_capability(kind, 'launch')
    require_provider(kind)
    observation=dict(kind=kind,cwd=path,env={k:os.environ[k] for k in ('CODEX_HOME','CLAUDE_CONFIG_DIR','PI_CODING_AGENT_DIR','PI_CODING_AGENT_SESSION_DIR') if k in os.environ},base=None,args=[])
    return conversations(observation)

def active_launch_sessions(request, kind):
    require_capability(kind, 'launch')
    require_provider(kind)
    # Process evidence only. An unrelated project transcript is never "active".
    active=set()
    try:
        rows=tmux(request,'list-panes','-a','-F','#{session_id}\t#{window_id}\t#{pane_id}\t#{pane_current_command}\t#{pane_dead}\t#{@cc_launch}').splitlines()
    except Failure: return active
    seen=set()
    for row in rows[:256]:
        fields=row.split('\t')
        if len(fields)!=6 or fields[2] in seen: continue
        try:
            metadata=json.loads(fields[5])
            if fields[4]=='0' and metadata.get('provider')==kind and metadata.get('pane')==fields[2] and metadata.get('conversation'):
                active.add(metadata['conversation'])
        except (ValueError,AttributeError): pass
        if provider_from_names((fields[3].lower(),)) != kind: continue
        seen.add(fields[2])
        if len(seen)>64: break
        try:
            observed=observe(dict(request,session=fields[0],window=fields[1],pane=fields[2]))
            active.update(process_sessions(observed,provider_home(observed)))
            args=observed['args']
            for i, arg in enumerate(args[:-1]):
                if arg in ('resume','--resume','--session-id','-r') and re.fullmatch(r'[0-9a-fA-F-]{36}',args[i+1]): active.add(args[i+1])
        except (Failure,OSError): continue
    return active

def launch_title(candidate, kind):
    require_capability(kind, 'launch')
    require_provider(kind)
    for record in head_records(candidate['path']):
        if record.get('isMeta') or record.get('isSidechain') or (kind=='claude' and claude_internal_user(record)): continue
        if kind=='codex':
            if record.get('type')!='response_item': continue
            message=record.get('payload',{})
            if codex_internal_user(message): continue
        elif kind=='pi':
            if record.get('type')!='message': continue
            message=record.get('message',{})
        else:
            if record.get('type')!='user': continue
            message=record.get('message',{})
        if message.get('role')!='user': continue
        content=message.get('content',[])
        if isinstance(content,str): text=content
        elif isinstance(content,list): text=' '.join(c.get('text','') for c in content if isinstance(c,dict) and c.get('type') in ('text','input_text'))
        else: continue
        if text.strip(): return ' '.join(text.split())[:160]
    return 'Conversation'

def launch_model(value):
    if value is None or value == '': return None
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/@+\[\]-]{0,199}',value):
        fail(400,'Model must be a name or alias of at most 200 characters, without spaces or CLI flags')
    return value

def launch_approval_policy(kind, value):
    if value is None or value == '' or value == 'default': return None
    if kind != 'codex' or value != 'approve-for-me':
        fail(400, 'Approval policy must be default or approve-for-me for Codex')
    return value

def codex_launch_flags(executable, approval_policy):
    # Probe the exact prepared executable; never silently downgrade a requested policy.
    try:
        result=subprocess.run([executable,'--help'],cwd=str(Path.home()),stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=2)
        help_text=result.stdout[:256*1024] if result.returncode==0 else b''
    except (OSError,subprocess.SubprocessError): help_text=b''
    supported=lambda flag: re.search(rb'(?<![\w-])'+re.escape(flag)+rb'(?![\w-])',help_text) is not None
    if approval_policy and not supported(b'--approve-for-me'):
        fail(400, 'Installed Codex does not advertise --approve-for-me; update Codex or explicitly choose harness default')
    return (['--no-daemon'] if supported(b'--no-daemon') else []) + (['--approve-for-me'] if approval_policy else [])

def launch_destination(request):
    session=request.get('target_session')
    if session is None or session=='':return None,None
    if not isinstance(session,str) or not re.fullmatch(r'\$[0-9]+',session):fail(400,'Choose an existing tmux session by its stable ID')
    fields=tmux(request,'display-message','-p','-t',session+':','#{session_id}\t#{session_created}\t#{pid}\t#{start_time}\t#{session_name}').rstrip('\n').split('\t',4)
    if len(fields)!=5 or fields[0]!=session or fields[4].startswith('cc-view-'):fail(409,'The selected tmux session is unavailable; choose a session again')
    try:
        base,start,_=proc(int(fields[2]));server=Path('/proc/sys/kernel/random/boot_id').read_text().strip()+':'+start
    except (OSError,ValueError):server=fields[3]
    identity=hashlib.sha256(json.dumps([fields[:4],server]).encode()).hexdigest()
    return session,identity

def launch_label(value, limit, label):
    if value is None or value == '':return None
    if not isinstance(value,str):fail(400,'Invalid '+label)
    value=value.strip()
    if len(value.encode('utf-8'))>limit or any(ord(c)<32 or 127<=ord(c)<160 for c in value):fail(400,label+' is too long or contains control characters')
    return value or None

def launch_options(request):
    require_capability(request.get('provider'), 'launch')
    require_provider(request.get('provider'))
    target_session,destination_identity=launch_destination(request)
    model=launch_model(request.get('model'))
    window_name=launch_label(request.get('window_name'),120,'Window name')
    card_name=launch_label(request.get('card_name'),240,'Agent card name')
    path,identity=project_directory(request.get('path'))
    kind=request.get('provider')
    defaults=request.get('project_venvs') or {}
    value=request.get('python_venv')
    if value is None: value=defaults.get(path)
    venv,venv_identity=python_venv(path,value)
    executable,executable_identity,_=launch_executable(kind)
    approval_policy=launch_approval_policy(kind,request.get('approval_policy'))
    if approval_policy: codex_launch_flags(executable,approval_policy)
    active=active_launch_sessions(request,kind)
    candidates=[]
    for candidate in launch_candidates(path,kind):
        session=candidate.get('session','')
        if not isinstance(session,str) or not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}',session): continue
        candidates.append(dict(id=candidate['id'],session=session,timestamp=candidate['timestamp'],title=launch_title(candidate,kind),active=session in active))
    return dict(python_venv=venv,venv_identity=venv_identity,project=path,directory_identity=identity,provider=kind,model=model,approval_policy=approval_policy,executable=executable,executable_identity=executable_identity,conversations=candidates,target_session=target_session,destination_identity=destination_identity,window_name=window_name,card_name=card_name)

def launch_status(request):
    identifier=request.get('launch_id','')
    if not isinstance(identifier,str) or not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',identifier): fail(400,'Invalid launch identity')
    name='cc-agent-'+identifier
    try:
        rows=tmux(request,'list-panes','-a','-F','#{session_id}\t#{window_id}\t#{pane_id}\t#{pane_dead}\t#{pane_current_command}\t#{s/[\x01-\x1f\x7f]/?/:session_name}\t#{s/[\x01-\x1f\x7f]/?/:window_name}\t#{@cc_launch}').splitlines()
    except Failure:return dict(found=False,launch_id=identifier)
    matches=[];incomplete=False;moved=False
    for raw in rows[:4096]:
        fields=raw.split('\t',7)
        if len(fields)!=8 or fields[5].startswith('cc-view-'):continue
        try:meta=json.loads(fields[7])
        except (ValueError,TypeError):meta={}
        if meta.get('launch_id')==identifier:
            if fields[0]==meta.get('session') and fields[1]==meta.get('window') and fields[2]==meta.get('pane'):matches.append((fields,meta))
            else:moved=True
        elif fields[5]==name or fields[6]==name:incomplete=True
    if not matches:
        if moved or len(rows)>4096:fail(409,'Original launch target moved or discovery exceeded its limit; inspect it before launching again')
        if incomplete:fail(409,'Launch setup is incomplete; inspect the new session/window before launching again')
        return dict(found=False,launch_id=identifier)
    if len(matches)!=1:fail(409,'Launch identity is ambiguous; inspect its session/window')
    fields,metadata=matches[0];row=fields[:5];session_id=row[0]
    kind=require_provider(metadata.get('provider'))
    require_capability(kind, 'launch')
    association={}
    if metadata.get('ticket') and row[3]=='0' and provider_from_names((row[4].lower(),)) == kind:
        try:
            observed=observe(dict(request,session=row[0],window=row[1],pane=row[2]))
            if observed.get('identity') and observed['env'].get('CC_LAUNCH_ID')==identifier:
                association['identity']=observed['identity']
                linked=[c for c in conversations(observed) if c.get('linked')]
                if len(linked)==1:association['conversation']=linked[0].get('session')
            else:association['replacement']=True
        except (Failure,OSError): pass
    if metadata.get('conversation'):association.setdefault('conversation',metadata['conversation'])
    return dict(found=True,launch_id=identifier,session=row[0],window=row[1],pane=row[2],
                session_name=fields[5],destination=metadata.get('destination','session'),project=metadata['project'],provider=kind,model=metadata.get('model'),python_venv=metadata.get('python_venv'),approval_policy=metadata.get('approval_policy'),
                running=row[3]=='0' and provider_from_names((row[4].lower(),)) == kind,exited=row[3]=='1',
                context=tmux(request,'capture-pane','-p','-t',row[2],'-S','0')[-12000:],**association)

def respawn_launch(request, pane, directory, environment, command):
    # tmux sets PATH from its spawning client after applying -e overrides.
    # Apply the literal venv environment after tmux, without a shell/script.
    values=dict(environment[i+1].split('=',1) for i in range(0,len(environment),2) if '=' in environment[i+1])
    if values.get('VIRTUAL_ENV'):
        command=['/usr/bin/env','PATH='+values['PATH'],'VIRTUAL_ENV='+values['VIRTUAL_ENV'],'PYTHONHOME=',*command]
    # tmux's protocol rejects large argv messages. A private one-shot argv file
    # keeps long prompts literal without typing terminal input or shell quoting.
    if sum(len(arg.encode())+1 for arg in environment+command) <= 6000:
        return tmux(request,'respawn-pane','-k','-t',pane,'-c',directory,*environment,*command)
    import tempfile
    fd, filename = tempfile.mkstemp(prefix='cc-launch-argv-',suffix='.json')
    try:
        with os.fdopen(fd,'w') as source: json.dump(command,source,ensure_ascii=False)
        loader = ("import os,sys,json,stat\n"
                  "fd=os.open(sys.argv[1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)\n"
                  "info=os.fstat(fd)\n"
                  "if not (stat.S_ISREG(info.st_mode) and info.st_uid==os.geteuid() and not info.st_mode&0o077 and info.st_size<=163840): raise RuntimeError('Invalid private launch handoff')\n"
                  "with os.fdopen(fd,'rb') as source: argv=json.load(source)\n"
                  "if not (isinstance(argv,list) and argv and all(isinstance(a,str) for a in argv)): raise RuntimeError('Invalid launch arguments')\n"
                  "os.unlink(sys.argv[1])\n"
                  "os.execv(argv[0],argv)\n")
        return tmux(request,'respawn-pane','-k','-t',pane,'-c',directory,*environment,sys.executable,'-c',loader,filename)
    except BaseException:
        try: os.unlink(filename)
        except FileNotFoundError: pass
        raise


def launch_agent(request):
    # Validate everything before creating a new, uniquely named session.
    require_capability(request.get('provider'), 'launch')
    require_provider(request.get('provider'))
    identifier=request.get('launch_id','')
    existing=launch_status(request)
    if existing['found']: fail(409,'This launch already exists; check its status instead of retrying')
    target_session,destination_identity=launch_destination(request)
    if destination_identity!=request.get('destination_identity'):fail(409,'The selected tmux session changed; prepare the launch again')
    path,identity=project_directory(request.get('project'))
    kind=request.get('provider')
    executable,executable_identity,search=launch_executable(kind)
    if identity!=request.get('directory_identity') or path!=request.get('project'): fail(409,'Project directory changed; prepare it again')
    if executable!=request.get('executable') or executable_identity!=request.get('executable_identity'): fail(409,'Agent installation changed; prepare again')
    venv,venv_identity=python_venv(path,request.get('python_venv'))
    if venv_identity!=request.get('venv_identity'): fail(409,'Python venv changed; prepare the launch again')
    if venv: search=str(Path(venv)/'bin')+os.pathsep+search
    model=launch_model(request.get('model'))
    command=[executable]
    approval_policy=launch_approval_policy(kind,request.get('approval_policy'))
    if kind=='codex': command += codex_launch_flags(executable,approval_policy)
    selected=request.get('conversation')
    if selected:
        allowed=next((c for c in request.get('conversations',[]) if c['id']==selected and not c['active']),None)
        chosen=next((c for c in launch_candidates(path,kind) if c['id']==selected),None)
        if not allowed or not chosen or chosen['session']!=allowed['session']: fail(409,'Conversation changed or is unavailable for this project')
        if chosen['session'] in active_launch_sessions(request,kind): fail(409,'This conversation already has a running agent; open it in AI Queue')
        command += ['resume',chosen['session']] if kind=='codex' else ['--session',chosen['path']] if kind=='pi' else ['--resume',chosen['session']]
    elif kind=='claude': command += ['--session-id',identifier]
    if model is not None: command += ['--model',model]
    initial=request.get('initial_prompt')
    if initial is not None:
        if selected or not isinstance(initial,str) or not initial.strip() or len(initial.encode('utf-8'))>24000 or '\0' in initial: fail(400,'Invalid initial ticket prompt')
        # Positional literal input; never shell code or simulated terminal typing.
        command += ['--',initial]
    name='cc-agent-'+identifier
    window_name=launch_label(request.get('window_name'),120,'Window name')
    launch_label(request.get('card_name'),240,'Agent card name')
    # A harmless placeholder lets us enable remain-on-exit before executing the
    # CLI. Never respawn or resize an existing user pane.
    if target_session:
        row=tmux(request,'new-window','-d','-P','-F','#{session_id}\t#{window_id}\t#{pane_id}','-t',target_session+':','-n',name,'-c',path,'/bin/sleep','86400').strip().split('\t')
    else:
        row=tmux(request,'new-session','-d','-P','-F','#{session_id}\t#{window_id}\t#{pane_id}','-s',name,'-n',kind,'-c',path,'-x','120','-y','36','/bin/sleep','86400').strip().split('\t')
    if len(row)!=3: fail(502,'Launch state uncertain; check the launch before trying again')
    try:
        metadata=json.dumps(dict(launch_id=identifier,project=path,python_venv=venv,provider=kind,model=model,approval_policy=approval_policy,session=row[0],window=row[1],pane=row[2],conversation=chosen['session'] if selected else identifier if kind=='claude' else None,ticket=initial is not None,destination='window' if target_session else 'session'))
        tmux(request,'set-option','-w','-t',row[1],'@cc_launch',metadata)
        if not target_session:tmux(request,'set-option','-t',row[0],'@cc_launch',metadata)
        else:tmux(request,'rename-window','-t',row[1],kind+'-'+identifier[:8])
        if window_name:
            tmux(request,'rename-window','-t',row[1],window_name)
            tmux(request,'set-option','-w','-t',row[1],'automatic-rename','off')
        tmux(request,'set-option','-w','-t',row[1],'remain-on-exit','on')
        environment=['-e','PATH='+search,'-e','CC_LAUNCH_ID='+identifier,'-e','VIRTUAL_ENV='+ (venv or '')]
        if venv: environment += ['-e','PYTHONHOME=']
        for key,default in (('CODEX_HOME','.codex'),('CLAUDE_CONFIG_DIR','.claude')):
            environment += ['-e',key+'='+os.environ.get(key,str(Path.home()/default))]
        for key in ('PI_CODING_AGENT_DIR','PI_CODING_AGENT_SESSION_DIR'):
            if key in os.environ: environment += ['-e',key+'='+os.environ[key]]
        respawn_launch(request,row[2],path,environment,command)
    except (Failure,subprocess.SubprocessError): fail(502,'Launch setup or delivery uncertain; check the new session before trying again')
    return launch_status(request)

def restart_plan(request, observation):
    require_capability(observation.get('kind'), 'restart')
    require_provider(observation.get('kind'))
    if not observation.get('identity') or observation['identity'] != request.get('identity'):
        fail(409, 'Agent process changed; no restart was attempted')
    linked = [c for c in conversations(observation) if c.get('linked')]
    if len(linked) != 1: fail(409, 'Restart requires one verified process-linked conversation')
    chosen = linked[0]
    session = chosen.get('session')
    if not isinstance(session,str) or not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}',session):
        fail(409, 'The active conversation has no supported resume identity')
    kind = observation['kind']
    executable, executable_identity, search = launch_executable(kind)
    project, directory_identity = project_directory(observation['cwd'])
    command = [executable]
    if kind == 'codex':
        try:
            result=subprocess.run([executable,'--help'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=2)
            if result.returncode==0 and b'--no-daemon' in result.stdout[:256*1024]: command += ['--no-daemon']
        except (OSError,subprocess.SubprocessError): pass
    command += ['resume',session] if kind=='codex' else ['--session',chosen['path']] if kind=='pi' else ['--resume',session]
    info=os.stat(chosen['path'])
    environment={key:value for key,value in observation['env'].items() if key in ('VIRTUAL_ENV','CODEX_HOME','CLAUDE_CONFIG_DIR','PI_CODING_AGENT_DIR','PI_CODING_AGENT_SESSION_DIR')}
    venv,venv_identity=python_venv(project,observation['env'].get('VIRTUAL_ENV'))
    if venv: search=str(Path(venv)/'bin')+os.pathsep+search
    environment['VIRTUAL_ENV']=venv or ''
    if venv: environment['PYTHONHOME']=''
    environment['PATH']=search
    return dict(python_venv=venv,venv_identity=venv_identity,identity=observation['identity'],provider=kind,session=session,conversation=chosen['id'],
                path=chosen['path'],project=project,directory_identity=directory_identity,
                executable_identity=executable_identity,command=command,environment=environment,
                log_device=info.st_dev,log_inode=info.st_ino)


def restart_agent(request, observation):
    plan=request.get('plan')
    if not isinstance(plan,dict) or restart_plan(request,observation)!=plan:
        fail(409,'Agent, conversation, directory or installation changed. Review a fresh restart.')
    identifier=request.get('restart_id','')
    if not isinstance(identifier,str) or not re.fullmatch(r'[0-9a-f-]{36}',identifier): fail(400,'Invalid restart identity')
    # The backend persisted this attempt before IO. The pane marker is additional
    # evidence for recovery; it never authorizes a second respawn.
    marker=json.dumps(dict(id=identifier,old=plan['identity']),sort_keys=True)
    tmux(request,'set-option','-p','-t',observation['target'],'@cc_restart',marker)
    tmux(request,'set-option','-p','-t',observation['target'],'remain-on-exit','on')
    fresh=observe(request)
    if fresh.get('identity')!=plan['identity'] or restart_plan(request,fresh)!=plan:
        fail(409,'The agent changed immediately before restart; inspect the pane')
    environment=[]
    for key,value in {**plan['environment'],'CC_RESTART_ID':identifier}.items(): environment += ['-e',key+'='+value]
    respawn_launch(request,observation['target'],plan['project'],environment,plan['command'])
    return dict(state='checking')


def restart_status(request):
    plan=request.get('plan',{});identifier=request.get('restart_id')
    try: observation=observe(request)
    except Failure: return dict(state='checking',note='The resumed CLI is not yet observable; inspect the pane if it exited.')
    if observation['identity']==plan.get('identity'): return dict(state='checking',note='Original process is still present; this restart will not be retried.')
    if (observation.get('env',{}).get('CC_RESTART_ID')!=identifier
        or observation['kind']!=plan.get('provider') or observation['cwd']!=plan.get('project')):
        fail(409,'A different process occupies this pane; restart settings were not transferred')
    marker=tmux(request,'show-options','-p','-v','-t',observation['target'],'@cc_restart').strip()
    try: marker=json.loads(marker)
    except ValueError: fail(409,'Restart evidence is unavailable; inspect the pane')
    if marker!=dict(id=identifier,old=plan.get('identity')): fail(409,'Restart marker changed; inspect the pane')
    linked=[c for c in conversations(observation) if c.get('linked')]
    if len(linked)!=1 or linked[0]['session']!=plan.get('session') or linked[0]['id']!=plan.get('conversation'):
        return dict(state='checking',note='Waiting for the exact resumed conversation to become process-linked.')
    return dict(state='complete',instance=observation['identity'])


def execute(request):
    action=request.get('action')
    if action in ('launch_options', 'launch'):
        require_capability(request.get('provider'), 'launch')
        require_provider(request.get('provider'))
    if action == 'discover_agents': return discover_agents(request)
    if action == 'launch_options': return launch_options(request)
    if action == 'launch_status': return launch_status(request)
    if action == 'launch': return launch_agent(request)
    if action == 'restart_status': return restart_status(request)
    observation = observe(request)
    if request.get('action') == 'restart_prepare': return restart_plan(request, observation)
    if request.get('action') == 'restart_agent': return restart_agent(request, observation)
    if request.get('action') == 'close_agent':
        require_capability(observation['kind'], 'close_agent')
        if not observation.get('identity') or observation['identity'] != request.get('identity'):
            fail(409,'Agent process changed; no window was closed')
        try:
            tmux(request,'kill-window','-t',request['session']+':'+request['window'])
        except (Failure,subprocess.SubprocessError):
            fail(502,'Close outcome is uncertain. Check agents before taking another action; this close will not be retried')
        return dict(closed=True)
    if request.get('action') == 'question_answer':
        namespace=dict(globals())
        exec(request['_question_code'],namespace)
        return namespace['answer_question'](request,observation)
    if request.get('action') == 'approval':
        require_capability(observation['kind'], 'native_approval')
        menu = approval_menu(observation)
        if (not menu or observation['identity'] != request.get('identity')
                or observation['screen'] != request.get('screen') or menu['id'] != request.get('approval_id')):
            fail(409, 'Approval or agent changed; no decision was sent. Refresh and review.')
        choice = next((c for c in menu['choices'] if c['id'] == request.get('choice')), None)
        if not choice:
            fail(400, 'Unsupported approval choice')
        fresh = observe(request)
        if (fresh['identity'] != observation['identity'] or fresh['screen'] != observation['screen']
                or approval_menu(fresh) != menu):
            fail(409, 'Approval or agent changed; no decision was sent. Refresh and review.')
        try:
            if choice['key'] == 'esc':
                tmux(request, 'send-keys', '-t', fresh['target'], 'Escape')
            else:
                tmux(request, 'send-keys', '-t', fresh['target'], '-l', choice['key'])
        except (Failure, subprocess.SubprocessError):
            fail(502, 'Decision delivery uncertain. Check the agent before responding again.')
        return dict(submitted=True)
    if request.get('action') == 'status':
        candidates=(conversations(observation) if observation['kind']!='goose' or request.get('conversation') else [])
        linked = [c for c in candidates if c['linked']]
        chosen = linked[0] if len(linked) == 1 else next((c for c in candidates if c['id'] == request.get('conversation')), None)
        if observation['kind']!='goose' and not chosen and len(candidates) == 1 and not observation['env'].get('CC_LAUNCH_ID'): chosen = candidates[0]
        reply=(goose_reply_observation(observation,chosen,request.get('known_reply_version'),request.get('known_reply_order_key'))
               if observation['kind']=='goose' and chosen else
               reply_observation(chosen, observation['kind'], request.get('known_reply_version'), request.get('known_reply_order_key'))
               if capability_available(observation['kind'], 'project_history') else None)
        result=dict(instance=observation['identity'], provider=observation['kind'], context=observation['context'],
                    capabilities=capability_payload(observation['kind']),reply=reply,
                    activity=provider_activity(observation, candidates),background_tasks=observed_background_tasks(observation,chosen if len(linked)==1 and chosen is linked[0] else None))
        if observation.get('history_error'): result['history_unavailable']=observation['history_error']
        return result
    if request.get('action') == 'outbox_status':
        if request.get('identity') and observation['identity'] != request['identity']:
            fail(409, 'Agent process changed; queued messages were not sent')
        candidates=conversations(observation)
        linked=[candidate for candidate in candidates if candidate.get('linked')]
        chosen=linked[0] if len(linked)==1 else None
        result=dict(instance=observation['identity'], screen=observation['screen'], context=observation['context'],
                    capabilities=capability_payload(observation['kind']),
                    activity=provider_activity(observation,candidates), log=None, users=[], pending_pi_session=None,
                    send_available=bool(observation['identity']) and not observation['in_mode'] and not approval_menu(observation)
                        and capability_available(observation['kind'], 'ordinary_message_submission')
                        and capability_available(observation['kind'], 'acceptance_confirmation')
                        and not native_input_dialog(observation))
        state=active_message_state(observation)
        result['input_guard']=message_input_guard(observation,state) if state else None
        if not result['send_available']:
            result['send_reason']=capability_reason(observation['kind'], 'ordinary_message_submission')
        if chosen:
            info=os.stat(chosen['path'])
            result['log']=dict(conversation=chosen['id'],device=info.st_dev,inode=info.st_ino,size=info.st_size)
            page=history(chosen['path'],observation['kind'],active_leaf=chosen.get('leaf_id',False),include_activity=False)
            result['users']=[dict(position=message['legacy_position'],digest=message.get('input_hash')) for message in page['messages'] if message['role']=='user' and message.get('input_hash') and type(message.get('legacy_position')) is int]
            result['commands']=page.get('commands',[])
            if observation['kind']=='pi': result['pi_session']=chosen['session']
        else:
            result['pending_pi_session']=pi_pending_session(observation)
        return result
    if request.get('action') == 'send':
        require_capability(observation['kind'], 'ordinary_message_submission')
        require_capability(observation['kind'], 'acceptance_confirmation')
        if native_input_dialog(observation): fail(409,'The native CLI is waiting for input in a dialog. Answer it in the terminal before sending a message.')
        if not observation['identity'] or observation['identity'] != request.get('identity'):
            fail(409, 'Agent process changed; refresh before sending')
        active=request.get('require_active') is True
        state=verify_active_message(request,observation) if active else None
        guard=message_input_guard(observation,state) if active else observation['screen']
        expected_guard=request.get('input_guard') if active else request.get('screen')
        if observation['in_mode']: fail(409,'Terminal is in copy mode; no message was pasted')
        # Busy Codex/Claude output can advance during the SSH round trip. The
        # verified process/conversation authorizes refreshing this observation;
        # a second exact fingerprint is still required immediately before paste.
        refresh_busy=bool(active and state['state']=='working' and observation['kind'] in ('codex','claude'))
        if not guard or not expected_guard or (guard!=expected_guard and not refresh_busy):
            if active: return dict(sent=False,deferred=True,not_sent=True)
            fail(409, 'Terminal changed; review the latest context before sending')
        text = request.get('text', '')
        if not isinstance(text, str) or not text.strip() or len(text.encode()) > 12000 or any(ord(c) < 32 and c not in '\n\t' or ord(c) == 127 for c in text):
            fail(400, 'Message must be 1–12000 UTF-8 bytes without control characters')
        if request.get('require_ready') and provider_activity(observation)['state'] != 'ready':
            fail(409, 'Agent is no longer Ready; no message was pasted')
        if provider_activity(observation)['state'] == 'approval':
            fail(409, 'Pi is waiting for input. Respond in the terminal.' if observation['kind']=='pi' else 'Agent is awaiting approval. Respond in the terminal.')
        if observation['kind']=='pi' and re.match(r'^[\s\ufeff]*!',text):
            fail(400,"Pi treats leading ! as shell input. Start with FYI: to send it as chat.")
        buffer = 'cc-message-' + uuid.uuid4().hex
        try:
            tmux(request, 'load-buffer', '-b', buffer, '-', input=text.encode())
            fresh = observe(request)
            if fresh['identity'] != observation['identity'] or fresh['in_mode'] or provider_activity(fresh)['state'] == 'approval' or native_input_dialog(fresh):
                fail(409, 'Agent or terminal changed; message was not pasted')
            fresh_state=verify_active_message(request,fresh) if active else None
            fresh_guard=message_input_guard(fresh,fresh_state) if active else fresh['screen']
            if not fresh_guard or fresh_guard!=guard:
                if active: return dict(sent=False,deferred=True,not_sent=True)
                fail(409,'Terminal changed; message was not pasted')
            if request.get('require_ready') and provider_activity(fresh)['state'] != 'ready':
                fail(409, 'Agent is no longer Ready; no message was pasted')
            # -p honors bracketed paste; contents never become shell syntax.
            try:
                tmux(request, 'paste-buffer', '-p', '-d', '-b', buffer, '-t', observation['target'])
                tmux(request, 'send-keys', '-t', observation['target'], 'Enter')
            except (Failure, subprocess.SubprocessError):
                fail(502, 'Delivery uncertain; check the terminal before sending again')
            return dict(sent=True,submitted_while_working=bool(fresh_state and fresh_state['state']=='working'))
        finally:
            try: tmux(request, 'delete-buffer', '-b', buffer)
            except Failure: pass
    candidates = conversations(observation)
    selected = request.get('conversation')
    if not selected:
        linked = [c for c in candidates if c['linked']]
        if len(linked) == 1: selected = linked[0]['id']
        elif len(candidates) == 1 and not observation['env'].get('CC_LAUNCH_ID'): selected = candidates[0]['id']
    chosen = next((c for c in candidates if c['id'] == selected), None)
    if selected and not chosen:
        fail(409, 'Conversation is no longer available for this project')
    result = dict(instance=observation['identity'], screen=observation['screen'], context=observation['context'],
                  project=observation['cwd'], provider=observation['kind'], selected=selected,
                  capabilities=capability_payload(observation['kind']),
                  approval=approval_menu(observation), input_request=input_question(observation),
                  association='process' if chosen and chosen['linked'] else 'project' if chosen else 'none',
                  conversations=[{k:v for k,v in c.items() if k != 'path'} for c in candidates],
                  activity=provider_activity(observation, candidates),
                  messages=[], older_cursor=None,
                  send_available=bool(observation['identity']) and not observation['in_mode']
                      and capability_available(observation['kind'], 'ordinary_message_submission')
                      and capability_available(observation['kind'], 'acceptance_confirmation'))
    if observation.get('history_error'): result['history_unavailable']=observation['history_error']
    if not result['send_available']:
        result['send_reason']=capability_reason(observation['kind'], 'ordinary_message_submission')
    if result['input_request'] and result['input_request']['supported']:
        question=result['input_request'];anchor=question_request_id(observation,question,candidates)
        if anchor:
            question['request_id']=anchor
            question['menu_id']=question['id']
            question['id']=hashlib.sha256((question['id']+'/'+anchor).encode()).hexdigest()
        else:
            question['supported']=False
            question['reason']='The pending native question call could not be verified; answer in the terminal.'
        try: result['input_request']['text_max_bytes']=min(512,max(0,int(tmux(request,'display-message','-p','-t',observation['target'],'#{pane_width}').strip())-12))
        except (Failure,ValueError):result['input_request']['text_max_bytes']=0
    if result['input_request'] or result['activity'].get('source')=='claude_input':
        result['send_available']=False
        result['send_reason']='Claude is waiting for an answer in a native dialog. Respond in the terminal.'
    if observation['kind']=='pi' and (pi_dialog(observation) or result['activity']['state']=='approval'):
        result['send_available']=False
        result['send_reason']='Pi is waiting for input in a dialog. Answer it in the terminal before sending a message.'
    result['background_tasks']=observed_background_tasks(observation,chosen)
    if chosen:
        if observation['kind']=='goose':
            try:
                result.update(goose_history_page(observation,chosen,request))
            except Failure as error:
                result.update(history_unavailable=error.message,messages=[],activities=[],history_reset=True,
                              history_notice=error.message,
                              history_page=dict(protocol='cc.history.v1',store_id=goose_history_store_id(observation,chosen),
                                                session_id=chosen['session'],revision='',reset=True,next_cursor=None))
        else:
            info, version = transcript_version(chosen)
            prefix = {'claude':'claude-visible-v3:', 'codex':'codex-visible-v2:'}.get(observation['kind'], '')
            history_version = prefix + version
            result['history_version'] = history_version
            history_before=request.get('before')
            cursor_reset=False
            if request.get('history_cursor') is not None:
                history_before,cursor_reset=decode_history_cursor(request['history_cursor'],observation['kind'],chosen,history_version)
            known_branch=None if cursor_reset else request.get('known_branch')
            if history_before is None and not cursor_reset and request.get('known_version') == history_version:
                result['history_unchanged'] = True
            else:
                result.update(history(chosen['path'], observation['kind'], history_before, known_branch, chosen.get('leaf_id',False)))
            if (observation['kind']=='codex' and isinstance(request.get('known_version'), str)
                and not request['known_version'].startswith(prefix)):
                result['history_reset'] = True
                result['history_notice'] = 'Conversation display updated to exclude harness-generated context.'
            reset=cursor_reset or bool(result.get('history_reset'))
            if cursor_reset:
                result['history_reset']=True
                result['history_notice']='History changed while paging; the latest page was reloaded.'
            older=result.get('older_cursor')
            result['history_page']=dict(protocol='cc.history.v1',store_id=history_store_id(chosen),
                                        session_id=chosen.get('session',chosen['id']),revision=history_version,
                                        reset=reset,next_cursor=encode_history_cursor(observation['kind'],chosen,history_version,older) if older is not None and not reset else None)
            if history_before is None and chosen.get('linked') and not result.get('history_unchanged'):
                result['_outbox_observation']=dict(log=dict(conversation=chosen['id'],device=info.st_dev,inode=info.st_ino,size=info.st_size),users=[dict(position=message['legacy_position'],digest=message.get('input_hash')) for message in result.get('messages',[]) if message['role']=='user' and message.get('input_hash') and type(message.get('legacy_position')) is int])
                if observation['kind']=='pi': result['_outbox_observation']['pi_session']=chosen['session']
            if history_before is None:
                result['reply'] = reply_observation(chosen, observation['kind'], request.get('known_reply_version'), request.get('known_reply_order_key'), None if result.get('history_unchanged') else result)
    return result

if __name__ == '__main__':
    try:
        body = sys.stdin.buffer.read(160 * 1024 + 1)
        if len(body) > 160 * 1024: fail(413, 'Agent request exceeded its bounded JSON limit')
        request = json.loads(body)
        response = {'ok': execute(request)}
    except Failure as e:
        response = {'status': e.status, 'error': e.message}
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, sqlite3.Error):
        response = {'status': 502, 'error': 'Agent observation failed; refresh or open the terminal'}
    json.dump(response, sys.stdout, ensure_ascii=True)
