import time
import cv2
import numpy as np
import os.path
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

warpedMat = cv2.imread("/home/pi/Desktop/boxProjectExtras/1Sqr.jpg", cv2.IMREAD_UNCHANGED)
#warpedMat = cv2.imread("/home/pi/Desktop/photoSets/compositeLight/spots/largeCircle0.jpg", cv2.IMREAD_UNCHANGED)

try:   
    heightCrop =warpedMat.shape[0]
    widthCrop = warpedMat.shape[1]
    #densitometerMat =warpedMat[150:heightCrop-150, 150:widthCrop-150]
    
    dsize = (500, 500)
    densitometerMat = cv2.resize(warpedMat, dsize)
    #densitometerMat =densitometerMat[5:heightCrop-5, 5:widthCrop-5]
   
    #cv2.imwrite("/home/pi/Desktop/resize1.jpg", densitometerMat)
    patch1 = cv2.getRectSubPix(densitometerMat, (5,5), (50, heightCrop - 50))
    patch2 = cv2.getRectSubPix(densitometerMat, (5,5), (widthCrop - 50, 50))
    patch3 = cv2.getRectSubPix(densitometerMat, (5,5), (widthCrop - 50, heightCrop - 50))
    patch4 = cv2.getRectSubPix(densitometerMat, (5,5), (50, 50))
                      
    shadow1= np.sum(patch1)/25
    shadow2= np.sum(patch2)/25
    shadow3= np.sum(patch3)/25
    shadow4= np.sum(patch4)/25
            
    backgroundAverage = (shadow1 + shadow2 + shadow3 + shadow4)/4
    #print(backgroundAverage)
    #print (shadow1)
    #print(shadow2)
    #print(shadow3)
    #print(shadow4)
    #densitometerMat = cv2.GaussianBlur(densitometerMat,(3,3),1)
    #cv2.imshow("blur", densitometerMat)
    #cv2.imwrite("/home/pi/Desktop/blur.jpg", densitometerMat)
    mask = densitometerMat.copy()
    maskCropHeight =mask.shape[0]
    maskCropWidth = mask.shape[1]
    mask =mask[100:maskCropHeight-100, 100:maskCropWidth-100]    
    densitometerMat = densitometerMat[100:maskCropHeight-100, 100:maskCropWidth-100]
    #cv2.imwrite("/home/pi/Desktop/closeCrop.jpg", densitometerMat)
    th, thresh = cv2.threshold(densitometerMat,backgroundAverage-8, 255, cv2.THRESH_TOZERO)
    #cv2.imshow("threshed", thresh)
    #cv2.imwrite("/home/pi/Desktop/thresh1.jpg", thresh)
    mask = cv2.bitwise_not(thresh)
    #cv2.imshow("notMask", mask)
    #cv2.imwrite("/home/pi/Desktop/invert.jpg", mask)
    th, mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY) 
    #cv2.imshow("binaryMask", mask)
    #cv2.imwrite("/home/pi/Desktop/binaryMask.jpg", mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    mask = cv2.erode(mask, kernel, iterations=15)
    #cv2.imwrite("/home/pi/Desktop/refine.jpg", mask)
    #mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel, iterations=3)
    #cv2.imshow("erodedMask", mask)
    #cv2.imwrite("/home/pi/Desktop/openCVMask.jpg", mask)
    final = cv2.bitwise_and(densitometerMat, mask, mask=mask)
    #cv2.imwrite("/home/pi/Desktop/overlayjpg", final)
    signalPixels = cv2.countNonZero(final)
    print("first round",signalPixels)
    #print(np.sum(final))

    if signalPixels > 200:
            signalIntensity = np.sum(final)/signalPixels
            signalIntensity = 255-signalIntensity         
            signalIntensity = (np.round(signalIntensity,2))
            print(signalIntensity)
            #cv2.imshow("final", final)
            #cv2.imwrite("/home/pi/Desktop/final.jpg", final)
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
            text = ("%s" %signalIntensity)
            (font_width, font_height) = font.getsize(text)
            draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),text,font=font,fill=255)
            # Display image
            oled.image(OLEDimage)
            oled.show()
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("else1")
        heightCrop =warpedMat.shape[0]
        widthCrop = warpedMat.shape[1]
        #densitometerMat =warpedMat[100:heightCrop-100, 100:widthCrop-100]
    
        dsize = (500, 500)
        densitometerMat = cv2.resize(densitometerMat, dsize)

        #cv2.imshow("orig", densitometerMat)
        #cv2.imwrite("/home/pi/Desktop/original_dark.jpg", densitometerMat)
        patch1 = cv2.getRectSubPix(densitometerMat, (5,5), (50, heightCrop - 50))
        patch2 = cv2.getRectSubPix(densitometerMat, (5,5), (widthCrop - 50, 50))
        patch3 = cv2.getRectSubPix(densitometerMat, (5,5), (widthCrop - 50, heightCrop - 50))
        patch4 = cv2.getRectSubPix(densitometerMat, (5,5), (50, 50))
                      
        shadow1= np.sum(patch1)/25
        shadow2= np.sum(patch2)/25
        shadow3= np.sum(patch3)/25
        shadow4= np.sum(patch4)/25
            
        backgroundAverage = (shadow1 + shadow2 + shadow3 + shadow4)/4
        #print(backgroundAverage)
        #print (shadow1)
        #print(shadow2)
        #print(shadow3)
        #print(shadow4)
        #densitometerMat = cv2.GaussianBlur(densitometerMat,(3,3),1)
        #cv2.imshow("blur", densitometerMat)
        #cv2.imwrite("/home/pi/Desktop/blur.jpg", densitometerMat)
        th, thresh = cv2.threshold(densitometerMat,backgroundAverage-8, 255, cv2.THRESH_TOZERO)
        #cv2.imshow("threshed", thresh)
        mask = cv2.bitwise_not(thresh)
        th, mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)
        #cv2.imwrite("/home/pi/Desktop/thresh2_elif.jpg", mask)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        mask = cv2.erode(mask, kernel, iterations=7)
        
        #mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel, iterations=3)
        #cv2.imwrite("/home/pi/Desktop/mask3_elif.jpg", mask)
        #cv2.imshow("mask", mask)
        maskCropHeight =mask.shape[0]
        maskCropWidth = mask.shape[1]
        mask =mask[125:maskCropHeight-125, 125:maskCropWidth-125]    
        densitometerMat = densitometerMat[125:maskCropHeight-125, 125:maskCropWidth-125]
        #cv2.imwrite("/home/pi/Desktop/opencvMaskquarter.jpg", mask)
        final = cv2.bitwise_and(densitometerMat, mask, mask=mask)
        #cv2.imwrite("/home/pi/Desktop/overlay_elif.jpg", final)
        #cv2.imshow("final", densitometerMat)
        signalPixels = cv2.countNonZero(final)
        print("second try", signalPixels)
        if signalPixels > 200:
            signalIntensity = np.sum(final)/signalPixels
            signalIntensity = 255-signalIntensity         
            signalIntensity = (np.round(signalIntensity,2))
            print(signalIntensity)
            #print("signal pixels", signalPixels)
            #cv2.imshow("final", final)
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
            text = ("%s" %signalIntensity)
            (font_width, font_height) = font.getsize(text)
            draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),text,font=font,fill=255)
            # Display image
            oled.image(OLEDimage)
            oled.show()
            cv2.waitKey(0)
            cv2.destroyAllWindows()
       
        else:
            print("else2")
            heightCrop =warpedMat.shape[0]
            widthCrop = warpedMat.shape[1]
            #densitometerMat =warpedMat[100:heightCrop-100, 100:widthCrop-100]
    
            dsize = (500, 500)
            densitometerMat = cv2.resize(densitometerMat, dsize)

            #cv2.imshow("orig", densitometerMat)
            #cv2.imwrite("/home/pi/Desktop/original_dark.jpg", densitometerMat)
            patch1 = cv2.getRectSubPix(densitometerMat, (5,5), (50, heightCrop - 50))
            patch2 = cv2.getRectSubPix(densitometerMat, (5,5), (widthCrop - 50, 50))
            patch3 = cv2.getRectSubPix(densitometerMat, (5,5), (widthCrop - 50, heightCrop - 50))
            patch4 = cv2.getRectSubPix(densitometerMat, (5,5), (50, 50))
                      
            shadow1= np.sum(patch1)/25
            shadow2= np.sum(patch2)/25
            shadow3= np.sum(patch3)/25
            shadow4= np.sum(patch4)/25
            
            backgroundAverage = (shadow1 + shadow2 + shadow3 + shadow4)/4
        
            densitometerMat = cv2.GaussianBlur(densitometerMat,(3,3),1)
            #cv2.imshow("blur", densitometerMat)
            #cv2.imwrite("/home/pi/Desktop/blur.jpg", densitometerMat)
            #densitometerMat = 255-densitometerMat
            #cv2.imshow("inverse", densitometerMat)
            th, thresh = cv2.threshold(densitometerMat,205, 200, cv2.THRESH_TOZERO)
            #cv2.imshow("threshed", thresh)
            #mask = thresh
            mask = cv2.bitwise_not(thresh)
            th, mask = cv2.threshold(mask, 205, 255, cv2.THRESH_BINARY)
            #cv2.imwrite("/home/pi/Desktop/thresh2_elif.jpg", mask)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
            mask = cv2.dilate(mask, kernel, iterations=2)
            mask = cv2.erode(mask, kernel, iterations=20)
            #cv2.imshow("binary", mask)

            #cv2.imwrite("/home/pi/Desktop/mask2_elif.jpg", mask)
            #mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel, iterations=3)
            #cv2.imwrite("/home/pi/Desktop/mask3_elif.jpg", mask)
            maskCropHeight =mask.shape[0]
            maskCropWidth = mask.shape[1]
            mask =mask[50:maskCropHeight-220, 200:maskCropWidth-70]    
            densitometerMat = densitometerMat[50:maskCropHeight-220, 200:maskCropWidth-70]
            final = cv2.bitwise_and(densitometerMat, mask, mask=mask)
            #th, fin = cv2.threshold(final,50, 55, cv2.THRESH_TOZERO)
            #cv2.imwrite("/home/pi/Desktop/opencvMask32Binary.jpg", mask)
            #cv2.imshow("final", final)
            signalPixels = cv2.countNonZero(final)
            print("third try", signalPixels)
            #cv2.imshow("final", fin)
            if signalPixels > 200 and signalPixels < 50000:
               signalIntensity = np.sum(final)/signalPixels
               signalIntensity = 255-signalIntensity         
               signalIntensity = (np.round(signalIntensity,2))
               #print(signalIntensity)
               #print("signal pixels", signalPixels)
               #cv2.imshow("final", fin)
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
               #text = ("no signal" )
               #print("No Signal", signalIntensity)
               (font_width, font_height) = font.getsize(text)
               draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),text,font=font,fill=255)
               # Display image
               oled.image(OLEDimage)
               oled.show()
               cv2.waitKey(0)
               cv2.destroyAllWindows()   
            else:
                signalIntensity = np.sum(final)/signalPixels
                signalIntensity = 255-signalIntensity         
                signalIntensity = (np.round(signalIntensity,2))
                #cv2.imshow("final", fin)
                print("background",signalIntensity)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                """
                heightCrop =warpedMat.shape[0]
                widthCrop = warpedMat.shape[1]
                #densitometerMat =warpedMat[175:heightCrop-175, 175:widthCrop-175]
                dsize = (500, 500)
                densitometerMat = cv2.resize(densitometerMat, dsize)

                #cv2.imshow("orig", densitometerMat)
                #cv2.imwrite("/home/pi/Desktop/original.jpg", densitometerMat)
                patch1 = cv2.getRectSubPix(densitometerMat, (5,5), (50, heightCrop - 50))
                patch2 = cv2.getRectSubPix(densitometerMat, (5,5), (widthCrop - 50, 50))
                patch3 = cv2.getRectSubPix(densitometerMat, (5,5), (widthCrop - 50, heightCrop - 50))
                patch4 = cv2.getRectSubPix(densitometerMat, (5,5), (50, 50))
                      
                shadow1= np.sum(patch1)/25
                shadow2= np.sum(patch2)/25
                shadow3= np.sum(patch3)/25
                shadow4= np.sum(patch4)/25
            
                backgroundAverage = (shadow1 + shadow2 + shadow3 + shadow4)/4
                #print(backgroundAverage)

                densitometerMat = cv2.GaussianBlur(densitometerMat,(3,3),1)
                #cv2.imshow("blur", densitometerMat)
                #cv2.imwrite("/home/pi/Desktop/blur.jpg", densitometerMat)
                th, thresh = cv2.threshold(densitometerMat,backgroundAverage-8, 255, cv2.THRESH_TOZERO)
                #cv2.imshow("threshed", thresh)
                mask = cv2.bitwise_not(thresh)
                th, mask = cv2.threshold(mask, 205, 255, cv2.THRESH_BINARY)
                #cv2.imwrite("/home/pi/Desktop/thresh2_elif.jpg", mask)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
                mask = cv2.dilate(mask, kernel, iterations=2)
                mask = cv2.erode(mask, kernel, iterations=20)
                #cv2.imshow("binary", mask)

                #cv2.imwrite("/home/pi/Desktop/mask2_elif.jpg", mask)
                #mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel, iterations=3)
                #cv2.imwrite("/home/pi/Desktop/mask3_elif.jpg", mask)
                maskCropHeight =mask.shape[0]
                maskCropWidth = mask.shape[1]
                mask =mask[50:maskCropHeight-220, 200:maskCropWidth-70]    
                densitometerMat = densitometerMat[50:maskCropHeight-220, 200:maskCropWidth-70]
                final = cv2.bitwise_and(densitometerMat, mask, mask=mask)
                #th, fin = cv2.threshold(final,50, 55, cv2.THRESH_TOZERO)
                #cv2.imwrite("/home/pi/Desktop/opencvMask32Binary.jpg", mask)
                #cv2.imshow("final", final)
                signalPixels = cv2.countNonZero(final)
                print("last", signalIntensity)
            
                signalIntensity = np.sum(final)/signalPixels
                signalIntensity = 255-signalIntensity         
                signalIntensity = (np.round(signalIntensity,2))

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
                text = ("0")
                (font_width, font_height) = font.getsize(text)
                draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),text,font=font,fill=255)
                # Display image
                oled.image(OLEDimage)
                oled.show()
                print("no signal", signalIntensity)
                #cv2.imwrite("/home/pi/Desktop/final.jpg", final)


                cv2.waitKey(0)
                cv2.destroyAllWindows()
 """
except:
    print("redo photo")
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
    text = ("no signal")
    (font_width, font_height) = font.getsize(text)
    draw.text((oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),text,font=font,fill=255)
    # Display image
    oled.image(OLEDimage)
    oled.show() 
