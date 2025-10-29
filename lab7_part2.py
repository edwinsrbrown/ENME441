import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# initialize GPIO pin numbers, initial values, and pwm frequency
led_pins = [14, 15, 18]
led_init = [0, 0, 0]
led_pwm =[]
freq = 1000

# sets up PWM for each LED
pwm_pins = {}
for k in led_pins:
    GPIO.setup(k, GPIO.OUT)
    pwm = GPIO.PWM(k, freq)
    pwm.start(0)
    led_pwm.append(pwm)


# parses POST data from the HTTP request
def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n') + 4  
    data = data[idx:]                
    data_pairs = data.split('&')     
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict


# generates the web interface HTML page
def html_java():
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


HOST = ''
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print(f"Type http://<IP Address>:{port}/")

try:
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode('utf-8')
        if not request:
            continue

        # --- inline handle_request logic ---
        if request.startswith("POST"):
            data = parsePOSTdata(request)
            
            try:
                led = int(data.get("led", 0))
                brightness = int(data.get("brightness", 0))
                
                if 'led' in data and 'brightness' in data:
                    led_init[led] = brightness
                    pwm_pins[led].ChangeDutyCycle(brightness)
            
            except Exception as e:
                print("POST err:", e)

        # prepare and send HTTP response
        response = html_page()
        conn.sendall(response.encode('utf-8'))
        conn.close()
            
except KeyboardInterrupt:
    print("\nEnding.")
finally:
    for pwm in led_pwm:
        pwm.stop()
    GPIO.cleanup()


if __name__ == "__main__":
    main()
