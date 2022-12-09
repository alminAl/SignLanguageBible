from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from .camera import VideoCamera
from django.views.decorators import gzip
# Create your views here.


def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def index(request):
	return render(request, 'home/index.html')




def video_feed(request):
	cam =VideoCamera()
	return StreamingHttpResponse(gen(cam),
					content_type='multipart/x-mixed-replace; boundary=frame')