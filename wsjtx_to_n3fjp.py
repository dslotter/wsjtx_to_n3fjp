#!/usr/bin/python3
###############################################################################
#
# Python adapter to connect logging output of WSJT-X to API input of N3FJP.
#
# Written by Dave Slotter, <slotter+W3DJS@gmail.com>
#
# Amateur Radio Callsign W3DJS
#
# Created May 2, 2019 - Copyrighted under the GPL v3
#
###############################################################################

import configparser
import socket
import sys
import time


class WsjtxToN3fjp:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config')
        self.set_computer_name()
        self.operator = self.config['DEFAULT']['operator']
        self.name_s = self.config['DEFAULT']['name']
        self.initials = self.config['DEFAULT']['initials']
        self.county = self.config['DEFAULT']['county']
        self.arrl_class_s = self.config['DEFAULT']['class']
        self.arrl_section_s = self.config['DEFAULT']['section']
        self.contest = self.config['DEFAULT']['contest']
        self.reset_vals()

    def reset_vals(self):
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
        self.power = "0"
        self.rst_r = ""
        self.rst_s = ""
        self.grid_r = ""
        self.grid_s = ""
        self.comments = ""
        self.points = self.get_points()

    def parse_adif(self):
        print("\nParsing log entry from WSJT-X...\n")
        for token in [
            'call',
            'gridsquare',
            'mode',
            'rst_sent',
            'rst_rcvd',
            'qso_date',
            'time_on',
            'qso_date_off',
            'time_off',
            'band',
            'freq',
            'station_callsign',
            'my_gridsquare',
            'tx_pwr',
            'comment',
            'name',
            'operator',
            'stx',
            'srx',
                'state']:
            strbuf = str(self.recv_buffer)
            search_token = "<" + token + ":"
            start = strbuf.lower().find(search_token)
            if start == -1:
                #              print("Didn't find token: %s" % search_token)
                continue
            end = strbuf.find(':', start) - 1
            if end == -1:
                break
#            print ( "Pos: %d End: %d Str: %s" % ( start , end, strbuf[start:end+1]) )
            pos = end + 2
            bFoundNum = True
            while bFoundNum:
                if strbuf[pos + 1].isdigit():
                    pos = pos + 1
                else:
                    bFoundNum = False

#            print ( "Start: %d  End: %d" % (end+2, pos) )
            attr_len = int(strbuf[end + 2:pos + 1])
#            print ( "Length: %s" % attr_len )
            strbuf = str(self.recv_buffer)
#            print ( "Pos+2: %d End+4: %d" % ( pos+2 , end+4))
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
            elif token == 'rst_rcvd':
                if self.contest == 'FD':
                    self.arrl_class_r = attr
                else:
                    self.rst_r = attr
            elif token == 'qso_date':
                date = attr[0:4] + '/' + attr[4:6] + '/' + attr[6:8]
#                print (date)
                self.date = date
            elif token == 'time_on':
                time = attr[0:2] + ':' + attr[2:4]
#                print (time)
                self.time_on = time
#            elif token == 'qso_date_off':
#                self.date_off = attr
            elif token == 'time_off':
                time = attr[0:2] + ':' + attr[2:4]
