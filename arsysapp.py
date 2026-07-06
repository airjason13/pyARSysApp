import asyncio
import json
import os
import shutil
import signal
import sys
from unix_server import UnixServer
from unix_client import UnixClient
from cmd_parser import CmdParser
from PyQt5.QtCore import QCoreApplication, QTimer, QObject, pyqtSignal
from qasync import QEventLoop, asyncSlot
from global_def import *
from utils.log_utils import root_dir
import subprocess
import time
from pathlib import Path
from utils.file_utils import parse_version_file, get_all_sw_version

from utils.system_volume import SystemVolumeController

class AsyncWorker(QObject):
    """一個在獨立 Thread 中運行 asyncio 事件迴圈的類別"""
    def __init__(self,async_loop,volume_controller,
               unix_server_path=UNIX_SYS_SERVER_URI):
        super().__init__()
        self.loop = async_loop
        self.volume_controller = volume_controller
        self.unix_server_path = unix_server_path
        self.tcp_server = None
        self.udp_server = None
        self.unix_server = None
        self.msg_app_unix_client = None
        self.cmd_parser = None
        self.all_sw_version = get_all_sw_version()


    async def custom_parser(data: bytes, addr):

        return 0

    def get_version(self):
        return Version

    def get_all_sw_version_dep(self):
        app_paths = {
            "ARGLASSESDEMO": ARGLASSESDEMO_URL,
            "MESSAGESERVER": MESSAGESERVER_URL,
            "LIGHTENGINE": LIGHTENGINE_URL,
            "ARSYSAPP": ARSYSAPP_URL,
            "FLASKMEDIAFILEMANAGER": FLASKMEDIAFILEMANAGER_URL
        }

        # 2. 建立一個字典來收集所有結果
        all_versions_info = {}

        # 3. 走訪每個路徑，組合出 version.py 的完整路徑並解析
        for app_name, base_path in app_paths.items():
            # 使用 os.path.join 自動處理斜線，組合出 /root/.../version.py
            file_path = os.path.join(base_path, "version.py")

            # 呼叫解析函式
            pn, version = parse_version_file(file_path)

            # 將結果存入字典
            all_versions_info[app_name] = {
                "PN": pn,
                "Version": version
            }

        # 4. 將字典轉換成 JSON 字串
        # indent=4 可以讓 JSON 格式化排版，更容易閱讀
        # ensure_ascii=False 確保如果未來有中文不會被轉碼
        json_output = json.dumps(all_versions_info, indent=4, ensure_ascii=False)

        # 5. 印出或儲存 JSON 結果
        log.debug(f"all_versions_info: {json_output}")

        try:
            with open(AR_SW_VERSION_URL, "w", encoding="utf-8") as f:
                f.write(json_output)
                f.flush()
                os.fsync(f.fileno())
            log.debug(f"✅ 成功將版本資訊寫入 {AR_SW_VERSION_URL}")

        except PermissionError:
            log.debug(f"❌ 錯誤：沒有權限寫入 {AR_SW_VERSION_URL}。")
            log.debug("💡 提示：/etc/ 是系統目錄，請加上 sudo 執行此腳本 (例如: sudo python3 your_script.py)")

        except Exception as e:
            log.debug(f"❌ 寫入檔案時發生未知的錯誤: {e}")

        return json_output

    def unix_data_recv_handler(self, msg:str, pid):
        log.debug(f"got {msg} from {pid}")
        self.cmd_parser.parse_cmds(msg)


    def send_to_msg_server(self, send_data:str):
        log.debug("send_data:%s", send_data)
        self._periodic_unix_msg(send_data.encode())

    async def start_all_server_client(self):
        log.debug("")

        self.msg_app_unix_client = UnixClient(UNIX_MSG_SERVER_URI)
        self.unix_server = UnixServer(self.unix_server_path)
        self.unix_server.unix_data_received.connect(self.unix_data_recv_handler)
        self.cmd_parser = CmdParser(self.msg_app_unix_client, self.volume_controller)
        self.cmd_parser.unix_data_ready_to_send.connect(self.send_to_msg_server)
        await self.unix_server.start()
        await self.msg_app_unix_client.connect()

        ''''# === 測試用 新增：每 5 秒觸發一次 test_send_unix_msg ===
        self.timer = QTimer(self)
        self.timer.setInterval(5000)  # 5 秒
        self.timer.timeout.connect(self._periodic_unix_msg)
        self.timer.start()'''

    def _periodic_unix_msg(self, data:bytes):
        """
        QTimer 觸發時呼叫，安排 coroutine 到 asyncio 事件迴圈
        """
        log.debug("")
        # 例如傳送字串 "Hello from QTimer"
        asyncio.run_coroutine_threadsafe(
            self.test_send_unix_msg(data.decode()),
            self.loop
        )

    async def test_send_unix_msg(self, unix_msg):
        log.debug("test_unix_loop")
        if unix_msg is not None:
            await self.msg_app_unix_client.send(unix_msg)

    async def async_job(self, cmd:str, data=None):

        log.debug("[%s] start", cmd)
        if "initial" in cmd:
            await self.start_all_server_client()
        elif "test_unix_loop" in cmd:
            await self.test_send_unix_msg(data)
        log.debug("[%s] end", cmd)


    def run(self):
        """Thread 進入點：設定並啟動事件迴圈"""
        asyncio.set_event_loop(self.loop)
        # 在啟動時排程一個 coroutine
        self.loop.create_task(self.async_job("initial",))
        log.debug("[AsyncWorker] event loop running ...")
        self.loop.run_forever()

    def add_task(self, name, data):
        """從主線程安排新的 coroutine"""
        asyncio.run_coroutine_threadsafe(self.async_job(name, data), self.loop)

    def stop(self):
        """安全關閉事件迴圈"""
        self.loop.call_soon_threadsafe(self.loop.stop)

