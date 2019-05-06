# wsjtx_to_n3fjp
WSJT-X to N3FJP log adapter written in Python written by Dave Slotter, Amateur Radio Callsign [W3DJS](https://www.qrz.com/db/W3DJS)

wsjtx_to_n3fjp is a Python script which listens to the UDP output from WSJT-X to what would ordinarily go to the N1MM+ Logger broadcasts and parses and reformats that log data to the TCP input of N3FJP so that QSOs can be automatically logged for Linux users of digital amateur radio.

To use, download "config" and "wsjtx_to_n3fjp.py" and put them in your path, or wherever from you wish to run it.

Next, edit the values in the config file:
```
[DEFAULT]
county = GWIN
operator = W4FAKE
name = John Doe
initials = jd
class =
section =
N3FJP_HOST  = 127.0.0.1
N3FJP_PORT  = 1100
WSJT_X_HOST = 127.0.0.1
WSJT_X_PORT = 2333
```
operator is your callsign. name and initials are the name and initials of the local station operator. county is the abbreviation for the county from which you are working. Class and section are for ARRL Field Day usage. In this example, Gwinnet County, Georgia is "GWIN".

The values, N3FJP_HOST and N3FJP_PORT are default values for a locally-running copy of N3FJP. You may change these values for non-standard ports, or if N3FJP is running on a remote computer.

Likewise, WSJT_X_HOST and WSJT_X_PORT are default values for a locally-running copy of WSJT-X. You may change these values for non-standard ports, or if WSJT-X is running on a remote computer.

Once the config file has been edited, you may launch wsjtx_to_n3fjp from the command line;
```
dave@Moonquake:~/projects/python/wsjtx_to_n3fjp$ ./wsjtx_to_n3fjp.py 
Waiting for new log entry...
```
