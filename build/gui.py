from pathlib import Path
import queue
# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox, filedialog
from tkinter import ttk
import serial.tools.list_ports
import serial
import csv
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import sys
import numpy as np



OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("assets/frame0")

#ASSETS_PATH = OUTPUT_PATH / Path(r"E:\Adobe Dont Move\Projects Pending\Shawiaz FYP\Boost Converter DashBoard\build\assets\frame0")

# Declare ser as a global variable
ser = None

#def relative_to_assets(path: str) -> Path:
 #   return ASSETS_PATH / Path(path)
def relative_to_assets(path: str) -> Path:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).parent

    return Path(base_path) / "assets" / "frame0" / Path(path)

window = Tk()

window.geometry("1366x768")
window.configure(bg = "#353535")


# ======================Create a new figure and subplot
fig = Figure(figsize=(3, 4), dpi=100)
fig.set_facecolor("#DCDCDC")
ax = fig.add_subplot(111)
ax.set_facecolor("#DCDCDC")  

# Change the color of the axis lines to white
ax.spines['bottom'].set_color('black')
ax.spines['top'].set_color('black') 
ax.spines['right'].set_color('black')
ax.spines['left'].set_color('black')

ax.xaxis.label.set_color('black')
ax.yaxis.label.set_color('black')

ax.tick_params(axis='x', colors='black')
ax.tick_params(axis='y', colors='black')


# ================Create a new figure and subplot
fig2 = Figure(figsize=(3, 4), dpi=100)
fig2.set_facecolor("#DCDCDC")
ax2 = fig2.add_subplot(111)
ax2.set_facecolor("#DCDCDC")  

# Change the color of the axis lines to white
ax2.spines['bottom'].set_color('black')
ax2.spines['top'].set_color('black') 
ax2.spines['right'].set_color('black')
ax2.spines['left'].set_color('black')

ax2.xaxis.label.set_color('black')
ax2.yaxis.label.set_color('black')

ax2.tick_params(axis='x', colors='black')
ax2.tick_params(axis='y', colors='black')


# Create a list to store dutycycle values
duty_cycle_values = [] 
output_voltage_values = [] 
input_voltage_values = [] 
# Create a queue to hold the serial data
serial_data_queue = queue.Queue()

Time = np.linspace(0, 10, 100)

def read_serial_data():
    global duty_cycle_values, output_voltage_values, input_voltage_values
    while True:
        #print("Reading serial data")
        if ser is None:
            print("Serial port not opened")
            time.sleep(1)  # Wait for a while before checking again
            continue
        try:
            line = ser.readline().decode('utf-8').rstrip()
            data = line.split(',')
            #print(data)
            if data[0] == "data":
                dutycycle = float(data[1])  # Extract Duty Cycle data
                o_volt = float(data[2])  # Extract Output Voltage data
                i_volt = float(data[3])  # Extract Input Voltage data
                o_current = float(data[4])  # Extract Output Current data
                i_current = float(data[5])  # Extract Input Current data
                Setpoint = float(data[6])  # Extract Setpoint data
                #print("Set point is :")
                #print(Setpoint)
                Kp = float(data[7])  # Extract Kp data
                Ki = float(data[8])  # Extract Ki data
                Kd = float(data[9])  # Extract Kd data
                power_output = round(o_volt * (o_current/1000), 1)
                power_output = max(0, power_output)
                power_input = round(i_volt * (i_current/1000), 1)
                power_input = max(0, power_input)
                if power_input != 0:
                    efficiency = round((power_output / power_input) * 100, 1)
                    efficiency = max(0, min(100, efficiency))
                else:
                    efficiency = 0
                if i_volt != 0:
                    gain = round((o_volt / i_volt), 1)
                else:
                    gain = 0
                duty_cycle_values.append(dutycycle)
                output_voltage_values.append(o_volt)
                input_voltage_values.append(i_volt)

                duty_cycle_values = duty_cycle_values[-100:]
                output_voltage_values = output_voltage_values[-100:]
                input_voltage_values = input_voltage_values[-100:]
                # Put the data in the queue
                serial_data_queue.put((dutycycle,o_volt, o_current, i_volt, i_current, power_output, Setpoint, Kp, Ki, Kd,power_input, efficiency, gain))
            elif data[0] == "flag":
                # Parse other things here
                #print(float(data[1], data[2], data[3], data[4]))
                pass
                
            

        except (ValueError, IndexError) as e:
            print("Error parsing data: ", e)
        else:
            pass
            
            



