import json
import os

from global_def import *
from PyQt5.QtCore import QObject, pyqtSignal
from unix_client import UnixClient
from utils.file_utils import file_to_dict, replace_lines_in_file_with_dict
from utils.log_utils import root_dir
from utils.system_volume import get_system_volume, set_system_volume


def parser_uap0_config_to_reply_data(data: dict, target_k: str) -> str:
    config_dict = file_to_dict(UAP0_HOSTAPD_FILE_URI, splitter="=")

    if config_dict[target_k] is not None:
        data['data'] = f"{config_dict[target_k]}"
    reply = ";".join(f"{k}:{v}" for k, v in data.items())
    return reply

def parser_uap0_config_list_to_reply_data(data: dict, list_target_k: list[str]) -> str:
    config_dict = file_to_dict(UAP0_HOSTAPD_FILE_URI, splitter="=")
    list_str_config = ""
    for k in list_target_k:
        if config_dict[k] is not None:
            list_str_config += config_dict[k] + "_"
        else:
            list_str_config += "no_data_"
    list_str_config = list_str_config[:-1]
    data['data'] = f"{list_str_config}"
    reply = ";".join(f"{k}:{v}" for k, v in data.items())
    return reply

class CmdParser(QObject):
    unix_data_ready_to_send = pyqtSignal(str)

    def __init__(self, msg_unix_client: UnixClient):
        super().__init__()
        self.msg_unix_client = msg_unix_client

    def parse_cmds(self, data: str):
        log.debug("data : %s", data)

        d = dict(item.split(':', 1) for item in data.split(';'))

        if 'data' not in data:
            d['data'] = 'no_data'
        else:
            pass
        log.debug("%s", d)

        try:
            self.cmd_function_map[d['cmd']](self, d)
        except Exception as e:
            log.error(e)

    def sys_get_sw_version(self, data: dict):
        data['src'], data['dst'] = data['dst'], data['src']
        data['data'] = Version
        log.debug("data : %s", data)
        # Dict to Str
        reply = ";".join(f"{k}:{v}" for k, v in data.items())
        self.unix_data_ready_to_send.emit(reply)

    def sys_get_wifi_uap0_ssid(self, data: dict):
        data['src'], data['dst'] = data['dst'], data['src']
        reply = parser_uap0_config_to_reply_data(data, target_k='ssid')
        self.unix_data_ready_to_send.emit(reply)

    def sys_get_wifi_uap0_pwd(self, data: dict):
        data['src'], data['dst'] = data['dst'], data['src']
        reply = parser_uap0_config_to_reply_data(data, target_k='wpa_passphrase')
        self.unix_data_ready_to_send.emit(reply)

    def sys_get_wifi_uap0_ssid_pwd(self, data: dict):
        data['src'], data['dst'] = data['dst'], data['src']
        list_target_k = ['ssid', 'wpa_passphrase']
        reply = parser_uap0_config_list_to_reply_data(data, list_target_k)
        self.unix_data_ready_to_send.emit(reply)

    def sys_get_wifi_uap0_hw_mode(self, data: dict):
        data['src'], data['dst'] = data['dst'], data['src']
        reply = parser_uap0_config_to_reply_data(data, target_k='hw_mode')
        self.unix_data_ready_to_send.emit(reply)

    def sys_set_wifi_uap0_ssid_pwd(self, data: dict):
        new_ssid = data['data'].split('_')[0]
        new_pwd = data['data'].split('_')[1]
        replace_dict = {'ssid': new_ssid,'wpa_passphrase': new_pwd}
        replace_lines_in_file_with_dict(UAP0_HOSTAPD_FILE_URI, replace_dict)

    def sys_set_wifi_uap0_pwd(self, data: dict):
        new_pwd = data['data']
        replace_dict = {'wpa_passphrase': new_pwd}
        replace_lines_in_file_with_dict(UAP0_HOSTAPD_FILE_URI, replace_dict)

    def sys_set_wifi_uap0_hw_mode(self, data: dict):
        new_hw_mode = data['data']
        replace_dict = {'hw_mode': new_hw_mode}
        replace_lines_in_file_with_dict(UAP0_HOSTAPD_FILE_URI, replace_dict)

    def sys_set_wifi_uap0_ssid(self, data: dict):
        new_ssid = data['data']
        replace_dict = {'ssid': new_ssid}
        replace_lines_in_file_with_dict(UAP0_HOSTAPD_FILE_URI, replace_dict)

    def sys_set_wifi_uap0_restart(self, data: dict):
        restart = data['data']
        if restart == 'true':
            os.popen(f"{root_dir}/scripts/restart_wifi_uap0_restart.sh")

    def sys_set_system_volume(self, data: dict):
        data['src'], data['dst'] = data['dst'], data['src']

        try:
            req = json.loads(data['data'])
            vol = float(req["volume"])  # 0.0 ~ 1.0

            vol = max(0.0, min(vol, 1.0))

            set_system_volume(vol)

            payload = {
                "status": "OK",
                "volume": vol
            }
        except Exception as e:
            payload = {
                "status": "NG",
                "error": str(e)
            }

        data['data'] = json.dumps(payload)
        reply = ";".join(f"{k}:{v}" for k, v in data.items())
        self.unix_data_ready_to_send.emit(reply)

    def sys_get_system_volume(self, data: dict):
        data['src'], data['dst'] = data['dst'], data['src']

        try:
            vol = get_system_volume()
            payload = {
                "status": "OK",
                "volume": vol
            }
        except Exception as e:
            payload = {
                "status": "NG",
                "error": str(e)
            }

        data['data'] = json.dumps(payload)
        reply = ";".join(f"{k}:{v}" for k, v in data.items())
        self.unix_data_ready_to_send.emit(reply)

    cmd_function_map = {
        SYS_GET_SW_VERSION: sys_get_sw_version,
        SYS_GET_WIFI_UAP0_SSID: sys_get_wifi_uap0_ssid,
        SYS_GET_WIFI_UAP0_PWD: sys_get_wifi_uap0_pwd,
        SYS_GET_WIFI_UAP0_SSID_PWD: sys_get_wifi_uap0_ssid_pwd,
        SYS_GET_WIFI_UAP0_HW_MODE: sys_get_wifi_uap0_hw_mode,
        SYS_SET_WIFI_UAP0_SSID: sys_set_wifi_uap0_ssid,
        SYS_SET_WIFI_UAP0_PWD: sys_set_wifi_uap0_pwd,
        SYS_SET_WIFI_UAP0_SSID_PWD: sys_set_wifi_uap0_ssid_pwd,
        SYS_SET_WIFI_UAP0_HW_MODE: sys_set_wifi_uap0_hw_mode,
        SYS_SET_WIFI_UAP0_RESTART: sys_set_wifi_uap0_restart,
        SYS_SET_SYSTEM_VOLUME: sys_set_system_volume,
        SYS_GET_SYSTEM_VOLUME: sys_get_system_volume,
    }
