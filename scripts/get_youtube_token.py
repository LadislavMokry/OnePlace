from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def main() -> None:
    creds_path = Path("credentials.json")
    if not creds_path.exists():
        raise FileNotFoundError("credentials.json not found in repo root.")

    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    creds = flow.run_local_server(port=0)

    youtube = build("youtube", "v3", credentials=creds)
    channels = youtube.channels().list(part="snippet", mine=True).execute()

    print("REFRESH_TOKEN:", creds.refresh_token)
    print("CHANNELS:")
    for item in channels.get("items", []):
        title = item.get("snippet", {}).get("title")
        channel_id = item.get("id")
        print(f"- {title} | {channel_id}")


if __name__ == "__main__":
    main()
