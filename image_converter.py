#!/usr/bin/env python3
"""
Converts images into a format suitable for display on Badger 2040.

Optionally resizes images to 296x128 to fit the display.

Crunches images down to dithered, 1bit colour depth.

Outputs either in raw binary format or as a .py file for embedding into MicroPython.

Output to py functionality is borrwed from data_to_py.py, Copyright (c) 2016 Peter Hinch
"""

import argparse
import io
from pathlib import Path

from PIL import Image, ImageEnhance

PY_HEADER = """# Code generated by convert.py.
"""

PY_FOOTER = """_mvdata = memoryview(_data)

def data():
    return _mvdata

"""


parser = argparse.ArgumentParser(description='Converts images into the format used by Badger2040.')
parser.add_argument('file', nargs="+", help='input files to convert')
parser.add_argument('--out_dir', type=Path, default=None, help='output directory')
parser.add_argument('--binary', action="store_true", help='output binary file for MicroPython')
parser.add_argument('--py', action="store_true", help='output .py file for MicroPython embedding')
parser.add_argument('--resize', action="store_true", help='force images to 296x128 pixels')
parser.add_argument('--bg', default=None, choices={'black', 'white'}, help='add a background color for images with transparency')

options = parser.parse_args()


class ByteWriter(object):
  bytes_per_line = 16

  def __init__(self, stream, varname):
    self.stream = stream
    self.stream.write('{} =\\\n'.format(varname))
    self.bytecount = 0  # For line breaks

  def _eol(self):
    self.stream.write("'\\\n")

  def _eot(self):
    self.stream.write("'\n")

  def _bol(self):
    self.stream.write("b'")

  # Output a single byte
  def obyte(self, data):
    if not self.bytecount:
      self._bol()
    self.stream.write('\\x{:02x}'.format(data))
    self.bytecount += 1
    self.bytecount %= self.bytes_per_line
    if not self.bytecount:
      self._eol()

  # Output from a sequence
  def odata(self, bytelist):
    for byt in bytelist:
      self.obyte(byt)

  # ensure a correct final line
  def eot(self):  # User force EOL if one hasn't occurred
    if self.bytecount:
      self._eot()
    self.stream.write('\n')


def convert_image(img):
  if options.bg:
    bg = Image.new('RGBA', img.size, options.bg)
    bg.paste(img, mask=img)
    img = bg
  if options.resize:
    img = img.resize((296, 128))  # resize
  try:
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
  except ValueError:
    pass
  img = img.convert("1")  # convert to black and white
  return img


def write_stream(header, footer, ip_stream, op_stream):
  op_stream.write(header)
  op_stream.write('\n')
  data = ip_stream.read()
  bw_data = ByteWriter(op_stream, '_data')
  bw_data.odata(data)
  bw_data.eot()
  op_stream.write(footer)


# create map of images based on input filenames
for input_filename in options.file:
  with Image.open(input_filename) as img:
    img = convert_image(img)

    image_name = Path(input_filename).stem

    w, h = img.size

    output_data = [~b & 0xff for b in list(img.tobytes())]

    if options.binary:
      if options.out_dir is not None:
        output_filename = (options.out_dir / image_name).with_suffix(".bin")
      else:
        output_filename = Path(input_filename).with_suffix(".bin")
      print(f"Saving to {output_filename}, {w}x{h}")
      with open(output_filename, "wb") as out:
        out.write(bytearray(output_data))
    elif options.py:
      if options.out_dir is not None:
        output_filename = (options.out_dir / image_name).with_suffix(".py")
      else:
        output_filename = Path(input_filename).with_suffix(".py")
      print(f"Saving to {output_filename}, {w}x{h}")
      with open(output_filename, "w") as out:
        write_stream(PY_HEADER, PY_FOOTER, io.BytesIO(bytes(output_data)), out)
    else:
      image_code = '''\
static const uint8_t {image_name}[{count}] = {{
    {byte_data}
}};
    '''.format(image_name=image_name, count=len(output_data), byte_data=", ".join(str(b) for b in output_data))

      print(image_code)
