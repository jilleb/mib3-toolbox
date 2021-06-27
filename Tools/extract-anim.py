#----------------------------------------------------------
#--- Quick 'n' dirty ANIM file decompressor
#
# File:        extract_anim
# Author:      Jille
# Revision:    2
# Purpose:     Extract MIB3 startScript_x.anim startup images files.
# Comments:    Usage: extract_anim.py <filename> <outdir>
# Changelog:   1:   First version
#              2:   BGRA to RGBA conversion to prevent red R-lines ;-) 
#----------------------------------------------------------

import struct
import sys
import os
import zlib

if sys.version_info[0] < 3:
    sys.exit("You need to run this with Python 3")

try:
  from PIL import Image
except ImportError:
  sys.exit("""  You are missing the PIL module!
  install it by running: 
  pip install image""")

if len(sys.argv) != 3:
  print ('usage: extract_anim.py <filename> <outdir>')
  sys.exit(1)

out_dir = sys.argv[2]
if not os.path.exists(out_dir):
  os.mkdir(out_dir)

data = open(sys.argv[1],'rb').read()
offset = 0
filesize = sys.getsizeof(data)
print("Size: %d" %(filesize))

(magic,) = struct.unpack_from('<8s', data, offset)
offset = offset + 12


(cmdblock_len,) = struct.unpack_from('<L', data, offset)
print ("cmdblock_len: %d" %(cmdblock_len))


offset = offset+cmdblock_len+16
(number_of_files,) = struct.unpack_from('<L', data, offset)
print ("number_of_files: %d" %(number_of_files))

i = 0
j = 0
offset = offset + 4
offsets_array = []

#fill offsets+array
while (i < number_of_files):
	(file_offset,) = struct.unpack_from('<L', data, offset)
	offsets_array.append(file_offset)
	offset = offset + 4
	i = i + 1

while j < number_of_files:
    offset = offsets_array[j]
    (img_width, img_height) = struct.unpack_from('<LL', data, offset)
    #print ("%d: %d - %dx%d" %(j,offset, img_width,img_height))
    offset = offset + 8
    if (j != number_of_files-1):
        zlibdata = data[offset:offsets_array[j+1]]
    else:
        zlibdata = data[offset:filesize]
    zlib_decompress = zlib.decompress(zlibdata)
    im = Image.frombuffer('RGBA', (img_width, img_height), zlib_decompress, 'raw', 'RGBA', 0, 1)
    b,g,r,a = im.split()
    rgb = Image.merge("RGBA", (r,g,b,a))
    print("extracting %d to %s\img_%d.png" % (j, out_dir, j))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_path = os.path.join(out_dir, 'img_%d.png' % j)
    rgb.save(out_path)
            
    j = j+1
