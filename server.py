#!/usr/bin/env python3
"""
NOVOS Cloud v0.4 backend
Local prototype of the REAL control plane:
- persistent queue/state in state.json
- user sessions
- admin scheduled shutdown
- host heartbeat
- host command queue for launching/stopping Playnite

Run:
  python3 server.py
Then open:
  http://127.0.0.1:8080

This is intentionally local/LAN-first. Put it behind HTTPS/auth before internet use.
"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, time, uuid, threading

ROOT=Path(__file__).resolve().parent
STATE_FILE=ROOT/"state.json"
HOST_ID="gaming-pc-01"
SESSION_SECONDS=3600

lock=threading.RLock()
default={
    "server_online": True,
    "shutdown_at": None,
    "queue": [],
    "users": {},
    "current_session": None,
    "host": {"id":HOST_ID,"online":False,"last_seen":0},
    "commands": []
}
if STATE_FILE.exists():
    try:
        state=json.loads(STATE_FILE.read_text())
    except Exception:
        state=default.copy()
else:
    state=default.copy()

def save():
    tmp=STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state,indent=2))
    tmp.replace(STATE_FILE)

def cleanup():
    now=time.time()
    if state["shutdown_at"] and now >= state["shutdown_at"]:
        state["shutdown_at"]=None
        state["server_online"]=False
        if state["current_session"]:
            state["commands"].append({"id":uuid.uuid4().hex,"type":"stop_session"})
            state["current_session"]=None
        save()
    sess=state["current_session"]
    if sess and now >= sess["ends_at"]:
        state["commands"].append({"id":uuid.uuid4().hex,"type":"stop_session"})
        state["current_session"]=None
        assign_next()
        save()

def assign_next():
    if not state["server_online"] or state["shutdown_at"] or state["current_session"] or not state["queue"]:
        return
    uid=state["queue"].pop(0)
    user=state["users"].get(uid)
    if not user: return
    sid=uuid.uuid4().hex
    state["current_session"]={
        "id":sid,"user_id":uid,"user_name":user["name"],
        "host_id":HOST_ID,"started_at":time.time(),
        "ends_at":time.time()+SESSION_SECONDS
    }
    state["commands"].append({"id":uuid.uuid4().hex,"type":"launch_playnite","session_id":sid,"user_id":uid})

def public_state(uid=None):
    cleanup()
    s=state["current_session"]
    pos=None
    if uid in state["queue"]:
        pos=state["queue"].index(uid)+1
    return {
        "server_online":state["server_online"],
        "shutdown_at":state["shutdown_at"],
        "shutdown_seconds":max(0,int(state["shutdown_at"]-time.time())) if state["shutdown_at"] else None,
        "queue_length":len(state["queue"]),
        "position":pos,
        "session":s if s and (uid is None or s["user_id"]==uid) else None,
        "host":{"id":HOST_ID,"online":state["host"]["online"]},
    }

def send_json(h, code, obj):
    data=json.dumps(obj).encode()
    h.send_response(code); h.send_header("Content-Type","application/json")
    h.send_header("Content-Length",str(len(data))); h.send_header("Cache-Control","no-store")
    h.end_headers(); h.wfile.write(data)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        if self.path.startswith("/api/state"):
            uid=self.headers.get("X-User-ID")
            with lock: send_json(self,200,public_state(uid)); return
        if self.path=="/api/host/command":
            with lock:
                cleanup()
                cmd=state["commands"].pop(0) if state["commands"] else None
                save()
                send_json(self,200,{"command":cmd}); return
        if self.path=="/":
            data=(ROOT/"index.html").read_bytes()
            self.send_response(200); self.send_header("Content-Type","text/html"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data); return
        p=ROOT/self.path.lstrip("/")
        if p.exists() and p.is_file():
            data=p.read_bytes(); c="text/plain"
            if p.suffix==".js": c="text/javascript"
            if p.suffix==".css": c="text/css"
            self.send_response(200); self.send_header("Content-Type",c); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data); return
        send_json(self,404,{"error":"not found"})

    def do_POST(self):
        try:
            n=int(self.headers.get("Content-Length","0")); body=json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            send_json(self,400,{"error":"invalid JSON"}); return
        path=self.path
        with lock:
            cleanup()
            if path=="/api/login":
                uid=uuid.uuid4().hex; name=str(body.get("name") or "NOVOS Player")[:40]
                state["users"][uid]={"name":name,"created_at":time.time()}
                save(); send_json(self,200,{"user_id":uid,"name":name}); return
            uid=self.headers.get("X-User-ID")
            if path=="/api/queue/join":
                if not uid or uid not in state["users"]: send_json(self,401,{"error":"login required"}); return
                if not state["server_online"] or state["shutdown_at"]: send_json(self,409,{"error":"service paused"}); return
                if uid not in state["queue"] and not (state["current_session"] and state["current_session"]["user_id"]==uid):
                    state["queue"].append(uid); assign_next()
                save(); send_json(self,200,public_state(uid)); return
            if path=="/api/queue/leave":
                if uid in state["queue"]: state["queue"].remove(uid)
                save(); send_json(self,200,public_state(uid)); return
            if path=="/api/session/end":
                if state["current_session"] and state["current_session"]["user_id"]==uid:
                    state["commands"].append({"id":uuid.uuid4().hex,"type":"stop_session"})
                    state["current_session"]=None; assign_next(); save()
                send_json(self,200,public_state(uid)); return
            if path=="/api/admin/shutdown":
                mins=max(1,min(60,int(body.get("minutes",5))))
                state["shutdown_at"]=time.time()+mins*60
                save(); send_json(self,200,{"ok":True,"shutdown_at":state["shutdown_at"]}); return
            if path=="/api/admin/shutdown/cancel":
                state["shutdown_at"]=None
                if state["server_online"]: assign_next()
                save(); send_json(self,200,{"ok":True}); return
            if path=="/api/admin/server":
                online=bool(body.get("online"))
                state["server_online"]=online
                if not online:
                    state["shutdown_at"]=None
                    if state["current_session"]:
                        state["commands"].append({"id":uuid.uuid4().hex,"type":"stop_session"})
                        state["current_session"]=None
                else: assign_next()
                save(); send_json(self,200,public_state(uid)); return
            if path=="/api/host/heartbeat":
                state["host"]["online"]=True; state["host"]["last_seen"]=time.time()
                save(); send_json(self,200,{"ok":True}); return
            if path=="/api/host/ack":
                cid=body.get("id")
                # Commands are removed when fetched. This endpoint is a no-op acknowledgement for now.
                send_json(self,200,{"ok":True,"id":cid}); return
            send_json(self,404,{"error":"unknown endpoint"})

def watchdog():
    while True:
        time.sleep(1)
        with lock:
            cleanup()
            if state["host"]["online"] and time.time()-state["host"]["last_seen"]>10:
                state["host"]["online"]=False
            save()

threading.Thread(target=watchdog,daemon=True).start()
print("NOVOS Cloud v0.4 backend")
print("Open http://127.0.0.1:8080")
ThreadingHTTPServer(("0.0.0.0",8080),Handler).serve_forever()
