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

class wsjtx_to_n3fjp:

    config = ""
    computer_name = ""
    operator = ""
    name_s = ""
    initials = ""
    county = ""
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
    recv_buffer = ""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config')
        self.set_computer_name()
        self.set_operator(self.config['DEFAULT']['operator'])
        self.set_name_s(self.config['DEFAULT']['name'])
        self.set_initials(self.config['DEFAULT']['initials'])
        self.set_county(self.config['DEFAULT']['county'])
        self.set_name_r("")
        self.set_call("")
        self.set_date("")
        self.set_time_on("")
        self.set_time_off("")
        self.set_band("")
        self.set_mode("")
        self.set_frequency("")
        self.set_power("0")
        self.set_rst_r("")
        self.set_rst_s("")
        self.set_grid_r("")
        self.set_grid_s("")
        self.set_comments("")
        self.set_points(self.get_points())

    def parse_adif(self):
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
            'operator' ]:
            strbuf = str(self.recv_buffer)
            search_token = "<" + token + ":"
            start = strbuf.find(search_token)
            if start == -1:
              break
            end = strbuf.find(':',start)-1
            if end == -1:
              break
#            print ( "Pos: %d End: %d Str: %s" % ( start , end, strbuf[start:end+1]) )
            pos = end + 2
            num_begin = strbuf[pos]
            bFoundNum = True
            while bFoundNum == True:
                if strbuf[pos + 1].isdigit() == True:
                    pos = pos + 1
                else:
                    bFoundNum = False

#            print ( "Start: %d  End: %d" % (end+2, pos) )

            attr_len = int(strbuf[end + 2:pos + 1])
#            print ( "Length: %s" % attr_len )
            strbuf = str(self.recv_buffer)
            attr = strbuf[pos + 2:end + 4 + int(attr_len)]
            print ( "%s: %s" % (token, attr) )

            if token == 'call':
                self.set_call(attr)
            elif token == 'gridsquare':
                self.set_grid_s(attr)
            elif token == 'mode':
                self.set_mode(attr)
            elif token == 'rst_sent':
                self.set_rst_s(attr)
            elif token == 'rst_rcvd':
                self.set_rst_r(attr)
            elif token == 'qso_date':
                date = attr[0:4] + '/' + attr[4:6] + '/' + attr[6:8]
#                print (date)
                self.set_date(date)
            elif token == 'time_on':
                time = attr[0:2] + ':' + attr[2:4]
#                print (time)
                self.set_time_on(time)
#            elif token == 'qso_date_off':
#                self.set_date_off(attr)
            elif token == 'time_off':
                time = attr[0:2] + ':' + attr[2:4]
#                print (time)
                self.set_time_off(time)
            elif token == 'band':
                end = attr.find('m')
                band = attr[:end]
                self.set_band(band)
            elif token == 'freq':
                self.set_frequency(attr)
            elif token == 'station_callsign':
                self.set_operator(attr)
            elif token == 'my_gridsquare':
                self.set_grid_s(attr)
            elif token == 'tx_pwr':
                self.set_power(attr)
            elif token == 'comment':
                self.set_comments(attr)
            elif token == 'name':
                self.set_name_r(attr)
            elif token == 'operator':
                self.set_operator(attr)


    def set_computer_name(self):
        self.computer_name = socket.gethostname()

    def set_operator(self, operator):
        self.operator = operator

    def set_name_s(self, name_s):
        self.name_s = name_s

    def set_initials(self, initials):
        self.initials = initials

    def set_county(self, county):
        self.county = county

    def set_name_r(self, name_r):
        self.name_r = name_r

    def set_call(self, call_s):
        self.call = call_s

    def set_date(self, date):
        self.date = date

    def set_time_on(self, time_on):
        self.time_on = time_on

    def set_time_off(self, time_off):
        self.time_off = time_off

    def set_band(self, band):
        self.band = band

    def set_mode(self, mode):
        self.mode = mode

    def set_frequency(self, frequency):
        self.frequency = frequency

    def set_power(self, power):
        self.power = int(power)

    def set_rst_r(self, rst_r):
        self.rst_r = rst_r

    def set_rst_s(self, rst_s):
        self.rst_s = rst_s

    def set_grid_r(self, grid_r):
        self.grid_r = grid_r

    def set_grid_s(self, grid_s):
        self.grid_s = grid_s

    def set_comments(self, comments):
        self.comments = comments

    def set_points(self, points):
        self.points = points

    def get_points(self):
        mult = 1

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
            'PSK31':  2
        } 
        mult = mult * switcher.get(self.mode, 1)

        if self.power <= 5:
            mult = mult * 5
        elif self.power <= 150:
            mult = mult * 2
        elif self.power >= 150:
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
         print ("Receiving...")
         chunk = self.sock.recvfrom(1024)
         print ("Received: %s" % chunk)
         if chunk == b'':
           raise RuntimeError("socket connection broken")
         chunks.append(chunk)
         totalRecv = totalRecv + len(chunk)
       return b''.join(chunks)

    def udp_recv_string(self):
        try:
            self.recv_buffer = ""
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.config['DEFAULT']['WSJT_X_HOST'], int(self.config['DEFAULT']['WSJT_X_PORT'])))
            print ("Waiting for new log entry...")
            self.recv_buffer = sock.recvfrom(1024)
            print ("Received log message:\n\n", self.recv_buffer)
        except KeyboardInterrupt:
            print ("User cancelled.")
            sock.close ()
            sys.exit()

    def log_new_qso(self):
        command = "<CMD><ADDDIRECT><EXCLUDEDUPES>TRUE</EXCLUDEDUPES><STAYOPEN>TRUE</STAYOPEN><fldComputerName>%s</fldComputerName><fldOperator>%s</fldOperator><fldNameS>%s</fldNameS><fldInitials>%s</fldInitials><fldCountyS>%s</fldCountyS><fldCall>%s</fldCall><fldNameR>%s</fldNameR><fldDateStr>%s</fldDateStr><fldTimeOnStr>%s</fldTimeOnStr><fldTimeOffStr>%s</fldTimeOffStr><fldBand>%s</fldBand><fldMode>%s</fldMode><fldFrequency>%s</fldFrequency><fldPower>%s</fldPower><fldRstR>%s</fldRstR><fldRstS>%s</fldRstS><fldGridR>%s</fldGridR><fldGridS>%s</fldGridS><fldComments>%s</fldComments><fldPoints>%s</fldPoints></CMD>\r\n" % (self.computer_name, self.operator, self.name_s, self.initials, self.county, self.call, self.name_r,  self.date, self.time_on, self.time_off, self.band, self.mode, self.frequency, self.power, self.rst_r, self.rst_s, self.grid_r, self.grid_s, self.comments, self.points)
        print (command)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.config['DEFAULT']['N3FJP_HOST'], int(self.config['DEFAULT']['N3FJP_PORT'])))
        print ("Sending log entry...")
        self.tcp_send_string(command)
        time.sleep(.2)
        command = "<CMD><CHECKLOG></CMD>\r\n"
        print ("Sending log refresh...")
        self.tcp_send_string(command)

if __name__ == "__main__":
    w = wsjtx_to_n3fjp()
    while True:
        w.udp_recv_string()
        w.parse_adif()
        w.set_points(w.get_points())
        w.log_new_qso()
    w.sock.close ()