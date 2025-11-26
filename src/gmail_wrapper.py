import os
import time
import random
import string
import re
import base64
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")

def get_gmail_service(credentials_path: str = CREDENTIALS_PATH, token_path: str = TOKEN_PATH):
    """Authenticates via OAuth2 and returns a Gmail API service."""
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # If refresh fails, force re-auth
                creds = None

        if not creds:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"credentials.json not found at {credentials_path}")
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

class GmailOAuthWrapper:
    def __init__(self, service):
        self.service = service

    def get_alias_email(self, email_address: str) -> str:
        username, domain = email_address.split("@")
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}+{suffix}@{domain}"

    def _extract_body_from_payload(self, payload: dict) -> str:
        body = payload['parts'][0].get('body', {}).get('data', '')        
        decoded = base64.urlsafe_b64decode(body.encode('ASCII'))
        try:
            return decoded.decode('utf-8', errors='replace')
        except UnicodeDecodeError:
            return decoded.decode('latin-1', errors='replace')

    def wait_for_verification_email(self, alias_email: str, timeout: int = 60, poll_interval: int = 5) -> Optional[str]:
        """Waits for an email to `alias_email` and extracts the verification link."""
        print(f"Waiting for email to {alias_email}...")
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                query = f'to:{alias_email}'
                resp = self.service.users().messages().list(userId='me', q=query, maxResults=1).execute()
                messages = resp.get('messages', [])

                if messages:
                    msg_id = messages[0]['id']
                    msg = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()

                    body = self._extract_body_from_payload(msg.get('payload', {}))

                    match = re.search(r'(https://[^\s]*login.tidal.com[^\s]*)', body)
                    if match:
                        return match.group(1)

            except Exception as e:
                print(f"Gmail API error: {e}")

            time.sleep(poll_interval)

        print("Timeout waiting for email.")
        return None