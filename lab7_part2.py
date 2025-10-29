import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# initialize pwm frequency, GPIO pin locations, and initial values
freq = 1000  # Hz
led_pins = {'1': 14, '2': 15, '3': 18}
led_init = {'1': 0, '2': 0, '3': 0}

# create pwm for all pins
pwm_channels = {}
for led, pin in led_pins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, freq)
    pwm.start(0)
    pwm_channels[led] = pwm

# given from slides
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


# =======================
# MAIN SERVER LOOP
# =======================
#function to create host server at Pi ip address -> Lec 7, slide 7
def run_server(host="", port=8080): #port 8080 -> non privilaged alternative to 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket
    s.bind((host, port)) #host IP address through the given PORT
    s.listen(1) # Listen for up to 1 queued connections
    #Print my Pi's IP address and link to control LEDs
    print("Visit http://172.20.10.8:8080 in your browser.")

    while True:
        conn, addr = s.accept() # Accept connection
        with conn:
            data = conn.recv(2048).decode("utf-8") # Receive up to 1024 bytes from client
            if not data:
                continue

            #Collect and parse through data
            if data.startswith("POST"):
                params = parsePOSTdata(data)
                led = params.get("led", "1")
                brightness = params.get("brightness", "0")

                try:
                    #Change duty cycle based on percantage value from slider
                    brightness = int(brightness)
                    brightness = max(0, min(100, brightness))
                    led_values[led] = brightness
                    pwm_leds[led].ChangeDutyCycle(brightness)
                    print(f"LED {led} set to {brightness}% brightness")
                except Exception as e:
                    print("POST parse error:", e)

                # Respond minimally to JS (no page reload)
                conn.sendall(b"HTTP/1.1 204 No Content\r\n\r\n")

            else:  # send updated HTML page
                response = html_page()
                conn.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    run()
