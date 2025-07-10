"""
URL configuration for FaceRecogSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recognition/', include('recognition.urls')),
]
"""

from django.contrib import admin
from django.urls import path, include
from recognition.views import * 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),  
    path('recognition/', include('recognition.urls')),  
    path('registrations/',registrations , name= 'Register'),
    path('attendance', attendance, name= 'attendance'),
    
    path('recognition/', include('recognition.urls')),
    path('register_student', register_student, name= 'register_student'),
    path('recognize_face/', recognize_face, name='recognize_face'),
    path('upload_attendance/',upload_attendance,name='upload_attendance'),
    path('presentees/',presentees, name='presentees'),
    path('get_presentees/',get_presentees, name='get_presentees'),
]
