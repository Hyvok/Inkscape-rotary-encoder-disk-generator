#!/usr/bin/env python3
import inkex
import math
import string
from lxml import etree
from inkex.transforms import Transform


# Function for calculating a point from the origin when you know the distance
# and the angle
def calculate_point(angle, distance):
    if (angle < 0 or angle > 360):
        return None
    else:
        return [
            distance * math.cos(math.radians(angle)),
            distance * math.sin(math.radians(angle))]


class EncoderDiskGenerator(inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument(
                "--tab",
                default="rotary_enc",
                help="Selected tab")
        self.arg_parser.add_argument(
                "--diameter",
                type=float, default=0.0,
                help="Diameter of the encoder disk")
        self.arg_parser.add_argument(
                "--hole_diameter",
                type=float, default=0.0,
                help="Diameter of the center hole")
        self.arg_parser.add_argument(
                "--segments",
                type=int, default=0,
                help="Number of segments")
        self.arg_parser.add_argument(
                "--outer_encoder_diameter",
                type=float, default=0.0,
                help="Diameter of the outer encoder disk")
        self.arg_parser.add_argument(
                "--outer_encoder_width",
                type=float, default=0.0,
                help="Width of the outer encoder disk")
        self.arg_parser.add_argument(
                "--inner_encoder_diameter",
                type=float, default=0.0,
                help="Diameter of the inner encoder disk")
        self.arg_parser.add_argument(
                "--inner_encoder_width",
                type=float, default=0.0,
                help="Width of the inner encoder disk")
        self.arg_parser.add_argument(
                "--bits",
                type=int, default=1,
                help="Number of bits/tracks")
        self.arg_parser.add_argument(
                "--encoder_diameter",
                type=float, default=0.0,
                help="Outer diameter of the last track")
        self.arg_parser.add_argument(
                "--track_width",
                type=float, default=0.0,
                help="Width of one track")
        self.arg_parser.add_argument(
                "--track_distance",
                type=float, default=0.0,
                help="Distance between tracks")
        self.arg_parser.add_argument(
                "--bm_diameter",
                type=float, default=0.0,
                help="Diameter of the encoder disk")
        self.arg_parser.add_argument(
                "--bm_hole_diameter",
                type=float, default=0.0,
                help="Diameter of the center hole")
        self.arg_parser.add_argument(
                "--bm_bits",
                default="",
                help="Bits of segments")
        self.arg_parser.add_argument(
                "--bm_outer_encoder_diameter",
                type=float, default=0.0,
                help="Diameter of the outer encoder disk")
        self.arg_parser.add_argument(
                "--bm_outer_encoder_width",
                type=float, default=0.0,
                help="Width of the outer encoder disk")
        self.arg_parser.add_argument(
                "--brgc_diameter",
                type=float, default=0.0,
                help="Diameter of the encoder disk")
        self.arg_parser.add_argument(
                "--stgc_diameter",
                type=float, default=0.0,
                help="Diameter of the encoder disk")
        self.arg_parser.add_argument(
                "--brgc_hole_diameter",
                type=float, default=0.0,
                help="Diameter of the center hole")
        self.arg_parser.add_argument(
                "--cutouts",
                type=int, default=1,
                help="Number of cutouts")
        self.arg_parser.add_argument(
                "--sensors",
                type=int, default=1,
                help="Number of sensors")
        self.arg_parser.add_argument(
                "--stgc_hole_diameter",
                type=float, default=0.0,
                help="Diameter of the center hole")
        self.arg_parser.add_argument(
                "--stgc_encoder_diameter",
                type=float, default=0.0,
                help="Outer diameter of the last track")
        self.arg_parser.add_argument(
                "--stgc_track_width",
                type=float, default=0.0,
                help="Width of track")

    # This function just concatenates the point and the command and returns
    # the data string
    def parse_path_data(self, command, point):

        path_data = command + ' %f ' % point[0] + ' %f ' % point[1]
        return path_data

    # Creates a gray code of size bits (n >= 1) in the format of a list
    def create_gray_code(self, bits):

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
    def draw_gray_encoder(
            self, line_style, bits, encoder_diameter, track_width,
            track_distance):
        gray_code = self.create_gray_code(bits)

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
                    segment = self.draw_segment(
                                line_style,
                                start_angle_position * position_size,
                                segment_size * position_size,
                                current_encoder_diameter,
                                track_width)
                    segments.append(segment)

                    segment_size = 0
                    previous_item = False
                    start_angle_position = 0

                index += 1

            if previous_item:
                segment = self.draw_segment(
                        line_style,
                        start_angle_position * position_size,
                        segment_size * position_size,
                        current_encoder_diameter, track_width)
                segments.append(segment)
                segment_size = 0
                previous_item = False
                start_angle_position = 0
            current_encoder_diameter -= (2 * track_distance + 2 * track_width)
            index = 0

        return segments

    # Check if there is too many cutouts compared to number of sensors
    def valid_single_track_gray_encoder(self, cutouts, sensors):
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
    def draw_single_track_gray_encoder(
            self, line_style, cutouts, sensors, encoder_diameter, track_width):

        segments = []
        resolution = 360.0 / (cutouts * 2 * sensors)
        current_angle = 0.0
        added_angle = ((2 * cutouts + 1) * resolution)
        for n in range(cutouts):
            current_segment_size = ((n * 2 + 2) * cutouts + 1) * resolution
            segments.append(
                self.draw_segment(
                    line_style, current_angle,
                    current_segment_size,
                    encoder_diameter, track_width))
            current_angle += added_angle + current_segment_size

        return segments

    def draw_label(
            self, group, angle, segment_angle, outer_diameter, labelNum):
        outer_radius = outer_diameter / 2
        label_angle = angle + (segment_angle / 2)
        point = calculate_point(label_angle, outer_radius)
        matrix = Transform('rotate(' + str(label_angle + 90) + ')').matrix
        matrix_str = str(matrix[0][0]) + "," + str(matrix[0][1])
        matrix_str += "," + str(matrix[1][0])
        matrix_str += "," + str(matrix[1][1]) + ",0,0"
        text = {
            'id': 'text' + str(labelNum),
            'style': 'font-size: 6px;font-style: normal;font-family: Sans',
            'x': str(point[0]),
            'y': str(point[1]),
            }
        textElement = etree.SubElement(group, inkex.addNS('text', 'svg'), text)
        textElement.text = string.printable[labelNum % len(string.printable)]

        self.svg.get_current_layer().append(textElement)

    # This function creates the path for one single segment
    def draw_segment(
            self, line_style, angle, segment_angle, outer_diameter, width):

        path = {'style': str(inkex.Style(line_style))}
        path['d'] = ''
        outer_radius = outer_diameter / 2

        # Go to the first point in the segment
        path['d'] += self.parse_path_data(
                'M', calculate_point(angle, outer_radius - width))

        # Go to the second point in the segment
        path['d'] += self.parse_path_data(
                'L', calculate_point(angle, outer_radius))

        # Go to the third point in the segment, draw an arc
        point = calculate_point(angle + segment_angle, outer_radius)
        path['d'] += self.parse_path_data('A', [outer_radius, outer_radius])
        path['d'] += '0 0 1' + self.parse_path_data(' ', point)

        # Go to the fourth point in the segment
        point = calculate_point(angle + segment_angle, outer_radius - width)
        path['d'] += self.parse_path_data('L', point)

        # Go to the beginning in the segment, draw an arc
        point = calculate_point(angle, outer_radius - width)
        # 'Z' closes the path
        path['d'] += (self.parse_path_data(
            'A',
            [outer_radius - width, outer_radius - width]) +
                '0 0 0' + self.parse_path_data(' ', point) + ' Z')

        # Return the path
        return path

    # This function adds an element to the document
    def add_element(self, element_type, group, element_attributes):
        etree.SubElement(
            group, inkex.addNS(element_type, 'svg'),
            element_attributes)

    def draw_circles(self, hole_diameter, diameter):
        # Attributes for the center hole, if diameter is larger than 0,
        # create it
        circle_elements = []
        attributes = {
            'style': str(inkex.Style({'stroke': 'none', 'fill': 'black'})),
            'r': str(hole_diameter / 2)
        }
        if self.options.hole_diameter > 0:
            circle_elements.append(attributes)

        # Attributes for the guide hole in the center hole, then create it
        attributes = {
            'style': str(inkex.Style(
                {'stroke': 'white', 'fill': 'white', 'stroke-width': '0.1'})),
            'r': '1'
        }
        circle_elements.append(attributes)

        # Attributes for the outer rim, then create it
        attributes = {
            'style': str(inkex.Style(
                {'stroke': 'black', 'stroke-width': '1', 'fill': 'none'})),
            'r': str(diameter / 2)
        }
        if self.options.diameter > 0:
            circle_elements.append(attributes)

        return circle_elements

    def draw_common_circles(self, group, diameter, hole_diameter):
        circle_elements = self.draw_circles(hole_diameter, diameter)

        for circle in circle_elements:
            self.add_element('circle', group, circle)

    # Binary reflected gray code encoder
    def effect_brgc(self, group, line_style, diameter, hole_diameter):
        center_hole_r = self.options.brgc_hole_diameter / 2
        diameter = self.options.encoder_diameter / 2
        encoder_width = self.options.bits * self.options.track_width
        encoder_width += (self.options.bits - 1) * self.options.track_distance
        if ((diameter - encoder_width) < center_hole_r):
            inkex.errormsg("Innermost encoder smaller than the center hole!")
        else:
            segments = self.draw_gray_encoder(
                line_style, self.options.bits,
                self.options.encoder_diameter,
                self.options.track_width,
                self.options.track_distance)
            for item in segments:
                self.add_element('path', group, item)

        self.draw_common_circles(group, diameter, hole_diameter)

    # Single track gray code encoder
    def effect_stgc(self, group, line_style, diameter, hole_diameter):
        encoder_r = self.options.stgc_encoder_diameter / 2
        hole_r = self.options.stgc_hole_diameter / 2
        if ((encoder_r - self.options.stgc_track_width) < hole_r):
            inkex.errormsg("Encoder smaller than the center hole!")
        elif not self.valid_single_track_gray_encoder(
                self.options.cutouts, self.options.sensors):
            inkex.errormsg("Too many cutouts compared to number of sensors!")
        else:
            segments = self.draw_single_track_gray_encoder(
                    line_style, self.options.cutouts, self.options.sensors,
                    self.options.stgc_encoder_diameter,
                    self.options.stgc_track_width)
            for item in segments:
                self.add_element('path', group, item)

        self.draw_common_circles(group, diameter, hole_diameter)

    # Regular rotary encoder
    def effect_rotary_encoder(
            self, group, line_style, diameter, hole_diameter):
        # Angle of one single segment
        segment_angle = 360.0 / (self.options.segments * 2)

        for segment_number in range(0, self.options.segments):
            angle = segment_number * (segment_angle * 2)
            outer_r = self.options.outer_encoder_diameter / 2
            if (self.options.outer_encoder_width > 0
                    and self.options.outer_encoder_diameter > 0
                    and outer_r > self.options.outer_encoder_width):

                segment = self.draw_segment(
                        line_style, angle, segment_angle,
                        self.options.outer_encoder_diameter,
                        self.options.outer_encoder_width)
                self.add_element('path', group, segment)

            # If the inner encoder diameter is something else than 0; create it
            inner_r = self.options.inner_encoder_diameter / 2
            if (self.options.outer_encoder_width > 0
                    and self.options.inner_encoder_diameter > 0
                    and inner_r > self.options.inner_encoder_width):

                # The inner encoder must be half an encoder segment ahead of
                # the outer one
                segment = self.draw_segment(
                    line_style, angle + (segment_angle / 2), segment_angle,
                    self.options.inner_encoder_diameter,
                    self.options.inner_encoder_width)

                self.add_element('path', group, segment)

        self.draw_common_circles(group, diameter, hole_diameter)

    # Bitmap encoder
    def effect_bitmap_encoder(
            self, group, line_style, diameter, hole_diameter):
        bits = self.options.bm_bits
        bm_segments = len(bits)
        # Angle of one single segment
        segment_angle = 360.0 / bm_segments

        for segment_number in range(0, bm_segments):

            angle = segment_number * segment_angle

            if (self.options.bm_outer_encoder_width > 0
                    and self.options.bm_outer_encoder_diameter > 0
                    and self.options.bm_outer_encoder_diameter
                    > self.options.bm_outer_encoder_width):

                self.draw_label(
                        group, angle, segment_angle, self.options.bm_diameter,
                        segment_number)
                # Drawing only the black segments
                if (bits[segment_number] == '1'):
                    segment = self.draw_segment(
                        line_style, angle,
                        segment_angle,
                        self.options.bm_outer_encoder_diameter,
                        self.options.bm_outer_encoder_width)

                    self.add_element('path', group, segment)

        self.draw_common_circles(group, diameter, hole_diameter)

    def effect(self):
        # Put all the elements in a group, center set in the middle of the view
        group = etree.SubElement(self.svg.get_current_layer(), 'g', {
            inkex.addNS('label', 'inkscape'): 'Encoder disk',
            'transform': 'translate' + str(self.svg.namedview.center)
        })

        # Line style for the encoder segments
        line_style = {
            'stroke': 'white',
            'stroke-width': '0',
            'fill': 'black'
        }

        if self.options.tab == "brgc":
            self.effect_brgc(
                    group, line_style, self.options.brgc_diameter,
                    self.options.brgc_hole_diameter)

        if self.options.tab == "stgc":
            self.effect_stgc(
                    group, line_style, self.options.stgc_diameter,
                    self.options.stgc_hole_diameter)

        if self.options.tab == "rotary_enc":
            self.effect_rotary_encoder(
                    group, line_style, self.options.diameter,
                    self.options.hole_diameter)

        if self.options.tab == "bitmap_enc":
            self.effect_bitmap_encoder(
                    group, line_style, self.options.bm_diameter,
                    self.options.bm_hole_diameter)


if __name__ == '__main__':
    EncoderDiskGenerator().run()
