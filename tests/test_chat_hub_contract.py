import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ChatHubContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_template = (ROOT / 'templates' / 'base.html').read_text(encoding='utf-8')
        cls.hub_script = (ROOT / 'static' / 'js' / 'chat-hub.js').read_text(encoding='utf-8')
        cls.main_script = (ROOT / 'static' / 'js' / 'main.js').read_text(encoding='utf-8')
        cls.app_source = (ROOT / 'app.py').read_text(encoding='utf-8')
        cls.chat_api_source = (ROOT / 'routes' / 'chat_api.py').read_text(encoding='utf-8')

    def test_drawer_is_global_but_not_duplicated_on_full_chat_page(self):
        self.assertIn("request.endpoint != 'chat'", self.base_template)
        self.assertIn('id="chat-hub-drawer"', self.base_template)

    def test_fab_cannot_submit_the_underlying_medical_record(self):
        fab_id = self.base_template.index('id="chat-hub-fab"')
        fab_markup = self.base_template[fab_id - 100:fab_id + 500]
        self.assertIn('type="button"', fab_markup)

    def test_chat_notifications_no_longer_navigate_away(self):
        self.assertNotIn("window.location.href = '/chat'", self.main_script)
        self.assertNotIn("onclick=\"window.location.href='/chat'\"", self.main_script)

    def test_messages_are_rendered_as_text_not_html(self):
        self.assertIn("text.textContent = message.message || '';", self.hub_script)
        self.assertNotIn('messagesElement.innerHTML', self.hub_script)

    def test_read_receipt_only_happens_after_messages_load(self):
        load_position = self.hub_script.index('const messagesChanged = renderMessages(Array.isArray(result) ? result : []);')
        read_position = self.hub_script.index('if (markRead && messagesChanged) await markConversationRead(contactId);')
        self.assertLess(load_position, read_position)

    def test_notification_state_is_scoped_to_the_authenticated_user(self):
        self.assertIn('`chatLastUnreadCount:${chatStorageScope}`', self.main_script)
        self.assertIn('`chatLastSeenMessageId:${chatStorageScope}`', self.main_script)

    def test_stale_contact_requests_are_ignored(self):
        self.assertIn('sequence !== contactsRequestSequence', self.hub_script)
        self.assertIn('contactsRequestSequence += 1;', self.hub_script)

    def test_closed_drawer_invalidates_pending_poll(self):
        self.assertIn('const generation = ++pollingGeneration;', self.hub_script)
        self.assertIn('if (generation === pollingGeneration) pollingMessages = false;', self.hub_script)

    def test_chat_api_rejects_invalid_and_oversized_messages(self):
        self.assertIn("return jsonify({'error': 'Destinatário inválido'}), 400", self.chat_api_source)
        self.assertIn("if len(message_text) > 4000:", self.chat_api_source)


if __name__ == '__main__':
    unittest.main()
