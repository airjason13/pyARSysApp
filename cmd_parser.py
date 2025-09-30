from global_def import *
from PyQt5.QtCore import QObject, pyqtSignal
from unix_client import UnixClient
from utils.file_utils import file_to_dict


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

    def parse_cmds(self, data) -> str:
        log.debug("data : %s", data)

        d = dict(item.split(':', 1) for item in data.split(';'))

        if 'data' not in data:
            d['data'] = 'no_data'
        else:
            pass
        log.debug("%s", d)

        try:
            if 'get' in d['cmd']:
                log.debug("i : %s, v: %s", 'cmd', d['cmd'])
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
        pass

    def sys_set_wifi_uap0_pwd(self, data: dict):
        pass

    def sys_set_wifi_uap0_hw_mode(self, data: dict):
        pass

    def sys_set_wifi_uap0_ssid(self, data: dict):
        pass

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
    }
