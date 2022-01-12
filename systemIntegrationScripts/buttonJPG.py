import RPi.GPIO as GPIO
import os
import time

def jpgButton_callback(channel):
    print("Capturing JPG photo...")
    os.system("python JPGtoEmail.py")
    
def dngButton_callback(channel):
    print("Capturing DNG photo...")
    os.system("python DNGtoEmail.py")
    
def powerOffButton_callback(channel):
    os.system("python3 lightsOff.py")
    time.sleep(1)
    os.system("python3 oledClear.py")
    time.sleep(1)
    os.system("sudo shutdown -h now")
    
def take_photo(channel):
    # time.sleep(1)
    os.system("python3 lights.py")
    time.sleep(1)
    print("lights on")
    os.system("python3 10HiResPhotos.py")
    os.system("python3 lightsOff.py")
    os.system("python3 oledClear.py")
    #print("measurement completed")
    
def do_measurement(channel):
    os.system("python3 lightsOff.py")
    print("lights off")
    os.system("python3 streamLinedDensitometry.py")
    time.sleep(5)
    os.system("python3 oledClear.py")

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#GPIO.add_event_detect(10, GPIO.RISING, callback= jpgButton_callback, bouncetime = 20000) # Setup event on pin 10 rising edge
#GPIO.add_event_detect(11, GPIO.RISING, callback= dngButton_callback, bouncetime = 20000)

#power off red button event
GPIO.add_event_detect(13, GPIO.FALLING, callback= powerOffButton_callback, bouncetime = 10000)

#take jpg photo on yellow button event
GPIO.add_event_detect(11, GPIO.FALLING, callback= do_measurement, bouncetime = 10000) 

#densitometry blue button event
GPIO.add_event_detect(10, GPIO.FALLING, callback= take_photo, bouncetime = 10000)


message = input("Press enter to quit\n\n")
  
GPIO.cleanup() # Clean up