import sys
import xml.etree.ElementTree as ET
from datetime import date, datetime, time, timedelta

if len(sys.argv) == 1:
	raise sys.exit("Filename not provided")
elif len(sys.argv) != 3:
    raise sys.exit("Please provide filename and seconds")

dateFormat = "%Y-%m-%dT%H:%M:%SZ"
ET.register_namespace('', "http://www.topografix.com/GPX/1/1")	
	
filename = sys.argv[1]
seconds = int(sys.argv[2])
tree = ET.parse(filename)
root = tree.getroot()

tracks = root[1][2]
for track in tracks:
    parsedTime = datetime.strptime(track[1].text, dateFormat)
    track[1].text=(parsedTime + timedelta(seconds=seconds)).strftime(dateFormat)

tree.write('shifted_'+ filename)