import os
from global_def import *

def replace_lines_in_file(filename: str, replacements: dict):
    """
    用 replacements dict 更新檔案內容。
    如果某行以 k= 開頭，就整行替換成 k=v
    """
    new_lines = []
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        updated = False
        for k, v in replacements.items():
            if line.strip().startswith(f"{k}="):
                new_lines.append(f"{k}={v}\n")
                updated = True
                break
        if not updated:
            new_lines.append(line)

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        f.truncate()
        f.flush()
        f.close()
        os.sync()

def file_to_dict(filename: str, splitter: str = "=") -> dict:
    """ 讀取檔案內容，每行用 splitter 分割成 key/value，並回傳 dict。 遇到空行或沒有 splitter 的行會跳過。 """

    result = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or splitter not in line:
                continue
            key, value = line.split(splitter, 1)
            result[key.strip()] = value.strip()
    return result


# example
if __name__ == "__main__":
    replacements = {
        "ssid": "MyWiFi",
        "channel": "6",
        "wpa_passphrase": "newpassword123"
    }
    replace_lines_in_file("uap0_hostapd.conf", replacements)
    log.debug("檔案已更新完成！")

