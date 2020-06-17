#!/usr/bin/python3
"""
Python adapter to connect logging output of WSJT-X to API input of N3FJP.

Written by Dave Slotter, <slotter+W3DJS@gmail.com>

Amateur Radio Callsign W3DJS

Created May 2, 2019 - Copyrighted under the GPL v3
"""

import socket
import sys
import time
import configparser


class WsjtxToN3fjp:
    """ Class WsjtxToN3fjp """
    # pylint: disable=too-many-instance-attributes
    # These are all required variables.
    config = ""
    computer_name = ""
    operator = ""
    name_s = ""
    initials = ""
    county = ""
    arrl_class_r = ""
    arrl_class_s = ""
    arrl_section_r = ""
    arrl_section_s = ""
    name_r = ""
    call = ""
    date = ""
    time_on = ""
    time_off = ""
    band = ""
    mode = ""
    frequency = 0
    power = 0
    rst_r = 0
    rst_s = 0
    grid_r = ""
    grid_s = ""
    comments = ""
    points = 0
    contest = ""
    recv_buffer = ""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config')
        self.computer_name = socket.gethostname()
        self.operator = self.config['DEFAULT']['operator']
        self.name_s = self.config['DEFAULT']['name']
        self.initials = self.config['DEFAULT']['initials']
        self.county = self.config['DEFAULT']['county']
        self.arrl_class_s = self.config['DEFAULT']['class']
        self.arrl_section_s = self.config['DEFAULT']['section']
        self.contest = self.config['DEFAULT']['contest']
        self.reset_vals()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def reset_vals(self):
        """ Reset all values to beginning state """
        self.name_r = ""
        self.call = ""
        self.arrl_class_r = ""
        self.arrl_section_r = ""
        self.date = ""
        self.time_on = ""
        self.time_off = ""
        self.band = ""
        self.mode = ""
        self.frequency = ""
        self.power = 0
        self.rst_r = ""
        self.rst_s = ""
        self.grid_r = ""
        self.grid_s = ""
        self.comments = ""
        self.points = self.get_points()

    def parse_adif(self):
        """ Parse ADIF record """
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # It's a parser after all
        print("\nParsing log entry from WSJT-X...\n")
        for token in [
                'call', 'gridsquare', 'mode', 'rst_sent', 'rst_rcvd',
                'qso_date', 'time_on', 'qso_date_off', 'time_off', 'band',
                'freq', 'station_callsign', 'my_gridsquare', 'tx_pwr',
                'comment', 'name', 'operator', 'stx', 'srx', 'state',
		'class', 'arrl_sect'
        ]:
            strbuf = str(self.recv_buffer)
            search_token = "<" + token + ":"
            start = strbuf.lower().find(search_token)
            if start == -1:
                continue
            end = strbuf.find(':', start) - 1
            if end == -1:
                break
            pos = end + 2
            found_num = True
            while found_num is True:
                if strbuf[pos + 1].isdigit() is True:
                    pos = pos + 1
                else:
                    found_num = False

            attr_len = int(strbuf[end + 2:pos + 1])
            strbuf = str(self.recv_buffer)
            attr = strbuf[pos + 2:pos + 2 + int(attr_len)]
            print("%s: %s" % (token, attr))

            if token == 'call':
                self.call = attr
            elif token == 'gridsquare':
                self.grid_r = attr
            elif token == 'mode':
                self.mode = attr
            elif token == 'rst_sent':
                if self.contest == 'FD':
                    self.arrl_class_s = attr
                else:
                    self.rst_s = attr
            elif token == 'class':
                    self.arrl_class_r = attr
            elif token == 'arrl_sect':
                    self.arrl_section_r = attr
            elif token == 'rst_rcvd':
                self.rst_r = attr
            elif token == 'qso_date':
                date = attr[0:4] + '/' + attr[4:6] + '/' + attr[6:8]
                self.date = date
            elif token == 'time_on':
                time_on = attr[0:2] + ':' + attr[2:4]
                self.time_on = time_on


