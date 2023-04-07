import aprslib
import mice

def build_package(callsign, path, latitude, longitude, lat_dir, lon_dir, symbol_table, symbol_code, heading, speed, altitude):
    mypkt = mice.mice_pkt()
    mypkt.callsign = callsign
    mypkt.path = path

    mypkt.lat_degrees = round(float(latitude) / 100)
    mypkt.lat_minutes = int(latitude.split(".")[0][-2:])
    mypkt.lat_minutes_hundreths = int(latitude.split(".")[1][:2])
    mypkt.north = 1 if lat_dir == "N" else 0

    mypkt.lon_degrees = round(float(longitude) / 100)
    mypkt.lon_minutes = int(longitude.split(".")[0][-2:])
    mypkt.lon_minutes_hundreths = int(longitude.split(".")[1][:2])
    mypkt.west = 1 if lon_dir == "W" else 0

    mypkt.symbol_table = symbol_table
    mypkt.symbol_code = symbol_code
    mypkt.heading = int(round(float(heading)))
    # uploading speed in knots?
    mypkt.speed = round(float(speed), 2)
    # uploading altitude in feet?
    mypkt.altitude = round(float(altitude) * 3.281, 2)
    return str(mypkt)

if __name__ == '__main__':
    package = build_package("KD8CJT-1", "TCPIP*", "4218.0497", "08346.5857", "N", "W", "/", ">", 79, 43.61, 289.7)
    # good example: KE8ISS>T2QW6S,WIDE2-1:`oF_l!]O/'"7)}|"6$v'W|!w<y!|3
    print(aprslib.parse(package))
