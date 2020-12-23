# Console interface application that connects to an MSP432P4001R embedded board
# through Serial UART. The application allows the user to control the internal
# board state machine responsible for controlling the on-board LED's.

import serial
import threading
from os import system, name

# Connection Fields
COM_NAME = "COM3"
BAUD_RATE = 1200

current_status = "" # Current state machine status

# Threaded function that listens and processes received serial data
def listen_state_change(serialport):
    global stop_thread
    global current_status

    while True:
        # Check if thread is not terminated
        if stop_thread:
            break

        command = serialport.read(1).decode("utf-8") # Read and convert one byte into a utf-8 string

        # Check received string and update status
        if command == 'F':
            output_interface(1)
        elif command != '':
            current_status = command
            output_interface() # Update interface with status change

# Clear console screen
def clear():
    if name == 'nt':  # for windows
        _ = system('cls')
    else:  # for mac and linux(here, os.name is 'posix')
        _ = system('clear')

# Prints program interface with option of error messages
def output_interface(error_code=0):
    clear()
    print("UART Control Console Application \n")
    print("States:")
    print("1 - Both Led's OFF")
    print("2 - Only P1 Led ON")
    print("3 - Only P2 Led ON")
    print("4 - Both Led's ON\n")
    print("Commands:")
    print("A - Increment state")
    print("D - Decrement state")
    print("S - Request current state")
    print("X - Exit the application \n")
    print("Current Status:", current_status)
    if error_code == 1:
        print("Change state request failed!")
    elif error_code == 2:
        print("Please input a single character only!")
    print("\nInput Command:", end="", flush=True)

# Sends a one char status change request to device
def change_status(serialport, status):
    if len(status) == 1:
        serialport.write(status.encode('utf-8'))
    else:
        output_interface(2)

# Starts serial UART connection with device
def serial_connect(com_name, baud_rate):
    try:
        return serial.Serial(com_name, baud_rate)
    except Exception as error:
        print(error)
        exit()

# Sends a request asking for the current status of the device
def request_current_status(serialport):
    global current_status
    serialport.write(b"S") # Device interrupts S char as return status request
    status = serialport.read(1).decode("utf-8") # Read and decode returned data

    # Check returned data and update status
    if status == 'F':
        current_status = "Unknown"
    else:
        current_status = status

if __name__ == "__main__":
    # Main Script #
    serial_port = serial_connect(COM_NAME, BAUD_RATE) # Connect to serial Device
    request_current_status(serial_port) # Send a request for current status of device

    output_interface()

    # Creating a thread for listen_state_change function
    stop_thread = False
    listen_thread = threading.Thread(target=listen_state_change, args=(serial_port,))
    listen_thread.start()

    # Wait for user input
    while True:
        input_status = input()

        # X or x to terminate connection and program
        if input_status == "X" or input_status == "x":
            break

        change_status(serial_port, input_status)

    # Stop listen thread
    stop_thread = True
    #listen_thread.join()

    serial_port.close() # Close the serial connection
    exit()