def update_plot(dutycycle,ivolt,ovolt):
     # Create a time array
    time = np.arange(len(dutycycle)) / 10  # assuming 10 data points per second
    ax.clear()
    ax.plot(time,dutycycle)
    ax.set_title('Duty Cycle', color='black', fontsize=14, fontname='Inter Bold')  # add title to the first plot
    ax.set_ylim([0, 110])  # set y-axis limits
    ax.set_ylabel('Duty Cycle (%)', color='black', fontsize=10, fontname='Inter Bold')  # add y-axis label
    ax.set_xlabel('Time (seconds)', color='black', fontsize=10, fontname='Inter Bold')  # add x-axis label
    canvas1.draw()

    ax2.clear()
    ax2.plot(time,ivolt, label='Input Voltage')
    ax2.plot(time,ovolt, label='Output Voltage')
    ax2.set_title('Input and Output Voltage', color='black', fontsize=14, fontname='Inter Bold')  # add title to the first plot
    ax2.legend(loc='upper right', fontsize=8, facecolor='#DCDCDC', labelcolor='white',  edgecolor='white', title_fontsize='10')  # add legend
    ax2.set_ylim([0, 40])  # set y-axis limits
    ax2.set_ylabel('Voltage (V)', color='black', fontsize=10, fontname='Inter Bold')  # add y-axis label
    ax2.set_xlabel('Time (seconds)', color='black', fontsize=10, fontname='Inter Bold')  # add x-axis label
    canvas2.draw()

def update_gui(canvas_texts):
    # Check if there is data in the queue
    while not serial_data_queue.empty():
        duty_cycle,oVolt, oCurrent, iVolt, iCurrent, power_output, Setpoint, Kp, Ki, Kd, power_input, effiecency, gain = serial_data_queue.get()
        canvas.itemconfig(canvas_texts['duty_cycle_text'], text=f"{duty_cycle}%")
        canvas.itemconfig(canvas_texts['input_current_text'], text=f"{round((iCurrent/1000),2)}A")
        canvas.itemconfig(canvas_texts['input_voltage_text'], text=f"{iVolt}V")
        canvas.itemconfig(canvas_texts['output_voltage_text'],  text=f"{round(oVolt, 1)}V")
        canvas.itemconfig(canvas_texts['output_power_text'], text=f"{power_output}W")
        canvas.itemconfig(canvas_texts['input_power_text'], text=f"{power_input}W")
        canvas.itemconfig(canvas_texts['output_current_text'], text=f"{round((oCurrent/1000),2)}A")
        canvas.itemconfig(canvas_texts['current_req_volt_text'], text=f"{Setpoint}")
        canvas.itemconfig(canvas_texts['gain_text'], text=f"{gain}x")
        canvas.itemconfig(canvas_texts['efficiency_text'], text=f"{(effiecency)}%")
        canvas.update()
        update_plot(duty_cycle_values, input_voltage_values, output_voltage_values)