#                print (time)
                self.time_off = time
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
                self.power = attr
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

    def set_computer_name(self):
        self.computer_name = socket.gethostname()

    def get_points(self):
        mult = 1
        power = int(self.power)

        switcher = {
            'FT4':    2,
            'FT8':    2,
            'DATA':   2,
            'RTTY':   2,
            'JT4':    2,
            'JT9':    2,
            'JT65':   2,
            'QRA64':  2,
            'ISCAT':  2,
            'MSK144': 2,
            'WSPR':   2,
            'MFSK':   2,
            'PSK':    2,
            'PSK31':  2
        }
        mult = mult * switcher.get(self.mode, 1)

        if power == 0:
            mult = mult * 1
        elif power <= 5:
            mult = mult * 5
        elif power <= 150:
            mult = mult * 2
        elif power >= 150:
            mult = mult * 1

        return mult

    def tcp_send_string(self, str):
        # print ("Length to send: %d" % len(str) )
        totalSent = 0
        while totalSent < len(str):
            # print ("Sending...")
            bytesSent = self.sock.send(str.encode())
            if bytesSent == 0:
                raise RuntimeError("socket connection broken")
            totalSent = totalSent + bytesSent

    def tcp_recv_string(self):
        chunks = []
        totalRecv = 0
        bFinished = 0
        while bFinished == 0:
            print("Receiving...")
            chunk = self.sock.recvfrom(1024)
            print("Received: %s" % chunk)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            totalRecv = totalRecv + len(chunk)
        return b''.join(chunks)

    def udp_recv_string(self):
        try:
            self.recv_buffer = ""
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.config['DEFAULT']['WSJT_X_HOST'], int(
                self.config['DEFAULT']['WSJT_X_PORT'])))
            print("Waiting for new log entry...")
            self.recv_buffer = sock.recvfrom(1024)
            print("Received log message:\n\n", self.recv_buffer)
        except KeyboardInterrupt:
            sys.stderr.write("User cancelled.")
            sock.close()
            sys.exit(0)
        except socket.error as msg:
            sys.stderr.write(
                "[ERROR] %s (is another copy of wsjtx_to_n3fjp running?)\n" % msg)
            sys.exit(2)

    def log_new_qso(self):
        if self.contest == 'FD':
            command = "<CMD><ADDDIRECT><EXCLUDEDUPES>TRUE</EXCLUDEDUPES><STAYOPEN>TRUE</STAYOPEN><fldComputerName>%s</fldComputerName><fldOperator>%s</fldOperator><fldNameS>%s</fldNameS><fldInitials>%s</fldInitials><fldCountyS>%s</fldCountyS><fldCall>%s</fldCall><fldNameR>%s</fldNameR><fldDateStr>%s</fldDateStr><fldTimeOnStr>%s</fldTimeOnStr><fldTimeOffStr>%s</fldTimeOffStr><fldBand>%s</fldBand><fldMode>%s</fldMode><fldFrequency>%s</fldFrequency><fldPower>%s</fldPower><fldGridR>%s</fldGridR><fldGridS>%s</fldGridS><fldComments>%s</fldComments><fldPoints>%s</fldPoints><fldClass>%s</fldClass><fldSection>%s</fldSection></CMD>\r\n" % (
                self.computer_name, self.operator, self.name_s, self.initials, self.county, self.call, self.name_r,  self.date, self.time_on, self.time_off, self.band, self.mode, self.frequency, self.power, self.grid_r, self.grid_s, self.comments, self.points, self.arrl_class_r, self.arrl_section_r)
        else:
            command = "<CMD><ADDDIRECT><EXCLUDEDUPES>TRUE</EXCLUDEDUPES><STAYOPEN>TRUE</STAYOPEN><fldComputerName>%s</fldComputerName><fldOperator>%s</fldOperator><fldNameS>%s</fldNameS><fldInitials>%s</fldInitials><fldCountyS>%s</fldCountyS><fldCall>%s</fldCall><fldNameR>%s</fldNameR><fldDateStr>%s</fldDateStr><fldTimeOnStr>%s</fldTimeOnStr><fldTimeOffStr>%s</fldTimeOffStr><fldBand>%s</fldBand><fldMode>%s</fldMode><fldFrequency>%s</fldFrequency><fldPower>%s</fldPower><fldRstR>%s</fldRstR><fldRstS>%s</fldRstS><fldGridR>%s</fldGridR><fldGridS>%s</fldGridS><fldComments>%s</fldComments><fldPoints>%s</fldPoints><fldClass>%s</fldClass><fldSection>%s</fldSection></CMD>\r\n" % (
                self.computer_name, self.operator, self.name_s, self.initials, self.county, self.call, self.name_r,  self.date, self.time_on, self.time_off, self.band, self.mode, self.frequency, self.power, self.rst_r, self.rst_s, self.grid_r, self.grid_s, self.comments, self.points, self.arrl_class_r, self.arrl_section_r)
        print("\nSending log entry to N3FJP...")
        print(command)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.config['DEFAULT']['N3FJP_HOST'], int(
                self.config['DEFAULT']['N3FJP_PORT'])))
            self.tcp_send_string(command)
            time.sleep(.2)
            command = "<CMD><CHECKLOG></CMD>\r\n"
            print("Sending log refresh...")
            self.tcp_send_string(command)
        except socket.error as msg:
            sys.stderr.write("[ERROR] Failed to connect to N3FJP: %s\n" % msg)


if __name__ == "__main__":
    w = WsjtxToN3fjp()
    while True:
        w.udp_recv_string()
        w.parse_adif()
        w.points = w.get_points()
        w.log_new_qso()
        w.reset_vals()
    w.sock.close()
