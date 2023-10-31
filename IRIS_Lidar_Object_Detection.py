import RPi.GPIO as GPIO
import serial
import time
import cv2
import torch
from gtts import gTTS
import os

# this will load the object detection model
model = torch.load("")

# this will initialize the lidar sensor
button_pin = 22
sensor_serial = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
collecting_data = False

def collect_data():
    global collecting_data
    try:
        while collecting_data:
            data = sensor_serial.readline().decode("utf-8").strip()
            if data:
                print("LiDAR Data:", data)
                distance = float(data) / 100  # this will convert LiDAR data to meters
                detect_and_play_audio(distance)
    except Exception as e:
        print(f"Error in collect_data: {e}")
    finally:
        sensor_serial.close()

def detect_and_play_audio(distance):
    cap = cv2.VideoCapture(0)  # this will initialize the camera

    try:
        while True:
            ret, frame = cap.read()  # this will read a frame from the camera

            if not ret:
                break

            # this will perform object detection using YOLOv8
            results = model(frame)

            for result in results.xyxy[0].cpu().numpy():
                class_id = int(result[5])
                class_label = model.names[class_id]
                if 1.0 <= distance <= 2.0:  # Filter objects within 1-2 meters
                    print(f"Detected {class_label} at {distance} meters")
                    play_audio_message(class_label, distance)

            cv2.imshow("Object Detection", frame)  # Display the video frame
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
    except Exception as e:
        print(f"Error in detect_and_play_audio: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def play_audio_message(class_label, distance):
    try:
        # this will generate the audio message
        message = f"A {class_label} is {distance} meters away."

        # this will use google text to speech to generate audio from the message
        tts = gTTS(text=message, lang='en')
        tts.save("temp_audio.mp3")  # this will save the generated audio to a temporary file

        # this will play the generated audio using mpg123 player.
        os.system("mpg123 temp_audio.mp3")
    except Exception as e:
        print(f"Error in play_audio_message: {e}")

try:
    while True:
        button_state = GPIO.input(button_pin)
        if not collecting_data and button_state == GPIO.LOW:
            print("Data collection started.")
            collecting_data = True
            collect_data()
        elif collecting_data and button_state == GPIO.LOW:
            print("Data collection stopped.")
            collecting_data = False
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting the program")
finally:
    GPIO.cleanup()
