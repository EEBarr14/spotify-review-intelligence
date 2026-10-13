# Interruption/resume video guide

The finished video is generated directly from captioned project slides. It is not a screen recording, so it cannot capture the desktop, Codex chat, browser tabs, notifications, or other personal information.

## What the student needs to do

Nothing needs to be presented or recorded live. Do **not** press **Start Presentation**, **Share Screen**, or **Shift-Command-5**.

1. Review the finished silent video using its [direct public file link](https://github.com/EEBarr14/spotify-review-intelligence/raw/refs/heads/main/demo/spotify-resume-walkthrough.webm), or open the local `demo/spotify-resume-walkthrough.webm` copy.
2. The repository copy is the viewer-accessible version; the same file can also be uploaded directly to the course submission system if requested.
3. The root README links to the repository copy.

## What the video demonstrates

The 52-second, 1920-by-1080 video uses saved evidence from the completed production run. It shows:

- the purpose of resumable SQLite storage;
- the saved checkpoint of 26,640 completed review IDs before the final resume;
- the three resume segments;
- the final checkpoint of 100,000 completed review IDs;
- 73,360 additional review IDs accounted for;
- zero remaining unique texts;
- zero repeated review IDs across resume calls; and
- final production-state spend of $3.737583948.

The video is silent and uses on-screen captions throughout, so narration is not required to understand it. Generating it makes no model calls and incurs no JEV cost.

## Privacy and publishing

Only the captioned slides are encoded into the video. The file contains no API key, `.env` contents, chat transcript, desktop image, browser chrome, or microphone audio. Only the verified `demo/spotify-resume-walkthrough.webm` file belongs in the public repository.
