from __future__ import annotations

import dataclasses
import json

import httpx
from secretbox import SecretBox

sb = SecretBox(auto_load=True)

AUTH_URL = "https://id.twitch.tv/oauth2/token"
BASE_URL = "https://api.twitch.tv/helix"


@dataclasses.dataclass(frozen=True)
class AuthData:
    access_token: str
    expires_in: int
    token_type: str

    def __str__(self) -> str:
        """Obfuscate token so that we don't do the bad."""
        token = self.access_token[-3:]
        return f"Token: {token} ({self.token_type})"

    __repr__ = __str__


def get_auth() -> AuthData:
    """Get auth key."""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": sb.get("CLIENT_ID"),
        "client_secret": sb.get("CLIENT_SECRET"),
        "grant_type": "client_credentials",
    }

    results = httpx.post(AUTH_URL, data=data, headers=headers)

    print(results.is_success)
    print(results.status_code)

    with open("temp_secrets", "w") as outfile:
        outfile.write(results.text)

    return AuthData(**results.json())


def get_user_id(username: str, authdata: AuthData) -> str:
    """Get a user."""
    headers = {
        "Authorization": f"Bearer {authdata.access_token}",
        "Client-id": sb.get("CLIENT_ID"),
    }
    results = httpx.get(f"{BASE_URL}/users?login={username}", headers=headers)

    print(json.dumps(results.json(), indent=4))

    return results.json()["data"][0]["id"]


def get_channel(broadcaster_id: str, authdata: AuthData) -> None:
    """Get a channel."""
    headers = {
        "Authorization": f"Bearer {authdata.access_token}",
        "Client-id": sb.get("CLIENT_ID"),
    }
    results = httpx.get(
        url=f"{BASE_URL}/channels?broadcaster_id={broadcaster_id}",
        headers=headers,
    )

    print(json.dumps(results.json(), indent=4))


def get_stream(username: str, authdata: AuthData) -> None:
    """Get a channel."""
    headers = {
        "Authorization": f"Bearer {authdata.access_token}",
        "Client-id": sb.get("CLIENT_ID"),
    }
    results = httpx.get(
        url=f"{BASE_URL}/streams?user_login={username}",
        headers=headers,
    )

    results_too = None
    if results.json()["pagination"]:
        cursor = results.json()["pagination"]["cursor"]
        results_too = httpx.get(
            url=f"{BASE_URL}/streams?user_login={username}&after={cursor}",
            headers=headers,
        )
    else:
        print("Nothing")

    print(json.dumps(results.json(), indent=4))

    if results_too:
        print(json.dumps(results_too.json(), indent=4))


if __name__ == "__main__":
    authdata = get_auth()
    # broadcaster_id = get_user_id("preocts", authdata)
    # get_channel(broadcaster_id, authdata)
    get_stream("preocts", authdata)
