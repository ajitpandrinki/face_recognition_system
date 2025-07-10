

# Create your models here.
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=10, unique=True)
    face_encoding = models.JSONField(null=True, blank=True)  # Stores list of face encodings




def __str__(self):
    return f"{self.name} ({self.roll_number})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[("Present", "Present"), ("Absent", "Absent")],
        default="Absent"
    )

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"