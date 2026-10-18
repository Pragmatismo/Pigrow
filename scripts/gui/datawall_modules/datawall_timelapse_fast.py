#!/usr/bin/env python3
"""Metadata-only timelapse status wall for the GUI datawall system."""

from timelapse_tools import make_timelapse_datawall


def read_datawall_options():
    return {"output": "./timelapse_fast_datawall.png"}, {
        "settings": {
            "capture_path": "auto",
            "interval": "auto",
            "start": "auto",
        },
        "info_read": [
            "boxname",
            "datetime",
            "timelapse detail=fast path={capture_path} interval={interval} start={start}",
        ],
    }


def make_datawall(data, opts=None):
    return make_timelapse_datawall(data, opts, detailed=False)
