import sys
import xml.etree.ElementTree as ET
from datetime import datetime

dateFormat = "%Y-%m-%dT%H:%M:%SZ"
namespace = "http://www.topografix.com/GPX/1/1"
namespaces = { 'gpxtpx' : 'http://www.topografix.com/GPX/1/1' }
ET.register_namespace('', namespace)

class Track:
	pass

def getTracks(hrFilename):
	tracks = []
	tree = ET.parse(hrFilename)
	root = tree.getroot()
	trkseg = getElement(getElement(root, 'trk'), 'trkseg')
	for track in getElements(trkseg, 'trkpt'):		
		time = getElement(track, 'time')
		extensions = getElement(track, 'extensions')
		
		el = Track()
		el.time = datetime.strptime(time.text, dateFormat)
		if extensions:
			el.hr = getElement(extensions, 'hr').text
			el.cadence = getElement(extensions, 'cadence').text

		tracks.append(el)
	return tracks
	
def getElement(tag, name):
	return tag.find('gpxtpx:%s' % name, namespaces)
	
def getElements(tag, name):
	return tag.findall('gpxtpx:%s' % name, namespaces)

def hasExtensions(track):
	for attr in track:
		if 'extensions' in attr.tag:
			return True;
	return False;

def matchHrToTracks(hrTracks, noHrTracks):
	for track in noHrTracks:
		for hrTrack in hrTracks:
			if track.time == hrTrack.time:
				track.hr = hrTrack.hr
				track.cadence = hrTrack.cadence
				break
			else:
				if isInProperTimeRange(track.time, hrTrack.time):
					if not hasattr(track, 'possibleHRs'):
						track.possibleHRs = []
						track.possibleCadence = []
					track.possibleHRs.append(hrTrack.hr)
					track.possibleCadence.append(hrTrack.cadence)
				track.hr = 0
				track.cadence = 0

	return noHrTracks
		
def isInProperTimeRange(firstDate, secondDate):
	return abs(firstDate - secondDate).seconds <= 3

def average(hrs):
	sum = 0
	for hr in hrs:
		sum += float(hr)
	return float(sum / len(hrs))
	
def getAverageElement(list):
	return average(list) if len(list) > 1 else list[0]

def getConsecutiveElements(unsortedList):	
	outerList = []
	innerListIdx = 0
	for id in unsortedList:
		innerList = outerList[innerListIdx] if len(outerList) else []
		
		if innerList == []:
			innerList.append(id)
			outerList.append(innerList)
		else:
			lastElement = innerList[len(innerList) - 1]
			if abs(lastElement - id) == 1:
				innerList.append(id)
			else:
				newList = []
				newList.append(id)
				outerList.append(newList)
				innerListIdx += 1
	return outerList
	
if len(sys.argv) < 3:
	raise sys.exit("Filenames not provided")
	
filenameHR = sys.argv[1]
filenameWoHR = sys.argv[2]

hrTracks = getTracks(filenameHR)
woHrTracks = getTracks(filenameWoHR)

print ('HR tracks from file:', filenameHR, len(hrTracks), 'tracks found')
print ('Speed tracks from file:', filenameWoHR, len(woHrTracks), 'tracks found')

### if time matches take hr and cadence from corresponding track
### if time doesn't match take hr and cadence from track within 3 sec range and put in possibleHRs array
### if time is outside 3 sec range -> hr and cadence are 0
matchHrToTracks(hrTracks, woHrTracks)

hrCounter = 0
cadenceCounter = 0
noHRs = []
noCadences = []

for track in woHrTracks:
	if hasattr(track, 'possibleHRs'):
		track.hr = getAverageElement(track.possibleHRs)
		track.cadence = getAverageElement(track.possibleCadence)
	if track.hr == 0:
		noHRs.append(hrCounter)
	if track.cadence == 0:
		noCadences.append(cadenceCounter)

	hrCounter += 1
	cadenceCounter += 1
sortedHRs = getConsecutiveElements(noHRs)
sortedCadences = getConsecutiveElements(noCadences)

for sortedHR in sortedHRs:
	firstElement = sortedHR[0]
	lastElement = sortedHR[len(sortedHR) - 1]
	
	for element in sortedHR:
		properHR = 0
		if firstElement == 0:
			properHR = woHrTracks[lastElement + 1].hr
		elif lastElement == len(woHrTracks) - 1:
			properHR = woHrTracks[firstElement - 1].hr
		else:
			properHR = float((float(woHrTracks[firstElement - 1].hr) + float(woHrTracks[lastElement + 1].hr))/2)
		woHrTracks[element].hr = properHR

for sortedCadence in sortedCadences:
	firstElement = sortedCadence[0]
	lastElement = sortedCadence[len(sortedCadence) - 1]
	
	for element in sortedCadence:
		properCadence = 0
		if firstElement == 0:
			properCadence = woHrTracks[lastElement + 1].cadence
		elif lastElement == len(woHrTracks) - 1:
			properCadence = woHrTracks[firstElement - 1].cadence
		else:
			properCadence = float((float(woHrTracks[firstElement - 1].cadence) + float(woHrTracks[lastElement + 1].cadence))/2)
		woHrTracks[element].cadence = properCadence

tree = ET.parse(filenameWoHR)
root = tree.getroot()
tracks = root[1][2]
idx = 0
for track in tracks:
	extensions = ET.Element("extensions")
	trackPointExtension = ET.Element("gpxtpx:TrackPointExtension")
	hr = ET.Element("gpxtpx:hr")
	cadence = ET.Element("gpxtpx:cad")
	
	hr.text = str(woHrTracks[idx].hr)
	cadence.text = str(woHrTracks[idx].cadence)
	
	track.append(extensions)		
	track[2].append(trackPointExtension)
	track[2][0].append(hr)
	track[2][0].append(cadence)
	idx += 1

tree.write('fixed_'+ filenameWoHR)


