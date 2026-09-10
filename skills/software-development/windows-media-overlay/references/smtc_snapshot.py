# -*- coding: utf-8 -*-
"""Tested SMTC snapshot for Windows media (Spotify etc.) via winsdk.
Drop next to app.py and `import smtc`. Returns dict or None.
"""
import asyncio, time
from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
)
STATUS = {0: "closed", 1: "opened", 2: "paused", 3: "stopped", 4: "playing", 5: "changing"}


async def _snapshot():
    manager = await MediaManager.request_async()
    sessions = manager.get_sessions()
    s = None
    for i in range(sessions.size):
        sess = sessions.get_at(i)
        aid = (sess.source_app_user_model_id or "").lower()
        if "spotify" in aid:
            s = sess
            break
    if s is None and sessions.size:
        s = sessions.get_at(0)
    if s is None:
        return None
    props = await s.try_get_media_properties_async()
    track = {"title": props.title or "", "artist": props.artist or "",
             "album": props.album_title or ""}
    pb = s.get_playback_info()
    tl = s.get_timeline_properties()
    pos = tl.position.total_seconds() if tl.position else 0.0
    # last_updated_time IS a datetime.datetime in winsdk -- use .timestamp()
    lu = tl.last_updated_time.timestamp() if tl.last_updated_time else time.time()
    return {"track": track, "status": STATUS.get(pb.playback_status, "unknown"),
            "pos": pos, "rate": pb.playback_rate if pb.playback_rate else 1.0,
            "last_update": lu}


def get_state():
    """Snapshot synchronously: track, status, position (seconds), rate."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_snapshot())
    finally:
        loop.close()
