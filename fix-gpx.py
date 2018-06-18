import sys
import xml.etree.ElementTree as ET

if len(sys.argv) is 1:
	raise sys.exit("Filename not provided")

ET.register_namespace('', "http://www.topografix.com/GPX/1/1")	
	
filename = sys.argv[1]
tree = ET.parse(filename)
root = tree.getroot()

tracks = root[1][2]
for track in tracks:
	track.remove(track[2])

tree.write('fixed_'+ filename)