#!/usr/bin/env python3
"""
NOVOS Cloud Host Agent v0.4
Run this on the Windows gaming PC that has Apollo + Playnite.

1. Edit PLAYNITE_EXE below.
2. Start server.py on the NOVOS Cloud backend.
3. Set BACKEND to the backend's LAN IP, e.g. http://192.168.1.50:8080
4. Run: py host_agent.py

The agent polls for commands and can launch Playnite Fullscreen.
It does NOT handle Epic credentials and does NOT expose the Windows desktop.
"""
import json, os, subprocess, time, urllib.request, urllib.error

BACKEND=os.environ.get("NOVOS_BACKEND","http://127.0.0.1:8080")
PLAYNITE_EXE=os.environ.get("PLAYNITE_EXE",r"C:\Program Files\Playnite\Playnite.FullscreenApp.exe")

def post(path, data):
    req=urllib.request.Request(BACKEND+path,data=json.dumps(data).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=5) as r: return json.loads(r.read())

def get(path):
    with urllib.request.urlopen(BACKEND+path,timeout=5) as r: return json.loads(r.read())

def launch_playnite():
    if not os.path.exists(PLAYNITE_EXE):
        print("Playnite path not found:",PLAYNITE_EXE)
        return
    subprocess.Popen([PLAYNITE_EXE], close_fds=True)
    print("Launched Playnite Fullscreen")

print("NOVOS Cloud Host Agent")
while True:
    try:
        post("/api/host/heartbeat",{})
        result=get("/api/host/command")
        cmd=result.get("command")
        if cmd:
            print("Command:",cmd["type"])
            if cmd["type"]=="launch_playnite":
                launch_playnite()
            elif cmd["type"]=="stop_session":
                # Deliberately do not kill arbitrary Windows processes.
                # Configure Apollo/Playnite cleanup separately once the host is isolated.
                print("STOP requested: configure safe Playnite/Apollo cleanup before production use.")
        time.sleep(1)
    except Exception as e:
        print("Backend unavailable:",e)
        time.sleep(3)
