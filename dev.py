"""Start the Django backend and the React frontend together.

Usage (from the repo root, with the virtual environment active):
    python dev.py

Backend:  http://127.0.0.1:8000
Frontend: http://localhost:5173
Press Ctrl+C once to stop both.
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "gabay" / "views" / "frontend"
IS_WINDOWS = sys.platform.startswith("win")


def project_python():
    """Use the project's own venv if it exists, otherwise the Python running this script."""
    for name in ("venv", ".venv"):
        exe = ROOT / name / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")
        if exe.exists():
            return str(exe)
    return sys.executable


def has_django(python):
    return subprocess.call([python, "-c", "import django, rest_framework"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def main():
    python = project_python()
    if not has_django(python):
        sys.exit(
            "Django is not installed for this Python:\n  " + python + "\n\n"
            "Set it up once from the repo root:\n"
            "  python -m venv venv\n"
            "  venv\\Scripts\\activate        (macOS/Linux: source venv/bin/activate)\n"
            "  pip install -r requirements.txt\n"
            "Then run:  python dev.py"
        )
    print("Using Python:", python)

    if not (FRONTEND / "node_modules").exists():
        print("First run: installing frontend packages (npm install)...")
        if subprocess.call("npm install", cwd=FRONTEND, shell=True) != 0:
            sys.exit("npm install failed. Is Node.js installed?")

    print("Starting backend and frontend. Press Ctrl+C to stop both.\n")
    # On macOS/Linux each server gets its own process group so Ctrl+C can stop npm's child too.
    group = {} if IS_WINDOWS else {"start_new_session": True}
    backend = subprocess.Popen([python, "manage.py", "runserver"], cwd=ROOT, **group)
    frontend = subprocess.Popen("npm run dev", cwd=FRONTEND, shell=True, **group)
    procs = [backend, frontend]

    def stop_now(*_):
        raise KeyboardInterrupt

    # Treat a normal "terminate" signal like Ctrl+C so both servers always get stopped.
    signal.signal(signal.SIGTERM, stop_now)

    try:
        while all(p.poll() is None for p in procs):
            time.sleep(0.5)
        print("\nOne of the servers stopped. Shutting down the other.")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        for p in procs:
            if p.poll() is None:
                if IS_WINDOWS:
                    # npm runs through a shell on Windows, so end the whole process tree.
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)


if __name__ == "__main__":
    main()
