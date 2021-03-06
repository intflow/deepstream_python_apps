#!/usr/bin/env python3

################################################################################
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

import argparse
import sys
sys.path.append('../')
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GObject, Gst, GstRtspServer
from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call

import cv2
import copy

import pyds


class DeepStream:

    def __init__(self,args):
        self.PGIE_CLASS_ID_VEHICLE = 0
        self.PGIE_CLASS_ID_BICYCLE = 1
        self.PGIE_CLASS_ID_PERSON = 2
        self.PGIE_CLASS_ID_ROADSIGN = 3
        self.codec = 'H264'
        self.bitrate = '1000000'
        self.stream_path = '/dev/video0'
        self.threshold = 0.1


    def osd_sink_pad_buffer_probe(self,pad,info,u_data):
        frame_number=0
        #Intiallizing object counter with 0.
        obj_counter = {
            self.PGIE_CLASS_ID_VEHICLE:0,
            self.PGIE_CLASS_ID_PERSON:0,
            self.PGIE_CLASS_ID_BICYCLE:0,
            self.PGIE_CLASS_ID_ROADSIGN:0
        }

        num_rects=0

        gst_buffer = info.get_buffer()
        if not gst_buffer:
            print("Unable to get GstBuffer ")
            return

        # Retrieve batch metadata from the gst_buffer
        # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
        # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
        l_frame = batch_meta.frame_meta_list
        while l_frame is not None:
            try:
                # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
                # The casting is done by pyds.NvDsFrameMeta.cast()
                # The casting also keeps ownership of the underlying memory
                # in the C code, so the Python garbage collector will leave
                # it alone.
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration:
                break

            frame_number=frame_meta.frame_num
            num_rects = frame_meta.num_obj_meta
            l_obj=frame_meta.obj_meta_list

            # Getting Image data using nvbufsurface
            # the input should be address of buffer and batch_id
            self.original_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)

            # convert python array into numy array format.
            self.frame_image = copy.deepcopy(self.original_frame)

            # covert the array into cv2 default color format
            # self.final_frame_tmp = cv2.cvtColor(self.frame_image, cv2.COLOR_RGBA2BGRA)
            # self.final_frame_tmp = cv2.cvtColor(self.frame_image, cv2.COLOR_RGBA2BGR)
            self.final_frame = cv2.cvtColor(self.frame_image, cv2.COLOR_RGBA2BGR)
            # self.final_frame = cv2.resize(self.final_frame_tmp, dsize=(0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

            face_detection_confidence = 0

            while l_obj is not None:
                try:
                    # Casting l_obj.data to pyds.NvDsObjectMeta
                    self.obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break
                # obj_counter[self.obj_meta.class_id] += 1
                # if self.obj_meta.confidence >= self.threshold:
                self.final_frame = self.draw_bounding_boxes(self.final_frame,self.obj_meta,self.obj_meta.confidence)
                face_detection_confidence = self.obj_meta.confidence
                try: 
                    l_obj=l_obj.next
                except StopIteration:
                    break
            



            ###### 이미지 처리 #########



            self.frame_to_stream = self.final_frame


            # Acquiring a display meta object. The memory ownership remains in
            # the C code so downstream plugins can still access it. Otherwise
            # the garbage collector will claim it when this probe function exits.
            display_meta=pyds.nvds_acquire_display_meta_from_pool(batch_meta)
            display_meta.num_labels = 1
            py_nvosd_text_params = display_meta.text_params[0]
            # Setting display text to be shown on screen
            # Note that the pyds module allocates a buffer for the string, and the
            # memory will not be claimed by the garbage collector.
            # Reading the display_text field here will return the C address of the
            # allocated string. Use pyds.get_string() to get the string content.
            # py_nvosd_text_params.display_text = f"Frame Number={frame_number} Number of Faces={num_rects} Confidence{face_detection_confidence}"
            py_nvosd_text_params.display_text = f"Frame Number={frame_number} Number of Faces={num_rects}"

            # Now set the offsets where the string should appear
            py_nvosd_text_params.x_offset = 10
            py_nvosd_text_params.y_offset = 12

            # Font , font-color and font-size
            py_nvosd_text_params.font_params.font_name = "Serif"
            py_nvosd_text_params.font_params.font_size = 10
            # set(red, green, blue, alpha); set to White
            py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)

            # Text background color
            py_nvosd_text_params.set_bg_clr = 1
            # set(red, green, blue, alpha); set to Black
            py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
            # Using pyds.get_string() to get display_text as string
            print(pyds.get_string(py_nvosd_text_params.display_text))
            pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)

            try:
                l_frame=l_frame.next
            except StopIteration:
                break
                
        return Gst.PadProbeReturn.OK

    def draw_bounding_boxes(self,image,obj_meta,confidence):
        confidence='{0:.2f}'.format(confidence)
        rect_params=obj_meta.rect_params
        top=int(rect_params.top)
        left=int(rect_params.left)
        width=int(rect_params.width)
        height=int(rect_params.height)
        # obj_name=pgie_classes_str[obj_meta.class_id]
        image=cv2.rectangle(image,(left,top),(left+width,top+height),(0,0,255,0),2)
        # Note that on some systems cv2.putText erroneously draws horizontal lines across the image
        # image=cv2.putText(image,obj_name+',C='+str(confidence),(left-10,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255,0),2)
        image=cv2.putText(image,'Face',(left-10,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255,0),2)
        return image


    def stream_to_flask(self):
        try:      
            while True:
                _, jpeg = cv2.imencode('.jpg', self.frame_to_stream)
                jpeg = jpeg.tobytes()
                    
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')
        except GeneratorExit:
            print('-----------browser disconnected---------')	


    def main(self):

        self.stream_path = '/dev/video0'
        # # Check input arguments
        # if len(args) != 2:
        #     sys.stderr.write("usage: %s <v4l2-device-path>\n" % args[0])
        #     sys.exit(1)

        # Standard GStreamer initialization
        GObject.threads_init()
        Gst.init(None)

        # Create gstreamer elements
        # Create Pipeline element that will form a connection of other elements
        print("Creating Pipeline \n ")
        pipeline = Gst.Pipeline()

        if not pipeline:
            sys.stderr.write(" Unable to create Pipeline \n")

        # Source element for reading from the file
        print("Creating Source \n ")
        source = Gst.ElementFactory.make("v4l2src", "usb-cam-source")
        if not source:
            sys.stderr.write(" Unable to create Source \n")

        caps_v4l2src = Gst.ElementFactory.make("capsfilter", "v4l2src_caps")
        if not caps_v4l2src:
            sys.stderr.write(" Unable to create v4l2src capsfilter \n")


        print("Creating Video Converter \n")

        # Adding videoconvert -> nvvideoconvert as not all
        # raw formats are supported by nvvideoconvert;
        # Say YUYV is unsupported - which is the common
        # raw format for many logi usb cams
        # In case we have a camera with raw format supported in
        # nvvideoconvert, GStreamer plugins' capability negotiation
        # shall be intelligent enough to reduce compute by
        # videoconvert doing passthrough (TODO we need to confirm this)


        # videoconvert to make sure a superset of raw formats are supported
        vidconvsrc = Gst.ElementFactory.make("videoconvert", "convertor_src1")
        if not vidconvsrc:
            sys.stderr.write(" Unable to create videoconvert \n")

        # nvvideoconvert to convert incoming raw buffers to NVMM Mem (NvBufSurface API)
        nvvidconvsrc = Gst.ElementFactory.make("nvvideoconvert", "convertor_src2")
        if not nvvidconvsrc:
            sys.stderr.write(" Unable to create Nvvideoconvert \n")

        caps_vidconvsrc = Gst.ElementFactory.make("capsfilter", "nvmm_caps")
        if not caps_vidconvsrc:
            sys.stderr.write(" Unable to create capsfilter \n")

        # Create nvstreammux instance to form batches from one or more sources.
        streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
        if not streammux:
            sys.stderr.write(" Unable to create NvStreamMux \n")

        # Use nvinfer to run inferencing on camera's output,
        # behaviour of inferencing is set through config file
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        if not pgie:
            sys.stderr.write(" Unable to create pgie \n")


        # Add nvvidconv1 and filter1 to convert the frames to RGBA
        # which is easier to work with in Python.
        print("Creating nvvidconv1 \n ")
        nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
        if not nvvidconv1:
            sys.stderr.write(" Unable to create nvvidconv1 \n")
        print("Creating filter1 \n ")
        caps1 = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
        filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
        if not filter1:
            sys.stderr.write(" Unable to get the caps filter1 \n")
        filter1.set_property("caps", caps1)



        # Use convertor to convert from NV12 to RGBA as required by nvosd
        nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
        if not nvvidconv:
            sys.stderr.write(" Unable to create nvvidconv \n")

        # Create OSD to draw on the converted RGBA buffer
        nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
        if not nvosd:
            sys.stderr.write(" Unable to create nvosd \n")

        # ==================== For RTSP ==========================

        nvvidconv_postosd = Gst.ElementFactory.make("nvvideoconvert", "convertor_postosd")
        if not nvvidconv_postosd:
            sys.stderr.write(" Unable to create nvvidconv_postosd \n")

        # Create a caps filter
        caps = Gst.ElementFactory.make("capsfilter", "filter")
        caps.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420"))

        # Make the encoder
        if self.codec == "H264":
            encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
            print("Creating H264 Encoder")
        elif self.codec == "H265":
            encoder = Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
            print("Creating H265 Encoder")
        if not encoder:
            sys.stderr.write(" Unable to create encoder")
            encoder.set_property('bitrate', self.bitrate)
        if is_aarch64():
            encoder.set_property('preset-level', 1)
            encoder.set_property('insert-sps-pps', 1)
            encoder.set_property('bufapi-version', 1)


        # Make the payload-encode video into RTP packets
        if self.codec == "H264":
            rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
            print("Creating H264 rtppay")
        elif self.codec == "H265":
            rtppay = Gst.ElementFactory.make("rtph265pay", "rtppay")
            print("Creating H265 rtppay")
        if not rtppay:
            sys.stderr.write(" Unable to create rtppay")

        # Make the UDP sink
        updsink_port_num = 5400
        sink = Gst.ElementFactory.make("udpsink", "udpsink")
        if not sink:
            sys.stderr.write(" Unable to create udpsink")


        # # Finally render the osd output
        # if is_aarch64():
        #     transform = Gst.ElementFactory.make("nvegltransform", "nvegl-transform")

        # print("Creating EGLSink \n")
        # sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
        # if not sink:
        #     sys.stderr.write(" Unable to create egl sink \n")

        sink.set_property('host', '224.224.255.255')
        sink.set_property('port', updsink_port_num)
        sink.set_property('async', False)
        sink.set_property('sync', 1)


        # print("Playing cam %s " %args[1])
        print("Playing cam %s " %self.stream_path)
        caps_v4l2src.set_property('caps', Gst.Caps.from_string("video/x-raw, framerate=30/1"))
        caps_vidconvsrc.set_property('caps', Gst.Caps.from_string("video/x-raw(memory:NVMM)"))
        # source.set_property('device', args[1])
        source.set_property('device', self.stream_path)
        streammux.set_property('width', 1920)
        streammux.set_property('height', 1080)
        streammux.set_property('batch-size', 1)
        streammux.set_property('batched-push-timeout', 4000000)
        # pgie.set_property('config-file-path', "dstest1_pgie_config.txt")
        pgie.set_property('config-file-path', "./facedetectir_pgie_config.txt")
        # Set sync = false to avoid late frame drops at the display-sink
        sink.set_property('sync', False)

        #===================================================
        print("Adding elements to Pipeline \n")
        pipeline.add(source)
        pipeline.add(caps_v4l2src)
        pipeline.add(vidconvsrc)
        pipeline.add(nvvidconvsrc)
        pipeline.add(caps_vidconvsrc)
        pipeline.add(streammux)
        pipeline.add(pgie)

        pipeline.add(nvvidconv1)
        pipeline.add(filter1)

        pipeline.add(nvvidconv)
        pipeline.add(nvosd)


        pipeline.add(nvvidconv_postosd)
        pipeline.add(caps)
        pipeline.add(encoder)
        pipeline.add(rtppay)
        pipeline.add(sink)


        # if is_aarch64():
        #     pipeline.add(transform)

        # we link the elements together
        # v4l2src -> nvvideoconvert -> mux -> 
        # nvinfer -> nvvideoconvert -> nvosd -> video-renderer
        print("Linking elements in the Pipeline \n")
        source.link(caps_v4l2src)
        caps_v4l2src.link(vidconvsrc)
        vidconvsrc.link(nvvidconvsrc)
        nvvidconvsrc.link(caps_vidconvsrc)

        sinkpad = streammux.get_request_pad("sink_0")
        if not sinkpad:
            sys.stderr.write(" Unable to get the sink pad of streammux \n")
        srcpad = caps_vidconvsrc.get_static_pad("src")
        if not srcpad:
            sys.stderr.write(" Unable to get source pad of caps_vidconvsrc \n")
        srcpad.link(sinkpad)
        streammux.link(pgie)

        # pgie.link(nvvidconv)
        pgie.link(nvvidconv1)
        nvvidconv1.link(filter1)
        filter1.link(nvvidconv)
        
        nvvidconv.link(nvosd)
        # if is_aarch64():
        #     nvosd.link(transform)
        #     transform.link(sink)
        # else:
        #     nvosd.link(sink)
        nvosd.link(nvvidconv_postosd)
        nvvidconv_postosd.link(caps)
        caps.link(encoder)
        encoder.link(rtppay)
        rtppay.link(sink)


        # create an event loop and feed gstreamer bus mesages to it
        loop = GObject.MainLoop()
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect ("message", bus_call, loop)

        rtsp_port_num = 8554

        server = GstRtspServer.RTSPServer.new()
        server.props.service = "%d" % rtsp_port_num
        server.attach(None)
        
        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch( "( udpsrc name=pay0 port=%d buffer-size=524288 caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 \" )" % (updsink_port_num, self.codec))
        factory.set_shared(True)
        server.get_mount_points().add_factory("/ds-test", factory)
        
        print("\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:%d/ds-test ***\n\n" % rtsp_port_num)


        # Lets add probe to get informed of the meta data generated, we add probe to
        # the sink pad of the osd element, since by that time, the buffer would have
        # had got all the metadata.
        osdsinkpad = nvosd.get_static_pad("sink")
        if not osdsinkpad:
            sys.stderr.write(" Unable to get sink pad of nvosd \n")

        osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, self.osd_sink_pad_buffer_probe, 0)

        # start play back and listen to events
        print("Starting pipeline \n")
        pipeline.set_state(Gst.State.PLAYING)
        try:
            loop.run()
        except:
            pass
        # cleanup
        pipeline.set_state(Gst.State.NULL)

    # def parse_args():
    #     parser = argparse.ArgumentParser(description='RTSP Output Sample Application Help ')
    #     parser.add_argument("-i", "--input", default="/dev/video0",
    #                 help="webcam", required=False)
    #     parser.add_argument("-c", "--codec", default="H264",
    #                 help="RTSP Streaming Codec H264/H265 , default=H264", choices=['H264','H265'])
    #     parser.add_argument("-b", "--bitrate", default=1000000,
    #                 help="Set the encoding bitrate ", type=int)
    #     # Check input arguments
    #     #if len(sys.argv)==1:
    #     #    parser.print_help(sys.stderr)
    #     #    sys.exit(1)
    #     args = parser.parse_args()
    #     global codec
    #     global bitrate
    #     global stream_path
    #     codec = args.codec
    #     bitrate = args.bitrate
    #     stream_path = args.input
    #     return 0

if __name__ == '__main__':
    # parse_args()
    # sys.exit(main(sys.argv))
    pass

