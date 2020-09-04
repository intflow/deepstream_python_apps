from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory

from onvif import ONVIFCamera
import time
import cv2
from onvif_ptz import onvif_ptz


app = Flask(__name__)

ptz_list = []
for i in range(0,8):
    ptz_list.append(onvif_ptz(IP = "192.168.0.21"+str(i),PORT = 80, USER = "admin", PASS = "intflow3121", wsdl_dir = "/works/Camera-Streaming-On-ThingsBoard/python-onvif-zeep/wsdl/"))

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1
ZMAX = 1.0
ZMIN = 0
positionrequest = None
ptz = None
active = False
homerequest = None
media_profile = None

def do_move(ptz, request):
    # Start continuous move
    global active
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.ContinuousMove(request)

def do_move_home(ptz, request):
    # Start continuous move
    global active
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.AbsoluteMove(request)
    
def do_zoom(ptz, request):
    global active
    if active:
        ptz.Stop({'ProfileToken': request.ProfileToken})
    active = True
    ptz.AbsoluteMove(request)

def move_up(ptz, request):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMAX
    do_move(ptz, request)

def move_down(ptz, request):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMIN
    do_move(ptz, request)

def move_right(ptz, request):
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = 0
    do_move(ptz, request)

def move_left(ptz, request):
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = 0
    do_move(ptz, request)
    

def move_upleft(ptz, request):
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = YMAX
    do_move(ptz, request)
    
def move_upright(ptz, request):
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = YMAX
    do_move(ptz, request)
    
def move_downleft(ptz, request):
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = YMIN
    do_move(ptz, request)
    
def move_downright(ptz, request):
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = YMIN
    do_move(ptz, request)

def move_home(ptz, request):
    request.Position.PanTilt.x = 1
    request.Position.PanTilt.y = 0
    request.Position.Zoom = 0
    do_move_home(ptz,request)

def Zoom_in(ptz,request):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = ZMAX
    do_move(ptz, request)

def Zoom_out(ptz,request):
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    request.Velocity.Zoom.x = ZMIN
    do_move(ptz,request)


@app.route('/')
def index():
    return render_template('camera_control.html')


@app.route('/up', methods=["POST"])
def up():
    ptz_list[0].move_up(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].move_up(ptz_list[1].ptz,ptz_list[1].positionrequest)
    move_up(ptz,positionrequest)
    return 'OK'

@app.route('/down', methods=["POST"])
def down():
    ptz_list[0].move_down(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].move_down(ptz_list[1].ptz,ptz_list[1].positionrequest)
    move_down(ptz,positionrequest)
    return 'OK'

@app.route('/left', methods=["POST"])
def left():
    ptz_list[0].move_left(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].move_left(ptz_list[1].ptz,ptz_list[1].positionrequest)
    move_left(ptz,positionrequest)
    return 'OK'

@app.route('/right', methods=["POST"])
def right():
    ptz_list[0].move_right(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].move_right(ptz_list[1].ptz,ptz_list[1].positionrequest)
    move_right(ptz,positionrequest)
    return 'OK'

@app.route('/left_up', methods=["POST"])
def left_up():
    ptz_list[0].move_upleft(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].move_upleft(ptz_list[1].ptz,ptz_list[1].positionrequest)
    move_upleft(ptz,positionrequest)
    return 'OK'

@app.route('/right_up', methods=["POST"])
def right_up():
    ptz_list[0].move_upright(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].move_upright(ptz_list[1].ptz,ptz_list[1].positionrequest)
    move_upright(ptz,positionrequest)
    return 'OK'

@app.route('/left_down', methods=["POST"])
def left_down():
    ptz_list[0].move_downleft(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].move_downleft(ptz_list[1].ptz,ptz_list[1].positionrequest)
    move_downleft(ptz,positionrequest)
    return 'OK'

@app.route('/right_down', methods=["POST"])
def right_down():
    ptz_list[0].move_downright(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].move_downright(ptz_list[1].ptz,ptz_list[1].positionrequest)
    move_downright(ptz,positionrequest)
    return 'OK'

@app.route('/zoom_in', methods=["POST"])
def zoom_in():
    ptz_list[0].Zoom_in(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].Zoom_in(ptz_list[1].ptz,ptz_list[1].positionrequest)
    Zoom_in(ptz,positionrequest)
    return 'OK'

@app.route('/zoom_out', methods=["POST"]) 
def zoom_out():
    ptz_list[0].Zoom_out(ptz_list[0].ptz,ptz_list[0].positionrequest)
    ptz_list[1].Zoom_out(ptz_list[1].ptz,ptz_list[1].positionrequest)
    Zoom_out(ptz,positionrequest)
    return 'OK'

@app.route('/home', methods=["POST"])
def home():
    ptz_list[0].move_home(ptz_list[0].ptz,ptz_list[0].homerequest)
    ptz_list[1].move_home(ptz_list[1].ptz,ptz_list[1].homerequest)
    move_home(ptz,homerequest)
    return 'OK'

@app.route('/stop', methods=["POST"])
def stop():
    ptz.Stop({'ProfileToken': positionrequest.ProfileToken})
    ptz_list[0].ptz.Stop({'ProfileToken': ptz_list[0].positionrequest.ProfileToken})
    ptz_list[1].ptz.Stop({'ProfileToken': ptz_list[1].positionrequest.ProfileToken})
    return 'OK'


def main():
    ip = "192.168.0.112"
    os.system("pkill webrtc-streamer")
    time.sleep(1)

    ### Run webRTC streamer
    os.system("./webrtc-streamer -H 0.0.0.0:9000 -a rtsp://{}:8554/main  &".format(ip))  
    time.sleep(1)

    app.run(host='0.0.0.0', port=5000, debug=False)
    

if __name__ == "__main__":
    main()