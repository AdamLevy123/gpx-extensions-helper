# gpx-extensions-helper
This tool lets you use your friend's gpx track as your activity without his HR, cadence, etc.
Usage example:
py fix-gpx.py Morning_Ride.gpx

And the other one is for merging hr and cadence info from one gpx to the other based on timestamp
Usage example:
py merge-gpx.py Morning_Ride_without_hr.gpx Morning_Ride_with_HR.gpx
