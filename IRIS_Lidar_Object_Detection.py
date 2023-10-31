import RPi.GPIO as GPIO
import serial
import time
import cv2
import torch
from gtts import gTTS
import os

# this will load object detection model 
model = torch.load("")

# this will initialize the LiDAR sensor
button_pin = 22
sensor_serial = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=1)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
collecting_data = False

# this will set camera configuration for decent video quality and narrow FOV
camera = cv2.VideoCapture(0)
camera.set(3, 1280)  # Width (720p resolution)
camera.set(4, 720)   # Height (720p resolution)
camera.set(cv2.CAP_PROP_FPS, 30)  # Frame rate

# this will define the central region dimensions
central_width = 320 
central_height = 720
central_x = (1280 - central_width) // 2  

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
    try:
        while True:
            ret, frame = camera.read()  # this will read a frame from the camera

            # this will crop the central region
            cropped_frame = frame[;, central_x:central_x + central_width]

            # this will perform object detection on the cropped frame
            results = model(cropped_frame)

            for result in results.xyxy[0].cpu().numpy():
                class_id = int(result[5])
                class_label = model.names[class_id]
                if 1.5 <= distance <= 3.0:  # this will filter objects within 1.5-3.0 meters
                    print(f"Detected {class_label} at {distance} meters")
                    play_audio_message(class_label, distance)

            cv2.imshow("Object Detection", cropped_frame)  # this will display the video frame
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
    except Exception as e:
        print(f"Error in detect_and_play_audio: {e}")
    finally:
        camera.release()
        cv2.destroyAllWindows()

def play_audio_message(class_label, distance):
    try:
        # this will generate the audio message
        message = f"A {class_label} is {distance} meters away."

        # this will use Google Text-to-Speech to generate audio from the message
        tts = gTTS(text=message, lang='en')
        tts.save("temp_audio.mp3")  # this will save the generated audio to a temporary file

        # this will play the generated audio using the mpg123 player
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
