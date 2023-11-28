import serial

# Define the serial port and baud rate
port = "/dev/ttyS0"  # Replace with your serial port (e.g., "/dev/ttyUSB0" for USB)
baud_rate = 9600  # Set the baud rate

# Open the serial port
try:
    serial_port = serial.Serial(port, baud_rate)
    print("Serial port opened successfully")
except serial.SerialException as e:
    print(f"Failed to open serial port: {e}")
    exit()

# Reading data from the serial port
try:
    while True:
        if serial_port.in_waiting > 0:
            data = serial_port.readline().decode().strip()  # Read and decode data
            print(f"Received data: {data}")
except KeyboardInterrupt:
    print("\nExiting...")
    serial_port.close()