canvas = Canvas(
    window,
    bg = "#EDEDED",
    height = 768,
    width = 1366,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
BG = PhotoImage(
    file=relative_to_assets("BG.png"))
button_image = PhotoImage(
    file=relative_to_assets("button.png"))

canvas.create_image(0.0, 0.0,anchor = 'nw', image=BG)
'''
image_image_2 = PhotoImage(
    file=relative_to_assets("Duty_cycle_image.png"))

image_2 = canvas.create_image(
    49.5,
    118.26,
    image=image_image_2,
    anchor='nw'
)

image_image_3 = PhotoImage(
    file=relative_to_assets("Output_image.png"))
image_3 = canvas.create_image(
    716,
    118.26,
    image=image_image_3,
    anchor='nw'
)

image_image_4 = PhotoImage(
    file=relative_to_assets("input_image.png"))
image_4 = canvas.create_image(
    353,
    118,
    image=image_image_4,
    anchor='nw'
)

image_image_5 = PhotoImage(
    file=relative_to_assets("Required_voltage_image.png"))
image_5 = canvas.create_image(
    1152.75,
    118.26,
    image=image_image_5,
    anchor='nw'
    )

image_image_6 = PhotoImage(
    file=relative_to_assets("image_6.png"))
image_6 = canvas.create_image(
    720.0,
    49.0,
    image=image_image_6
)'''



canvas_texts = {}
canvas_texts['duty_cycle_text'] = canvas.create_text(
    85.0+54.0,
    164.0+18.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 30 * -1)
)



canvas_texts['input_current_text'] = canvas.create_text(
    305.0+54.0,
    164.0+18.0,
    anchor="center",
    text="NaN", 
    fill="#464646",
    font=("Inter Bold", 28 * -1)
)
canvas_texts['input_voltage_text'] = canvas.create_text(
    440.0+37.0,
    164.0+18.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 30 * -1)
)
canvas_texts['input_power_text'] = canvas.create_text(
    545.0+37.0,
    164.0+18.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 30 * -1)
)
canvas_texts['output_current_text'] = canvas.create_text(
    669.0+55.0,
    164.0+18.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 28 * -1)
)
canvas_texts['output_voltage_text'] = canvas.create_text(
    781.0+56.0,
    164.0+18.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 30 * -1)
)

canvas_texts['output_power_text'] = canvas.create_text(
    895.0+53.0,
    164.0+18.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 30 * -1)
)
canvas_texts['gain_text'] = canvas.create_text(
    998.0+56.0,
    164.0+18.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 30 * -1)
)
canvas_texts['efficiency_text'] = canvas.create_text(
    1183.0+56.0,
    154.0+18.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 35 * -1)
)
canvas_texts['current_req_volt_text'] = canvas.create_text(
    258.0+61.0,
    310.0+12.0,
    anchor="center",
    text="NaN",
    fill="#464646",
    font=("Inter Bold", 24 * -1)
)

def only_numeric_input(P):
    # checks if entry's value is a float (including integers) or empty and returns an appropriate boolean
    if len(P) > 4:  # check if the input is longer than 6 characters
        return False
    if P == "" or P.isdigit():
        return True
    try:
        float(P)
    except ValueError:
        return False
    # check if the number is between 0 and 24
    return 0 <= float(P) <= 24

validate_command = window.register(only_numeric_input)  # registers a Tcl to Python callback

req_volt_entry = Entry(
    font=("Inter Bold", 20),
    bd=0,
    bg="#B6B6B6",
    fg="#464646",
    highlightthickness=0,
    validate="key",  # apply validation on every keystroke
    validatecommand=(validate_command, '%P'),  # calls the callback with the proposed text as %P
    insertbackground='white'  # changes the cursor color to white
)
req_volt_entry.place(
    x=53.0,
    y=301.0,
    width=130.0,
    height=35.0
)

# Entry for Kp
kp_entry = Entry(
    font=("Inter Bold", 20),
    bd=0,
    bg="#B6B6B6",
    fg="#464646",
    highlightthickness=0,
    validate="key",  # apply validation on every keystroke
    validatecommand=(validate_command, '%P'),  # calls the callback with the proposed text as %P
    insertbackground='white'  # changes the cursor color to white
)
kp_entry.place(
    x=528.0,
    y=301.0,
    width=100.0,
    height=35.0
)

# Entry for Ki
ki_entry = Entry(
    font=("Inter Bold", 20),
    bd=0,
    bg="#B6B6B6",
    fg="#464646",
    highlightthickness=0,
    validate="key",  # apply validation on every keystroke
    validatecommand=(validate_command, '%P'),  # calls the callback with the proposed text as %P
    insertbackground='white'  # changes the cursor color to white
)
ki_entry.place(
    x=733.0,
    y=301.0,
    width=100.0,
    height=35.0
)

