import socket
import RPi.GPIO as GPIO

# -------------------------------
# Hardware setup
# -------------------------------
GPIO.setmode(GPIO.BCM)
LED_PINS = [17, 27, 22]  # example GPIO pins for LED1, LED2, LED3
pwms = []

# Initialize PWM for each LED
for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 1000)  # 1 kHz PWM frequency
    pwm.start(0)
    pwms.append(pwm)

# Keep track of brightness levels for each LED
led_brightness = [0, 0, 0]

# -------------------------------
# HTML page generator
# -------------------------------
def generate_html():
    return f"""\
HTTP/1.1 200 OK
Content-Type: text/html

<html>
<head>
    <title>LED Brightness Control</title>
</head>
<body>
    <h3>Brightness level:</h3>
    <form method="POST">
        <input type="range" name="brightness" min="0" max="100" value="50"><br><br>
        <b>Select LED:</b><br>
        <input type="radio" name="led" value="0" checked> LED 1 ({led_brightness[0]}%)<br>
        <input type="radio" name="led" value="1"> LED 2 ({led_brightness[1]}%)<br>
        <input type="radio" name="led" value="2"> LED 3 ({led_brightness[2]}%)<br><br>
        <input type="submit" value="Change Brightness">
    </form>
    <hr>
    <h4>Current LED Brightness Levels:</h4>
    <ul>
        <li>LED 1: {led_brightness[0]}%</li>
        <li>LED 2: {led_brightness[1]}%</li>
        <li>LED 3: {led_brightness[2]}%</li>
    </ul>
</body>
</html>
"""

# -------------------------------
# Main TCP server loop
# -------------------------------
HOST = ''  # listen on all interfaces
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server running on port {PORT}... Visit http://<Pi_IP_address>:{PORT}")

try:
    while True:
        conn, addr = server_socket.accept()
        request = conn.recv(1024).decode('utf-8')
        
        # Debug: print raw HTTP request
        # print(request)
        
        # Determine request type
        if request.startswith('POST'):
            # Extract POST data (after blank line)
            body = request.split('\r\n\r\n')[1]
            
            # Parse form data
            data = dict(param.split('=') for param in body.split('&'))
            selected_led = int(data.get('led', 0))
            new_brightness = int(data.get('brightness', 0))
            
            # Update LED brightness
            led_brightness[selected_led] = new_brightness
            pwms[selected_led].ChangeDutyCycle(new_brightness)
        
        # Send HTML response
        response = generate_html()
        conn.sendall(response.encode('utf-8'))
        conn.close()

except KeyboardInterrupt:
    print("\nShutting down server...")

finally:
    for pwm in pwms:
        pwm.stop()
    GPIO.cleanup()
    server_socket.close()
