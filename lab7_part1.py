import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# initialize GPIO pin numbers, initial values, and pwm frequency
led_pins = {'1': 14, '2': 15, '3': 18}
led_init = {'1': 0, '2': 0, '3': 0}
freq = 1000

# sets up PWM for each LED
pwm_pins = {}
for led, pin in led_pins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, freq)
    pwm.start(0)
    pwm_pins[led] = pwm


# given in slides
def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n')+4  
    data = data[idx:]                
    data_pairs = data.split('&')     
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict


# generates the HTML/Java web interface
def html():
   return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LED Brightness Control</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    border: 3px solid black;
    width: 250px;
    padding: 15px;
  }}
  label {{
    display: block;
    margin-top: 10px;
  }}
  input[type="range"] {{
    width: 100%;
  }}
  input[type="submit"] {{
    margin-top: 15px;
  }}
</style>
</head>
<body>
  <form method="POST">
    <label for="brightness">Brightness level:</label>
    <input type="range" id="brightness" name="brightness" min="0" max="100" value="0">

    <label style="margin-top:10px;">Select LED:</label>
    <input type="radio" id="led1" name="led" value="0" required>
    <label for="led1">LED 1 ({led_init[0]}%)</label><br>

    <input type="radio" id="led2" name="led" value="1">
    <label for="led2">LED 2 ({led_init[1]}%)</label><br>

    <input type="radio" id="led3" name="led" value="2">
    <label for="led3">LED 3 ({led_init[2]}%)</label><br>

    <input type="submit" value="Change Brightness">
  </form>
</body>
</html>"""


HOST = ''
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print("Type http://<IP Address>:8080")

try:
    while True:
        conn, addr = s.accept()
        with conn:
            request = conn.recv(1024).decode('utf-8')
            if not request:
                continue

            # handle POST requests
            if request.startswith("POST"):
                try:
                    data = parsePOSTdata(request)
                    if 'led' in data and 'brightness' in data:
                        led = data['led']
                        brightness = int(data['brightness'])
                        led_init[led] = brightness
                        pwm_pins[led].ChangeDutyCycle(brightness)
                except Exception as e:
                    print("POST error:", e)

            # send HTTP response (needed LLM assistance with this)
            response_body = html()
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n" +
                response_body
            )
            conn.sendall(response.encode('utf-8'))

except KeyboardInterrupt:
    print("\nEnding.")
finally:
    for pwm in pwm_pins.values():
        pwm.stop()
    GPIO.cleanup()
