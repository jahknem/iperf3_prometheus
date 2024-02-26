#!/bin/bash

# Start iperf3 in server mode with output redirected to /tmp/iperf3.log
iperf3 -s -D -p 5201 >> /tmp/iperf3_5201.log 2>&1 &
iperf3 -s -D -p 5202 >> /tmp/iperf3_5202.log 2>&1 &
iperf3 -s -D -p 5203 >> /tmp/iperf3_5203.log 2>&1 &
iperf3 -s -D -p 5204 >> /tmp/iperf3_5204.log 2>&1 &
iperf3 -s -D -p 5205 >> /tmp/iperf3_5205.log 2>&1 &
iperf3 -s -D -p 5206 >> /tmp/iperf3_5206.log 2>&1 &

# Run the Flask application
flask run --host=0.0.0.0
