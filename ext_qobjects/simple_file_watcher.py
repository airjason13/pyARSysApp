import os
import threading
import time
from global_def import *
from utils.file_utils import get_persist_config_float, set_persist_config_float


# Simple file monitor that operates independently of PyQt
class SimpleWatcher:
    def __init__(self, file_path, callback):
        self.file_path = file_path
        self.callback = callback
        self._last_mtime = self._get_mtime()
        self._running = True

        # Initialize and start a background thread for file monitoring
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _get_mtime(self):
        """Returns the last modification time of the file."""
        try:
            return os.path.getmtime(self.file_path)
        except OSError:
            return 0

    def _run(self):
        """Main monitoring loop running in the background thread."""
        while self._running:
            # Polling interval: 1 second to minimize CPU overhead
            time.sleep(1)
            current_mtime = self._get_mtime()

            # Trigger callback if modification time has changed
            if current_mtime != self._last_mtime:
                self._last_mtime = current_mtime
                log.info(f"[Watcher] Detect file change: {self.file_path}")
                self.callback()

    def stop(self):
        """Safely stops the monitoring loop."""
        self._running = False