#!/usr/bin/env python
# encoding: utf-8
# BPscope v 1.2
# Author: hwmayer
# Site: hwmayer.blogspot.com
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# From: http://dangerousprototypes.com/forum/index.php?topic=976
# More: http://dangerousprototypes.com/docs/Bus_Pirate:_Python_Oscilloscope
# USAGE:
# f - trigger on falling slope
# r - trigger on rising slope
# s - trigger off
# key_up 		- trigger level++
# key_down 	- trigger level--
# 9 - time scale++ (zoom out)
# 0 - time scale-- (zoom in)
# q - QUIT
#
#"pygame" and "pyBusPirate" libraries are needed to run this script.
#
#To install in Ubuntu use this command:
# sudo apt-get install python-pygame
import sys
import pygame

from pyBusPirateLite.BitBang import BBIO
from contextlib import closing

NO_SYNC = 0
RISING_SLOPE = 1
FALLING_SLOPE = 2

#change this path
BUS_PIRATE_DEV = "/dev/ttyUSB0"

RES_X = 640
RES_Y = 480
MAX_VOLTAGE = 6
OFFSET = 10
TRIGGER_LEV_RES = 0.05
TRIG_CAL = 0.99
DEFAULT_TIME_DIV = 1
DEFAULT_TRIGGER_LEV = 1.0
DEFAULT_TRIGGER_MODE = 0



DATA_RATE = 5720.0 #measures/second (estimated experimenticaly)

DEFAULT_TIME_SCALE = RES_X / DATA_RATE #default time in seconds to make one window fill

def scan_plot(bp, window):
	on_the_fly = not bp.cont_support
	plot = {}
	font = pygame.font.Font(None, 19)
	
	if on_the_fly:
		prev_trig = None
		maxv = None
		minv = None
		prev_time_div = None
	
	if(trig_mode != NO_SYNC):
		voltage = bp.read()
		for k in range(2,2000):
			prev_voltage = voltage
			voltage = bp.read()
			#rising slope
			if((voltage >= trigger_level) and (prev_voltage < (voltage * TRIG_CAL)) and (trig_mode == RISING_SLOPE)):
				break
			if((voltage < trigger_level) and (voltage > 0.01) and (prev_voltage > voltage/TRIG_CAL) and (trig_mode == FALLING_SLOPE)):
				break
		
	for i in range(RES_X):
		
		for k in range(time_div - 1):
			#ignoring (time_div-1) samples to achieve proper time resolution
			bp.read()
		plot[i] = bp.read()
		
		if not on_the_fly:
			continue
		
		if(i!=0):
			plot_update(window, i, plot[i], plot[i-1])
		
		if prev_trig is None or trigger_level != prev_trig:
			if prev_trig is not None:
				draw_trig(window, prev_trig, background)
			draw_trig(window)
			prev_trig = trigger_level
		
		if maxv is None or plot[i] > maxv:
			if maxv is not None:
				window.fill(background,prev_maxv_Rect)
			maxv = plot[i]
			prev_maxv_Rect = draw_maxv(window, font, maxv)
		if minv is None or plot[i] < minv:
			if minv is not None:
				window.fill(background,prev_minv_Rect)
			minv = plot[i]
			prev_minv_Rect = draw_minv(window, font, minv)
		
		if prev_time_div is None or time_div != prev_time_div:
			if prev_time_div is not None:
				window.fill(background,prev_time_Rect)
			prev_time_Rect = draw_time(window, font)
			prev_time_div = time_div
		
		pygame.display.flip() 
		handle_events()
	
	if not on_the_fly:
		draw_plot(window, font, plot)
		pygame.display.flip()
		handle_events()

def draw_plot(window, font, plot):
	for i in range(1,RES_X):
			plot_update(window, i, plot[i], plot[i-1])
	
	draw_trig(window)
	draw_maxv(window, font, max(plot.values()))
	draw_minv(window, font, min(plot.values()))
	draw_time(window, font)

def plot_update(window, i, voltage, prev_voltage):
	y = (RES_Y) - voltage*(RES_Y/MAX_VOLTAGE) - OFFSET
	x = i
	px = i-1;
	py = (RES_Y) - prev_voltage*(RES_Y/MAX_VOLTAGE) - OFFSET
	pygame.draw.line(window, line, (px, py), (x, y))	

def draw_trig(window, value=None, color=None):
	if value is None:
		value = trigger_level
	if color is None:
		color = trig_color
	trig_y = RES_Y - value * (RES_Y/MAX_VOLTAGE)
	pygame.draw.line(window, color, (0, trig_y), (RES_X, trig_y))

