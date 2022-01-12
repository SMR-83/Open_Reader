from picamera import PiCamera
import picamera.array
import cv2
import numpy as np
import time
import os
import shutil
import io
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import board
# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 5

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)


# Clear display.
oled.fill(0)
oled.show()

def grab_contours(cnts):
    # if the length the contours tuple returned by cv2.findContours
    # is '2' then we are using either OpenCV v2.4, v4-beta, or
    # v4-official
    if len(cnts) == 2:
        cnts = cnts[0]

    # if the length of the contours tuple is '3' then we are using
    # either OpenCV v3, v4-pre, or v4-alpha
    elif len(cnts) == 3:
        cnts = cnts[1]

    # otherwise OpenCV has changed their cv2.findContours return
    # signature yet again and I have no idea WTH is going on
    else:
        raise Exception(("Contours tuple must have length 2 or 3, "
            "otherwise OpenCV changed their cv2.findContours return "
            "signature yet again. Refer to OpenCV's documentation "
            "in that case"))

    # return the actual contours array
    return cnts

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    #valCount = valCount+1
    # return the warped image
    #time.sleep(1)
    return warped



#make a directory to hold files with measurements, if it already exists, delete it and remake

dirPath = ("/home/pi/Desktop/")

#if os.path.exists(dirPath):
#    shutil.rmtree(dirPath)
#os.makedirs(dirPath)

# Create the in-memory stream
stream = io.BytesIO()
with picamera.PiCamera() as camera:
    camera.start_preview()
    camera.capture(stream, format='jpeg')

# Construct a numpy array from the stream
data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
# "Decode" the image from the array, preserving colour
image = cv2.imdecode(data, 1)

#image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#image = cv2.imread("/home/pi/Desktop/fileTypeExperiment/original.jpg", cv2.IMREAD_UNCHANGED)
#image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

image = cv2.resize(image, dsize=(820, 616))
R,G,B = cv2.split(image)

#cv2.imshow("image", image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

orig = G.copy()

#orig = image.copy()
#dsize = (500, 500)
#orig = cv2.resize(orig, dsize)
#cv2.imshow("orig", orig)

edges = cv2.Canny(orig, 100, 200)
#cv2.imshow("edges", edges)

cnts = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
# loop over the contours
for c in cnts:
    # approximate the contour
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    # if our approximated contour has four points, then we
    # can assume that we have found our screen
    if len(approx) == 4:     
        screenCnt = approx
        cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
        print("photo captured")
        squareImage = four_point_transform(orig, screenCnt.reshape(4, 2))# * ratio)
        #cv2.imshow("square", squareImage)
        isImage = True

        if isImage == True:
            #cv2.imwrite(dirPath + "/blank.jpg", squareImage)
            cv2.imwrite(dirPath + "/blank.jpg", image)            
                    
            OLEDimage = Image.new("1", (oled.width, oled.height))
            # Get drawing object to draw on image.
            draw = ImageDraw.Draw(OLEDimage)

            # Draw a white background
            draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
            # Draw a smaller inner rectangle
            draw.rectangle((BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),outline=0,fill=0)
            # Load default font.
            font = ImageFont.load_default()
            # Draw Some Text
            text = ("Photo Captured")
            (font_width, font_height) = font.getsize(text)
            draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),text,font=font,fill=255)
           # Display image
            oled.image(OLEDimage)
            oled.show()
            
            #camera.close
            break
    else:
        print("check lights and alignment")
        
                
        OLEDimage = Image.new("1", (oled.width, oled.height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(OLEDimage)

        # Draw a white background
        draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

        # Draw a smaller inner rectangle
        draw.rectangle((BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),outline=0,fill=0)

        # Load default font.
        font = ImageFont.load_default()

        # Draw Some Text
        text = ("Check Alignment")
        (font_width, font_height) = font.getsize(text)
    
        draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),text,font=font,fill=255)

        # Display image
        oled.image(OLEDimage)
        oled.show()
        
        cv2.imwrite(dirPath + "/nope.jpg", image)
        #camera.close
        break

    
