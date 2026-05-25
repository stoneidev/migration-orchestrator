import os
import signal
import socket
import subprocess
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

_services: dict[str, dict] = {
    "frontend": {"process": None, "port": 3001, "status": "stopped"},
    "backend": {"process": None, "port": 8080, "status": "stopped"},
}


def _is_port_open(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(("localhost", port)) == 0
    except:
        return False


@router.get("/services/status")
def get_services_status():
    for name, svc in _services.items():
        port_open = _is_port_open(svc["port"])
        if port_open:
            svc["status"] = "running"
        elif svc["process"] and svc["process"].poll() is not None:
            svc["status"] = "stopped"
            svc["process"] = None
    return {
        "success": True,
        "data": {
            name: {"port": svc["port"], "status": svc["status"], "url": f"http://localhost:{svc['port']}"}
            for name, svc in _services.items()
        },
    }


@router.post("/services/frontend/start")
def start_frontend():
    svc = _services["frontend"]
    if _is_port_open(svc["port"]):
        svc["status"] = "running"
        return {"success": True, "data": {"status": "already running", "url": f"http://localhost:{svc['port']}"}}

    project_root = Path(__file__).parent.parent.parent.parent.parent.parent
    frontend_dir = project_root / "apps" / "frontend"

    proc = subprocess.Popen(
        ["npx", "next", "dev", "--port", str(svc["port"])],
        cwd=str(frontend_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )
    svc["process"] = proc
    svc["status"] = "running"
    return {"success": True, "data": {"status": "started", "port": svc["port"], "url": f"http://localhost:{svc['port']}"}}


@router.post("/services/frontend/stop")
def stop_frontend():
    svc = _services["frontend"]
    if svc["process"]:
        try:
            os.killpg(os.getpgid(svc["process"].pid), signal.SIGKILL)
        except:
            svc["process"].kill()
        svc["process"] = None
    # Also kill any remaining next dev on that port
    os.system(f"lsof -ti:{svc['port']} | xargs kill -9 2>/dev/null")
    svc["status"] = "stopped"
    return {"success": True, "data": {"status": "stopped"}}


@router.post("/services/backend/start")
def start_backend():
    svc = _services["backend"]
    if _is_port_open(svc["port"]):
        svc["status"] = "running"
        return {"success": True, "data": {"status": "already running", "url": f"http://localhost:{svc['port']}"}}

    project_root = Path(__file__).parent.parent.parent.parent.parent.parent
    backend_dir = project_root / "apps" / "backend"

    proc = subprocess.Popen(
        ["./gradlew", "bootRun"],
        cwd=str(backend_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )
    svc["process"] = proc
    svc["status"] = "running"
    return {"success": True, "data": {"status": "started", "port": svc["port"], "url": f"http://localhost:{svc['port']}"}}


@router.post("/services/backend/stop")
def stop_backend():
    svc = _services["backend"]
    if svc["process"]:
        try:
            os.killpg(os.getpgid(svc["process"].pid), signal.SIGKILL)
        except:
            svc["process"].kill()
        svc["process"] = None
    os.system(f"lsof -ti:{svc['port']} | xargs kill -9 2>/dev/null")
    svc["status"] = "stopped"
    return {"success": True, "data": {"status": "stopped"}}