# Entry for Kd
kd_entry = Entry(
    font=("Inter Bold", 20),
    bd=0,
    bg="#B6B6B6",
    fg="#464646",
    highlightthickness=0,
    validate="key",  # apply validation on every keystroke
    validatecommand=(validate_command, '%P'),  # calls the callback with the proposed text as %P
    insertbackground='white'  # changes the cursor color to white
)
kd_entry.place(
    x=958.0,
    y=301.0,
    width=100.0,
    height=35.0
)

# Get a list of all available serial ports
style = ttk.Style()
style.map('TCombobox', fieldbackground=[('readonly', 'dark grey')])
style.map('TCombobox', selectbackground=[('readonly', 'dark grey')])
style.map('TCombobox', selectforeground=[('readonly', 'white')])
ports = serial.tools.list_ports.comports()
port_names = [port.device for port in ports]

combobox = ttk.Combobox(window, values=port_names, style="TCombobox")
combobox.place(x=45, y=37)

def send_to_arduino():
    # Get the data from the entries
    setpoint = req_volt_entry.get()
    kp = kp_entry.get()
    ki = ki_entry.get()
    kd = kd_entry.get()

    # Format the data as a CSV string
    data = f"{setpoint},{kp},{ki},{kd}\n"

    # Send the data to the Arduino
    if ser is not None:
        ser.write(data.encode())
        print("Data sent to Arduino: ", data)
    else:
        print("Serial port not opened")

button = Button(
    text="",
    font=("Inter Bold", 10),
    bd=0,
    image=button_image,  # Set the image as the button background
    compound="center",  # This will ensure the text is centered over the image
    fg="#464646",
    activebackground="#DCDCDC",
    activeforeground="#DCDCDC",
    command=send_to_arduino 
)
button.place(x=1192, y=282, width=138, height=46)

def on_select(event):
    global ser
    try:
        # Define serial port and baud rate
        serial_port = combobox.get() # Replace 'COMX' with your ESP32's serial port
        baud_rate = 9600
        # Establish serial communication
        ser = serial.Serial(serial_port, baud_rate)
        print("Serial port opened successfully")
    except serial.SerialException as e:
        # If an error occurs, show a warning message
        messagebox.showwarning("Warning", "Could not open serial port: " + str(e))

# Bind the event to the function
combobox.bind("<<ComboboxSelected>>", on_select)




# Create the canvas_tk to display the matplotlib figure
canvas1 = FigureCanvasTkAgg(fig, master=window)
ax.set_xlabel('Time (10 points = 1s)', color='black', fontsize=10, fontname='Inter Bold')  # add x-axis label
ax.set_ylabel('Voltage (V)', color='black', fontsize=10, fontname='Inter Bold')  # add y-axis label
# Adjust the bottom margin
fig.subplots_adjust(bottom=0.2)
canvas1.draw()
canvas1.get_tk_widget().place(x=150, y=365, width=500, height=340) 

canvas2 = FigureCanvasTkAgg(fig2, master=window)
ax2.set_ylabel('Voltage (V)', color='black', fontsize=10, fontname='Inter Bold')  # add y-axis label
ax2.set_xlabel('Time (10 points = 1s)', color='black', fontsize=10, fontname='Inter Bold')  # add x-axis label
# Adjust the bottom margin
fig2.subplots_adjust(bottom=0.2)
canvas2.draw()

canvas2.get_tk_widget().place(x=800, y=365, width=500, height=340) 

#Start reading serial data in a separate thread
serial_thread = threading.Thread(target=read_serial_data)
serial_thread.daemon = True
serial_thread.start()

window.resizable(True, True)
window.title("Boost Converter DashBoard")
def update_gui_wrapper():
    update_gui(canvas_texts)
    window.after(100, update_gui_wrapper)  # Schedule the function to run again after 100ms

window.after(100, update_gui_wrapper)
window.mainloop()
