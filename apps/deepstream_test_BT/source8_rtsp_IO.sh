#!/bin/bash

python3 deepstream_test_rtsp_io.py "rtsp://admin:intflow3121@192.168.0.100:554/cam/realmonitor?channel=1&subtype=0" \
                                   "rtsp://admin:intflow3121@192.168.0.100:554/cam/realmonitor?channel=2&subtype=0" 
                                   #"rtsp://admin:intflow3121@192.168.0.101:554/cam/realmonitor?channel=1&subtype=0" \
                                   #"rtsp://admin:intflow3121@192.168.0.101:554/cam/realmonitor?channel=2&subtype=0" \
                                   #"rtsp://admin:intflow3121@192.168.0.102:554/cam/realmonitor?channel=1&subtype=0" \
                                   #"rtsp://admin:intflow3121@192.168.0.102:554/cam/realmonitor?channel=2&subtype=0" \
                                   #"rtsp://admin:intflow3121@192.168.0.103:554/cam/realmonitor?channel=1&subtype=0" \
                                   #"rtsp://admin:intflow3121@192.168.0.103:554/cam/realmonitor?channel=2&subtype=0" 