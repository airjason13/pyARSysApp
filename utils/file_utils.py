import os
import random
import string
from pathlib import Path

from global_def import *
import json
import re

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


def replace_lines_in_file_with_dict(filename: str, replacements: dict):
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


def list_files_by_ext(root_path: str, **kwargs) -> str:
    """
    遍歷 root_path 下的所有檔案，根據副檔名條件回傳 JSON 格式 (保留目錄層級)

    :param root_path: 目錄路徑
    :param kwargs: 例如 ext=[".mp4", ".jpg"]
    :return: JSON 字串
    """
    # 如果 kwargs 為空，表示不過濾
    exts = None
    if kwargs:
        exts = kwargs.get("ext", None)
        if exts is not None:
            exts = [e.lower() for e in exts]

    def walk_dir(path):
        tree = {}
        for entry in sorted(os.listdir(path)):
            fullpath = os.path.join(path, entry)
            if os.path.isdir(fullpath):
                tree[entry] = walk_dir(fullpath)
            else:
                # 沒有過濾條件 → 全部列出
                if exts is None or os.path.splitext(entry)[1].lower() in exts:
                    tree.setdefault("files", []).append(entry)
        return tree

    result = walk_dir(root_path)
    return json.dumps(result, indent=2, ensure_ascii=False)

def gen_string(length: int) -> str:
    chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choice(chars) for _ in range(length))

def get_persist_config_int(persist_filename: str, def_value: int) -> int :
    path_persist_folder = Path(PERSIST_CONFIG_URI_PATH)
    path_persist_folder.mkdir(parents=True, exist_ok=True)
    target_persist_uri = Path(os.path.join(PERSIST_CONFIG_URI_PATH, persist_filename))
    if not target_persist_uri.exists():
        with open(target_persist_uri, 'w', encoding='utf-8') as f:
            f.write(str(def_value))

    with open(target_persist_uri, 'r', encoding='utf-8') as f:
        str_value = f.read().strip()

    return int(str_value)

def get_persist_config_str(persist_filename: str, def_value: str) -> str:
    path_persist_folder = Path(PERSIST_CONFIG_URI_PATH)
    path_persist_folder.mkdir(parents=True, exist_ok=True)
    target_persist_uri = Path(os.path.join(PERSIST_CONFIG_URI_PATH, persist_filename))
    with open(target_persist_uri, 'w', encoding='utf-8') as f:
        f.write(str(def_value))

    with open(target_persist_uri, 'r', encoding='utf-8') as f:
        str_value = f.read().strip()
    return str_value

def set_persist_config_int(persist_filename: str, def_value: int) -> None:
    path_persist_folder = Path(PERSIST_CONFIG_URI_PATH)
    path_persist_folder.mkdir(parents=True, exist_ok=True)
    target_persist_uri = Path(os.path.join(PERSIST_CONFIG_URI_PATH, persist_filename))
    with open(target_persist_uri, 'w', encoding='utf-8') as f:
        f.write(str(def_value))

def set_persist_config_str(persist_filename: str, def_value: str) -> None:
    path_persist_folder = Path(PERSIST_CONFIG_URI_PATH)
    path_persist_folder.mkdir(parents=True, exist_ok=True)
    target_persist_uri = Path(os.path.join(PERSIST_CONFIG_URI_PATH, persist_filename))
    with open(target_persist_uri, 'w', encoding='utf-8') as f:
        f.write(def_value)


def get_persist_config_float(persist_filename: str, def_value: float) -> float:
    path_persist_folder = Path(PERSIST_CONFIG_URI_PATH)
    path_persist_folder.mkdir(parents=True, exist_ok=True)
    target_persist_uri = Path(os.path.join(PERSIST_CONFIG_URI_PATH, persist_filename))

    if not target_persist_uri.exists():
        with open(target_persist_uri, 'w', encoding='utf-8') as f:
            f.write(str(def_value))

    try:
        with open(target_persist_uri, 'r', encoding='utf-8') as f:
            str_value = f.read().strip()
        return float(str_value)
    except:
        return def_value
    
def set_persist_config_float(persist_filename: str, value: float) -> None:
    path_persist_folder = Path(PERSIST_CONFIG_URI_PATH)
    path_persist_folder.mkdir(parents=True, exist_ok=True)
    target_persist_uri = Path(os.path.join(PERSIST_CONFIG_URI_PATH, persist_filename))

    with open(target_persist_uri, 'w', encoding='utf-8') as f:
        f.write(str(value))


