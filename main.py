#!/usr/bin/env python3
"""
DRO — Agentic Commerce Engine v2.0
Entry point for the complete dropshipping automation system.

Usage:
    # Production: start both API + dashboard
    python main.py start

    # Start API server only
    python main.py server
    
    # Start Streamlit dashboard only
    python main.py dashboard
    
    # Generate license key (admin only)
    python main.py license-gen
    
    # Run diagnostics
    python main.py doctor
"""

import sys
import os
import signal
# Ensure project root is in path (critical for embeddable Python)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
import subprocess
from licensing import license_manager
from config import config


def cmd_doctor():
    """Run system diagnostics."""
    print("\n" + "=" * 60)
    print("  DRO System Diagnostics")
    print("=" * 60)
    
    print(f"\n  [+] Python version: {sys.version.split()[0]}")
    
    # Check API keys
    print(f"  {'[OK]' if config.openai_key else '[--]'} OpenAI: {'configured' if config.openai_key else 'not set'}")
    print(f"  {'[OK]' if config.claude_key else '[--]'} Claude: {'configured' if config.claude_key else 'not set'}")
    print(f"  [->] Active AI: {config.active_ai_service.upper()}")
    
    # Check license
    lic = license_manager.validate()
    if lic["valid"]:
        print(f"  [OK] License: valid ({lic['days_remaining']} days)")
    else:
        print(f"  [--] License: {lic['message']}")
    
    # Check data files
    from pathlib import Path
    data_file = Path("data/sample_data.json")
    print(f"  {'[OK]' if data_file.exists() else '[!!]'} Data file: {'exists' if data_file.exists() else 'missing'}")
    
    print(f"\n  [i] Server: http://{config.host}:{config.port}")
    print(f"  [i] Dashboard: http://localhost:8501")
    print(f"  [i] API Docs: http://{config.host}:{config.port}/docs")
    print("=" * 60 + "\n")


def cmd_server():
    """Start the FastAPI server."""
    print(f"\n  DRO Server starting on http://{config.host}:{config.port}")
    print(f"  API Docs at http://{config.host}:{config.port}/docs\n")
    
    if config.debug:
        uvicorn.run("app.routes_api:app", host=config.host, port=config.port, reload=True)
    else:
        uvicorn.run("app.routes_api:app", host=config.host, port=config.port, reload=False)


def cmd_dashboard():
    """Start the Streamlit dashboard."""
    port = int(os.getenv("DASHBOARD_PORT", "8501"))
    print(f"\n  DRO Dashboard starting on http://localhost:{port}\n")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/dashboard.py",
                    f"--server.port={port}"])


def cmd_start():
    """Start both API server and dashboard concurrently."""
    import time
    import atexit

    processes = []

    def cleanup():
        for p in processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()

    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, lambda *_: cleanup())
    signal.signal(signal.SIGINT, lambda *_: cleanup())

    api_port = config.port
    dash_port = int(os.getenv("DASHBOARD_PORT", "8501"))

    print(f"\n  DRO starting — API :{api_port}, Dashboard :{dash_port}\n")

    # Start API server
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.routes_api:app",
         "--host", config.host, "--port", str(api_port),
         "--log-level", "info"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    processes.append(api_proc)

    # Start dashboard
    dash_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/dashboard.py",
         f"--server.port={dash_port}", "--server.headless=true"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    processes.append(dash_proc)

    # Stream output from both
    import io
    while all(p.poll() is None for p in processes):
        for p in processes:
            try:
                line = p.stdout.readline()
                if line:
                    sys.stdout.write(line.decode("utf-8", errors="replace"))
            except (ValueError, OSError):
                pass
        time.sleep(0.1)

    # If one dies, kill the other
    cleanup()


def cmd_license_gen():
    """Generate a new license key (admin command)."""
    expiry = int(input("  Expiry days [365]: ") or "365")
    tier = input("  Tier [enterprise]: ") or "enterprise"
    
    result = license_manager.generate_license_key(expiry_days=expiry, tier=tier)
    print(f"\n  [-] Generated License Key:")
    print(f"  {'=' * 50}")
    print(f"  Key: {result['key']}")
    print(f"  Expires: {result['expiry']}")
    print(f"  Tier: {result['tier']}")
    print(f"  HWID: {result['hwid'][:16]}...")
    print(f"  {'=' * 50}")
    print(f"  Save this key for distribution.\n")
    
    save = input("  Save to license file? [Y/n]: ") or "y"
    if save.lower() == "y":
        path = license_manager.save_license(result)
        print(f"  [OK] Saved to {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    commands = {
        "server": cmd_server,
        "dashboard": cmd_dashboard,
        "start": cmd_start,
        "license-gen": cmd_license_gen,
        "doctor": cmd_doctor,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print("Available: start, server, dashboard, license-gen, doctor")
        sys.exit(1)
