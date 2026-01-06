import getpass
import platform

import utils.log_utils
from version import *
from arglassescmd.cmd_def import *

LOG_FILE_PREFIX = "ar_sys_app.log"

log = utils.log_utils.logging_init(__file__, LOG_FILE_PREFIX)

TCP_PORT = 9527
UDP_PORT = 9528


UNIX_MSG_SERVER_URI = '/tmp/ipc_msg_server.sock'
UNIX_DEMO_APP_SERVER_URI = '/tmp/ipc_demo_app_server.sock'
UNIX_SYS_SERVER_URI = '/tmp/ipc_sys_server.sock'
UNIX_LE_SERVER_URI = '/tmp/ipc_le_server.sock'


STR_REPLY_OK = ";OK"
STR_REPLY_NG = ";NG"
# i.MX93 lacks an Audio Manager, which means we can't control the whole system's volume at once.
HAS_AUDIO_MANAGER = False

# file uri
UAP0_HOSTAPD_FILE_URI = "/etc/uap0_hostapd.conf"

current_user = getpass.getuser()
# Media File Uri Path
if platform.machine() == 'x86_64':
    MEDIAFILE_URI_PATH = f"/home/{current_user}/Videos/"
    SNAPSHOTS_URI_PATH = f"/home/{current_user}/Videos/Snapshots/"
    RECORDINGS_URI_PATH = f"/home/{current_user}/Videos/Recordings/"
    MEDIA_URI_PATH = f"/home/{current_user}/Videos/Media/"
    THUMBNAILS_URI_PATH = f"/home/{current_user}/Videos/thumbnails/"
    PLAYLISTS_URI_PATH = f"/home/{current_user}/Videos/Playlists/"
    PERSIST_CONFIG_URI_PATH = f"/home/{current_user}/Videos/persist/"
else:
    MEDIAFILE_URI_PATH = "/root/MediaFiles/"
    SNAPSHOTS_URI_PATH = "/root/MediaFiles/Snapshots/"
    RECORDINGS_URI_PATH = "/root/MediaFiles/Recordings/"
    MEDIA_URI_PATH = "/root/MediaFiles/Media/"
    THUMBNAILS_URI_PATH = "/root/MediaFiles/thumbnails/"
    PLAYLISTS_URI_PATH = "/root/MediaFiles/Playlists/"
    PERSIST_CONFIG_URI_PATH = "/root/persist_config/"


PERSIST_SYSTEM_VOLUME_FILENAME = "persist_system_volume"
DEFAULT_SYSTEM_VOLUME_FLOAT = 0.4