def parse_version_file(file_path):
    # 建立一個字典來存放抓取到的變數
    version_data = {}

    # 定義正則表達式：用來匹配變數名稱與引號內的數值
    # 範例匹配：Version_PN = "ARSYS" 或 Version_Year = '2025'
    pattern = re.compile(r'^(Version_[a-zA-Z]+)\s*=\s*[\'"]([^\'"]+)[\'"]')

    # 1. 使用 File I/O 開啟檔案
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()  # 去除頭尾空白與換行符號

            # 嘗試匹配每一行
            match = pattern.match(line)
            if match:
                key = match.group(1)  # 例如: Version_PN
                value = match.group(2)  # 例如: ARSYS
                version_data[key] = value

    # 2. 獲取 PN
    pn = version_data.get("Version_PN", "UNKNOWN")

    # 3. 依照你檔案內的邏輯拼湊出完整 Version 字串
    # 邏輯: PN_YYYYMMDD_MajorMinorPatch
    try:
        version = (
            f"{pn}_"
            f"{version_data['Version_Year']}"
            f"{version_data['Version_Month']}"
            f"{version_data['Version_Date']}_"
            f"{version_data['Version_Major']}"
            f"{version_data['Version_Minor']}"
            f"{version_data['Version_Patch']}"
        )
    except KeyError as e:
        print(f"警告：檔案中缺少必要的版本變數 {e}")
        version = "UNKNOWN_VERSION"

    return pn, version

def parse_cmd_version_file(file_path):
    # 建立一個字典來存放抓取到的變數
    version_data = {}

    # 定義正則表達式：用來匹配變數名稱與引號內的數值
    # 範例匹配：Version_PN = "ARSYS" 或 Version_Year = '2025'
    pattern = re.compile(r'^(CMD_Version_[a-zA-Z]+)\s*=\s*[\'"]([^\'"]+)[\'"]')

    # 1. 使用 File I/O 開啟檔案
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()  # 去除頭尾空白與換行符號

            # 嘗試匹配每一行
            match = pattern.match(line)
            if match:
                key = match.group(1)  # 例如: Version_PN
                value = match.group(2)  # 例如: ARSYS
                version_data[key] = value

    # 2. 獲取 PN
    pn = version_data.get("CMD_Version_PN", "UNKNOWN")

    # 3. 依照你檔案內的邏輯拼湊出完整 Version 字串
    # 邏輯: PN_YYYYMMDD_MajorMinorPatch
    try:
        version = (
            f"{pn}_"
            f"{version_data['CMD_Version_Year']}"
            f"{version_data['CMD_Version_Month']}"
            f"{version_data['CMD_Version_Date']}_"
            f"{version_data['CMD_Version_Major']}"
            f"{version_data['CMD_Version_Minor']}"
            f"{version_data['CMD_Version_Patch']}"
        )
    except KeyError as e:
        print(f"警告：檔案中缺少必要的版本變數 {e}")
        version = "UNKNOWN_VERSION"

    return pn, version


def sys_get_msg_sw_version():
    pn, version = parse_version_file(os.path.join(MESSAGESERVER_URL, "version.py"))
    return pn + version

def get_all_sw_version():
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
        pn_file_path = os.path.join(base_path, "version.py")

        cmd_version_path = os.path.join(base_path, "arglassescmd/cmd_def.py")

        # 呼叫解析函式
        pn, version = parse_version_file(pn_file_path)

        if os.path.exists(cmd_version_path):
            cmd_pn, cmd_version = parse_cmd_version_file(cmd_version_path)
        else:
            cmd_pn = "NONE"
            cmd_version = "NONE"

        # 將結果存入字典
        all_versions_info[app_name] = {
            "PN": pn,
            "Version": version,
            "CMD_PN": cmd_pn,
            "CMD_VERSION": cmd_version
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

# 範例：
if __name__ == "__main__":
    root = "."
    print("=== 列出所有檔案 ===")
    print(list_files_by_ext(root))   # kwargs 為空，列出所有檔案

    print("\n=== 只列出 mp4/jpg ===")
    print(list_files_by_ext(root, ext=[".mp4", ".jpg"]))


# example
'''if __name__ == "__main__":
    replacements = {
        "ssid": "MyWiFi",
        "channel": "6",
        "wpa_passphrase": "newpassword123"
    }
    replace_lines_in_file("uap0_hostapd.conf", replacements)
    log.debug("檔案已更新完成！")'''

