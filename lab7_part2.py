import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# initialize GPIO pin numbers, initial values, and pwm frequency
led_pins = {'1': 14, '2': 15, '3': 18}
led_init = {'1': 0, '2': 0, '3': 0}
freq = 1000

#sets up PWM for each LED
pwm_pins = {}
for led, pin in led_pins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, freq)
    pwm.start(0)
    pwm_pins[led] = pwm

# given from slides
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

# LLM generated HTML and Java code
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
    <input type="range" id="led1" min="0" max="100" value="{led_init['1']}" oninput="updateLED(1, this.value)">
    <span id="val1">{led_init['1']}</span>
  </div>

  <div class="led-control">
    <label>LED2</label>
    <input type="range" id="led2" min="0" max="100" value="{led_init['2']}" oninput="updateLED(2, this.value)">
    <span id="val2">{led_init['2']}</span>
  </div>

  <div class="led-control">
    <label>LED3</label>
    <input type="range" id="led3" min="0" max="100" value="{led_init['3']}" oninput="updateLED(3, this.value)">
    <span id="val3">{led_init['3']}</span>
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

# defining a function for parsing the message (example code also shown in slides)
def handle_request(request):
    global led_init

    # only follows through if given request is a POST request
    if request.startswith("POST"):
        try:
            # takes the data and assigns it to variable 'data'
            data = parsePOSTdata(request)  
            if 'led' in data and 'brightness' in data:
                led = data['led']
                brightness = int(data['brightness'])
                led_init[led] = brightness
                pwm_pins[led].ChangeDutyCycle(brightness)
        except Exception as e:
            print("POST error:", e)

    # sends the HTTP response 
    response_body = html_page()
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        "\r\n" +
        response_body
    )
    return response

def run(host='', port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print(f"Type http://IP Address:8080/")

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
            print("Ending.")
        finally:
            for pwm in pwm_pins.values():
                pwm.stop()
            GPIO.cleanup()
            


if __name__ == "__main__":
    run()
