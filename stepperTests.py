import Jetson.GPIO as GPIO
import time

# Pin Definitions
# Define the GPIO pins for the stepper motors
# Update these pin numbers based on your wiring
F_STEP_PIN = 15
F_DIR_PIN = 12
F_SLEEP_PIN = 7

I_STEP_PIN = 35
I_DIR_PIN = 33
I_SLEEP_PIN = 37

Z_STEP_PIN = 21
Z_DIR_PIN = 19
Z_SLEEP_PIN = 23

IRH = 13
IRL = 15
h = 1

# Motor Speeds  DO NOT EXCEED!
F_SPEED = 3200
I_SPEED = 80
Z_SPEED = 3200

# File name to store the motor positions
POSITIONS_FILE = "motor_positions.txt"

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(F_STEP_PIN, GPIO.OUT)
GPIO.setup(F_DIR_PIN, GPIO.OUT)
GPIO.setup(F_SLEEP_PIN, GPIO.OUT)
GPIO.setup(I_STEP_PIN, GPIO.OUT)
GPIO.setup(I_DIR_PIN, GPIO.OUT)
GPIO.setup(I_SLEEP_PIN, GPIO.OUT)
GPIO.setup(Z_STEP_PIN, GPIO.OUT)
GPIO.setup(Z_DIR_PIN, GPIO.OUT)
GPIO.setup(Z_SLEEP_PIN, GPIO.OUT)
GPIO.setup(IRH, GPIO.OUT)
GPIO.setup(IRL, GPIO.OUT)

# Pull sleep pins LOW at the start
GPIO.output(F_SLEEP_PIN, GPIO.LOW)
GPIO.output(I_SLEEP_PIN, GPIO.LOW)
GPIO.output(Z_SLEEP_PIN, GPIO.LOW)

# Motor Positions
F_POSITION = 0
I_POSITION = 0
Z_POSITION = 0

flimit = 9354*4
ilimit = 75*4
zlimit = 4073*4


# Function to rotate a motor
def rotate_motor(step_pin, dir_pin, sleep_pin, steps, direction, speed):
    # Set the motor direction
    if direction == "clockwise":
        GPIO.output(dir_pin, GPIO.HIGH)
    elif direction == "counter-clockwise":
        GPIO.output(dir_pin, GPIO.LOW)

    # Activate sleep pin
    GPIO.output(sleep_pin, GPIO.HIGH)
    time.sleep(0.1)  # Delay before motor movement

    # Rotate the motor
    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(1 / speed)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(1 / speed)

    # Deactivate sleep pin
    GPIO.output(sleep_pin, GPIO.LOW)


# Function to move F motor
def move_F_motor(target_position):
    global F_POSITION
    steps = target_position - F_POSITION
    direction = "clockwise" if steps <= 0 else "counter-clockwise"
    rotate_motor(F_STEP_PIN, F_DIR_PIN, F_SLEEP_PIN, abs(steps), direction, F_SPEED)
    F_POSITION = target_position


# Function to move I motor
def move_I_motor(target_position):
    global I_POSITION
    steps = target_position - I_POSITION
    direction = "clockwise" if steps <= 0 else "counter-clockwise"
    rotate_motor(I_STEP_PIN, I_DIR_PIN, I_SLEEP_PIN, abs(steps), direction, I_SPEED)
    I_POSITION = target_position


# Function to move Z motor
def move_Z_motor(target_position):
    global Z_POSITION
    steps = target_position - Z_POSITION
    direction = "clockwise" if steps <= 0 else "counter-clockwise"
    rotate_motor(Z_STEP_PIN, Z_DIR_PIN, Z_SLEEP_PIN, abs(steps), direction, Z_SPEED)
    Z_POSITION = target_position


# Function to save the motor positions to a file
def save_motor_positions():
    with open(POSITIONS_FILE, "w") as file:
        file.write(f"{F_POSITION},{I_POSITION},{Z_POSITION}")


# Function to load the motor positions from a file
def load_motor_positions():
    try:
        with open(POSITIONS_FILE, "r") as file:
            positions = file.readline().strip().split(",")
            if len(positions) == 3:
                return int(positions[0]), int(positions[1]), int(positions[2])
    except FileNotFoundError:
        pass

    # If the file doesn't exist or the positions couldn't be loaded, return default positions
    return 0, 0, 0

def f_conversion(percentage):
    fnsteps = (percentage * flimit) / 100
    return int(fnsteps)

def i_conversion(percentage):
    insteps = (percentage * ilimit) / 100
    return int(insteps)

def z_conversion(percentage):
    znsteps = (percentage * zlimit) / 100
    return int(znsteps)

# Main program
if __name__ == "__main__":
    # Load motor positions from the file
    F_POSITION, I_POSITION, Z_POSITION = load_motor_positions()

    while True:
        # Pull sleep pins LOW at the start of each iteration
        print("F Motor Position:", F_POSITION)
        print("I Motor Position:", I_POSITION)
        print("Z Motor Position:", Z_POSITION)
        print("F Motor %:", ((F_POSITION/flimit)*100))
        print("I Motor %:", ((I_POSITION/ilimit)*100))
        print("Z Motor %:", ((Z_POSITION/zlimit)*100))
       
        GPIO.output(F_SLEEP_PIN, GPIO.LOW)
        GPIO.output(I_SLEEP_PIN, GPIO.LOW)
        GPIO.output(Z_SLEEP_PIN, GPIO.LOW)

        # Terminal input for motor coordinate and axis
        motor_input = input("Enter the motor axis (F, I, Z) and target coordinate or 'q' to quit: ")

        if motor_input == "q":
            # Save motor positions before quitting
            save_motor_positions()
            break

        # Parse the motor axis and target coordinate
        axis, target_coord = motor_input.split(',')
        target_position = int(target_coord)
        
     #   if target_position < 0:
      #      print("Positive values between 1 and 100 only")
            # Move the specified motor
        if axis == "f":
            move_F_motor(f_conversion(target_position))
        elif axis == "i":
            move_I_motor(i_conversion(target_position))
        elif axis == "z":
            move_Z_motor(z_conversion(target_position))
        else:
            print("Invalid motor axis. Please try again.")

        # Print motor positions
    # Cleanup GPIO
    GPIO.cleanup()