def draw_maxv(window, font, maxv):
	return draw_text(window, font, "Max: %f V" % maxv, 10)
def draw_minv(window, font, minv):
	return draw_text(window, font, "Min: %f V" % minv, 30)

def draw_time(window, font):
	time_scale = DEFAULT_TIME_SCALE * time_div
	return draw_text(window, font, "Timescale: %f s" % time_scale, 50)

def draw_text(window, font, text, y):
	text = font.render(text, 1, (255, 255, 255))
	Rect = text.get_rect()
	Rect.x = 10
	Rect.y = y
	window.blit(text, Rect)
	return Rect

def handle_events():
	global time_div
	global trig_mode
	global trigger_level
			
	for event in pygame.event.get(): 
		if event.type == pygame.QUIT: 
			sys.exit(0) 	
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_0:
				print "timescale x 2"
				time_div = time_div * 2
			elif event.key == pygame.K_9:
				if (time_div >= 2):
					print "timescale / 2"
					time_div = time_div / 2
			elif event.key == pygame.K_s:
				print "Trigger of, no sync"
				trig_mode = NO_SYNC
			elif event.key == pygame.K_f:
				print "Trigger set to falling slope"
				trig_mode = FALLING_SLOPE
			elif event.key == pygame.K_r:
				print "Trigger set to rising slope"
				trig_mode = RISING_SLOPE
			elif event.key == pygame.K_UP:
				trigger_level += TRIGGER_LEV_RES
				print "Trigger level: %f" % trigger_level
			elif event.key == pygame.K_DOWN:
				trigger_level -= TRIGGER_LEV_RES
				print "Trigger levelL: %f" % trigger_level
			elif event.key == pygame.K_q:
				sys.exit(0)

class VoltageProbe(object):
	# Buffering more than 13 bytes causes the Bus Pirate to miss buffered
	# commands, and interpret commands incorrectly, until reset.
	WRITE_LIMIT = 13
	
	def __init__(self, bp):
		self.bp = bp
		
		self.cont_support = not version or version >= (5, 9)
		if self.cont_support:
			self.bp.port.write(byte(VOLTAGE_CONT))
		else:
			self.pending = self.WRITE_LIMIT
			self.bp.port.write(byte(VOLTAGE) * self.pending)
	
	def read(self):
		measure = self.bp.response(2, True)
		voltage = ord(measure[0]) << 8
		voltage = voltage + ord(measure[1])
		voltage = (voltage/1024.0) * 6.6
		
		if not self.cont_support:
			self.bp.port.write(byte(VOLTAGE))
		
		return voltage
	
	def close(self):
		if not self.cont_support:
			self.bp.response(self.pending * 2)
			self.pending = 0
	
	def __del__(self):
		self.close()

# Turn a byte value into an unambiguous byte (not unicode) string
byte = chr

pygame.init() 

bp = BBIO(BUS_PIRATE_DEV,115200)

RESET = 0x0F
VOLTAGE = 0x14
VOLTAGE_CONT = 0x15

try:
	# Probe for firmware version
	if not bp.BBmode():
		raise EnvironmentError("BBIO.BBmode failed")
	bp.port.write(byte(RESET))
	bp.timeout()
	if not bp.response():
		raise EnvironmentError("Bus Pirate reset failed")
	banner = bp.port.read(bp.port.inWaiting())
	
	prefix = b"Firmware v"
	try:
		pos = banner.rindex(prefix) + len(prefix)
		end = banner.index(".", pos)
		major = int(banner[pos:end])
		
		pos = end + 1
		end = pos
		while end < len(banner) and banner[end].isdigit():
			end += 1
		minor = int(banner[pos:end])
	
	except ValueError:
		raise EnvironmentError("Could not parse firmware version")
	
	version = (major, minor)
	print "Firmware version: {0}.{1}".format(*version)

except EnvironmentError:
	sys.excepthook(*sys.exc_info())
	version = None

print "Entering binmode: ",
if not bp.BBmode():
	print "failed."
	sys.exit()
try:
	print "OK."
		
	window = pygame.display.set_mode((RES_X, RES_Y)) 
	background = (0,0,0)
	line = (0,255,0)
	trig_color = (100,100,0)
	
	time_div = DEFAULT_TIME_DIV
	trigger_level = DEFAULT_TRIGGER_LEV
	trig_mode = DEFAULT_TRIGGER_MODE
	
	with closing(VoltageProbe(bp)) as voltage:
		while 1:
			scan_plot(voltage, window)
			window.fill(background)

finally:
	bp.resetBP()

#END


