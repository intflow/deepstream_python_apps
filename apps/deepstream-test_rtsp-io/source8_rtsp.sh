#!/bin/bash

python3 deepstream_test_rtsp_io.py "rtsp://192.168.0.200:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.201:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.202:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.203:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.204:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.205:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.206:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.207:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.206:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://192.168.0.207:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=4000" \
                                   "rtsp://admin:intflow3121@192.168.0.103:554/cam/realmonitor?channel=1&subtype=0" \
                                   "rtsp://admin:intflow3121@192.168.0.103:554/cam/realmonitor?channel=2&subtype=0" \
                                   "rtsp://admin:kmjeon3121@192.168.0.108:554/cam/realmonitor?channel=1&subtype=0" \
                                   "rtsp://admin:kmjeon3121@192.168.0.108:554/cam/realmonitor?channel=2&subtype=0"