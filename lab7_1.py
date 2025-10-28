import socket
from urllib.parse import parse_qs
import RPi.GPIO as GPIO

# =======================
# GPIO SETUP
# =======================
GPIO.setmode(GPIO.BCM)

# Assign GPIO pins for LEDs (change these if needed)
LED_PINS = {'1': 17, '2': 27, '3': 22}
PWM_FREQUENCY = 1000  # Hz

# Initialize PWM channels
pwm_channels = {}
for led, pin in LED_PINS.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, PWM_FREQUENCY)
    pwm.start(0)  # start with LEDs off
    pwm_channels[led] = pwm

# Track current LED brightness values
led_values = {'1': 0, '2': 0, '3': 0}


# =======================
# HTML PAGE
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
        width: 230px;
        padding: 10px;
        font-family: Arial, sans-serif;
    }}
    label {{
        display: block;
        margin-top: 8px;
    }}
    input[type="range"] {{
        width: 100%;
    }}
    input[type="submit"] {{
        margin-top: 10px;
        width: 100%;
    }}
</style>
</head>
<body>
    <form method="POST">
        <label for="brightness">Brightness level:</label>
        <input type="range" id="brightness" name="brightness" min="0" max="100" value="0">

        <label style="margin-top: 10px;">Select LED:</label>
        <input type="radio" id="led1" name="led" value="1" checked>
        <label for="led1">LED 1 ({led_values['1']}%)</label><br>

        <input type="radio" id="led2" name="led" value="2">
        <label for="led2">LED 2 ({led_values['2']}%)</label><br>

        <input type="radio" id="led3" name="led" value="3">
        <label for="led3">LED 3 ({led_values['3']}%)</label><br>

        <input type="submit" value="Change Brightness">
    </form>
</body>
</html>"""


# =======================
# REQUEST HANDLER
# =======================
def handle_request(request):
    global led_values

    if request.startswith("POST"):
        try:
            body = request.split("\r\n\r\n", 1)[1]
            data = parse_qs(body)
            if 'led' in data and 'brightness' in data:
                led = data['led'][0]
                brightness = int(data['brightness'][0])
                led_values[led] = brightness

                # Apply PWM brightness
                pwm_channels[led].ChangeDutyCycle(brightness)
                print(f"Updated LED {led} to {brightness}% brightness.")
        except Exception as e:
            print("Error processing POST data:", e)

    # Return updated HTML
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
            print("\nShutting down server...")
        finally:
            for pwm in pwm_channels.values():
                pwm.stop()
            GPIO.cleanup()
            print("GPIO cleaned up. Goodbye!")


if __name__ == "__main__":
    run_server()
