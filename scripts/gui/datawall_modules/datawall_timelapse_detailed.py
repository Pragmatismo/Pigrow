#!/usr/bin/env python3
"""Timelapse status, file history and selected photographs in one datawall."""

from timelapse_tools import make_timelapse_datawall


def read_datawall_options():
    return {"output": "./timelapse_detailed_datawall.png"}, {
        "settings": {
            "capture_path": "auto",
            "interval": "auto",
            "start": "auto",
            "gallery_mode": ["recent", "hourly", "daily"],
            "daily_time": "1700",
        },
        "info_read": [
            "boxname",
            "datetime",
            "timelapse detail=detailed path={capture_path} interval={interval} "
            "start={start} selection={gallery_mode} daily_time={daily_time}",
        ],
    }


def make_datawall(data, opts=None):
    return make_timelapse_datawall(data, opts, detailed=True)
