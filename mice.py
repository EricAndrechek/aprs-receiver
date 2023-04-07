#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# adapted from https://github.com/txjacob/stardusterIII/blob/master/aprs/mice.py

# Work based HEAVILY on https://hugosprojects.wordpress.com/2014/03/20/implementing-aprs-gps-data/

from math import floor

characters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

def comment_altitude(altitude):
    altitude = min(999999, altitude)
    altitude = max(-99999, altitude)
    return "/A={0:06.0f}".format(altitude)

def encode_dest(degrees, minutes, minutes_hundreths, north, mode, long_offset, west):
    string = ""

    degrees_10 = floor(degrees / 10)
    degrees_1 = degrees - (degrees_10 * 10)

    minutes_10 = floor(minutes / 10)
    minutes_1 = minutes - (minutes_10 * 10)

    minutes_hundreths_10 = floor(minutes_hundreths / 10)
    minutes_hundreths_1 = minutes_hundreths - (minutes_hundreths_10 * 10)

    if(mode & 0x4):
        string += characters[degrees_10 + 22]
    else:
        string += characters[degrees_10]

    if(mode & 0x2):
        string += characters[degrees_1 + 22]
    else:
        string += characters[degrees_1]

    if(mode & 0x1):
        string += characters[minutes_10 + 22]
    else:
        string += characters[minutes_10]

    if(north):
        string += characters[minutes_1 + 22]
    else:
        string += characters[minutes_1]

    if(long_offset):
        string += characters[minutes_hundreths_10 + 22]
    else:
        string += characters[minutes_hundreths_10]

    if(west):
        string += characters[minutes_hundreths_1 + 22]
    else:
        string += characters[minutes_hundreths_1]

    return string

def encode_info(degrees, minutes, minutes_hundreths, west, speed, heading, symbol_table, symbol_code):

    string = "`"

    speed_ht = floor(speed / 10)
    speed_units = speed - (speed_ht * 10)

    heading_hundreds = floor(heading / 100)
    heading_tens_units = heading - (heading_hundreds * 100)

    if(degrees <= 9):
        string += chr(degrees + 118)
        long_offset = 1
    elif(10 <= degrees and degrees <= 99):
        string += chr(degrees + 28)
        long_offset = 0
    elif(100 <= degrees and degrees <= 109):
        string += chr(degrees + 8)
        long_offset = 1
    elif(110 <= degrees):
        string += chr(degrees - 72)
        long_offset = 1

    if(minutes <= 9):
        string += chr(minutes + 88)
    else:
        string += chr(minutes + 28)

    string += chr(minutes_hundreths + 28)

    if(speed <= 199):
        string += chr(speed_ht + 108)
    else:
        string += chr(speed_ht + 28)

    string += chr((int(speed_units*10)) + heading_hundreds + 32)

    string += chr(heading_tens_units + 28)

    # Add the symbol for a balloon
    string += symbol_code
    string += symbol_table


    return string, west, long_offset

def altitude(alt):
    alt_m = round(alt * 0.3048)
    rel_alt = alt_m + 10000
    
    val_1 = int(rel_alt / 8281)
    rem = rel_alt % 8281

    val_2 = int(rem / 91)
    val_3 = rem % 91

    return chr(val_1 + 33) + chr(val_2 + 33) + chr(val_3 + 33) + "}"


class mice_pkt(object):
    callsign  = ""
    path      = ""
    mode      = 7
    lat_degrees, lat_minutes, lat_minutes_hundreths, north = 0, 0, 0, 0
    lon_degrees, lon_minutes, lon_minutes_hundreths, west = 0, 0, 0, 0
    heading   = 0

    # In knots
    speed = 0.0
    # In feet
    altitude = 0.0

    symbol_table = "/"
    symbol_code = ">"

    def __init__(self):
        self.data = []

    def __str__(self):

        (info_string, west, long_offset) = encode_info(self.lon_degrees, self.lon_minutes, self.lon_minutes_hundreths, self.west, self.speed, self.heading, self.symbol_table, self.symbol_code)
        dest_string = encode_dest(self.lat_degrees, self.lat_minutes, self.lat_minutes_hundreths, self.north, self.mode, long_offset, west)
        alt_string = altitude(self.altitude)
        return self.callsign + ">" + dest_string + "," + self.path + ":" + info_string + alt_string
