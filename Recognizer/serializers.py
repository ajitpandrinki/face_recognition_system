from rest_framework import serializers
from .models import Student, Attendance

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'roll_number', 'photo']

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'date', 'time']