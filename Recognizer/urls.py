from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_student, name='register_student'),
    path('registrations',registrations, name= 'Register'),
    path('attendance', attendance, name= 'attendance'),
    path('recognize_face/', recognize_face, name='recognize_face'),
    path('upload_attendance/',upload_attendance,name='upload_attendance'),
    path('presentees/',presentees, name='presentees'),
    path('get_presentees/',get_presentees, name='get_presentees'),
]