#            elif token == 'qso_date_off':
#                self.date_off = attr
            elif token == 'time_off':
                time_off = attr[0:2] + ':' + attr[2:4]
                self.time_off = time_off
            elif token == 'band':
                end = attr.lower().find('m')
                band = attr[:end]
                self.band = band
            elif token == 'freq':
                self.frequency = attr
            elif token == 'station_callsign':
                self.operator = attr
            elif token == 'my_gridsquare':
                self.grid_s = attr
            elif token == 'tx_pwr':
                self.power = float(attr)
            elif token == 'comment':
                self.comments = attr
            elif token == 'name':
                self.name_r = attr
            elif token == 'operator':
                self.operator = attr
            elif token == 'state':
                self.arrl_section_r = attr

            # Special handling for FLDigi
            if self.mode == 'PSK':
                self.rst_s = '599'
                self.rst_r = '599'

    def get_points(self):
        """ Calculate points """
        mult = 1

        switcher = {
            'FT4': 2,
            'FT8': 2,
            'DATA': 2,
            'RTTY': 2,
            'JT4': 2,
            'JT9': 2,
            'JT65': 2,
            'QRA64': 2,
            'ISCAT': 2,
            'MSK144': 2,
            'WSPR': 2,
            'MFSK': 2,
            'PSK': 2,
            'PSK31': 2
        }
        mult = mult * switcher.get(self.mode, 1)

        if self.power == 0:
            mult = mult * 1
        elif self.power <= 5:
            mult = mult * 5
        elif self.power <= 150:
            mult = mult * 2
        elif self.power >= 150:
            mult = mult * 1

        return mult

    def tcp_send_string(self, sock, send_str):
        """ Send text string over TCP socket """
        total_sent = 0
        while total_sent < len(send_str):
            bytes_sent = sock.send(send_str.encode())
            if bytes_sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + bytes_sent

    def udp_recv_string(self):
        """ Receive text string over UDP socket """
        try:
            self.recv_buffer = ""
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.config['DEFAULT']['WSJT_X_HOST'],
                       int(self.config['DEFAULT']['WSJT_X_PORT'])))
            print("Waiting for new log entry...")
            self.recv_buffer = sock.recvfrom(1024)
            print("Received log message:\n\n", self.recv_buffer)
        except KeyboardInterrupt:
            sys.stderr.write("User cancelled.")
            sock.close()
            sys.exit(0)
        except socket.error as msg:
            sys.stderr.write(
                "[ERROR] %s (is another copy of wsjtx_to_n3fjp running?)\n" %
                msg)
            sys.exit(2)

    def log_new_qso(self):
        """ Log new QSO to N3FJP """
        if self.contest == 'FD':
            command = """<CMD><ADDDIRECT><EXCLUDEDUPES>TRUE</EXCLUDEDUPES>
<STAYOPEN>TRUE</STAYOPEN>
<fldComputerName>%s</fldComputerName>
<fldOperator>%s</fldOperator>
<fldNameS>%s</fldNameS>
<fldInitials>%s</fldInitials>
<fldCountyS>%s</fldCountyS>
<fldCall>%s</fldCall>
<fldNameR>%s</fldNameR>
<fldDateStr>%s</fldDateStr>
<fldTimeOnStr>%s</fldTimeOnStr>
<fldTimeOffStr>%s</fldTimeOffStr>
<fldBand>%s</fldBand>
<fldMode>%s</fldMode>
<fldFrequency>%s</fldFrequency>
<fldPower>%s</fldPower>
<fldGridR>%s</fldGridR>
<fldGridS>%s</fldGridS>
<fldComments>%s</fldComments>
<fldPoints>%s</fldPoints>
<fldClass>%s</fldClass>
<fldSection>%s</fldSection></CMD>\r\n""" % (self.computer_name, self.operator,
                                            self.name_s, self.initials,
                                            self.county, self.call,
                                            self.name_r, self.date,
                                            self.time_on, self.time_off,
                                            self.band, self.mode,
                                            self.frequency, self.power,
                                            self.grid_r, self.grid_s,
                                            self.comments, self.points,
                                            self.arrl_class_r,
                                            self.arrl_section_r)
        else:
            command = """<CMD><ADDDIRECT><EXCLUDEDUPES>TRUE</EXCLUDEDUPES>
<STAYOPEN>TRUE</STAYOPEN>
<fldComputerName>%s</fldComputerName>
<fldOperator>%s</fldOperator>
<fldNameS>%s</fldNameS>
<fldInitials>%s</fldInitials>
<fldCountyS>%s</fldCountyS>
<fldCall>%s</fldCall>
<fldNameR>%s</fldNameR>
<fldDateStr>%s</fldDateStr>
<fldTimeOnStr>%s</fldTimeOnStr>
<fldTimeOffStr>%s</fldTimeOffStr>
<fldBand>%s</fldBand>
<fldMode>%s</fldMode>
<fldFrequency>%s</fldFrequency>
<fldPower>%s</fldPower>
<fldRstR>%s</fldRstR>
<fldRstS>%s</fldRstS>
<fldGridR>%s</fldGridR>
<fldGridS>%s</fldGridS>
<fldComments>%s</fldComments>
<fldPoints>%s</fldPoints>
<fldClass>%s</fldClass>
<fldSection>%s</fldSection></CMD>\r\n""" % (self.computer_name, self.operator,
                                            self.name_s, self.initials,
                                            self.county, self.call,
                                            self.name_r, self.date,
                                            self.time_on, self.time_off,
                                            self.band, self.mode,
                                            self.frequency, self.power,
                                            self.rst_r, self.rst_s,
                                            self.grid_r, self.grid_s,
                                            self.comments, self.points,
                                            self.arrl_class_r,
                                            self.arrl_section_r)
        print("\nSending log entry to N3FJP...")
        print(command)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.config['DEFAULT']['N3FJP_HOST'],
                               int(self.config['DEFAULT']['N3FJP_PORT'])))
            self.tcp_send_string(sock, command)
            time.sleep(.5)
            command = "<CMD><CHECKLOG></CMD>\r\n"
            print("Sending log refresh...")
            self.tcp_send_string(sock, command)
            sock.close()
        except socket.error as msg:
            sys.stderr.write("[ERROR] Failed to connect to N3FJP: %s\n" % msg)


if __name__ == "__main__":
    W = WsjtxToN3fjp()
    print("WSJT-X to N3FJP written by Dave Slotter callsign W3DJS\n")
    while True:
        W.udp_recv_string()
        W.parse_adif()
        W.points = W.get_points()
        W.log_new_qso()
        W.reset_vals()
    W.sock.close()
