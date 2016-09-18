# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import socket
import threading

from neopixel import *


# LED strip configuration:
LED_COUNT      = 20      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

BIT_GREEN=1<<4
GREEN = (0, 1.0, 0)

BIT_RED=1<<6
RED = (1.0, 0, 0)

BIT_YELLOW=1<<3
YELLOW = (1.0,1.0,0)

BIT_BLUE=1<<5
BLUE = (0, 0, 1.0)

BIT_ORANGE=1<<7
ORANGE = (1.0, 0.27, 0)

BIT_UP=1<<0
WHITE = (1.0, 1.0, 1.0)

BIT_DOWN=1<<6
BLACK = (0,0,0)

BIT_PLUS=1<<2
BIT_MINUS=1<<4

def oneto255(color):
	return (int(i*255) for i in color)

def RGBtoGRB(color):
	return (color[1], color[0], color[2])

# Just set to one color
def colorSet(strip, color):
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)

	strip.show()

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel(((i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	for j in range(256):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)


def cap(f):
	if f < 0.0: return 0.0
	if f > 1.0: return 1.0
	return f

class LEDThread(threading.Thread):
	def makedelta(self, to):
		self.deltasteps = 100
		self.delta = (
			(to[0]-self.currentcolor[0])/100,
			(to[1]-self.currentcolor[1])/100,
			(to[2]-self.currentcolor[2])/100
		)
		print "new delta", self.delta, self.deltasteps

	def applydelta(self):
		if self.deltasteps:
			self.currentcolor = (
				cap(self.currentcolor[0] + self.delta[0]),
				cap(self.currentcolor[1] + self.delta[1]),
				cap(self.currentcolor[2] + self.delta[2])
			)
			self.deltasteps = self.deltasteps - 1

	def fadeTo(self, color):
		self.makedelta(color)

	def fadeToMax(self):
		max = max(self.currentcolor)
		maxcolor = (
			self.currentcolor[0] / max,
			self.currentcolor[1] / max,
			self.currentcolor[2] / max
		)
		self.makedelta(maxcolor)

	def hold(self):
		self.deltasteps = 0

	def run(self):
		# Create NeoPixel object with appropriate configuration.
		self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
		# Intialize the library (must be called once before other functions).
		self.strip.begin()
		self.currentcolor=(1.0,1.0,1.0)
		self.delta=(0.0, 0.0, 0.0)
		self.deltasteps=0

		while True:
			time.sleep(1/100.0)

			self.applydelta()

			# print self.currentcolor
			colorSet(self.strip, Color(*(oneto255(RGBtoGRB(self.currentcolor)))))

# Main program logic follows:
if __name__ == '__main__':
	ledthread = LEDThread()
	ledthread.start()
	print ('Press Ctrl-C to quit.')
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('', 2000))

	on = True

	maxmixing = True

	while True:
		newcolors = []
		newcolor = None

		data = sock.recv(6)
		print data.encode('hex')

		b4 = ord(data[4])
		b5 = ord(data[5])

		if not b5 & BIT_GREEN:
			newcolors.append(GREEN)
		if not b5 & BIT_RED:
			newcolors.append(RED)
		if not b5 & BIT_YELLOW:
			newcolors.append(YELLOW)
		if not b5 & BIT_BLUE:
			newcolors.append(BLUE)
		if not b5 & BIT_ORANGE:
			newcolors.append(ORANGE)
		if not b4 & BIT_DOWN:
			newcolors.append(BLACK)
		if not b5 & BIT_UP:
			newcolors.append(WHITE)

		if not b4 & BIT_PLUS:
			maxmixing = True

		if not b4 & BIT_MINUS:
			maxmixing = False

		if newcolors:
			if maxmixing:
				newcolor = (
					max(x[0] for x in newcolors),
					max(x[1] for x in newcolors),
					max(x[2] for x in newcolors)
				)
			else:
				newcolor = (
					sum(x[0] for x in newcolors) / len(newcolors),
					sum(x[1] for x in newcolors) / len(newcolors),
					sum(x[2] for x in newcolors) / len(newcolors)
				)

		print 'new color', newcolor, 'maxmixing', maxmixing

		if newcolor:
			ledthread.fadeTo(newcolor)
		else:
			ledthread.hold()

		# print ledthread.color

#		# Color wipe animations.
#		colorWipe(strip, Color(255, 0, 0))  # Red wipe
#		colorWipe(strip, Color(0, 255, 0))  # Blue wipe
#		colorWipe(strip, Color(0, 0, 255))  # Green wipe
#		# Theater chase animations.
#		theaterChase(strip, Color(127, 127, 127))  # White theater chase
#		theaterChase(strip, Color(127,   0,   0))  # Red theater chase
#		theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
#		# Rainbow animations.
#		rainbow(strip)
#		rainbowCycle(strip)
#		theaterChaseRainbow(strip)
