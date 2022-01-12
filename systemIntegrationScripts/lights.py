# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time

from rpi_ws281x import Color, PixelStrip, ws
import rpi_ws281x
# LED strip configuration:
LED_COUNT = 12        # Number of LED pixels.
LED_PIN = 13          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100 # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1
LED_STRIP = ws.SK6812_STRIP_RGBW
#LED_STRIP = ws.SK6812W_STRIP
LED_PIN1 = 18
LED_CHANNEL1 = 0

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Main program logic follows:
if __name__ == '__main__':
    # Create PixelStrip object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    #strip1 = PixelStrip(LED_COUNT, LED_PIN1, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL1, LED_STRIP) 
    # Intialize the library (must be called once before other functions).
    strip.begin()
    
    #strip1.begin()
    #print('Press Ctrl-C to quit.')
    #while True:
        # Color wipe animations.
        #colorWipe(strip, Color(255, 0, 0), 0)  # Red wipe
        #time.sleep(2)
        #colorWipe(strip, Color(0, 255, 0), 0)  # Blue wipe
        #time.sleep(2)
        #colorWipe(strip, Color(0, 0, 255), 0)  # Green wipe
        #time.sleep(2)
        #colorWipe(strip, Color(0, 0, 0, 255), 0)  # White wipe
        #time.sleep(2)
        #colorWipe(strip, Color(255, 255, 255), 0)  # Composite White wipe
        #time.sleep(2)
    colorWipe(strip, Color(255, 0, 0), 0)  # Composite White + White LED wipe
        #time.sleep(120)
        #colorWipe(strip1, Color(255, 255, 255, 255), 0)
        #time.sleep(20)
        #colorWipe(strip, Color(0, 0, 0, 0), 0)
        #time.sleep(5)
          # Composite White + White LED wipe
        
        #colorWipe(strip1, Color(0, 0, 0, 0), 0)
        #time.sleep(15)
    #strip.clear()
