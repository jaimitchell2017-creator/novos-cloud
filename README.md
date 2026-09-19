# NOVOS Cloud — Test Prototype

This is a LOCAL prototype of the NOVOS Cloud Gaming interface.

Important:
- This prototype does NOT contain commercial games.
- It does NOT bypass game licenses, DRM, or publisher restrictions.
- The current Play button starts a simulated cloud session.
- The architecture is designed so a real authorized game-streaming backend can be connected later.

## Run it

The easiest option is to open `index.html` in a browser.

For a more realistic local test, run a small web server from this folder:

```bash
python3 -m http.server 8080
```

Then open:

http://localhost:8080

## Next stage

A real backend would replace the simulated session with:
1. An authorized gaming host.
2. A session manager.
3. WebRTC/game-stream transport.
4. Controller and keyboard/mouse input forwarding.
5. Microphone/audio handling.
6. Authentication and per-user sessions.
