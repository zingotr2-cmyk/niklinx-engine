"""
Keep-Alive Service — Prevents Render free-tier sleep during active sessions.
Self-pings the /api/health endpoint every 4 minutes to keep the service warm.
Auto-activates on app startup, respects active user sessions.
"""

import asyncio
import logging
import time
import os
import threading

import httpx

logger = logging.getLogger("keep_alive")

KEEP_ALIVE_INTERVAL = 240  # 4 minutes — Render spins down after 5 min idle
HEALTH_URL = "https://niklinx-engine-v2.onrender.com/api/health"
INTERNAL_PING_PATH = "/api/health"
LAST_ACTIVITY = time.time()
_ACTIVE = False
_THREAD = None

def mark_activity():
    global LAST_ACTIVITY
    LAST_ACTIVITY = time.time()

def get_uptime() -> float:
    return time.time() - LAST_ACTIVITY if LAST_ACTIVITY else 0

class KeepAliveService:
    def __init__(self):
        self._active = True
        self._thread = None
        self._lock = threading.Lock()

    def _ping_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while self._active:
            try:
                url = os.getenv("RENDER_EXTERNAL_URL", HEALTH_URL)
                with httpx.Client(timeout=10.0) as client:
                    resp = client.get(f"{url.rstrip('/')}/api/health", headers={"User-Agent": "NikLinx-KeepAlive/1.0"})
                    if resp.status_code == 200:
                        logger.debug(f"Keep-alive ping successful ({resp.status_code})")
                    else:
                        logger.warning(f"Keep-alive ping returned {resp.status_code}")
            except Exception as e:
                logger.debug(f"Keep-alive ping failed: {e}")
            for _ in range(KEEP_ALIVE_INTERVAL):
                if not self._active:
                    return
                time.sleep(1)

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                logger.info("Keep-alive already running")
                return
            self._active = True
            self._thread = threading.Thread(target=self._ping_loop, daemon=True, name="keep-alive")
            self._thread.start()
            logger.info("Keep-alive service started (4-min interval)")

    def stop(self):
        with self._lock:
            self._active = False
            if self._thread:
                self._thread.join(timeout=5)
                logger.info("Keep-alive service stopped")

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()


# Singleton instance
keep_alive = KeepAliveService()


def start_keep_alive():
    """Start the keep-alive service — call from FastAPI lifespan."""
    keep_alive.start()


def stop_keep_alive():
    """Stop the keep-alive service — call from FastAPI lifespan."""
    keep_alive.stop()
