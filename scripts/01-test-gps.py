from neom8p.main import GPS

# CHANGE THIS TO YOUR SETUP - THIS LINE IS VERY SPECIFIC TO MY SETUP, SEE README.MD
ADDRESS = "/dev/cu.usbserial-14210"

def on_update_fn(latitude, longitude, speedkm):
	print (f"{latitude}, {longitude} | Speed (km/h) {speedkm}")

def on_error_fn(msg):
	print (f"Error: {msg}")

sensor = GPS(port=ADDRESS)

sensor.on_update = on_update_fn
sensor.on_error = on_error_fn

while True:
	sensor.query()

	# if you want, you can split the following string via "\\" - that corresponds to the newline
	print (f"Last incoming signal was: `{sensor.last_gps_stream}`")