def ensure_pipewire_running():
    # Only run on specific platforms (e.g., skip x86_64)
    if platform.machine() == 'x86_64':
        return

    if HAS_AUDIO_MANAGER:
        BASE_DIR = Path(__file__).resolve().parent
        SCRIPT = BASE_DIR / "scripts" / "restart_audio.sh"

        # Defensive check: ensure the script exists
        if not SCRIPT.exists():
            log.debug(f"Error: Script not found at {SCRIPT}")
            return

        try:
            # Use 'sh' to execute the script in case of missing execute permissions
            subprocess.run(["sh", str(SCRIPT)], check=True)
            log.debug("Audio services (PipeWire & WirePlumber) restarted successfully.")
        except subprocess.CalledProcessError as e:
            log.debug(f"Error: Failed to restart audio services. Return code: {e.returncode}")
        except Exception as e:
            log.debug(f"An unexpected error occurred: {e}")



def main():
    log.debug(f"Welcome to {Version}")
    # Load Persist config
    volume_controller = SystemVolumeController()
    # === ensure audio system service ===
    ensure_pipewire_running()
    # 使用 QCoreApplication 取代 QApplication，不需要 GUI 子系統
    app = QCoreApplication(sys.argv)
    # 用 qasync 把 Qt 事件迴圈包裝成 asyncio 事件迴圈
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    worker = AsyncWorker(loop ,volume_controller=volume_controller)

    # 友善的 Ctrl+C 結束
    def handle_sigint(*_):
        print("\n[Main] SIGINT received, quitting ...")
        app.quit()

    # Unix 下可用 add_signal_handler，跨平台保險也掛一個 signal.signal
    try:
        loop.add_signal_handler(signal.SIGINT, handle_sigint)
    except NotImplementedError:
        pass
    signal.signal(signal.SIGINT, handle_sigint)

    log.debug("Run AsyncWorker")
    worker.run()


if __name__ == "__main__":
    main()
