from onvif import ONVIFCamera
import time

class onvif_ptz:
    
    def __init__(self,IP,PORT,USER,PASS,wsdl_dir = "/works/webrtc_camera_control/python-onvif-zeep/wsdl/"):

        self.active = False
        mycam = ONVIFCamera(IP, PORT, USER, PASS, wsdl_dir = wsdl_dir)
        # Create media service object
        media = mycam.create_media_service()
        
        # Create ptz service object
        self.ptz = mycam.create_ptz_service()

        # Get target profile11
        self.media_profile = media.GetProfiles()[0]

        # Get PTZ configuration options for getting continuous move range
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        self.positionrequest = self.ptz.create_type('ContinuousMove')
        self.positionrequest.ProfileToken = self.media_profile.token
        if self.positionrequest.Velocity is None:

            self.positionrequest.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            self.positionrequest.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
            self.positionrequest.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

        self.homerequest = self.ptz.create_type('AbsoluteMove')
        self.homerequest.ProfileToken = self.media_profile.token
        if self.homerequest.Position is None :
            self.homerequest.Position = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            self.homerequest.Position.PanTilt.space = ptz_configuration_options.Spaces.AbsolutePanTiltPositionSpace[0].URI
            self.homerequest.Position.Zoom.space = ptz_configuration_options.Spaces.AbsoluteZoomPositionSpace[0].URI

        # Get range of pan and tilt
        # NOTE: X and Y are velocity vector
        self.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
        self.ZMAX = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Max
        self.ZMIN = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Min


    def do_move(self,ptz, request):
        # Start continuous move
        if self.active:
            self.ptz.Stop({'ProfileToken': request.ProfileToken})
        self.active = True
        self.ptz.ContinuousMove(request)

    def do_move_home(self,ptz, request):
        # Start continuous move
        if self.active:
            self.ptz.Stop({'ProfileToken': request.ProfileToken})
        self.active = True
        self.ptz.AbsoluteMove(request)

    def move_up(self,ptz, request):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = self.YMAX
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))

    def move_down(self,ptz, request):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = self.YMIN
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))

    def move_right(self,ptz, request):
        request.Velocity.PanTilt.x = self.XMAX
        request.Velocity.PanTilt.y = 0
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))

    def move_left(self,ptz, request):
        request.Velocity.PanTilt.x = self.XMIN
        request.Velocity.PanTilt.y = 0
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))
        

    def move_upleft(self,ptz, request):
        request.Velocity.PanTilt.x = self.XMIN
        request.Velocity.PanTilt.y = self.YMAX
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))
        
    def move_upright(self,ptz, request):
        request.Velocity.PanTilt.x = self.XMAX
        request.Velocity.PanTilt.y = self.YMAX
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))
        
    def move_downleft(self,ptz, request):
        request.Velocity.PanTilt.x = self.XMIN
        request.Velocity.PanTilt.y = self.YMIN
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))
        
    def move_downright(self,ptz, request):
        request.Velocity.PanTilt.x = self.XMAX
        request.Velocity.PanTilt.y = self.YMIN
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))

    def move_home(self,ptz, request):
        request.Position.PanTilt.x = 1
        request.Position.PanTilt.y = 0
        request.Position.Zoom = 0
        self.do_move_home(ptz,request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))

    def Zoom_in(self,ptz,request):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 0
        request.Velocity.Zoom.x = self.ZMAX
        self.do_move(ptz, request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))

    def Zoom_out(self,ptz,request):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 0
        request.Velocity.Zoom.x = self.ZMIN
        self.do_move(ptz,request)
        print("x = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['x']))
        print("y = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['PanTilt']['y']))
        print("z = {}".format(ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position['Zoom']['x']))

        