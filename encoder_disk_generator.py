#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inkex, sys
import simplestyle, math
import gettext
_ = gettext.gettext

# Function for calculating a point from the origin when you know the distance 
# and the angle
def calculatePoint(angle, distance):
	if angle < 0 or angle > 360:
		return None
	else:
		return [distance*math.cos(math.radians(angle)),
				distance*math.sin(math.radians(angle))]

class EncoderDiskGenerator(inkex.Effect):
		
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("--diameter",
				        action="store", type="float",
						dest="diameter", default=0.0,
				        help="Diameter of the encoder disk")
		self.OptionParser.add_option("--hole_diameter",
				        action="store", type="float", 
				        dest="hole_diameter", default=0.0,
				        help="Diameter of the center hole")
		self.OptionParser.add_option("--segments",
				        action="store", type="int", 
				        dest="segments", default=0,
				        help="Number of segments")
		self.OptionParser.add_option("--outer_encoder_diameter",
				        action="store", type="float", 
				        dest="outer_encoder_diameter", default=0.0,
				        help="Diameter of the outer encoder disk")
		self.OptionParser.add_option("--outer_encoder_width",
				        action="store", type="float", 
				        dest="outer_encoder_width", default=0.0,
				        help="Width of the outer encoder disk")
		self.OptionParser.add_option("--inner_encoder_diameter",
				        action="store", type="float", 
				        dest="inner_encoder_diameter", default=0.0,
				        help="Diameter of the inner encoder disk")
		self.OptionParser.add_option("--inner_encoder_width",
				        action="store", type="float", 
				        dest="inner_encoder_width", default=0.0,
				        help="Width of the inner encoder disk")

	# This function just concatenates the point and the command and returns
	# the data string
	def parsePathData(self, command, point):
		path_data = command + ' %f ' %point[0] + ' %f ' %point[1] 
		return path_data

	# This function creates the path for one single segment
	def drawSegment(self, line_style, angle, segment_angle, outer_diameter, width):

		path = {'style' : simplestyle.formatStyle(line_style)}
		path['d'] = ''
		outer_radius = outer_diameter/2

		# Go to the first point in the segment
		path['d'] += self.parsePathData('M', calculatePoint(angle, outer_radius-width))

		# Go to the second point in the segment
		path['d'] += self.parsePathData('L', calculatePoint(angle, outer_radius))

		# Go to the third point in the segment, draw an arc
		point = calculatePoint(angle+segment_angle, outer_radius)
		path['d'] += self.parsePathData('A', [outer_radius, outer_radius]) + \
					'0 0 1' + self.parsePathData(' ', point)

		# Go to the fourth point in the segment
		point = calculatePoint(angle+segment_angle, outer_radius-width)
		path['d'] += self.parsePathData('L', point)

		# Go to the beginning in the segment, draw an arc
		point = calculatePoint(angle, outer_radius-width)
		# 'Z' closes the path
		path['d'] += self.parsePathData('A', [outer_radius-width, outer_radius-width])\
					 + '0 0 0' + self.parsePathData(' ', point) + ' Z'

		# Return the path
		return path

	# This function adds an element to the document
	def addElement(self, element_type, group, element_attributes):
		self.current_layer.append(inkex.etree.SubElement(group, 
		inkex.addNS(element_type,'svg'), element_attributes))

	def effect(self):

		# Group to put all the elements in, center set in the middle of the view
		group = inkex.etree.SubElement(self.current_layer, 'g', {
			inkex.addNS('label', 'inkscape'):'Encoder disk', 
			'transform':'translate' + str(self.view_center)
		})

		# Attributes for the center hole, then create it
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'none', 'fill':'black'}),
			'r'         : str(self.options.hole_diameter/2)
		}
		self.addElement('circle', group, attributes)

		# Attributes for the guide hole in the center hole, then create it
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'white','fill':'white'}),
			'r'         : '1'
		}
		self.addElement('circle', group, attributes)

		# Attributes for the outer rim, then create it
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'black', 'stroke-width':'1', 'fill':'none'}),
			'r'         : str(self.options.diameter/2)
		}
		self.addElement('circle', group, attributes)

		# Line style for the encoder segments
		line_style   = { 
			'stroke'		: 	'black',
			'stroke-width'	:	'1',
			'fill'			:	'black'
		}

		# Angle of one single segment
		segment_angle = 360.0/(self.options.segments*2)

		for segment_number in range(0, self.options.segments):

			angle = segment_number*(segment_angle*2)

			segment = self.drawSegment(line_style, angle, segment_angle,
				self.options.outer_encoder_diameter, self.options.outer_encoder_width)
			self.addElement('path', group, segment)

			# If the inner encoder diameter is something else than 0; create it
			if self.options.inner_encoder_diameter > 0:
				# The inner encoder must be half an encoder segment ahead of the outer one
				segment = self.drawSegment(line_style, angle+(segment_angle/2), segment_angle,
					self.options.inner_encoder_diameter, self.options.inner_encoder_width)
				self.addElement('path', group, segment)

if __name__ == '__main__':
	# Run the effect
	effect = EncoderDiskGenerator()
	effect.affect()
