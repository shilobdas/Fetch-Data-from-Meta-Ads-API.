import hashlib
import json
import os
import secrets
import string
import webbrowser
import requests
import urllib3
from dotenv import load_dotenv

# NOTE: This disables SSL certificate verification, which is only safe for
# quick local testing (e.g. behind a corporate proxy that breaks cert checks).
# Remove this and the verify=False flags below once you're off this network.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Load credentials from .env (keep that file out of git!) ---
# Load from the .env sitting next to this script, regardless of the folder
# you're running the command from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

missing = [
    name
    for name in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI")
    if not os.environ.get(name)
]
if missing:
    raise RuntimeError(
        f"Missing from .env: {', '.join(missing)}. "
        f"Make sure .env is in {SCRIPT_DIR} and has no extra quotes/spaces."
    )

CLIENT_KEY = os.environ["TIKTOK_CLIENT_KEY"]
CLIENT_SECRET = os.environ["TIKTOK_CLIENT_SECRET"]
REDIRECT_URI = os.environ["TIKTOK_REDIRECT_URI"]


def generate_pkce_pair() -> tuple[str, str]:
    """TikTok requires PKCE for any redirect URI using localhost/127.0.0.1
    (treated as a Desktop app). code_challenge = hex(SHA256(code_verifier))."""
    alphabet = string.ascii_letters + string.digits + "-._~"
    code_verifier = "".join(secrets.choice(alphabet) for _ in range(64))
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).hexdigest()
    return code_verifier, code_challenge


def get_auth_code(code_challenge: str) -> str:
    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        "&scope=user.info.basic,video.list"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&state=abc123"
        f"&code_challenge={code_challenge}"
        "&code_challenge_method=S256"
    )

    print("Opening the TikTok login page in your browser.")
    print("Log in with your NORMAL account (the Target User) and approve access.\n")
    webbrowser.open(auth_url)

    print("If it didn't open automatically, paste this URL into your browser:")
    print(auth_url)
    print(
        "\nAfter approve, the browser will try to load a localhost page and "
        "fail to connect - that's fine and expected. Copy the FULL URL from the "
        "address bar at that point (it contains 'code=...')."
    )
    redirected_url = input("\nPaste the full redirected URL here: ").strip()

    if "code=" not in redirected_url:
        raise ValueError("No 'code=' found in that URL - did the approval succeed?")
    return redirected_url.split("code=")[1].split("&")[0]


def get_access_token(code: str, code_verifier: str) -> str:
    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        },
        verify=False,
    )
    if resp.status_code != 200:
        print(f"\nHTTP status: {resp.status_code}")
        print(f"Raw response body:\n{resp.text[:1000]}\n")

    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"Token exchange failed: {data}")
    return data["access_token"]


def fetch_videos(access_token: str) -> dict:
    resp = requests.post(
        "https://open.tiktokapis.com/v2/video/list/"
        "?fields=id,title,video_description,create_time,view_count,like_count",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"max_count": 20},
        verify=False,
    )
    return resp.json()


if __name__ == "__main__":
    code_verifier, code_challenge = generate_pkce_pair()
    code = get_auth_code(code_challenge)
    token = get_access_token(code, code_verifier)
    print(f"\nAccess token (valid 24h): {token}\n")

    videos = fetch_videos(token)
    print("Your videos:")
    print(json.dumps(videos, indent=2))