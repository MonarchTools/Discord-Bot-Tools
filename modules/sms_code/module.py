import pyautogui
import time
from modules.base_module import BaseModule

class SmsCodeModule(BaseModule):
    NAME = "SMS/Message Spammer"
    ICON = "⌨"
    REQUIRES_TOKEN = False
    REQUIRES_GUILD = False

    def _build_ui(self):
        self._create_label("Message:", 0)
        self._create_entry("message", 0, "Message to type...")
        self._create_label("Count:", 1)
        self._create_entry("count", 1, "e.g., 100")
        self._create_label("Delay (seconds):", 2)
        self._create_entry("delay", 2, "e.g., 5")
        self._create_button("⚡ START (5s countdown)", self._execute, 3, color="#ffcc00")
        self._create_label("⚠ Click any text field after starting!", 4)

    def _execute(self):
        message = self._get_entry("message")
        count = self._get_entry("count")
        delay = self._get_entry("delay") or "5"
        
        if not message or not count.isdigit():
            return self.logger.error("Invalid inputs!")
        
        self.parent.winfo_toplevel().run_in_thread(self._run_spam, message, int(count), float(delay))

    def _run_spam(self, message: str, count: int, delay: float):
        self.logger.warning(f"Starting in {delay} seconds... Click target field!")
        time.sleep(float(delay))
        
        self.logger.info(f"Spamming '{message[:30]}...' {count} times")
        for i in range(count):
            try:
                pyautogui.write(message)
                pyautogui.press('enter')
                if (i + 1) % 10 == 0:
                    self.logger.success(f"Sent {i+1}/{count}")
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error: {e}")
                break
        self.logger.success("Spam completed!")