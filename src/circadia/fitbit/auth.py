import base64
import json
import logging
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

TOKEN_FILE = Path("./data/tokens.json")


class FitbitAuth:
    def __init__(self, client_id: str, client_secret: str, token_path: Path = TOKEN_FILE):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_path = token_path
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    @property
    def refresh_token(self) -> Optional[str]:
        return self._refresh_token

    def load_tokens(self) -> tuple[Optional[str], Optional[str]]:
        if self.token_path.exists():
            with open(self.token_path) as f:
                tokens = json.load(f)
                self._access_token = tokens.get("access_token")
                self._refresh_token = tokens.get("refresh_token")
        return self._access_token, self._refresh_token

    def save_tokens(self, access_token: str, refresh_token: str) -> None:
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        self._access_token = access_token
        self._refresh_token = refresh_token
        with open(self.token_path, "w") as f:
            json.dump({"access_token": access_token, "refresh_token": refresh_token}, f)
        logger.info("Tokens saved to %s", self.token_path)

    def refresh(self, current_refresh_token: Optional[str] = None) -> tuple[str, str]:
        if current_refresh_token is None:
            current_refresh_token = self._refresh_token

        if current_refresh_token is None:
            raise ValueError("No refresh token available")

        url = "https://api.fitbit.com/oauth2/token"
        credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": current_refresh_token,
        }

        response = httpx.post(url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        new_access_token = token_data["access_token"]
        new_refresh_token = token_data["refresh_token"]

        self.save_tokens(new_access_token, new_refresh_token)
        logger.info("Tokens refreshed successfully")

        return new_access_token, new_refresh_token

    def initialize(self, initial_refresh_token: Optional[str] = None) -> str:
        if initial_refresh_token:
            self._refresh_token = initial_refresh_token
            access_token, refresh_token = self.refresh(initial_refresh_token)
            return access_token

        self.load_tokens()
        if self._refresh_token:
            access_token, _ = self.refresh(self._refresh_token)
            return access_token

        raise ValueError("No refresh token available. Provide FITBIT_REFRESH_TOKEN in .env")
