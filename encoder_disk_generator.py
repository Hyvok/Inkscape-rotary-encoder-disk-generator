#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inkex
import simplestyle
import math
import string
import simpletransform


# Function for calculating a point from the origin when you know the distance
# and the angle
def calculatePoint(angle, distance):
	if (angle < 0 or angle > 360):
		return None
	else:
		return [
			distance * math.cos(math.radians(angle)),
			distance * math.sin(math.radians(angle))]


class EncoderDiskGenerator(inkex.Effect):

	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("--tab",
					action="store", type="string",
					dest="tab", default="rotary_enc",
					help="Selected tab")
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
		self.OptionParser.add_option("--bits",
					action="store", type="int",
					dest="bits", default=1,
					help="Number of bits/tracks")
		self.OptionParser.add_option("--encoder_diameter",
					action="store", type="float",
					dest="encoder_diameter", default=0.0,
					help="Outer diameter of the last track")
		self.OptionParser.add_option("--track_width",
					action="store", type="float",
					dest="track_width", default=0.0,
					help="Width of one track")
		self.OptionParser.add_option("--track_distance",
					action="store", type="float",
					dest="track_distance", default=0.0,
					help="Distance between tracks")
		self.OptionParser.add_option("--bm_diameter",
					action="store", type="float",
					dest="bm_diameter", default=0.0,
					help="Diameter of the encoder disk")
		self.OptionParser.add_option("--bm_hole_diameter",
					action="store", type="float",
					dest="bm_hole_diameter", default=0.0,
					help="Diameter of the center hole")
		self.OptionParser.add_option("--bm_bits",
					action="store", type="string",
					dest="bm_bits", default="",
					help="Bits of segments")
		self.OptionParser.add_option("--bm_outer_encoder_diameter",
					action="store", type="float",
					dest="bm_outer_encoder_diameter", default=0.0,
					help="Diameter of the outer encoder disk")
		self.OptionParser.add_option("--bm_outer_encoder_width",
					action="store", type="float",
					dest="bm_outer_encoder_width", default=0.0,
					help="Width of the outer encoder disk")
		self.OptionParser.add_option("--brgc_diameter",
					action="store", type="float",
					dest="brgc_diameter", default=0.0,
					help="Diameter of the encoder disk")
		self.OptionParser.add_option("--stgc_diameter",
					action="store", type="float",
					dest="stgc_diameter", default=0.0,
					help="Diameter of the encoder disk")
		self.OptionParser.add_option("--brgc_hole_diameter",
					action="store", type="float",
					dest="brgc_hole_diameter", default=0.0,
					help="Diameter of the center hole")
		self.OptionParser.add_option("--cutouts",
					action="store", type="int",
					dest="cutouts", default=1,
					help="Number of cutouts")
		self.OptionParser.add_option("--sensors",
					action="store", type="int",
					dest="sensors", default=1,
					help="Number of sensors")
		self.OptionParser.add_option("--stgc_hole_diameter",
					action="store", type="float",
					dest="stgc_hole_diameter", default=0.0,
					help="Diameter of the center hole")
		self.OptionParser.add_option("--stgc_encoder_diameter",
					action="store", type="float",
					dest="stgc_encoder_diameter", default=0.0,
					help="Outer diameter of the last track")
		self.OptionParser.add_option("--stgc_track_width",
					action="store", type="float",
					dest="stgc_track_width", default=0.0,
					help="Width of track")

	# This function just concatenates the point and the command and returns
	# the data string
	def parsePathData(self, command, point):

		path_data = command + ' %f ' % point[0] + ' %f ' % point[1]
		return path_data

	# Creates a gray code of size bits (n >= 1) in the format of a list
	def createGrayCode(self, bits):

		gray_code = [[False], [True]]

		if bits == 1:
			return gray_code

		for i in range(bits - 1):
			temp = []
			# Reflect values
			for j in range(len(gray_code[0]), 0, -1):
				for k in range(0, len(gray_code)):
					if j == len(gray_code[0]):
						temp.append([gray_code[k][-j]])
					else:
						temp[k].append(gray_code[k][-j])
			while temp:
				gray_code.append(temp.pop())
			# Add False to the "old" values and true to the new ones
			for j in range(0, len(gray_code)):
				if j < len(gray_code) / 2:
					gray_code[j].insert(0, False)
				else:
					gray_code[j].insert(0, True)
			temp = []

		return gray_code

	# This function returns the segments for a gray encoder
	def drawGrayEncoder(self, line_style, bits, encoder_diameter, track_width,
		track_distance):
		gray_code = self.createGrayCode(bits)

		segments = []
		segment_size = 0
		start_angle_position = 0
		index = 0
		current_encoder_diameter = encoder_diameter
		previous_item = False
		position_size = 360.0 / (2 ** bits)

		for i in range(len(gray_code[0]) - 1, -1, -1):
			for j in gray_code:
				if j[i]:
					segment_size += 1
					if segment_size == 1:
						start_angle_position = index
					previous_item = True
				elif not j[i] and previous_item:
					segments.append(
						self.drawSegment(line_style,
						start_angle_position * position_size,
						segment_size * position_size,
						current_encoder_diameter,
						track_width))

					segment_size = 0
					previous_item = False
					start_angle_position = 0

				index += 1

			if previous_item:
				segments.append(self.drawSegment(line_style,
					start_angle_position * position_size,
					segment_size * position_size,
					current_encoder_diameter, track_width))
				segment_size = 0
				previous_item = False
				start_angle_position = 0
			current_encoder_diameter -= (2 * track_distance + 2 * track_width)
			index = 0

		return segments

	# Check if there is too many cutouts compared to number of sensors
	def validSTGrayEncoder(self, cutouts, sensors):
		if sensors < 6 and cutouts > 1:
			pass
		elif sensors <= 10 and cutouts > 2:
			pass
		elif sensors <= 16 and cutouts > 3:
			pass
		elif sensors <= 23 and cutouts > 4:
			pass
		elif sensors <= 36 and cutouts > 5:
			pass
		else:
			return True

		return False

	# This function returns the segments for a single-track gray encoder
	def drawSTGrayEncoder(
		self, line_style, cutouts, sensors, encoder_diameter, track_width):

		segments = []
		resolution = 360.0 / (cutouts * 2 * sensors)
		current_angle = 0.0
		added_angle = ((2 * cutouts + 1) * resolution)
		for n in range(cutouts):
			current_segment_size = ((n * 2 + 2) * cutouts + 1) * resolution
			segments.append(
				self.drawSegment(
					line_style, current_angle,
					current_segment_size,
					encoder_diameter, track_width))
			current_angle += added_angle + current_segment_size

		return segments

	def drawLabel(self, group, angle, segment_angle, outer_diameter, labelNum):
		outer_radius = outer_diameter / 2
		label_angle = angle + (segment_angle / 2)
		point = calculatePoint(label_angle, outer_radius)
		matrix = simpletransform.parseTransform(
			'rotate(' + str(label_angle + 90) + ')')
		matrix_str = str(matrix[0][0]) + "," + str(matrix[0][1])
		matrix_str += "," + str(matrix[1][0]) + "," + str(matrix[1][1]) + ",0,0"
		text = {
			'id': 'text' + str(labelNum),
			#'sodipodi:linespacing': '0%',
			'style': 'font-size: 6px;font-style: normal;font-family: Sans',
			#'transform': 'matrix(' + matrix_str + ')',
			'x': str(point[0]),
			'y': str(point[1]),
			#'xml:space': 'preserve'
			}
		textElement = inkex.etree.SubElement(group, inkex.addNS('text', 'svg'), text)
		#tspanElement = inkex.etree.Element(
		#	textElement, '{%s}%s' % (svg_uri, 'tspan'), tspan)
		textElement.text = string.printable[labelNum % len(string.printable)]

		self.current_layer.append(textElement)

	# This function creates the path for one single segment
	def drawSegment(self, line_style, angle, segment_angle, outer_diameter, width):

		path = {'style': simplestyle.formatStyle(line_style)}
		path['d'] = ''
		outer_radius = outer_diameter / 2

		# Go to the first point in the segment
		path['d'] += self.parsePathData(
			'M', calculatePoint(angle, outer_radius - width))

		# Go to the second point in the segment
		path['d'] += self.parsePathData('L', calculatePoint(angle, outer_radius))

		# Go to the third point in the segment, draw an arc
		point = calculatePoint(angle + segment_angle, outer_radius)
		path['d'] += self.parsePathData('A', [outer_radius, outer_radius]) + \
					'0 0 1' + self.parsePathData(' ', point)

		# Go to the fourth point in the segment
		point = calculatePoint(angle + segment_angle, outer_radius - width)
		path['d'] += self.parsePathData('L', point)

		# Go to the beginning in the segment, draw an arc
		point = calculatePoint(angle, outer_radius - width)
		# 'Z' closes the path
		path['d'] += (self.parsePathData(
			'A',
			[outer_radius - width, outer_radius - width]) +
				'0 0 0' + self.parsePathData(' ', point) + ' Z')

		# Return the path
		return path

	# This function adds an element to the document
	def addElement(self, element_type, group, element_attributes):
		inkex.etree.SubElement(
			group, inkex.addNS(element_type, 'svg'),
			element_attributes)

	def drawCircles(self, hole_diameter, diameter):
		# Attributes for the center hole, then create it, if diameter is 0, dont
		# create it
		circle_elements = []
		attributes = {
			'style': simplestyle.formatStyle({'stroke': 'none', 'fill': 'black'}),
			'r': str(hole_diameter / 2)
		}
		if self.options.hole_diameter > 0:
			circle_elements.append(attributes)

		# Attributes for the guide hole in the center hole, then create it
		attributes = {
			'style': simplestyle.formatStyle(
				{'stroke': 'white', 'fill': 'white', 'stroke-width': '0.1'}),
			'r': '1'
		}
		circle_elements.append(attributes)

		# Attributes for the outer rim, then create it
		attributes = {
			'style': simplestyle.formatStyle(
				{'stroke': 'black', 'stroke-width': '1', 'fill': 'none'}),
			'r': str(diameter / 2)
		}
		if self.options.diameter > 0:
			circle_elements.append(attributes)

		return circle_elements

	def drawCommonCircles(self, group, diameter, hole_diameter):
		circle_elements = self.drawCircles(hole_diameter, diameter)

		for circle in circle_elements:
			self.addElement('circle', group, circle)

	def effectBrgc(self, group, line_style, diameter, hole_diameter):

		if (((self.options.encoder_diameter / 2) -
			(self.options.bits * self.options.track_width +
			(self.options.bits - 1) * self.options.track_distance)) <
			self.options.brgc_hole_diameter / 2):
			inkex.errormsg("Innermost encoder smaller than the center hole!")
		else:
			segments = self.drawGrayEncoder(
				line_style, self.options.bits,
				self.options.encoder_diameter,
				self.options.track_width,
				self.options.track_distance)
			for item in segments:
				self.addElement('path', group, item)

		self.drawCommonCircles(group, diameter, hole_diameter)

	def effectStgc(self, group, line_style, diameter, hole_diameter):

		if ((self.options.stgc_encoder_diameter / 2) -
			self.options.stgc_track_width < self.options.stgc_hole_diameter / 2):
			inkex.errormsg("Encoder smaller than the center hole!")
		elif not self.validSTGrayEncoder(self.options.cutouts, self.options.sensors):
			inkex.errormsg("Too many cutouts compared to number of sensors!")
		else:
			segments = self.drawSTGrayEncoder(line_style, self.options.cutouts,
				self.options.sensors, self.options.stgc_encoder_diameter,
				self.options.stgc_track_width)
			for item in segments:
				self.addElement('path', group, item)

		self.drawCommonCircles(group, diameter, hole_diameter)

	def effectRotaryEnc(self, group, line_style, diameter, hole_diameter):

		# Angle of one single segment
		segment_angle = 360.0 / (self.options.segments * 2)

		for segment_number in range(0, self.options.segments):

			angle = segment_number * (segment_angle * 2)

			if (self.options.outer_encoder_width > 0 and
				self.options.outer_encoder_diameter > 0 and
				self.options.outer_encoder_diameter / 2 >
				self.options.outer_encoder_width):

				segment = self.drawSegment(line_style, angle,
					segment_angle,
					self.options.outer_encoder_diameter,
					self.options.outer_encoder_width)
				self.addElement('path', group, segment)

			# If the inner encoder diameter is something else than 0; create it
			if (self.options.outer_encoder_width > 0 and
				self.options.inner_encoder_diameter > 0 and
				self.options.inner_encoder_diameter / 2 >
				self.options.inner_encoder_width):

				# The inner encoder must be half an encoder segment ahead of the outer one
				segment = self.drawSegment(
					line_style, angle + (segment_angle / 2), segment_angle,
					self.options.inner_encoder_diameter,
					self.options.inner_encoder_width)

				self.addElement('path', group, segment)

		self.drawCommonCircles(group, diameter, hole_diameter)

	def effectBitmapEnc(self, group, line_style, diameter, hole_diameter):

		bits = self.options.bm_bits
		bm_segments = len(bits)
		# Angle of one single segment
		segment_angle = 360.0 / bm_segments

		for segment_number in range(0, bm_segments):

			angle = segment_number * segment_angle

			if (self.options.bm_outer_encoder_width > 0 and
				self.options.bm_outer_encoder_diameter > 0 and
				self.options.bm_outer_encoder_diameter >
				self.options.bm_outer_encoder_width):

				self.drawLabel(group,
					angle, segment_angle,
					self.options.bm_diameter,
					segment_number)
				# Drawing only the black segments
				if (bits[segment_number] == '1'):
					segment = self.drawSegment(
						line_style, angle,
						segment_angle,
						self.options.bm_outer_encoder_diameter,
						self.options.bm_outer_encoder_width)

					self.addElement('path', group, segment)

		self.drawCommonCircles(group, diameter, hole_diameter)

	def effect(self):

		# Group to put all the elements in, center set in the middle of the view
		group = inkex.etree.SubElement(self.current_layer, 'g', {
			inkex.addNS('label', 'inkscape'): 'Encoder disk',
			'transform': 'translate' + str(self.view_center)
		})

		# Line style for the encoder segments
		line_style = {
			'stroke': 'white',
			'stroke-width': '0',
			'fill': 'black'
		}

		if self.options.tab == "\"brgc\"":
			self.effectBrgc(group, line_style,
			self.options.brgc_diameter,
			self.options.brgc_hole_diameter)

		if self.options.tab == "\"stgc\"":
			self.effectStgc(group, line_style,
			self.options.stgc_diameter,
			self.options.stgc_hole_diameter)

		if self.options.tab == "\"rotary_enc\"":
			self.effectRotaryEnc(group, line_style,
			self.options.diameter,
			self.options.hole_diameter)

		if self.options.tab == "\"bitmap_enc\"":
			self.effectBitmapEnc(group, line_style,
			self.options.bm_diameter,
			self.options.bm_hole_diameter)


if __name__ == '__main__':
	# Run the effect
	effect = EncoderDiskGenerator()
	effect.affect()
