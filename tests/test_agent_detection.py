"""Foreground wrapper detection, terminal/group proof and identity stability."""
import importlib.util,hashlib,os,stat,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('agent',Path(__file__).parents[1]/'src/agent_remote.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class Detection(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.processes={};self.kinds={}
  for pid,parent,group,kind in [(100,1,100,None),(200,100,200,None),(201,200,200,'claude')]:self.add(pid,parent,group,kind)
  (self.root/'200/task/200/children').write_text('201')
 def add(self,pid,parent,group,kind):
  base=self.root/str(pid);(base/'task'/str(pid)).mkdir(parents=True);(base/'task'/str(pid)/'children').write_text('')
  (base/'comm').write_text(kind or 'bash')
  (base/'cmdline').write_bytes((kind or '/bin/bash').encode()+b'\0')
  self.processes[pid]=dict(pid=pid,parent=parent,group=group,tty=99,foreground=200,start=str(pid)+'-start',base=base);self.kinds[str(base)]=kind
 def resolve(self,info=None,device=None,actual_kind=False):
  kind_lookup=a.process_kind if actual_kind else lambda base:self.kinds[str(base)]
  with patch.object(a,'process_info',side_effect=info or (lambda pid:dict(self.processes[pid]))),patch.object(a,'process_kind',side_effect=kind_lookup),patch.object(a.os,'stat',side_effect=device or (lambda path:SimpleNamespace(st_mode=stat.S_IFCHR|0o600,st_rdev=99))):
   return a.foreground_agent(100)
 def test_unique_same_terminal_foreground_child_is_detected(self):
  result=self.resolve();self.assertEqual(result[2]['pid'],201);self.assertEqual(result[3],'claude')
 def test_background_groups_other_terminals_and_redirected_stdin_are_rejected(self):
  self.processes[201]['group']=300;self.assertIsNone(self.resolve());self.processes[201]['group']=200
  self.processes[201]['tty']=88;self.assertIsNone(self.resolve());self.processes[201]['tty']=99
  self.assertIsNone(self.resolve(device=lambda path:SimpleNamespace(st_mode=stat.S_IFCHR|0o600,st_rdev=88 if '/201/' in str(path) else 99)))
 def test_ambiguous_clis_and_pid_reuse_are_rejected(self):
  self.add(202,200,200,'codex');(self.root/'200/task/200/children').write_text('201 202');self.assertIsNone(self.resolve())
  (self.root/'200/task/200/children').write_text('201');counts={}
  def info(pid):
   counts[pid]=counts.get(pid,0)+1;result=dict(self.processes[pid])
   if pid==201 and counts[pid]>1:result['start']='reused'
   return result
  self.assertIsNone(self.resolve(info=info))
 def test_known_group_leader_remains_primary_and_bounds_fail_closed(self):
  self.kinds[str(self.root/'200')]='codex';self.assertEqual(self.resolve()[2]['pid'],200)
  self.kinds[str(self.root/'200')]=None
  for pid in range(210,244):self.add(pid,200,200,None)
  (self.root/'200/task/200/children').write_text(' '.join(map(str,range(210,244))))
  with self.assertRaises(a.Failure) as error:self.resolve()
  self.assertEqual(error.exception.status,413)
 def test_direct_identity_hash_is_unchanged_and_wrappers_include_child_identity(self):
  base=self.root/'200';(base/'cmdline').write_bytes(b'claude\0');(base/'environ').write_bytes(b'VIRTUAL_ENV=/fixture/.venv\0UNRELATED_SECRET=ignore\0');(base/'cwd').symlink_to(self.root)
  pane=dict(self.processes[100]);leader=dict(self.processes[200]);candidate=dict(leader)
  def tmux(request,*args,**kw):
   if args[0]=='list-panes':return '@1\t%1'
   if args[0]=='display-message':return '100\tclaude\t0\t0'
   return ''
  request=dict(session='$1',window='@1',pane='%1',socket='/tmp/fixture.sock')
  with patch.object(a,'tmux',side_effect=tmux),patch.object(a,'foreground_agent',return_value=(pane,leader,candidate,'claude',None)):
   direct=a.observe(request)
  self.assertEqual(direct['env'],{'VIRTUAL_ENV':'/fixture/.venv'});self.assertEqual(direct['socket'],'/tmp/fixture.sock')
  boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip();expected=hashlib.sha256(f'{boot}:100:100-start:200:200-start:claude'.encode()).hexdigest();self.assertEqual(direct['identity'],expected)
  child=dict(candidate,pid=201,start='201-start')
  with patch.object(a,'tmux',side_effect=tmux),patch.object(a,'foreground_agent',return_value=(pane,leader,child,'claude',None)):
   wrapped=a.observe(request)
  self.assertNotEqual(wrapped['identity'],expected);self.assertEqual(wrapped['kind'],'claude')

 def test_outer_interactive_goose_wins_over_delegated_cli_children(self):
  (self.root/'200/comm').write_text('goose')
  (self.root/'200/cmdline').write_bytes(b'/usr/bin/goose\0session\0')
  (self.root/'201/comm').write_text('claude')
  (self.root/'201/cmdline').write_bytes(b'/usr/bin/claude\0')
  self.assertEqual(self.resolve(actual_kind=True)[3:5],('goose','session'))

 def test_wrapped_interactive_goose_wins_over_its_provider_child(self):
  self.add(202,201,200,'claude')
  (self.root/'200/task/200/children').write_text('201')
  (self.root/'201/task/201/children').write_text('202')
  (self.root/'201/comm').write_text('goose')
  (self.root/'201/cmdline').write_bytes(b'/usr/bin/goose\0session\0')
  self.assertEqual(self.resolve(actual_kind=True)[3:5],('goose','session'))

 def test_noninteractive_goose_parent_cannot_expose_a_delegated_provider(self):
  (self.root/'200/comm').write_text('goose')
  (self.root/'200/cmdline').write_bytes(b'/usr/bin/goose\0run\0--text\0one shot\0')
  (self.root/'201/comm').write_text('claude')
  (self.root/'201/cmdline').write_bytes(b'/usr/bin/claude\0')
  self.assertIsNone(self.resolve(actual_kind=True))

 def test_direct_interactive_goose_with_redirected_stdin_is_rejected(self):
  (self.root/'200/comm').write_text('goose')
  (self.root/'200/cmdline').write_bytes(b'/usr/bin/goose\0session\0')
  device=lambda path:SimpleNamespace(st_mode=stat.S_IFCHR|0o600,st_rdev=88 if '/200/' in str(path) else 99)
  self.assertIsNone(self.resolve(device=device,actual_kind=True))

class ProviderBoundary(unittest.TestCase):
 def test_provider_names_are_exact_and_pi_alias_is_preserved(self):
  for kind in ('codex','claude','pi'):
   self.assertEqual(a.provider_from_names((kind,)),kind)
  self.assertEqual(a.provider_from_names(('pi-coding-agent',)),'pi')
  self.assertEqual(a.provider_from_names(('goose',)),'goose')
  self.assertEqual(a.provider_from_names(('goose-cli',)),'goose')
  for unrelated in ('my-claude-wrapper','codex-helper','pip','ping','my-goose','goose-helper'):
   self.assertIsNone(a.provider_from_names((unrelated,)))

 def test_goose_cli_classification_accepts_only_interactive_native_forms(self):
  accepted=(
   (['/usr/bin/goose','session'],'session'),
   (['/usr/bin/goose','s','--resume','--session-id','20261106_1'],'session'),
   (['/usr/bin/goose','run','--interactive','--text','initial work'],'run-interactive'),
   (['/usr/bin/goose','run','-t','initial work','-s'],'run-interactive'),
   (['/usr/bin/goose','run','-i','-','-s'],'run-interactive'),
  )
  for argv,expected in accepted:
   with self.subTest(argv=argv):self.assertEqual(a.goose_invocation(argv),expected)
  rejected=(
   ['/usr/bin/goose'],
   ['/usr/bin/goose','session','list'],
   ['/usr/bin/goose','run','--text','one shot'],
   ['/usr/bin/goose','run','--text','text with --interactive'],
   ['/usr/bin/goose','run','--interactive=false'],
   ['/usr/bin/goose','run','--interactive','--explain'],
   ['/usr/bin/goose','acp'], ['/usr/bin/goose','serve'], ['/usr/bin/goose','mcp','developer'],
   ['/usr/bin/goose','configure'], ['/usr/bin/goose','doctor'], ['/usr/bin/goose','--help'],
   ['/usr/bin/goose','session','--fork'],
   ['/usr/bin/goose','session','--session-id','20261106_1'],
   ['/usr/bin/my-goose','session'],
  )
  for argv in rejected:
   with self.subTest(argv=argv):self.assertIsNone(a.goose_invocation(argv))

 def test_goose_data_roots_follow_provider_environment_and_platform_rules(self):
  self.assertEqual(str(a.goose_data_dir({'HOME':'/home/fixture'})),
                   '/home/fixture/.local/share/goose')
  self.assertEqual(str(a.goose_data_dir({'HOME':'/home/fixture','XDG_DATA_HOME':'/data/fixture'})),
                   '/data/fixture/goose')
  self.assertEqual(str(a.goose_data_dir({'HOME':'/home/fixture','XDG_DATA_HOME':'relative'})),
                   '/home/fixture/.local/share/goose')
  self.assertEqual(str(a.goose_data_dir({'HOME':'/home/fixture','GOOSE_PATH_ROOT':'/profile/goose'})),
                   '/profile/goose/data')
  self.assertEqual(str(a.goose_data_dir({'HOME':'/home/fixture','GOOSE_PATH_ROOT':'relative'})),
                   '/home/fixture/.local/share/goose')
  self.assertEqual(str(a.goose_data_dir({},platform='darwin',home='/Users/fixture')),
                   '/Users/fixture/Library/Application Support/Block/goose')
  self.assertEqual(str(a.goose_data_dir({'APPDATA':r'C:\Users\fixture\Roaming'},platform='win32',home=r'C:\Users\fixture')),
                   r'C:\Users\fixture\Roaming\Block\goose\data')

 def test_goose_store_replacement_changes_the_scoped_storage_identity(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)/'goose-data';(root/'sessions').mkdir(parents=True)
   database=root/'sessions'/'sessions.db';database.write_bytes(b'fixture')
   before=a.goose_data_identity(root)
   database.rename(root/'sessions'/'old.db')
   database.write_bytes(b'replacement')
   self.assertNotEqual(a.goose_data_identity(root),before)

 def test_unknown_provider_is_rejected_before_launch_io(self):
  with patch.object(a,'tmux',side_effect=AssertionError('unexpected tmux IO')), \
       patch.object(a,'project_directory',side_effect=AssertionError('unexpected filesystem work')):
   for provider in ('mystery', [], None):
    with self.subTest(provider=provider):
     with self.assertRaises(a.Failure) as error:
      a.execute(dict(action='launch',provider=provider))
     self.assertEqual(error.exception.status,400)

 def test_unknown_provider_cannot_fall_through_to_claude_history(self):
  with self.assertRaises(a.Failure) as error:
   a.conversations(dict(kind='unknown',cwd='/tmp',env={},base=None,args=[]))
  self.assertEqual(error.exception.status,400)
  with self.assertRaises(a.Failure) as error:
   a.history('/definitely/not/read','unknown')
  self.assertEqual(error.exception.status,400)

 def test_goose_process_and_read_only_project_history_capabilities_are_enabled(self):
  values=a.capability_payload('goose')
  for capability in a.CAPABILITY_NAMES:
   available=capability in ('process_observation','project_history','close_agent')
   self.assertEqual(values[capability]['available'],available)
   self.assertEqual(bool(values[capability]['reason']),not available)
  for provider in ('codex','claude','pi'):
   self.assertTrue(a.capability_payload(provider)['ordinary_message_submission']['available'])
  self.assertFalse(a.capability_payload('pi')['native_approval']['available'])

 def test_direct_goose_actions_are_rejected_before_mutating_io(self):
  observation=dict(kind='goose',identity='process',screen='screen',target='$1:@1.%1',
                   context='',visible='',in_mode=False,env={},cwd='/tmp',base=None,args=[])
  actions=(
   dict(action='send',identity='process',screen='screen',text='hello'),
   dict(action='approval',identity='process',screen='screen'),
   dict(action='restart_prepare',identity='process'),
  )
  with patch.object(a,'observe',return_value=observation), \
       patch.object(a,'tmux',side_effect=AssertionError('unexpected terminal IO')), \
       patch.object(a,'launch_executable',side_effect=AssertionError('unexpected launch IO')):
   for request in actions:
    with self.subTest(action=request['action']):
     with self.assertRaises(a.Failure) as error:
      a.execute(request)
     self.assertEqual(error.exception.status,409)
   for action in ('launch_options','launch'):
    with self.subTest(action=action):
     with self.assertRaises(a.Failure) as error:
      a.execute(dict(action=action,provider='goose'))

 def test_goose_close_requires_exact_process_identity_before_killing_window(self):
  observation=dict(kind='goose',identity='process',screen='screen',target='$1:@1.%1',
                   context='',visible='',in_mode=False,env={},cwd='/tmp',base=None,args=[])
  request=dict(action='close_agent',session='$1',window='@1',pane='%1',identity='stale')
  with patch.object(a,'observe',return_value=observation),patch.object(a,'tmux') as tmux:
   with self.assertRaises(a.Failure) as error:a.execute(request)
   self.assertEqual(error.exception.status,409);tmux.assert_not_called()
   request['identity']='process'
   self.assertEqual(a.execute(request),dict(closed=True))
   tmux.assert_called_once_with(request,'kill-window','-t','$1:@1')
