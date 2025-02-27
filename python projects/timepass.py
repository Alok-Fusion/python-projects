import cv2
import numpy as np
import time
from deepface import DeepFace
from scipy.signal import find_peaks

# Global variables for heart rate estimation
heart_rates = []
blink_rate = 0
stress_score = 0
quiz_score = 0

# Load the Haar Cascade Classifiers for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Depression and Stress Questionnaire (Expanded)
questions = [
    "Do you feel tired or exhausted most of the time? (yes/no): ",
    "Do you experience frequent headaches or body pain? (yes/no): ",
    "Do you feel isolated or lonely often? (yes/no): ",
    "Do you have trouble concentrating on tasks? (yes/no): ",
    "Do you experience frequent mood swings? (yes/no): ",
    "Do you feel nervous or anxious most of the time? (yes/no): ",
    "Do you have difficulty falling asleep or staying asleep? (yes/no): ",
    "Do you feel a lack of motivation to do daily activities? (yes/no): "
]

def capture_image_and_analyze():
    global blink_rate, stress_score, quiz_score
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the camera")
        return

    print("The system will capture an image automatically in 5 seconds...")
    
    # Countdown for 5 seconds before capturing image
    for i in range(5, 0, -1):
        print(f"Capturing in {i} seconds...")
        time.sleep(1)

    blink_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        blink_detected = False

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) == 0:
                blink_detected = True

        if blink_detected:
            blink_count += 1

        cv2.imshow("Press 's' to analyze", frame)

        # Automatically capture after countdown (after 5 seconds)
        if time.time() - start_time >= 5:  # Automatically after 5 seconds
            cv2.imwrite("captured_face.jpg", frame)
            print("Image captured as 'captured_face.jpg'")

            # Analyze face emotions only if a face is detected
            if len(faces) == 0:
                print("No face detected in the captured image.")
                continue

            try:
                # Set enforce_detection=False to allow analysis even if face is not detected
                analysis = DeepFace.analyze("captured_face.jpg", actions=['emotion'], enforce_detection=False)
                emotion = analysis[0]['dominant_emotion']
                print(f"Detected Emotion: {emotion}")

                # Stress score from facial emotion
                stress_score = {
                    "happy": 1, "neutral": 3, "sad": 5, "fear": 5,
                    "angry": 4, "disgust": 4, "surprise": 2
                }.get(emotion, 3)

                # Calculate blink rate per minute
                elapsed_time = time.time() - start_time
                blink_rate = (blink_count / elapsed_time) * 60
                print(f"Blink Rate: {blink_rate:.2f} blinks/min")

                # Estimate heart rate using the camera
                capture_video_for_heart_rate()

                # Automated stress level based on combined results
                if heart_rates:  # Ensure heart_rates is not empty before accessing
                    final_result = evaluate_stress(stress_score, blink_rate, heart_rates[-1], quiz_score)
                    print("\n🔹 Final Mental Health Assessment:")
                    print(final_result)

                    # Display results on the captured image
                    cv2.putText(frame, f"Emotion: {emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Heart Rate: {heart_rates[-1]:.2f} BPM", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    cv2.putText(frame, final_result, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow("Result", frame)

                    # Save the image with results
                    cv2.imwrite("mood_assessment.jpg", frame)
                    print("Results saved as 'mood_assessment.jpg'")

                    cv2.waitKey(5000)
                    break
                else:
                    print("Heart rate data is missing, unable to evaluate final assessment.")
                    break

            except Exception as e:
                print(f"Error in face analysis: {e}")
                break

        elif cv2.waitKey(1) & 0xFF == ord('q'):  
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

def capture_video_for_heart_rate():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the camera")
        return

    heart_rate_signal = []
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_region = frame[y:y+h, x:x+w]  # Extract the face region

            # Calculate the average color in the face region
            avg_color = np.mean(face_region, axis=(0, 1))  # Get average RGB values
            avg_color_intensity = np.mean(avg_color)  # Get intensity (brightness)

            # Append the intensity to the heart rate signal
            heart_rate_signal.append(avg_color_intensity)

            # Show the frame with a rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Heart Rate Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):  
            print("Capturing video for heart rate estimation...")
            break
        elif key == ord('q'):  
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

    # After video capture, process the heart rate signal
    calculate_heart_rate(heart_rate_signal, start_time)

def calculate_heart_rate(heart_rate_signal, start_time):
    if len(heart_rate_signal) < 2:
        print("Not enough data to estimate heart rate.")
        return

    heart_rate_signal = np.array(heart_rate_signal) - np.mean(heart_rate_signal)
    peaks, _ = find_peaks(heart_rate_signal, distance=30)  # Find peaks (each corresponds to a heartbeat)

    num_peaks = len(peaks)
    elapsed_time = time.time() - start_time  # Total time in seconds
    heart_rate = (num_peaks / elapsed_time) * 60  # Convert to BPM (beats per minute)

    print(f"Estimated Heart Rate: {heart_rate:.2f} BPM")
    heart_rates.append(heart_rate)

def ask_questions():
    global quiz_score
    score = 0
    for question in questions:
        answer = input(question).strip().lower()
        if answer == "yes":
            score += 1
    quiz_score = score
    return score

def evaluate_stress(face_score, blink_rate, heart_rate, quiz_score):
    total_score = face_score + quiz_score

    if blink_rate > 15:  # High blink rate indicates stress
        total_score += 2
    if heart_rate > 90:  # High heart rate indicates stress
        total_score += 2

    if total_score <= 4:
        return "✅ Low Stress: Keep up your healthy habits!"
    elif total_score <= 7:
        return "⚠️ Moderate Stress: Try yoga, breathing exercises, and relaxing music."
    else:
        return "🚨 High Stress/Depression Detected: Seek professional help or therapy."

# Run the enhanced system
capture_image_and_analyze()

# After image is captured, ask the questions
print("Now, let's ask a few questions to assess your mental health.")
quiz_score = ask_questions()

# The final evaluation based on facial expression, blink rate, heart rate, and quiz score
if heart_rates:  # Ensure heart_rates is not empty before accessing
    final_assessment = evaluate_stress(face_score=stress_score, blink_rate=blink_rate, heart_rate=heart_rates[-1], quiz_score=quiz_score)
    print(f"\n🔹 Final Mental Health Assessment based on questionnaire:")
    print(final_assessment)
else:
    print("Heart rate data is missing, unable to perform final assessment.")
