import os
import subprocess
import re

from ext_qobjects.simple_file_watcher import SimpleWatcher
from global_def import *
from utils.file_utils import set_persist_config_float, get_persist_config_float


class SystemVolumeController:
    def __init__(self):
        self.wpctl_path = "/usr/bin/wpctl"
        self.system_volume = 0.0
        self.volume_file_watcher = None
        self.init_audio_persist_config()

    def set_system_volume(self, vol: float):
        """Set volume and save to persist config."""
        clamped = max(0.0, min(1.0, vol))
        set_persist_config_float(PERSIST_SYSTEM_VOLUME_FILENAME, clamped)
        log.info(f"[Volume] set_volume -> {clamped}")

        if HAS_AUDIO_MANAGER:
            env = os.environ.copy()
            env["XDG_RUNTIME_DIR"] = "/run/user/0"

            try:
                # vol: 0.0 ~ 1.0 (0.5, 50%)
                subprocess.run(
                    [self.wpctl_path, "set-volume", "@DEFAULT_AUDIO_SINK@", str(vol)],
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

    def get_system_volume(self) -> float:
        """Get current volume from hardware (if available) or internal state."""
        if HAS_AUDIO_MANAGER:
            env = os.environ.copy()
            env["XDG_RUNTIME_DIR"] = "/run/user/0"

            try:
                p = subprocess.run(
                    [self.wpctl_path, "get-volume", "@DEFAULT_AUDIO_SINK@"],
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

        return self.system_volume

    def refresh_volume_changed(self):
        """Callback triggered by SimpleWatcher when file changes."""
        new_v = get_persist_config_float(
            PERSIST_SYSTEM_VOLUME_FILENAME,
            DEFAULT_SYSTEM_VOLUME_FLOAT
        )
        new_v = max(0.0, min(1.0, new_v))
        self.system_volume = new_v
        log.info(f"[Volume] Updated from persist: {new_v}")

    def init_audio_persist_config(self):
        """Initial configuration and file watcher setup."""
        # 1. Load initial value
        self.system_volume = get_persist_config_float(
            PERSIST_SYSTEM_VOLUME_FILENAME,
            DEFAULT_SYSTEM_VOLUME_FLOAT
        )
        log.info(f"[Volume] Initial value: {self.system_volume}")

        # 2. Setup SimpleWatcher
        file_full_path = os.path.join(PERSIST_CONFIG_URI_PATH, PERSIST_SYSTEM_VOLUME_FILENAME)
        
        # 3. create callback
        self.volume_file_watcher = SimpleWatcher(file_full_path, self.refresh_volume_changed)

        # 4. Synchronize state immediately
        self.refresh_volume_changed()

