"""Synthetic common schema-17 fixtures for pinned v1.55/v1.57 layouts (Plan U1)."""
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('agent_remote',Path(__file__).parents[1]/'src/agent_remote.py')
agent=importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


def create_store(root,version=17,journal='delete'):
    data=Path(root)/'data'
    sessions=data/'sessions'
    sessions.mkdir(parents=True)
    database=sessions/'sessions.db'
    connection=sqlite3.connect(database)
    connection.execute(f'PRAGMA journal_mode={journal}')
    connection.executescript('''
      CREATE TABLE schema_version(version INTEGER NOT NULL);
      CREATE TABLE sessions(
        id TEXT PRIMARY KEY, name TEXT, user_set_name INTEGER,
        session_type TEXT NOT NULL, working_dir TEXT, created_at TEXT,
        updated_at TEXT, extension_data TEXT, provider_name TEXT,
        model_config_json TEXT, goose_mode TEXT, archived_at TIMESTAMP,
        project_id TEXT, parent_session_id TEXT, schedule_id TEXT,
        recipe_json TEXT, user_recipe_values_json TEXT,
        system_prompt_override TEXT, system_prompt_extras_json TEXT,
        container_id TEXT
      );
      CREATE TABLE messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT, message_id TEXT,
        session_id TEXT NOT NULL REFERENCES sessions(id), role TEXT NOT NULL,
        content_json TEXT NOT NULL, created_timestamp INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, tokens INTEGER,
        metadata_json TEXT
      );
      CREATE INDEX idx_messages_session_message ON messages(session_id,message_id);
    ''')
    connection.execute('INSERT INTO schema_version(version) VALUES (?)',(version,))
    connection.commit()
    os.chmod(database,0o600)
    return data,database,connection


def add_session(connection,session_id,cwd,*,session_type='user',schedule_id=None,
                archived_at=None,name='Fixture session',created_at='2026-11-06 10:00:00',
                updated_at='2026-11-06 10:05:00'):
    connection.execute('''INSERT INTO sessions(
      id,name,user_set_name,session_type,working_dir,created_at,updated_at,
      extension_data,provider_name,model_config_json,goose_mode,archived_at,
      schedule_id,recipe_json,system_prompt_override)
      VALUES(?,?,0,?,?,?,?,?,?,?,?,?,?,?,?)''',(
        session_id,name,session_type,cwd,created_at,updated_at,'{}','openai',
        '{"model_name":"fixture-model"}','approve',archived_at,schedule_id,
        '{"secret":"never return"}','SYSTEM_SECRET'))


def add_message(connection,session_id,role,text,created_timestamp,*,message_id=None,metadata=None):
    connection.execute('''INSERT INTO messages(message_id,session_id,role,content_json,
      created_timestamp,metadata_json) VALUES(?,?,?,?,?,?)''',(
        message_id,session_id,role,json.dumps([{'type':'text','text':text}]),
        created_timestamp,json.dumps(metadata or {'userVisible':True})))


