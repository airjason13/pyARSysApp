import os
import subprocess
import re

from global_def import log

WPCTL = "/usr/bin/wpctl"

def set_system_volume(vol: float):
    env = os.environ.copy()
    env["XDG_RUNTIME_DIR"] = "/run/user/0"

    try:
        # vol: 0.0 ~ 1.0 (0.5, 50%)
        # wpctl set-volume
        subprocess.run(
            ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", str(vol)],
            env=env,
            check=True,
            capture_output=True,
            text=True
        )
        log.debug(f"System volume set to: {vol}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown error"
        log.error(f"Failed to set volume: {error_msg}")
        raise Exception(f"wpctl set-volume error: {error_msg}")


def get_system_volume() -> float:
    env = os.environ.copy()
    env["XDG_RUNTIME_DIR"] = "/run/user/0"

    try:
        p = subprocess.run(
            ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        parts = p.stdout.strip().split()
        if len(parts) >= 2:
            return float(parts[1])
        return 0.0

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else e.stdout
        raise Exception(f"wpctl error: {error_msg.strip()}")
