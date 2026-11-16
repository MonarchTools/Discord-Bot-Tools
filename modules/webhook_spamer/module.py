import requests
import threading
import time
import re
from modules.base_module import BaseModule

class WebhookSpamerModule(BaseModule):
    NAME = "Webhook Spamer"
    ICON = "🪝"
    REQUIRES_TOKEN = False
    REQUIRES_GUILD = False

    def _build_ui(self):
        self._create_label("Webhook URL:", 0)
        self._create_entry("webhook_url", 0, "https://discord.com/api/webhooks/...")
        self._create_label("Message 1:", 1)
        self._create_entry("msg1", 1, "First message...")
        self._create_label("Message 2:", 2)
        self._create_entry("msg2", 2, "Second message...")
        self._create_label("Total Messages:", 3)
        self._create_entry("count", 3, "e.g., 100")
        self._create_button("⚡ START SPAM", self._execute, 4, color="#660000")

    def _execute(self):
        url = self._get_entry("webhook_url")
        msg1 = self._get_entry("msg1")
        msg2 = self._get_entry("msg2")
        count = self._get_entry("count")
        
        if not re.match(r'https://discord.com/api/webhooks/\d+/[A-Za-z0-9_-]+', url):
            return self.logger.error("Invalid Webhook URL!")
        if not count.isdigit() or int(count) <= 0:
            return self.logger.error("Invalid count!")
        
        self.parent.winfo_toplevel().run_in_thread(self._run_spam, url, msg1, msg2, int(count))

    def _run_spam(self, url: str, msg1: str, msg2: str, count: int):
        self.logger.info(f"Starting webhook spam ({count} messages)...")
        success, failed = 0, 0
        
        def send_message(msg):
            nonlocal success, failed
            try:
                response = requests.post(url, json={"content": msg}, timeout=10)
                if response.status_code in [200, 204]:
                    success += 1
                elif response.status_code == 429:
                    retry = response.json().get("retry_after", 1)
                    time.sleep(retry)
                    send_message(msg)
                else:
                    failed += 1
            except Exception:
                failed += 1

        for i in range(count):
            msg = msg1 if i % 2 == 0 else (msg2 or msg1)
            t = threading.Thread(target=send_message, args=(msg,))
            t.start()
            time.sleep(0.1)
        
        time.sleep(2)
        self.logger.success(f"Done! Success: {success}, Failed: {failed}")