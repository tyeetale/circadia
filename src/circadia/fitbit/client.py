import logging
import time
from typing import Any, Optional

import httpx
import pytz

from .auth import FitbitAuth

logger = logging.getLogger(__name__)


class FitbitRateLimitError(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after} seconds")


class FitbitClient:
    BASE_URL = "https://api.fitbit.com"

    def __init__(self, auth: FitbitAuth, client_id: str, client_secret: str):
        self.auth = auth
        self.client_id = client_id
        self.client_secret = client_secret
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=30.0)
        return self._client

    def _get_headers(self) -> dict[str, str]:
        if not self.auth.access_token:
            raise ValueError("Not authenticated. Call initialize() first.")
        return {
            "Authorization": f"Bearer {self.auth.access_token}",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        url: str,
        params: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> dict[str, Any] | httpx.Response:
        full_url = f"{self.BASE_URL}{url}"

        try:
            response = self.client.request(
                method, full_url, headers=self._get_headers(), params=params
            )

            if response.status_code == 200:
                if url.endswith(".tcx"):
                    return response
                return response.json()

            elif response.status_code == 429:
                retry_after = int(response.headers.get("Fitbit-Rate-Limit-Reset", 300)) + 60
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds")
                time.sleep(retry_after)
                return self._request(method, url, params, retry_count + 1)

            elif response.status_code == 401:
                logger.warning("Token expired, refreshing...")
                self.auth.refresh()
                return self._request(method, url, params, retry_count)

            elif response.status_code in (500, 502, 503, 504):
                if retry_count < 3:
                    logger.warning(f"Server error {response.status_code}, retrying...")
                    time.sleep(120)
                    return self._request(method, url, params, retry_count + 1)
                raise Exception(f"Server error after 3 retries: {response.status_code}")

            else:
                response.raise_for_status()
                return {}

        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}, retrying in 30 seconds")
            time.sleep(30)
            return self._request(method, url, params, retry_count + 1)

    def get(self, url: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return self._request("GET", url, params)

    def get_profile(self) -> dict[str, Any]:
        return self.get("/1/user/-/profile.json")

    def get_timezone(self) -> str:
        return self.get_profile()["user"]["timezone"]

    def get_timezone_obj(self) -> pytz.timezone:
        tz_name = self.get_timezone()
        if tz_name == "Automatic":
            tz_name = "UTC"
        return pytz.timezone(tz_name)

    def get_devices(self) -> list[dict[str, Any]]:
        return self.get("/1/user/-/devices.json")

    def get_battery_level(self, device_name: str) -> Optional[dict[str, Any]]:
        devices = self.get_devices()
        for device in devices:
            if device.get("deviceName") == device_name:
                return {
                    "last_sync_time": device.get("lastSyncTime"),
                    "battery_level": device.get("batteryLevel"),
                }
        return None

    def get_heart_rate_intraday(self, date: str, detail_level: str = "1sec") -> dict[str, Any]:
        return self.get(f"/1/user/-/activities/heart/date/{date}/1d/{detail_level}.json")

    def get_steps_intraday(self, date: str, detail_level: str = "1min") -> dict[str, Any]:
        return self.get(f"/1/user/-/activities/steps/date/{date}/1d/{detail_level}.json")

    def get_hrv(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1/user/-/hrv/date/{start_date}/{end_date}.json")

    def get_breathing_rate(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1/user/-/br/date/{start_date}/{end_date}.json")

    def get_skin_temperature(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1/user/-/temp/skin/date/{start_date}/{end_date}.json")

    def get_spo2(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1/user/-/spo2/date/{start_date}/{end_date}.json")

    def get_spo2_all(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1/user/-/spo2/date/{start_date}/{end_date}/all.json")

    def get_weight(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1/user/-/body/log/weight/date/{start_date}/{end_date}.json")

    def get_sleep(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1.2/user/-/sleep/date/{start_date}/{end_date}.json")

    def get_activity_minutes(self, start_date: str, end_date: str, activity: str) -> dict[str, Any]:
        return self.get(
            f"/1/user/-/activities/tracker/{activity}/date/{start_date}/{end_date}.json"
        )

    def get_activity_summary(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1/user/-/activities/tracker/distance/date/{start_date}/{end_date}.json")

    def get_heart_rate_zones(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(f"/1/user/-/activities/heart/date/{start_date}/{end_date}.json")

    def get_active_zone_minutes(self, start_date: str, end_date: str) -> dict[str, Any]:
        return self.get(
            f"/1/user/-/activities/active-zone-minutes/date/{start_date}/{end_date}.json"
        )

    def get_activities_list(self, before_date: str, limit: int = 50) -> dict[str, Any]:
        return self.get(
            f"/1/user/-/activities/list.json",
            params={"beforeDate": before_date, "sort": "desc", "limit": limit, "offset": 0},
        )

    def get_tcx(self, tcx_url: str) -> httpx.Response:
        return self._request("GET", tcx_url)

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
