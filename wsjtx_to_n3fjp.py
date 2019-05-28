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
    power = "0"
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
        self.__set_computer_name()
        self.__set_operator(self.config['DEFAULT']['operator'])
        self.__set_name_s(self.config['DEFAULT']['name'])
        self.__set_initials(self.config['DEFAULT']['initials'])
        self.__set_county(self.config['DEFAULT']['county'])
        self.__set_arrl_class_s(self.config['DEFAULT']['class'])
        self.__set_arrl_section_s(self.config['DEFAULT']['section'])
        self.__set_contest(self.config['DEFAULT']['contest'])
        self.reset_vals()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def reset_vals(self):
        """ Reset all values to beginning state """
        self.__set_name_r("")
        self.__set_call("")
        self.__set_arrl_class_r("")
        self.__set_arrl_section_r("")
        self.__set_date("")
        self.__set_time_on("")
        self.__set_time_off("")
        self.__set_band("")
        self.__set_mode("")
        self.__set_frequency("")
        self.__set_power("0")
        self.__set_rst_r("")
        self.__set_rst_s("")
        self.__set_grid_r("")
        self.__set_grid_s("")
        self.__set_comments("")
        self.set_points(self.get_points())

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
                'comment', 'name', 'operator', 'stx', 'srx', 'state'
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
                self.__set_call(attr)
            elif token == 'gridsquare':
                self.__set_grid_r(attr)
            elif token == 'mode':
                self.__set_mode(attr)
            elif token == 'rst_sent':
                if self.contest == 'FD':
                    self.__set_arrl_class_s(attr)
                else:
                    self.__set_rst_s(attr)
            elif token == 'rst_rcvd':
                if self.contest == 'FD':
                    self.__set_arrl_class_r(attr)
                else:
                    self.__set_rst_r(attr)
            elif token == 'qso_date':
                date = attr[0:4] + '/' + attr[4:6] + '/' + attr[6:8]
                self.__set_date(date)
            elif token == 'time_on':
                time_on = attr[0:2] + ':' + attr[2:4]
                self.__set_time_on(time_on)


#            elif token == 'qso_date_off':
#                self.__set_date_off(attr)
            elif token == 'time_off':
                time_off = attr[0:2] + ':' + attr[2:4]
                self.__set_time_off(time_off)
            elif token == 'band':
                end = attr.lower().find('m')
                band = attr[:end]
                self.__set_band(band)
            elif token == 'freq':
                self.__set_frequency(attr)
            elif token == 'station_callsign':
                self.__set_operator(attr)
            elif token == 'my_gridsquare':
                self.__set_grid_s(attr)
            elif token == 'tx_pwr':
                self.__set_power(attr)
            elif token == 'comment':
                self.__set_comments(attr)
            elif token == 'name':
                self.__set_name_r(attr)
            elif token == 'operator':
                self.__set_operator(attr)
            elif token == 'state':
                self.__set_arrl_section_r(attr)

            # Special handling for FLDigi
            if self.mode == 'PSK':
                self.__set_rst_s('599')
                self.__set_rst_r('599')

    def __set_computer_name(self):
        self.computer_name = socket.gethostname()

    def __set_operator(self, operator):
        self.operator = operator

    def __set_name_s(self, name_s):
        self.name_s = name_s

    def __set_initials(self, initials):
        self.initials = initials

    def __set_county(self, county):
        self.county = county

    def __set_arrl_class_r(self, arrl_class_r):
        self.arrl_class_r = arrl_class_r

    def __set_arrl_class_s(self, arrl_class_s):
        self.arrl_class_s = arrl_class_s

    def __set_arrl_section_r(self, arrl_section_r):
        self.arrl_section_r = arrl_section_r

    def __set_arrl_section_s(self, arrl_section_s):
        self.arrl_section_s = arrl_section_s

    def __set_contest(self, contest):
        self.contest = contest

    def __set_name_r(self, name_r):
        self.name_r = name_r

    def __set_call(self, call_s):
        self.call = call_s

    def __set_date(self, date):
        self.date = date

    def __set_time_on(self, time_on):
        self.time_on = time_on

    def __set_time_off(self, time_off):
        self.time_off = time_off

    def __set_band(self, band):
        self.band = band

    def __set_mode(self, mode):
        self.mode = mode

    def __set_frequency(self, frequency):
        self.frequency = frequency

    def __set_power(self, power):
        self.power = float(power)

    def __set_rst_r(self, rst_r):
        self.rst_r = rst_r

    def __set_rst_s(self, rst_s):
        self.rst_s = rst_s

    def __set_grid_r(self, grid_r):
        self.grid_r = grid_r

    def __set_grid_s(self, grid_s):
        self.grid_s = grid_s

    def __set_comments(self, comments):
        self.comments = comments

    def set_points(self, points):
        """ Set points for ARRL Field Day calculation """
        self.points = points

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

    def tcp_send_string(self, send_str):
        """ Send text string over TCP socket """
        total_sent = 0
        while total_sent < len(send_str):
            bytes_sent = self.sock.send(send_str.encode())
            if bytes_sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + bytes_sent

    def tcp_recv_string(self):
        """ Receive text string over TCP socket """
        chunks = []
        total_recv = 0
        finished = 0
        while finished == 0:
            print("Receiving...")
            chunk = self.sock.recvfrom(1024)
            print("Received: %s" % chunk)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            total_recv = total_recv + len(chunk)
        return b''.join(chunks)

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
            self.sock.connect((self.config['DEFAULT']['N3FJP_HOST'],
                               int(self.config['DEFAULT']['N3FJP_PORT'])))
            self.tcp_send_string(command)
            time.sleep(.2)
            command = "<CMD><CHECKLOG></CMD>\r\n"
            print("Sending log refresh...")
            self.tcp_send_string(command)
        except socket.error as msg:
            sys.stderr.write("[ERROR] Failed to connect to N3FJP: %s\n" % msg)


if __name__ == "__main__":
    W = WsjtxToN3fjp()
    print("WSJT-X to N3FJP written by Dave Slotter callsign W3DJS\n")
    while True:
        W.udp_recv_string()
        W.parse_adif()
        W.set_points(W.get_points())
        W.log_new_qso()
        W.reset_vals()
    W.sock.close()
