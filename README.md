# NOVOS Cloud — Local Test Server v0.2

This version adds:
- Fullscreen button for the cloud stream area
- Controller test panel
- Browser microphone permission test
- 1-hour maximum session countdown
- A small local Python server with a session API
- Safe simulated cloud sessions (no commercial games included)

## Run the local test server

You need Python 3.

From this folder, run:

```bash
python3 server.py
```

Then open:

http://localhost:8080

On Windows, this may be:

```bash
py server.py
```

## What this server does

It is a development server for the NOVOS Cloud session system. It does NOT stream a game yet.

The local server:
- creates a test session
- gives it a session ID
- enforces a maximum session length of 1 hour
- reports remaining session time to the browser
- ends sessions when they expire

The browser UI tests fullscreen, controller input, microphone permissions, and session controls.

## Important

This project does not contain Fortnite or other commercial games and does not bypass DRM or licensing.

The next real cloud-gaming stage will require an authorized gaming host plus a real low-latency streaming system such as WebRTC/game-stream infrastructure.
