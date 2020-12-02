import os
import sys
c_folder = os.path.abspath(os.path.dirname(__file__))
# p_folder = os.path.abspath(os.path.dirname(c_folder))
sys.path.append(c_folder)
# sys.path.append(p_folder)

import argparse
import threading
# from pytorch_har import Do_HAR
from flask import Flask, render_template, Response
from deepstream import DeepStream

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/video_feed')
def video_feed():
    return Response(vid.stream_to_flask(), mimetype='multipart/x-mixed-replace; boundary=frame')

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

    return None


def main(args):

    global vid

    vid = DeepStream(args)

    vid_thread = threading.Thread(target=vid.main)
    vid_thread.start()

    app.run(host='0.0.0.0', port=5252, debug=False)

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IntFlow Human Action Recognition.')
    parser.add_argument('--cam1', default='/dev/video0') 
    parser.add_argument('--cpu', default=False, help='Use cpu or not', type=str2bool)
    
    args = parser.parse_args()
    args = vars(args)
    main(args)
