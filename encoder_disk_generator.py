#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inkex, gettext
import cubicsuperpath, simplestyle, math
_ = gettext.gettext

# Function for calculating a point when you know the distance and the angle
# from the origin
def calculatePoint(angle, distance):
	if angle < 0.0 or angle > 360.0:
		return None
	elif angle == 0.0 or angle == 360.0:
		return [distance, 0.0]
	elif angle == 90.0:
		return [0.0, distance]
	elif angle == 180.0:
		return [-1.0*distance, 0.0]
	elif angle == 270.0:
		return [0.0, -1.0*distance]
	else:
		return [distance*math.cos(math.radians(angle)), distance*math.sin(math.radians(angle))]

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

	def drawSegment(self, line_style, angle, segment_angle, outer_diameter, width):

		line_attributes = {'style' : simplestyle.formatStyle(line_style)}

		# Go to the first point in the segment
		point = calculatePoint(angle, (outer_diameter-width)/2.0)
		line_attributes['d'] = 'M '+str(point[0])+' '+str(point[1])

		# Go to the second point in the segment
		point = calculatePoint(angle, outer_diameter/2.0)
		line_attributes['d'] += ' L '+ str(point[0])+' '+str(point[1])

		# Go to the third point in the segment, draw an arc
		point = calculatePoint(angle+segment_angle, outer_diameter/2.0)
		control_point = calculatePoint(angle+(segment_angle/2.0), (outer_diameter/2.0)/(math.cos(math.radians(segment_angle/2.0))))
		line_attributes['d'] += ' Q '+ str(control_point[0]) + ',' + str(control_point[1]) + ' ' + str(point[0])+','+str(point[1])

		# Go to the fourth point in the segment
		point = calculatePoint(angle+segment_angle,(outer_diameter-width)/2.0)
		line_attributes['d'] += ' L '+ str(point[0])+' '+str(point[1])

		# Go to the beginning in the segment, draw an arc
		point = calculatePoint(angle, (outer_diameter-width)/2.0)
		control_point = calculatePoint(angle+(segment_angle/2.0), ((outer_diameter-width)/2.0)/(math.cos(math.radians(segment_angle/2.0))))
		line_attributes['d'] += ' Q '+ str(control_point[0]) + ',' + str(control_point[1]) + ' ' + str(point[0])+','+str(point[1])


		# 'Z' closes the path
		line_attributes['d'] += ' Z'

		#inkex.errormsg(_("Data = " + str(line_attributes['d'])))

		# Add the path to the document
		return line_attributes

	def effect(self):

		# Group to put all the elements in, center set in the middle of the view
		group = inkex.etree.SubElement(self.current_layer, 'g', {inkex.addNS('label', 'inkscape'):'Encoder disk', 'transform':'translate' + str(self.view_center)})

		# Attributes for the center hole, then create it
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'none', 'fill':'#000000'}),
			'r'         : str(self.options.hole_diameter/2.0)
		}
		self.current_layer.append(inkex.etree.SubElement(group, inkex.addNS('circle','svg'), attributes))

		# Attributes for the guide hole in the center hole, then create it
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'white','fill':'white'}),
			'r'         : '1'
		}
		self.current_layer.append(inkex.etree.SubElement(group, inkex.addNS('circle','svg'), attributes))

		# Attributes for the outer rim, then create it
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'black', 'stroke-width':'1', 'fill':'none'}),
			'r'         : str(self.options.diameter/2.0)
		}
		self.current_layer.append(inkex.etree.SubElement(group, inkex.addNS('circle','svg'), attributes))

		# Line style for the encoder segments
		line_style   = { 'stroke':'black',
				         'stroke-width':'1',
				         'fill':'black'
				       }


		for segment in range(0, self.options.segments, 2):
			self.current_layer.append(inkex.etree.SubElement(group, inkex.addNS('path', 'svg'), self.drawSegment(line_style, segment*(360.0/self.options.segments), 360.0/self.options.segments, self.options.outer_encoder_diameter, self.options.outer_encoder_width)))


if __name__ == '__main__':
	# Run the effect
	effect = EncoderDiskGenerator()
	effect.affect()
