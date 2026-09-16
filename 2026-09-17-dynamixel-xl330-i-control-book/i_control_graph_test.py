#!/usr/bin/env python3
import time, csv
from datetime import datetime
import matplotlib.pyplot as plt
from dynamixel_sdk import PortHandler, PacketHandler, COMM_SUCCESS

DEVICENAME = "/dev/ttyUSB0"
BAUDRATE = 1000000
PROTOCOL_VERSION = 2.0
DXL_ID = 11

ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

TARGET_A = 3500
TARGET_B = 2800
TARGET = TARGET_A

KI = 0.02
CONTROL_PERIOD = 0.05
INTEGRAL_LIMIT = 5000.0
I_OUTPUT_LIMIT = 150.0
ARRIVAL_TOLERANCE = 20
HOLD_TIME = 3.0
POSITION_MIN = 0
POSITION_MAX = 4095

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE = f"i_control_{timestamp}.csv"
csv_file = open(CSV_FILE, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["time","target","actual","error","integral","i_output","command","state"])

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

if not portHandler.openPort():
    raise RuntimeError(f"PORT OPEN FAILED: {DEVICENAME}")
if not portHandler.setBaudRate(BAUDRATE):
    raise RuntimeError("BAUDRATE SET FAILED")

packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

plt.ion()
fig, axes = plt.subplots(3, 1, figsize=(12, 9))
line_target, = axes[0].plot([], [], "--", label="TARGET")
line_actual, = axes[0].plot([], [], label="ACTUAL")
axes[0].set_title("TARGET vs ACTUAL"); axes[0].grid(True); axes[0].legend()
line_error, = axes[1].plot([], [], label="ERROR")
axes[1].axhline(0, linestyle="--"); axes[1].set_title("POSITION ERROR"); axes[1].grid(True); axes[1].legend()
line_integral, = axes[2].plot([], [], label="INTEGRAL")
line_output, = axes[2].plot([], [], label="I OUTPUT")
axes[2].axhline(0, linestyle="--"); axes[2].set_title("INTEGRAL / I OUTPUT"); axes[2].grid(True); axes[2].legend()
plt.tight_layout()

time_data=[]; target_data=[]; actual_data=[]; error_data=[]; integral_data=[]; output_data=[]
integral = 0.0
start_time = time.monotonic()
previous_time = start_time
state = "MOVE"
hold_start_time = None

try:
    while True:
        loop_start = time.monotonic()
        elapsed_time = loop_start - start_time
        dt = loop_start - previous_time
        previous_time = loop_start
        if dt <= 0: dt = CONTROL_PERIOD

        position, result, dxl_error = packetHandler.read4ByteTxRx(
            portHandler, DXL_ID, ADDR_PRESENT_POSITION
        )
        if result != COMM_SUCCESS or dxl_error != 0:
            time.sleep(CONTROL_PERIOD)
            continue

        position_error = TARGET - position

        if state == "MOVE":
            integral += position_error * dt
            integral = max(-INTEGRAL_LIMIT, min(INTEGRAL_LIMIT, integral))
            i_output = KI * integral
            i_output = max(-I_OUTPUT_LIMIT, min(I_OUTPUT_LIMIT, i_output))
            command = int(position + i_output)
            command = max(POSITION_MIN, min(POSITION_MAX, command))
            packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, command)

            if abs(position_error) <= ARRIVAL_TOLERANCE:
                state = "HOLD"
                hold_start_time = loop_start
                integral = 0.0
        else:
            i_output = 0.0
            command = TARGET
            packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, command)
            if loop_start - hold_start_time >= HOLD_TIME:
                TARGET = TARGET_B if TARGET == TARGET_A else TARGET_A
                integral = 0.0
                state = "MOVE"

        print(f"T={elapsed_time:7.2f} | {state:4s} | TARGET={TARGET:4d} | "
              f"ACTUAL={position:4d} | ERROR={position_error:5d} | "
              f"INT={integral:9.2f} | I_OUT={i_output:7.2f} | CMD={command:4d}")

        csv_writer.writerow([elapsed_time,TARGET,position,position_error,integral,i_output,command,state])
        csv_file.flush()

        time_data.append(elapsed_time); target_data.append(TARGET); actual_data.append(position)
        error_data.append(position_error); integral_data.append(integral); output_data.append(i_output)
        line_target.set_data(time_data,target_data); line_actual.set_data(time_data,actual_data)
        line_error.set_data(time_data,error_data); line_integral.set_data(time_data,integral_data)
        line_output.set_data(time_data,output_data)
        xmin=max(0,elapsed_time-60); xmax=max(10,elapsed_time)
        for ax in axes:
            ax.set_xlim(xmin,xmax); ax.relim(); ax.autoscale_view(scalex=False,scaley=True)
        fig.canvas.draw_idle(); fig.canvas.flush_events(); plt.pause(0.001)

        sleep_time = CONTROL_PERIOD - (time.monotonic() - loop_start)
        if sleep_time > 0: time.sleep(sleep_time)

except KeyboardInterrupt:
    print("I CONTROL TEST STOP")
finally:
    packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    portHandler.closePort()
    csv_file.close()
    print(f"CSV SAVED : {CSV_FILE}")
    plt.ioff()
    plt.show()
