from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Student, Attendance
from datetime import datetime
from django.shortcuts import render
import os
import face_recognition
import cv2
import numpy as np
from PIL import Image
from django.shortcuts import get_object_or_404



STUDENT_IMAGE_PATH = 'media/student/'

@csrf_exempt
def register_student(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            roll_number = data.get('roll_number')

            if not name or not roll_number:
                return JsonResponse({'error': 'Missing name or roll number'}, status=400)

            student_path = os.path.join(STUDENT_IMAGE_PATH, roll_number)
            os.makedirs(student_path, exist_ok=True)

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return JsonResponse({'error': 'Failed to open camera'}, status=500)

            all_encodings = []
            saved_images = []
            images_captured = 0

            while images_captured < 5:
                ret, frame = cap.read()
                if not ret:
                    continue

                rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_img)

                if encodings:
                    all_encodings.append(encodings[0])  # Store face encoding
                    img_path = os.path.join(student_path, f"{images_captured+1}.jpg")
                    cv2.imwrite(img_path, frame)  # Save original image
                    saved_images.append(img_path)
                    images_captured += 1

            cap.release()
            cv2.destroyAllWindows()

            if len(all_encodings) == 5:
                avg_encoding = np.mean(all_encodings, axis=0).tolist()  # Compute average encoding

                student, created = Student.objects.get_or_create(
                    roll_number=roll_number,
                    defaults={'name': name, 'face_encoding': avg_encoding}
                )

                if not created:
                    return JsonResponse({'error': 'Student already registered'}, status=400)

                return JsonResponse({
                    'message': 'Student Registered Successfully!',
                    'photos_saved_at': saved_images,
                    'reset_form': True
                })

            else:
                return JsonResponse({'error': 'No face detected in enough images'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


known_encodings = []
known_roll_numbers = []

# Store known encodings
def load_known_faces():
    """
    Loads all student face encodings from the database.
    """
    global known_encodings, known_roll_numbers
    known_encodings.clear()
    known_roll_numbers.clear()

    students = Student.objects.all()  # Fetch all students from DB
    for student in students:
        if not student.face_encoding:
            print(f"⚠️ Skipping {student.roll_number}: No encoding found.")
            continue  # Skip students without encodings

        try:
            # Convert JSON string to list if stored as string
            encoding = json.loads(student.face_encoding) if isinstance(student.face_encoding, str) else student.face_encoding
            encoding = np.array(encoding, dtype=np.float32)

            # Ensure encoding has the correct shape (128,)
            if encoding.shape == (128,):
                known_encodings.append(encoding)
                known_roll_numbers.append(student.roll_number)
            else:
                print(f"⚠️ Skipping {student.roll_number}: Invalid encoding shape {encoding.shape}")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Error decoding face encoding for {student.roll_number}: {e}")
            continue  # Skip the student if decoding fails

    print(f"✅ Loaded {len(known_encodings)} valid face encodings from database.")

    return known_encodings, known_roll_numbers  # Always return lists (never None)
    
from django.conf import settings


def recognize_face(request):
    """
    Uploads an image, detects faces, and marks attendance.
    """
    if request.method == "POST" and request.FILES.get("image"):
        print(f"Received file: {request.FILES.get('image')}")

        try:
            # Load uploaded image
            image_file = request.FILES["image"]
            img = Image.open(image_file).convert("RGB")  # Convert to RGB
            img_array = np.array(img)

            # Detect faces and extract encodings
            face_locations = face_recognition.face_locations(img_array)
            print(f"Detected face locations: {face_locations}")

            face_encodings1 = []
            face_encodings1 = face_recognition.face_encodings(img_array, face_locations)
            print("face Encodings:",face_encodings1)

            if not face_encodings1:
                return JsonResponse({"error": "No faces detected"}, status=400)

            # Load known student encodings
            known_encodings, known_roll_numbers = load_known_faces()
            print(f"Loaded {len(known_encodings)} known faces")

            matched_students = []

            # Compare detected faces with known encodings
            threshold = 0.6  # Distance threshold for matching
            for face_encoding in face_encodings1:
                distances = np.linalg.norm(known_encodings - face_encoding, axis=1)
                best_match_index = np.argmin(distances) if len(distances) > 0 else None

                if best_match_index is not None and distances[best_match_index] < threshold:
                    roll_number = known_roll_numbers[best_match_index]

                    if roll_number not in matched_students:
                        student = get_object_or_404(Student, roll_number=roll_number)
                        Attendance.objects.get_or_create(student=student, status="Present")
                        matched_students.append(roll_number)
            print(f"Distances: {distances}")
            print(f"Best match index: {best_match_index}")

            print(">>>>>>>>>>>>>>>>>>>",matched_students)
            if matched_students:
                return JsonResponse({
                    "message": "Attendance marked successfully!",
                    "present_students": matched_students
                })
            else:
                return JsonResponse({"error": "No matching students found"}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({"error": "No image file provided"}, status=400)







def upload_attendance(request):
    """
    Uploads an image, detects faces, and marks attendance.
    """
    if request.method == "POST" and request.FILES.get("image"):
        try:
            # Load uploaded image
            image_file = request.FILES["image"]
            img = Image.open(image_file).convert("RGB")  # Convert to RGB
            img_array = np.array(img)

            # Detect faces and extract encodings
            face_locations = face_recognition.face_locations(img_array)
            face_encodings = face_recognition.face_encodings(img_array, face_locations)

            if not face_encodings:
                return JsonResponse({"error": "No faces detected"}, status=400)

            # Load known student encodings
            known_encodings, known_roll_numbers = load_known_faces()

            matched_students = []

            # Compare detected faces with known encodings
            threshold = 0.6  # Distance threshold for matching
            for face_encoding in face_encodings:
                distances = np.linalg.norm(known_encodings - face_encoding, axis=1)
                best_match_index = np.argmin(distances) if len(distances) > 0 else None

                if best_match_index is not None and distances[best_match_index] < threshold:
                    roll_number = known_roll_numbers[best_match_index]

                    if roll_number not in matched_students:
                        student = get_object_or_404(Student, roll_number=roll_number)
                        Attendance.objects.get_or_create(student=student, status="Present")
                        matched_students.append(roll_number)

            if matched_students:
                return JsonResponse({
                    "message": "Attendance marked successfully!",
                    "present_students": matched_students
                })
            else:
                return JsonResponse({"error": "No matching students found"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "No image file provided"}, status=400)


def index(request):
    return render(request, "index.html")


def registrations(request):
    return render(request, "registration.html")


def attendance(request):
    return render(request, "attendance.html")

def presentees(request):
    return render(request, 'presentees.html')

def get_presentees(request):
    """Return JSON data of presentees (Roll Number + Name) for AJAX request."""
    present_students = Attendance.objects.filter(status="Present").values_list('student__roll_number', 'student__name')
    presentees_list = [{"roll_number": roll, "name": name} for roll, name in present_students]
    
    return JsonResponse({"presentees": presentees_list})
