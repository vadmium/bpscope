#!/usr/bin/env python
# encoding: utf-8

import os, sys
import Image
import serial
import pygame

from pyBusPirateLite.UART import *
from pyBusPirateLite.BitBang import *

RES_X = 640
RES_Y = 480
MAX_VOLTAGE = 6
OFFSET = 10
BUS_PIRATE_DEV = "/dev/ttyUSB0"

pygame.init() 

bp = UART(BUS_PIRATE_DEV,115200)

print "Entering binmode: ",
if bp.BBmode():
	print "OK."
else:
	print "failed."
	sys.exit()
	
window = pygame.display.set_mode((RES_X, RES_Y)) 
background = (0,0,0)
line = (0,255,0)

while 1:
	plot = {}
	voltage = {}
	maxv = 0
	minv = 100
	
	for i in range(RES_X):
		#this is the same as ADC_measure but without timeout
		bp.port.write("\x14")
		measure = bp.response(2, True)
		
		voltage = ord(measure[0]) << 8
		voltage = voltage + ord(measure[1])
		voltage = (voltage/1024.0) * 6.6
		plot[i] = voltage
		if(i>0):
			if plot[i] > maxv:
				maxv = plot[i]
			if plot[i] < minv:
				minv = plot[i]
				
			y = (RES_Y) - plot[i]*(RES_Y/MAX_VOLTAGE) - OFFSET
			x = i
			px = i-1;
			py = (RES_Y) - plot[i-1]*(RES_Y/MAX_VOLTAGE) - OFFSET
			pygame.draw.line(window, line, (px, py), (x, y))	
		
			font = pygame.font.Font(None, 19)
		    	text_max_voltage = font.render("Max: %f V" % maxv, 1, (255, 255, 255))
		    	text_min_voltage = font.render("Min: %f V" % minv, 1, (255, 255, 255))
			text_maxv_Rect = text_max_voltage.get_rect()
			text_minv_Rect = text_min_voltage.get_rect()
			text_maxv_Rect.x = 10
			text_maxv_Rect.y = 10
			text_minv_Rect.x = 10 
			text_minv_Rect.y = 30
			blank_rect = pygame.Rect(0,0,200,100)
			window.fill(background,blank_rect)
			window.blit(text_max_voltage, text_maxv_Rect)
		    	window.blit(text_min_voltage, text_minv_Rect)

			pygame.display.flip() 
			
			for event in pygame.event.get(): 
				if event.type == pygame.QUIT: 
					sys.exit(0) 	
	
	window.fill(background)

#END


