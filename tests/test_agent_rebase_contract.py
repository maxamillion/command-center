"""Synthetic contracts at the upstream/Goose history and message boundary."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('agent', Path(__file__).parents[1] / 'src/agent_remote.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class RebaseContracts(unittest.TestCase):
    def test_pi_outbox_keeps_command_receipts_separate_from_opaque_chat_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'session.jsonl'
            path.write_text('')
            observation = dict(kind='pi', identity='process', screen='screen', context='', in_mode=False)
            chosen = dict(id='conversation', session='native', path=str(path), linked=True)
            command = dict(position=200, digest='command-digest')
            history = dict(messages=[dict(id='opaque-display-id', legacy_position=123, role='user', input_hash='chat-digest')], commands=[command])
            with patch.object(a, 'observe', return_value=observation), patch.object(a, 'conversations', return_value=[chosen]), patch.object(a, 'provider_activity', return_value=dict(state='unknown')), patch.object(a, 'approval_menu', return_value=None), patch.object(a, 'native_input_dialog', return_value=False), patch.object(a, 'active_message_state', return_value=None), patch.object(a, 'history', return_value=history):
                result = a.execute(dict(action='outbox_status', identity='process'))
            self.assertEqual(result['users'], [dict(position=123, digest='chat-digest')])
            self.assertEqual(result['commands'], [command])
            self.assertEqual(result['pi_session'], 'native')

    def test_codex_filter_migration_resets_opaque_paging_and_keeps_receipt_positions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rollout.jsonl'
            path.write_text('\n'.join(json.dumps(dict(type='response_item', payload=dict(type='message', role=role, content=[dict(type='input_text' if role=='user' else 'output_text', text=text)]))) for role, text in [('user', 'Human input'), ('assistant', 'Visible reply')])+'\n')
            chosen = dict(id='conversation', session='native', path=str(path), linked=True)
            old_version = 'codex-visible-v1:old'
            token = a.encode_history_cursor('codex', chosen, old_version, 1)
            observation = dict(kind='codex', identity='process', screen='screen', context='', visible='', cwd=directory, env={}, in_mode=False)
            with patch.object(a, 'observe', return_value=observation), patch.object(a, 'conversations', return_value=[chosen]), patch.object(a, 'provider_activity', return_value=dict(state='unknown')), patch.object(a, 'approval_menu', return_value=None), patch.object(a, 'observed_background_tasks', return_value=None):
                result = a.execute(dict(action='details', known_version=old_version, history_cursor=token))
            self.assertTrue(result['history_reset'])
            self.assertTrue(result['history_page']['reset'])
            self.assertIsNone(result['history_page']['next_cursor'])
            self.assertTrue(result['history_version'].startswith('codex-visible-v2:'))
            self.assertEqual([message['text'] for message in result['messages']], ['Human input', 'Visible reply'])
            self.assertIsInstance(result['_outbox_observation']['users'][0]['position'], int)

    def test_goose_send_is_denied_before_upstream_busy_input_logic(self):
        with patch.object(a, 'observe', return_value=dict(kind='goose')), patch.object(a, 'native_input_dialog') as dialog, patch.object(a, 'verify_active_message') as active, patch.object(a, 'tmux') as transport:
            with self.assertRaises(a.Failure) as error:
                a.execute(dict(action='send', require_active=True))
            self.assertEqual(error.exception.status, 409)
            dialog.assert_not_called()
            active.assert_not_called()
            transport.assert_not_called()
