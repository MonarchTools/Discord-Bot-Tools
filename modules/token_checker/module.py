import requests
from modules.base_module import BaseModule


class TokenCheckerModule(BaseModule):
    NAME = "Token Checker"
    ICON = "🔍"
    REQUIRES_TOKEN = False
    REQUIRES_GUILD = False

    def _build_ui(self):
        self._create_label("Token to check:", 0)
        self._create_entry("token", 0, "Enter token here...", show="•")
        
        self._create_label("Token Type (auto/bot/user):", 1)
        self._create_entry("token_type", 1, "auto")
        
        self._create_button("🔍 CHECK TOKEN", self._execute, 2, color="#008f11")

    def _execute(self):
        token = self._get_entry("token")
        token_type = self._get_entry("token_type").lower() or "auto"
        
        if not token:
            self.logger.error("Token cannot be empty!")
            return
        
        self.parent.winfo_toplevel().run_in_thread(
            self._check_token, token, token_type
        )

    def _test(self, token: str, as_bot: bool):
        auth = f"Bot {token}" if as_bot else token
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        try:
            r = requests.get("https://discord.com/api/v10/users/@me", 
                           headers=headers, timeout=10)
            return r.status_code, r.json() if r.status_code == 200 else None
        except Exception as e:
            return 0, str(e)

    def _check_token(self, token: str, token_type: str):
        self.logger.info("Checking token...")
        
        if token.lower().startswith("bot "):
            token = token[4:].strip()
        
        status, data = None, None
        detected = None
        
        if token_type == "auto":
            status, data = self._test(token, as_bot=True)
            if status == 200:
                detected = "BOT"
            else:
                status, data = self._test(token, as_bot=False)
                if status == 200:
                    detected = "USER"
        elif token_type == "bot":
            status, data = self._test(token, as_bot=True)
            detected = "BOT" if status == 200 else "UNKNOWN"
        else:
            status, data = self._test(token, as_bot=False)
            detected = "USER" if status == 200 else "UNKNOWN"
        
        if status == 200 and data:
            username = data.get("username", "N/A")
            disc = data.get("discriminator", "0")
            email = data.get("email") or "Not available"
            phone = data.get("phone") or "Not available"
            mfa = "✅ Yes" if data.get("mfa_enabled") else "❌ No"
            nitro = ["❌ No", "💎 Classic", "💎 Full"][data.get("premium_type", 0)]
            is_bot = data.get("bot", False)
            
            # تعیین سطح توکن
            if not is_bot:
                if data.get("premium_type", 0) == 2 or (email != "Not available" and phone != "Not available"):
                    level = "High (Verified & Nitro)"
                elif email != "Not available" and phone != "Not available":
                    level = "Medium (Verified)"
                elif email != "Not available" or phone != "Not available":
                    level = "Low (Partially Verified)"
                else:
                    level = "Very Low (Unverified)"
            else:
                level = "Bot Token"
            
            self.logger.success(f"✅ VALID {detected} TOKEN!")
            self.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━")
            self.logger.info(f"👤 Username: {username}#{disc}")
            self.logger.info(f"🆔 ID: {data.get('id', 'N/A')}")
            self.logger.info(f"📧 Email: {email}")
            self.logger.info(f"📱 Phone: {phone}")
            self.logger.info(f"🔒 2FA: {mfa}")
            self.logger.info(f"💎 Nitro: {nitro}")
            self.logger.info(f"📊 Level: {level}")
            self.logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━")
        elif status == 401:
            self.logger.error("❌ INVALID TOKEN (401)")
        elif status == 403:
            self.logger.error("❌ FORBIDDEN (403)")
        elif status == 429:
            self.logger.error("❌ RATE LIMITED (429)")
        else:
            self.logger.error(f"❌ Error (Status: {status})")