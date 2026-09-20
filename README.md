# NOVOS Cloud v0.4 — REAL CONTROL-PLANE PROTOTYPE

This version is different from v0.3: the queue and session state live in a Python backend, not just in the browser.

## Start locally
```bash
python3 server.py
```
Open http://127.0.0.1:8080

## Test
1. Open the site in two browser windows/devices on the same LAN.
2. Sign in in each.
3. Each user joins the real backend queue.
4. The first available slot is assigned.
5. Open Admin with Ctrl+A.
6. Start a 1/5/10/15 minute shutdown.
7. The warning is generated from backend state, so clients see the same shutdown.
8. Cancel it or bring the server back online.

## Gaming host
`host_agent.py` is designed to run on the Windows PC with Apollo + Playnite.
Set:
`NOVOS_BACKEND=http://BACKEND-IP:8080`
and optionally:
`PLAYNITE_EXE=C:\Program Files\Playnite\Playnite.FullscreenApp.exe`

The host agent heartbeats to the backend and can receive a `launch_playnite` command.

## Important
This is still not a public cloud service. It does not implement Epic OAuth, Internet relay, or a browser-native Moonlight/Apollo stream. Those are separate integrations.

Apollo is a real streaming host with a web UI and GameStream-compatible clients; it also has client permission controls. The NOVOS backend should control allocation while Apollo remains the streaming layer.

Before exposing this backend to the Internet, add HTTPS, real authentication/authorization, secure per-session credentials, and server isolation.