class GooseStore(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='cc-goose-store-')
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.cwd=self.root/'project'
        self.cwd.mkdir()
        self.data,self.database,self.writer=create_store(self.root)
        self.addCleanup(self.writer.close)
        add_session(self.writer,'20261106_1',str(self.cwd))
        self.writer.commit()

    def observation(self,data=None,cwd=None):
        data=Path(data or self.data)
        return dict(kind='goose',storage_root=str(data),
                    storage_identity=agent.goose_data_identity(data),
                    cwd=str(cwd or self.cwd))

    def test_candidates_are_project_scoped_whitelisted_and_session_rows_are_read_only(self):
        add_session(self.writer,'20261106_2',str(self.cwd),session_type='hidden')
        add_session(self.writer,'20261106_3',str(self.cwd),schedule_id='scheduled-job')
        add_session(self.writer,'20261106_4',str(self.root),name='Other project')
        add_session(self.writer,'20261106_5',str(self.cwd),archived_at='2026-11-06 11:00:00')
        self.writer.commit()
        before=self.database.read_bytes()
        contents=set(path.name for path in self.database.parent.iterdir())
        result=agent.goose_store_sessions(self.observation())
        self.assertEqual([row['session'] for row in result['conversations']],
                         ['20261106_5','20261106_1'])
        self.assertTrue(result['conversations'][0]['archived'])
        self.assertFalse(result['conversations'][0]['linked'])
        self.assertNotIn('path',result['conversations'][0])
        self.assertNotIn('recipe_json',json.dumps(result))
        self.assertNotIn('SYSTEM_SECRET',json.dumps(result))
        self.assertNotIn('secret',json.dumps(result))
        self.assertEqual(self.database.read_bytes(),before)
        self.assertEqual(set(path.name for path in self.database.parent.iterdir()),contents)
        with agent.GooseSessionStore(self.observation()) as store:
            with self.assertRaises(sqlite3.OperationalError):
                store.connection.execute("INSERT INTO sessions(id,session_type) VALUES('write','user')")
        self.assertEqual(self.database.read_bytes(),before)

    def test_rows_are_parameterized_bounded_and_order_by_timestamp_then_integer_id(self):
        session='20261106_1'
        add_message(self.writer,session,'assistant','Later timestamp, first row',30,message_id='same')
        add_message(self.writer,session,'user','Older timestamp',10,message_id='same')
        add_message(self.writer,session,'assistant','Tie, lower ID',30,message_id=None)
        add_message(self.writer,session,'assistant','Hidden by message metadata',10000,metadata={'userVisible':False})
        for index in range(105):
            add_message(self.writer,session,'assistant',f'Page row {index}',100+index)
        self.writer.commit()
        page=agent.goose_store_messages(self.observation(),session)
        self.assertEqual(len(page['messages']),agent.GOOSE_STORE_MAX_MESSAGES)
        self.assertIsNotNone(page['older'])
        ordered=[(int(row['created_timestamp']),int(row['id'])) for row in page['messages']]
        self.assertEqual(ordered,sorted(ordered))
        self.assertTrue(all(isinstance(row['id'],str) for row in page['messages']))
        self.assertTrue(any(row['user_visible'] is False for row in page['messages']))
        with self.assertRaises(agent.Failure):
            agent.goose_store_messages(self.observation(),"20261106_1' OR 1=1 --")
        older=agent.goose_store_messages(self.observation(),session,page['older'])
        self.assertGreater(len(page['messages']),0)
        self.assertLess((int(older['messages'][-1]['created_timestamp']),int(older['messages'][-1]['id'])),ordered[0])
        self.assertEqual(len(older['messages']),9)

    def test_malformed_and_oversized_rows_are_explicitly_omitted(self):
        self.writer.execute("INSERT INTO messages(session_id,role,content_json,created_timestamp,metadata_json) VALUES(?,?,?,?,?)",
                            ('20261106_1','assistant','not-json',50,'{}'))
        self.writer.execute("INSERT INTO messages(session_id,role,content_json,created_timestamp,metadata_json) VALUES(?,?,?,?,?)",
                            ('20261106_1','assistant',json.dumps([{'type':'text','text':'x'*70000}]),51,'{}'))
        self.writer.commit()
        result=agent.goose_store_messages(self.observation(),'20261106_1')
        self.assertEqual(result['messages'],[])
        self.assertTrue(result['limited'])

    def test_missing_corrupt_unknown_schema_and_unsafe_paths_fail_without_initializing(self):
        missing=self.root/'missing'/'data'
        missing.mkdir(parents=True)
        with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation(missing))
        self.assertEqual(list(missing.iterdir()),[])
        with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation(self.root))

        unknown_root=self.root/'unknown'
        unknown_data,unknown_db,unknown_writer=create_store(unknown_root,version=18)
        unknown_writer.close()
        with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation(unknown_data))
        unknown_db.write_bytes(b'not a SQLite file')
        os.chmod(unknown_db,0o600)
        with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation(unknown_data))

        link_root=self.root/'linked'
        link_data=link_root/'data';(link_data/'sessions').mkdir(parents=True)
        (link_data/'sessions'/'sessions.db').symlink_to(self.database)
        with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation(link_data))

        view_root=self.root/'view-schema'
        view_data,_,view_writer=create_store(view_root)
        view_writer.execute('DROP TABLE sessions')
        view_writer.execute('CREATE VIEW sessions AS SELECT NULL AS id,NULL AS name,NULL AS session_type,NULL AS working_dir,NULL AS created_at,NULL AS updated_at,NULL AS archived_at,NULL AS schedule_id')
        view_writer.commit();view_writer.close()
        with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation(view_data))

    def test_wal_only_commits_are_visible_without_writing_database_or_wal(self):
        wal_root=self.root/'wal-root'
        data,database,writer=create_store(wal_root,journal='wal')
        add_session(writer,'20261106_1',str(self.cwd))
        add_message(writer,'20261106_1','assistant','Committed only to WAL',500)
        writer.commit()
        self.assertTrue(Path(str(database)+'-wal').is_file())
        self.assertTrue(Path(str(database)+'-shm').is_file())
        before_db=database.read_bytes()
        before_wal=Path(str(database)+'-wal').read_bytes()
        result=agent.goose_store_messages(self.observation(data),'20261106_1')
        self.assertEqual(result['messages'][0]['content'][0]['text'],'Committed only to WAL')
        self.assertEqual(database.read_bytes(),before_db)
        self.assertEqual(Path(str(database)+'-wal').read_bytes(),before_wal)

        with agent.GooseSessionStore(self.observation(data)) as store:
            store.connection.execute('SELECT count(*) FROM messages').fetchone()
            completed=threading.Event()
            def concurrent_write():
                with sqlite3.connect(database,timeout=.5) as other:
                    other.execute("INSERT INTO messages(session_id,role,content_json,created_timestamp,metadata_json) VALUES(?,?,?,?,?)",
                                  ('20261106_1','assistant',json.dumps([{'type':'text','text':'Concurrent writer'}]),501,'{}'))
                completed.set()
            thread=threading.Thread(target=concurrent_write)
            thread.start()
            thread.join(1)
            self.assertTrue(completed.is_set())
            snapshot=store.messages('20261106_1')
            self.assertNotIn('Concurrent writer',[row['content'][0]['text'] for row in snapshot['messages']])
        writer.commit()
        concurrent=agent.goose_store_messages(self.observation(data),'20261106_1')
        self.assertIn('Concurrent writer',[row['content'][0]['text'] for row in concurrent['messages']])
        writer.close()

    def test_clean_wal_store_is_unavailable_without_creating_sidecars(self):
        wal_root=self.root/'clean-wal-root'
        data,database,writer=create_store(wal_root,journal='wal')
        add_session(writer,'20261106_1',str(self.cwd))
        writer.commit()
        writer.close()
        self.assertFalse(Path(str(database)+'-wal').exists())
        self.assertFalse(Path(str(database)+'-shm').exists())
        before=set(path.name for path in database.parent.iterdir())
        with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation(data))
        self.assertEqual(set(path.name for path in database.parent.iterdir()),before)

    def test_wal_without_existing_shared_memory_fails_without_creating_it(self):
        wal_root=self.root/'missing-shm-root'
        data,database,writer=create_store(wal_root,journal='wal')
        add_session(writer,'20261106_1',str(self.cwd))
        writer.commit()
        shm=Path(str(database)+'-shm')
        self.assertTrue(shm.exists())
        shm.unlink()
        with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation(data))
        self.assertFalse(shm.exists())
        writer.close()

    def test_busy_rollback_journal_returns_unavailable_within_deadline(self):
        blocker=sqlite3.connect(self.database,timeout=.1,isolation_level=None)
        blocker.execute('BEGIN EXCLUSIVE')
        started=time.monotonic()
        try:
            with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation())
        finally:
            blocker.execute('ROLLBACK')
            blocker.close()
        self.assertLess(time.monotonic()-started,.5)

    def test_world_or_group_writable_store_is_rejected(self):
        os.chmod(self.database,0o622)
        try:
            with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation())
        finally:
            os.chmod(self.database,0o600)

    def test_replaced_store_is_rejected_after_a_read(self):
        with self.assertRaises(agent.Failure):
            with agent.GooseSessionStore(self.observation()) as store:
                replacement_root=self.root/'replacement'
                _,replacement,replacement_writer=create_store(replacement_root)
                replacement_writer.close()
                os.replace(replacement,self.database)
                store.verify_current()

    def test_large_sparse_project_scan_stops_at_the_progress_budget(self):
        self.writer.executemany('''INSERT INTO sessions(
          id,name,session_type,working_dir,created_at,updated_at,schedule_id)
          VALUES(?,?,?,?,'2026-11-06','2026-11-06',NULL)''',
          ((f'other-{index}',None,'user',str(self.root/'other')) for index in range(30000)))
        self.writer.commit()
        started=time.monotonic()
        # Lower the limit to exercise progress-handler cancellation on a full table scan.
        with patch.object(agent,'GOOSE_STORE_MAX_QUERY_STEPS',10):
            with self.assertRaises(agent.Failure):agent.goose_store_sessions(self.observation())
        self.assertLess(time.monotonic()-started,1.0)

    def test_query_plans_show_bounded_row_ordering_and_known_scan_cost(self):
        with agent.GooseSessionStore(self.observation()) as store:
            session_plan=store.connection.execute(
                "EXPLAIN QUERY PLAN SELECT id,name FROM sessions WHERE working_dir=? "
                "AND session_type='user' AND schedule_id IS NULL ORDER BY rowid DESC LIMIT ?",
                (str(self.cwd),agent.GOOSE_STORE_MAX_SESSIONS+1)).fetchall()
            message_plan=store.connection.execute(
                'EXPLAIN QUERY PLAN SELECT id,message_id,session_id,role,content_json,created_timestamp,metadata_json '
                'FROM messages WHERE session_id=? ORDER BY created_timestamp DESC,id DESC LIMIT ?',
                ('20261106_1',agent.GOOSE_STORE_MAX_MESSAGES+1)).fetchall()
        self.assertTrue(any('SCAN sessions' in row[3] for row in session_plan),session_plan)
        self.assertTrue(any('idx_messages_session_message' in row[3] for row in message_plan),message_plan)
        self.assertTrue(any('TEMP B-TREE FOR ORDER BY' in row[3] for row in message_plan),message_plan)


if __name__=='__main__':unittest.main()
