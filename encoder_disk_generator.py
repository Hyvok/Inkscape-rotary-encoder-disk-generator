#!/usr/bin/env python 

import inkex
import cubicsuperpath, simplestyle

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
		self.OptionParser.add_option("--inner_encoder_diameter",
				        action="store", type="float", 
				        dest="inner_encoder_diameter", default=0.0,
				        help="Diameter of the inner encoder disk")

	def effect(self):

		# Group to put all the elements in, center set in the middle of the view
		group = inkex.etree.SubElement(self.current_layer, 'g', {inkex.addNS('label', 'inkscape'):'Encoder disk', 											'transform':'translate' + str(self.view_center)})

		# Attributes for the center hole
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'none', 'fill':'#000000'}),
			'r'         : str(self.options.hole_diameter/2.0)
		}
		self.current_layer.append(inkex.etree.SubElement(group, inkex.addNS('circle','svg'), attributes ))

		# Attributes for the guide hole in the center hole
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'white','fill':'white'}),
			'r'         : '1'
		}
		# Add center circle to the document
		self.current_layer.append(inkex.etree.SubElement(group, inkex.addNS('circle','svg'), attributes ))

		# Attributes for the outer rim
		attributes = {
			'style'     : simplestyle.formatStyle({'stroke':'black', 'stroke-width':'1', 'fill':'none'}),
			'r'         : str(self.options.diameter/2.0)
		}
		self.current_layer.append(inkex.etree.SubElement(group, inkex.addNS('circle','svg'), attributes ))

if __name__ == '__main__':
	effect = EncoderDiskGenerator()
	effect.affect()
