import socket
import RPi.GPIO as GPIO

# =======================
# GPIO SETUP
# =======================
GPIO.setmode(GPIO.BCM)

LED_PINS = {'1': 17, '2': 27, '3': 22}
PWM_FREQUENCY = 1000  # Hz

pwm_channels = {}
for led, pin in LED_PINS.items():
  GPIO.setup(pin, GPIO.OUT)
	pwm = GPIO.PWM(pin, PWM_FREQUENCY)
	pwm.start(0)
	pwm_channels[led] = pwm

led_values = {'1': 0, '2': 0, '3': 0}


# =======================
# Helper function for POST parsing
# =======================
def parsePOSTdata(data):
	"""
	Custom helper function to extract key=value pairs from POST request body.
	Looks for the start of POST data after headers and splits the pairs manually.
	"""
	data_dict = {}
	idx = data.find('\r\n\r\n') + 4  # find start of POST body
	data = data[idx:]                # extract only the body
	data_pairs = data.split('&')     # split into key=value pairs
	for pair in data_pairs:
		key_val = pair.split('=')
		if len(key_val) == 2:
			data_dict[key_val[0]] = key_val[1]
	return data_dict


# =======================
# HTML + JAVASCRIPT PAGE
# =======================
def html_page():
	return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LED Brightness Control</title>
<style>
	body {{
		border: 3px solid black;
		width: 250px;
		padding: 10px;
		font-family: Arial, sans-serif;
	}}
	.led-control {{
		margin-bottom: 10px;
	}}
	input[type="range"] {{
		width: 140px;
		vertical-align: middle;
	}}
	span {{
		display: inline-block;
		width: 25px;
		text-align: right;
	}}
</style>
</head>
<body>
	<div class="led-control">
		<label>LED1</label>
		<input type="range" id="led1" min="0" max="100" value="{led_values['1']}" oninput="updateLED(1, this.value)">
		<span id="val1">{led_values['1']}</span>
	</div>

	<div class="led-control">
		<label>LED2</label>
		<input type="range" id="led2" min="0" max="100" value="{led_values['2']}" oninput="updateLED(2, this.value)">
		<span id="val2">{led_values['2']}</span>
	</div>

	<div class="led-control">
		<label>LED3</label>
		<input type="range" id="led3" min="0" max="100" value="{led_values['3']}" oninput="updateLED(3, this.value)">
		<span id="val3">{led_values['3']}</span>
	</div>

	<script>
		function updateLED(led, brightness) {{
			document.getElementById('val' + led).textContent = brightness;
			fetch('/', {{
				method: 'POST',
				headers: {{
					'Content-Type': 'application/x-www-form-urlencoded'
				}},
				body: 'led=' + led + '&brightness=' + brightness
			}});
		}}
	</script>
</body>
</html>"""


# =======================
# REQUEST HANDLER
# =======================
def handle_request(request):
	global led_values

	if request.startswith("POST"):
		try:
			data = parsePOSTdata(request)  # <-- use custom parser instead of parse_qs
			if 'led' in data and 'brightness' in data:
				led = data['led']
				brightness = int(data['brightness'])
				led_values[led] = brightness
				pwm_channels[led].ChangeDutyCycle(brightness)
				print(f"LED {led} set to {brightness}%")
		except Exception as e:
			print("POST error:", e)

	# Return updated page
	response_body = html_page()
	response = (
		"HTTP/1.1 200 OK\r\n"
		"Content-Type: text/html\r\n"
		f"Content-Length: {len(response_body)}\r\n"
		"\r\n" +
		response_body
	)
	return response


# =======================
# MAIN SERVER LOOP
# =======================
def run_server(host='', port=8080):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((host, port))
		s.listen(1)
		print(f"LED control server running on http://{host or 'localhost'}:{port}/")
		print("Press Ctrl+C to stop.")

		try:
			while True:
				conn, addr = s.accept()
				with conn:
					request = conn.recv(1024).decode('utf-8')
					if not request:
						continue
					response = handle_request(request)
					conn.sendall(response.encode('utf-8'))
		except KeyboardInterrupt:
			print("\nStopping server...")
		finally:
			for pwm in pwm_channels.values():
				pwm.stop()
			GPIO.cleanup()
			print("GPIO cleaned up. Goodbye!")


if __name__ == "__main__":
	run_server()
