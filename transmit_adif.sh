#!/bin/bash
###############################################################################
#
# BASH script to transmit ADIF logfile to wsjtx_to_n3fjp log adapter.
# 
# Written by Dave Slotter, <slotter+W3DJS@gmail.com>
#
# Amateur Radio Callsign W3DJS
#
# Created May 26, 2019 - Copyrighted under the GPL v3
#
###############################################################################

if [ "$1" == "" ] ; then
    echo "Must supply logfile name."
    exit
fi

while read -r line; do
    echo ""
    echo "Transmitting record: $line";
    echo "$line" | nc -q 1 -u 127.0.0.1 2333
    sleep 1;
done < "$1"
