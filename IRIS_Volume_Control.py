import RPi.GPIO as GPIO
import alsaaudio

mixer = alsaaudio.Mixer()

#this sets the volume button pins
VOLUME_UP_PIN = 17
VOLUME_DOWN_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(VOLUME_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(VOLUME_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# everytime we press the volume button the volume will be increased or decreaded by 5 
VOLUME_STEP = 5
# function to increase volume
def increase_volume(channel):
    current_volume = mixer.getvolume()[0]
    new_volume = min(100, current_volume + VOLUME_STEP)
    mixer.setvolume(new_volume)
# function to decrease volume
def decrease_volume(channel):
    current_volume = mixer.getvolume()[0]
    new_volume = max(0, current_volume - VOLUME_STEP)
    mixer.setvolume(new_volume)
GPIO.add_event_detect(VOLUME_UP_PIN, GPIO.FALLING, callback=increase_volume, bouncetime=200)

GPIO.add_event_detect(VOLUME_DOWN_PIN, GPIO.FALLING, callback=decrease_volume, bouncetime=200)
try:
    while True:
        pass
except KeyboardInterrupt:
    GPIO.cleanup()
