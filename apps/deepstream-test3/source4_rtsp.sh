#!/bin/bash

python3 deepstream_test_3_rtspout.py "rtsp://192.168.0.200:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=100" \
                                     "rtsp://192.168.0.201:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=100" \
                                     "rtsp://192.168.0.202:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=100" \
                                     "rtsp://192.168.0.203:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=100" \
                                     "rtsp://192.168.0.204:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=100" \
                                     "rtsp://192.168.0.205:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=100" \
                                     "rtsp://192.168.0.206:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=100" \
                                     "rtsp://192.168.0.207:554/user=admin&password=123456&channel=1&stream=0.sdp?real_stream--rtp-caching=100" \
                                    "file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264"\
                                    "file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264"