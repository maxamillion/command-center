"""Synthetic Goose history projection/reset contracts; no live CLI or store."""
import json
import sqlite3
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_agent_goose_store as fixtures

agent=fixtures.agent


def add_blocks(connection,session_id,role,blocks,timestamp,*,message_id=None,metadata=None):
    connection.execute('''INSERT INTO messages(message_id,session_id,role,content_json,
      created_timestamp,metadata_json) VALUES(?,?,?,?,?,?)''',
      (message_id,session_id,role,json.dumps(blocks),timestamp,json.dumps(metadata or {'userVisible':True})))


class GooseHistory(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='cc-goose-history-')
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.cwd=self.root/'project';self.cwd.mkdir()
        self.data,self.database,self.writer=fixtures.create_store(self.root)
        self.addCleanup(self.writer.close)
        fixtures.add_session(self.writer,'20261106_1',str(self.cwd))
        self.writer.commit()
        self.observation=dict(kind='goose',storage_root=str(self.data),
                              storage_identity=agent.goose_data_identity(self.data),cwd=str(self.cwd))
        self.chosen=agent.goose_store_sessions(self.observation)['conversations'][0]

    def page(self,request=None):
        return agent.goose_history_page(self.observation,self.chosen,request or {})

    def test_chat_visibility_audience_hidden_context_and_media_are_projected_safely(self):
        add_blocks(self.writer,'20261106_1','user',[
            {'type':'text','text':'Visible question'},
            {'type':'text','text':'HIDDEN_AUDIENCE','annotations':{'audience':['assistant']}},
            {'type':'text','text':'EMPTY_AUDIENCE','annotations':{'audience':[]}},
            {'type':'image','data':'IMAGE_SECRET','mimeType':'image/png'},
            {'type':'document','data':'DOCUMENT_SECRET','mimeType':'text/plain','name':'private.txt'},
            {'type':'actionRequired','data':{'actionType':'elicitation','prompt':'CONTROL_SECRET'}},
        ],100,message_id='user-1')
        add_blocks(self.writer,'20261106_1','assistant',[
            {'type':'text','text':'Visible answer','annotations':{'audience':['user','assistant']}},
            {'type':'thinking','thinking':'THINKING_SECRET','signature':'SIGNATURE_SECRET'},
            {'type':'redactedThinking','data':'REDACTED_SECRET'},
            {'type':'systemNotification','msg':'SYSTEM_SECRET'},
        ],101,message_id='assistant-1')
        add_blocks(self.writer,'20261106_1','assistant',[{'type':'text','text':'HIDDEN_CONTEXT'}],102,
                   message_id='context-1',metadata={'userVisible':True,'turnContext':True})
        add_blocks(self.writer,'20261106_1','assistant',[{'type':'text','text':'HIDDEN_COMPACTION'}],103,
                   message_id='summary-1',metadata={'userVisible':True,'compactionSummary':True})
        add_blocks(self.writer,'20261106_1','user',[
            {'type':'toolResponse','id':'tool-only','toolResult':{'status':'success','value':[{'type':'text','text':'TOOL_RESULT_SECRET'}]}}
        ],104,message_id='result-1')
        self.writer.commit()

        result=self.page()
        self.assertEqual([(message['role'],message['text']) for message in result['messages']],[
            ('user','Visible question\n[Image omitted]\n[Document omitted]'),
            ('assistant','Visible answer'),
        ])
        self.assertEqual(result['messages'],sorted(result['messages'],key=lambda message:message['order_key']))
        encoded=json.dumps(result)
        self.assertEqual([entry['text'] for entry in result['activities'] if entry['kind']=='thinking'],['THINKING_SECRET'])
        for secret in ('HIDDEN_AUDIENCE','EMPTY_AUDIENCE','IMAGE_SECRET','DOCUMENT_SECRET','private.txt',
                       'CONTROL_SECRET','SIGNATURE_SECRET','REDACTED_SECRET',
                       'SYSTEM_SECRET','HIDDEN_CONTEXT','HIDDEN_COMPACTION','TOOL_RESULT_SECRET'):
            self.assertNotIn(secret,encoded)
        self.assertEqual(result['messages'][0]['timestamp'],'1970-01-01T00:01:40Z')

    def test_tool_activity_pairs_repeated_and_null_ids_and_hides_resource_paths(self):
        add_blocks(self.writer,'20261106_1','assistant',[
            {'type':'toolRequest','id':'repeat','toolCall':{'status':'success','value':{'name':'shell','arguments':{'command':'pwd'}}}},
        ],10,message_id='call-1')
        add_blocks(self.writer,'20261106_1','assistant',[
            {'type':'toolRequest','id':'repeat','toolCall':{'status':'success','value':{'name':'shell','arguments':{'command':'ls'}}}},
        ],11,message_id='call-2')
        add_blocks(self.writer,'20261106_1','assistant',[
            {'type':'toolRequest','id':None,'toolCall':{'status':'success','value':{'name':'nullable','arguments':{}}}},
        ],12,message_id='call-null')
        add_blocks(self.writer,'20261106_1','user',[
            {'type':'toolResponse','id':'repeat','toolResult':{'status':'success','value':[
                {'type':'text','text':'First output'},
                {'type':'resource','resource':{'uri':'file:///PRIVATE_SPILL_PATH'}},
                {'type':'image','data':'IMAGE_SECRET'},
            ]}},
        ],13,message_id='result-1')
        add_blocks(self.writer,'20261106_1','user',[
            {'type':'toolResponse','id':'repeat','toolResult':{'status':'error','error':'Second call failed'}},
        ],14,message_id='result-2')
        add_blocks(self.writer,'20261106_1','user',[
            {'type':'toolResponse','id':None,'toolResult':{'status':'success','value':{'content':[{'type':'text','text':'Null-id output'}],'isError':True}}},
        ],15,message_id='result-null')
        self.writer.commit()

        with agent.GooseSessionStore(self.observation) as store:
            raw=store.messages('20261106_1')
            wanted={(int(row['id']),index) for row in raw['messages'] if row['role']=='assistant'
                    for index,block in enumerate(row['content']) if block.get('type')=='toolRequest'}
            occurrences=store.activity_occurrences('20261106_1',wanted)
            self.assertTrue(occurrences['complete'],repr(occurrences))
            self.assertEqual(len(occurrences['calls']),3,repr(occurrences))
            self.assertEqual(len(occurrences['results']),3,repr(occurrences))

        result=self.page();activities=result['activities']
        self.assertEqual([entry['title'] for entry in activities],['shell','shell','nullable'])
        self.assertEqual([entry['status'] for entry in activities],['completed','error','error'],json.dumps(result))
        self.assertIn('First output\n[Resource omitted]\n[Image omitted]',activities[0]['output'])
        self.assertEqual(activities[1]['output'],'Second call failed')
        self.assertEqual(activities[2]['output'],'Null-id output')
        self.assertNotIn('PRIVATE_SPILL_PATH',json.dumps(result))
        self.assertNotIn('IMAGE_SECRET',json.dumps(result))
        self.assertNotIn('toolResult',json.dumps(result))
        self.assertNotIn('toolCall',json.dumps(result))

    def test_tool_result_update_does_not_move_reply_cursor_and_reinsert_resets(self):
        add_blocks(self.writer,'20261106_1','assistant',[{'type':'text','text':'Answer'}],100,
                   message_id='stable-assistant-id')
        add_blocks(self.writer,'20261106_1','assistant',[
            {'type':'toolRequest','id':'call','toolCall':{'status':'success','value':{'name':'shell','arguments':{}}}},
        ],101,message_id='call-row')
        add_blocks(self.writer,'20261106_1','user',[
            {'type':'toolResponse','id':'call','toolResult':{'status':'success','value':[{'type':'text','text':'before'}]}},
        ],102,message_id='result-row')
        self.writer.commit()
        before=agent.goose_reply_observation(self.observation,self.chosen)
        self.writer.execute("UPDATE messages SET content_json=? WHERE message_id='result-row'",
                            (json.dumps([{'type':'toolResponse','id':'call','toolResult':{'status':'success','value':[{'type':'text','text':'after'}]}}]),))
        self.writer.commit()
        updated=agent.goose_reply_observation(self.observation,self.chosen,before['version'],before['reply_order_key'])
        self.assertEqual(updated['cursor'],before['cursor'])
        self.assertEqual(updated['reply_order_key'],before['reply_order_key'])
        self.assertFalse(updated['reset'])

        add_blocks(self.writer,'20261106_1','assistant',[{'type':'text','text':'New reply'}],103,
                   message_id='new-assistant-id')
        self.writer.commit()
        fresh=agent.goose_reply_observation(self.observation,self.chosen,updated['version'],updated['reply_order_key'])
        self.assertNotEqual(fresh['cursor'],updated['cursor'])
        self.assertGreater(fresh['reply_order_key'],updated['reply_order_key'])
        self.assertFalse(fresh['reset'])

        self.writer.execute("DELETE FROM messages WHERE message_id='new-assistant-id'")
        self.writer.commit()
        add_blocks(self.writer,'20261106_1','assistant',[{'type':'text','text':'New reply'}],103,
                   message_id='new-assistant-id')
        self.writer.commit()
        reinserted=agent.goose_reply_observation(self.observation,self.chosen,fresh['version'],fresh['reply_order_key'])
        self.assertTrue(reinserted['reset'])
        self.assertEqual(reinserted['cursor'],fresh['cursor'])

    def test_cursor_pages_are_opaque_source_bound_and_revalidate_loaded_pages(self):
        for index in range(230):
            fixtures.add_message(self.writer,'20261106_1','user',f'Row {index}',index+100,
                                 message_id=f'user-{index}')
        self.writer.commit()
        first=self.page()
        cursor=first['history_page']['next_cursor']
        self.assertTrue(cursor.startswith('cc-history-v1.'))
        self.assertLessEqual(len(cursor),1024)
        second=self.page({'history_cursor':cursor})
        self.assertFalse(second['history_reset'])
        self.assertEqual(first['history_page']['revision'],second['history_page']['revision'])
        next_cursor=second['history_page']['next_cursor']
        self.assertIsNotNone(next_cursor)

        # Edit an already-loaded older page. The cursor carries bounded page
        # fingerprints, so loading the next page forces a fresh latest view.
        self.writer.execute("UPDATE messages SET content_json=? WHERE message_id='user-120'",
                            (json.dumps([{'type':'text','text':'edited loaded row'}]),))
        self.writer.commit()
        stale=self.page({'history_cursor':next_cursor})
        self.assertTrue(stale['history_reset'])
        self.assertTrue(stale['history_notice'])
        self.assertTrue(any('Row 229'==message['text'] for message in stale['messages']))

    def test_latest_page_revision_change_reloads_in_place_edits(self):
        fixtures.add_message(self.writer,'20261106_1','assistant','Before edit',100,message_id='editable')
        self.writer.commit()
        first=self.page()
        self.writer.execute("UPDATE messages SET content_json=? WHERE message_id='editable'",
                            (json.dumps([{'type':'text','text':'After edit'}]),))
        self.writer.commit()
        updated=self.page({'known_version':first['history_version']})
        self.assertTrue(updated['history_reset'])
        self.assertTrue(updated['history_page']['reset'])
        self.assertEqual([message['text'] for message in updated['messages']],['After edit'])

    def test_tool_call_and_result_across_page_boundary_are_reconciled(self):
        add_blocks(self.writer,'20261106_1','assistant',[
            {'type':'toolRequest','id':'across','toolCall':{'status':'success','value':{'name':'boundary-tool','arguments':{}}}},
        ],1,message_id='old-call')
        for index in range(105):
            fixtures.add_message(self.writer,'20261106_1','user',f'Intervening {index}',index+2,
                                 message_id=f'intervening-{index}')
        add_blocks(self.writer,'20261106_1','user',[
            {'type':'toolResponse','id':'across','toolResult':{'status':'success','value':[{'type':'text','text':'Boundary result'}]}},
        ],200,message_id='new-result')
        self.writer.commit()
        first=self.page()
        self.assertFalse(any(activity['title']=='boundary-tool' for activity in first['activities']))
        older=self.page({'history_cursor':first['history_page']['next_cursor']})
        boundary=next(activity for activity in older['activities'] if activity['title']=='boundary-tool')
        self.assertEqual(boundary['status'],'completed')
        self.assertEqual(boundary['output'],'Boundary result')

    def test_incomplete_full_store_activity_scan_does_not_claim_success(self):
        add_blocks(self.writer,'20261106_1','assistant',[
            {'type':'toolRequest','id':'limited','toolCall':{'status':'success','value':{'name':'bounded-tool','arguments':{}}}},
        ],1,message_id='call')
        add_blocks(self.writer,'20261106_1','user',[
            {'type':'toolResponse','id':'limited','toolResult':{'status':'success','value':[{'type':'text','text':'result'}]}},
        ],2,message_id='result')
        self.writer.commit()
        with patch.object(agent,'GOOSE_STORE_MAX_ACTIVITY_ROWS',1):
            result=self.page()
        entry=next(activity for activity in result['activities'] if activity['title']=='bounded-tool')
        self.assertEqual(entry['status'],'pending')
        self.assertTrue(result['activity_limited'])
        self.assertNotIn('result',entry.get('output',''))

    def test_conversation_list_is_unlinked_and_history_has_no_input_acceptance_hashes(self):
        candidates=agent.conversations(dict(self.observation))
        self.assertEqual(len(candidates),1)
        self.assertFalse(candidates[0]['linked'])
        self.assertNotIn('path',candidates[0])
        fixtures.add_message(self.writer,'20261106_1','user','Human-looking persisted row',50,message_id='u')
        self.writer.commit()
        result=self.page()
        user=next(message for message in result['messages'] if message['role']=='user')
        self.assertNotIn('input_hash',user)

    def test_malformed_rows_are_omitted_and_disclosed(self):
        self.writer.execute("INSERT INTO messages(session_id,role,content_json,created_timestamp,metadata_json) VALUES(?,?,?,?,?)",
                            ('20261106_1','assistant','not-json',50,'{}'))
        large=json.dumps([{'type':'text','text':'LARGE_SECRET'+'x'*70000}])
        self.writer.execute("INSERT INTO messages(session_id,role,content_json,created_timestamp,metadata_json) VALUES(?,?,?,?,?)",
                            ('20261106_1','assistant',large,51,json.dumps({'userVisible':True})))
        fixtures.add_message(self.writer,'20261106_1','user','Visible survives',52,message_id='visible')
        self.writer.commit()
        result=self.page()
        self.assertEqual([message['text'] for message in result['messages']],['Visible survives'])
        self.assertTrue(result['limited'])
        self.assertNotIn('LARGE_SECRET',json.dumps(result))

    def test_details_dispatch_returns_read_only_history_and_keeps_actions_disabled(self):
        observation=dict(self.observation,identity='a'*64,screen='b'*64,target='$1:@2.%3',
                         context='',visible='',in_mode=False,env={},base=None,args=[],project=str(self.cwd))
        add_blocks(self.writer,'20261106_1','user',[{'type':'text','text':'Selected project history'}],70,
                   message_id='project-message')
        self.writer.commit()
        with patch.object(agent,'observe',return_value=observation):
            result=agent.execute(dict(action='details',session='$1',window='@2',pane='%3',
                                       conversation=self.chosen['id']))
        self.assertEqual(result['association'],'project')
        self.assertFalse(next(row for row in result['conversations'] if row['id']==self.chosen['id'])['linked'])
        self.assertEqual(result['messages'][0]['text'],'Selected project history')
        self.assertTrue(result['capabilities']['project_history']['available'])
        self.assertFalse(result['capabilities']['ordinary_message_submission']['available'])
        self.assertFalse(result['send_available'])
        self.assertIsNone(result.get('message_token'))


if __name__=='__main__':unittest.main()
