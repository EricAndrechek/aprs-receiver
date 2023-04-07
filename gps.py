def check_gps_valid(gps_str):
    # check if the gps string is valid

    # check if the string starts with a $ (ascii 36)
    if len(gps_str) > 2 and gps_str[0] == 36 and gps_str[-1:] == b"\r":
        return True
    return False
    
def get_gps_str_type(gps_str):
    if check_gps_valid(gps_str):
        return gps_str[1:6].decode("utf-8")
    else:
        return None

def get_clean_gps_str(gps_str):
    if check_gps_valid(gps_str):
        return gps_str[7:-1].decode("utf-8")
    else:
        return None

def get_gps_str_data(gps_str):
    # split bytes into list
    gps_list = gps_str.split(b"\n")

    gps_data = {}

    # find the last gpgga string
    for i in range(len(gps_list) - 1, 0, -1):
        gps_data[get_gps_str_type(gps_list[i])] = get_clean_gps_str(gps_list[i])
    
    # remove None values
    gps_data = {k: v for k, v in gps_data.items() if v is not None}

    return gps_data

def get_gps_data(gps_str):
    str_data = get_gps_str_data(gps_str)

    gps_data = {}

    if "GPGSA" in str_data:
        mode = str_data["GPGSA"].split(",")[2]
        if mode == "1":
            gps_data["fix"] = "None"
        elif mode == "2":
            gps_data["fix"] = "2D"
        elif mode == "3":
            gps_data["fix"] = "3D"
    if "GPGGA" in str_data:
        gps_data["time"] = str_data["GPGGA"].split(",")[0]
        gps_data["lat"] = str_data["GPGGA"].split(",")[1]
        gps_data["lat_dir"] = str_data["GPGGA"].split(",")[2]
        gps_data["lon"] = str_data["GPGGA"].split(",")[3]
        gps_data["lon_dir"] = str_data["GPGGA"].split(",")[4]
        gps_data["fix_quality"] = str_data["GPGGA"].split(",")[5]
        gps_data["satellites"] = str_data["GPGGA"].split(",")[6]
        gps_data["hdop"] = str_data["GPGGA"].split(",")[7]
        gps_data["altitude"] = str_data["GPGGA"].split(",")[8]
    if "GPRMC" in str_data:
        gps_data["date"] = str_data["GPRMC"].split(",")[8]
        gps_data["speed"] = str_data["GPRMC"].split(",")[6]
        gps_data["course"] = str_data["GPRMC"].split(",")[7]
    
    return gps_data

    
