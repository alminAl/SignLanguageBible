from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('prediction', views.prediction, name='prediction'),
    # path('mask_feed', views.mask_feed, name='mask_feed'),
	# path('livecam_feed', views.livecam_feed, name='livecam_feed'),
    ]
