from imutils.video import VideoStream
import cv2
import imutils
import time
import RPi.GPIO as GPIO
from time import sleep

greenLower = (29, 86, 6)
redLower = (150,150,0)
greenUpper = (64,255, 255)
redUpper = (180,255,255)

delay = 0.1

power_saver_flag = 0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

def smallRight():
    GPIO.output(17, GPIO.HIGH)
    sleep(delay)
    GPIO.output(17, GPIO.LOW)
def smallLeft():
    GPIO.output(27, GPIO.HIGH)
    sleep(delay)
    GPIO.output(27, GPIO.LOW)
def straight():
    GPIO.output(27, GPIO.HIGH)
    GPIO.output(17, GPIO.HIGH)
    sleep(delay)
    GPIO.output(27, GPIO.LOW)
    GPIO.output(17, GPIO.LOW)
def bigRight():
    GPIO.output(17, GPIO.HIGH)
    sleep(delay*1.5)
    GPIO.output(17, GPIO.LOW)
def bigLeft():
    GPIO.output(27,GPIO.HIGH)
    sleep(delay*1.5)
    GPIO.output(27,GPIO.LOW)
def shutdown():
    quit()

vs = VideoStream(src=0).start()

time.sleep(2.0)

while True:
    frame = vs.read()

    if frame is None:
        break

    frame = imutils.resize(frame, width=400)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    center = None

    mask1 = cv2.inRange(hsv, redLower, redUpper)
    mask1 = cv2.erode(mask1, None, iterations=2)
    mask1 = cv2.dilate(mask1, None, iterations=2)

    cnts1 = cv2.findContours(mask1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts1 = cnts1[0] if imutils.is_cv2() else cnts1[1]
    center1 = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        power_saver_flag = 0
        if radius> 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,0,255), -1)
            if(radius<100):
                if(x>275):
                    smallRight()
                elif(x<125):
                    smallLeft()
                else:
                    straight()
            else:
                if len(cnts1) > 0:
                    c = max(cnts1, key=cv2.contourArea)
                    ((x1, y1), radius1) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center1 = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                    if radius1> 10:
                        cv2.circle(frame, (int(x1), int(y1)), int(radius1), (255,0,255), 2)
                        cv2.circle(frame, center1, 5, (0,0,255), -1)
                        if(radius1<200):
                            if(x1>275):
                                smallRight()
                            elif(x1<125):
                                smallLeft()
                            else:
                                straight()
                        else:
                            print("GOAL!!!!!")
                            break
                        print("GATE radius: ",round(radius1,2) , " -- Position: ", int(x1), int(y1))
                else:
                    bigLeft()
            print("BALL radius: ",round(radius,2) , " -- Position: ", int(x), int(y))
    else:
        bigRight()
        power_saver_flag = power_saver_flag + 1
        if power_saver_flag > 240:
            shutdown()

    cv2.imshow("Footballist Vision - Roboman", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

vs.stop()
cv2.destroyAllWindows()
