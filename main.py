import aprslib
import serial
import serial.tools.list_ports as list_ports
import json
import time
import gps
import packager

# --------------- config settings ---------------
gps_baud = 4800
ham_baud = 9600

call_sign = "KD8CJT-1"
passcode = "19121"
# https://aprs.do3sww.de/

aprs_is_server = "rotate.aprs2.net"
aprs_is_port = 14580

tracker_call_signs = ["KD8CJT", "KE8ISS", "KE8ISR", "KE8TYE"]

verbose = True
super_verbose = False

# http://www.aprs.org/symbols/symbolsX.txt
symbol_table = "/"
symbol_code = ">"

# ------------- end config settings -------------

# global variables
gps_port = None
ham_port = None
AIS = None

def setup_ports():
    global gps_port
    global ham_port
    gps_port = None
    ham_port = None
    ports = list_ports.grep("USB")
    for port in ports:
        # open port at gps baud and check for gps data
        test_port = serial.Serial(port.device, gps_baud, timeout=1)
        # read from the port for 1 second
        test_data = test_port.read(1000)
        test_port.close()
        if b"$GPGGA" in test_data:
            gps_port = serial.Serial(port.device, gps_baud, timeout=5)
        else:
            ham_port = serial.Serial(port.device, ham_baud, timeout=5)

    # check that both ports are open
    if gps_port is None or ham_port is None:
        print("Error: Unable to open serial ports")
        exit(1)

def process_data(gps_data):
    # create a packet
    try:
        packet = packager.build_package(call_sign, "TCPIP*", gps_data["lat"], gps_data["lon"], gps_data["lat_dir"], gps_data["lon_dir"], symbol_table, symbol_code, gps_data["course"], gps_data["speed"], gps_data["altitude"])
        print(packet)
        print()
        # send update to APRS-IS of current location
        if super_verbose:
            print("Sending APRS-IS Update")
        if super_verbose:
            print(json.dumps(aprslib.parse(packet), indent=4))
            print()

        # send packet to APRS-IS
        AIS.sendall(packet)
        return True
    except:
        if verbose:
            print("Failed to create APRS Packet")
        if super_verbose:
            print(json.dumps(gps_data, indent=4))
            print()
        return False

def wait_for_gps():
    if super_verbose:
        print("Waiting for GPS")
    time.sleep(5)
    send_update()

def send_update():
    gps_data = gps.get_gps_data(gps_port.read(gps_port.in_waiting))
    if gps_data is not None:
        if super_verbose:
            print("GPS Data Received")
        if super_verbose:
            print(json.dumps(gps_data, indent=4))
        if not process_data(gps_data):
            return False
        if super_verbose:
            print("APRS-IS Update Sent")
            print()
        return True
    else:
        return False

def upload_packet(packet):
    if super_verbose:
        print("Uploading APRS Packet")
    # upload packet to APRS-IS
    AIS.sendall(packet)

def decode(packet):
    if packet is None or packet == b'' or packet == b'\r\n':
        return None
    
    if super_verbose:
        print("Decoding APRS Packet: ")

    try:
        decoded = aprslib.parse(packet)
        if verbose:
            print(decoded["raw"])
            print()
    except:
        if verbose:
            print("Failed to decode APRS Packet")
            print(packet)
            print()
        return None
    
    if decoded["from"] in tracker_call_signs or ("-" in decoded["from"] and decoded["from"].split("-")[0] in tracker_call_signs):
        if super_verbose:
            print("APRS Packet from Tracker")
            print(json.dumps(decoded, indent=4))
            print()
        return decoded
    else:
        if super_verbose:
            print("APRS Packet not from Tracker")
            print(json.dumps(decoded, indent=4))
            print()
        return None

def check_aprs():
    aprs_packet = ham_port.readline()
    aprs_data = decode(aprs_packet)
    if aprs_data is not None:
        upload_packet(aprs_data["raw"])
        if super_verbose:
            print("APRS Packet Uploaded")
        return True
    return False

if __name__ == '__main__':
    AIS = aprslib.IS(call_sign, passwd=passcode, host=aprs_is_server, port=aprs_is_port)
    AIS.connect()

    # Connect to the serial port
    setup_ports()

    print("Serial ports opened")
    print()

    wait_for_gps()
    last_update = time.time()

    while True:
        try:
            check_aprs()
            if time.time() - last_update > 30:
                if not send_update():
                    setup_ports()
                last_update = time.time()
        except KeyboardInterrupt:
            print()
            print("Keyboard Interrupt - Exiting...")
            exit(0)
        except Exception as e:
            print()
            print("Error: Unknown")
            print(e)
            

    


