#!/usr/bin/env python3

import time
import math
import csv
from datetime import datetime
from collections import deque

import matplotlib.pyplot as plt
from dynamixel_sdk import PortHandler, PacketHandler

# ============================================================
# DUCKBOT ROLLER SKATING - LIVE MONITOR
#
# LEFT  DYNAMIXEL : ID 11
# RIGHT DYNAMIXEL : ID 12
#
# 기능
# 1. 두 모터 스케이팅 동작
# 2. 실제 위치 실시간 측정
# 3. 속도 / 전류 측정
# 4. CSV 자동 저장
# 5. 실시간 각도 그래프
# ============================================================

PORT = "/dev/ttyUSB0"
BAUD = 1000000
PROTOCOL = 2.0

LEFT_ID = 11
RIGHT_ID = 12

# XL330 Control Table
ADDR_TORQUE_ENABLE = 64
ADDR_PROFILE_VELOCITY = 112
ADDR_GOAL_POSITION = 116

ADDR_PRESENT_CURRENT = 126
ADDR_PRESENT_VELOCITY = 128
ADDR_PRESENT_POSITION = 132

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# ------------------------------------------------------------
# Motion parameters
# ------------------------------------------------------------

LEFT_CENTER = 2048
RIGHT_CENTER = 2048

AMPLITUDE = 250

PROFILE_VELOCITY = 200

# 한 사이클 시간
CYCLE_TIME = 2.0

# 제어 주기
DT = 0.03

# 그래프에 최근 몇 초를 표시할지
GRAPH_WINDOW = 10.0


# ============================================================
# Conversion
# ============================================================

def raw_to_deg(raw):
    return raw * 360.0 / 4096.0


def signed16(value):
    if value >= 32768:
        value -= 65536
    return value


def signed32(value):
    if value >= 2147483648:
        value -= 4294967296
    return value


# ============================================================
# DYNAMIXEL
# ============================================================

port = PortHandler(PORT)
packet = PacketHandler(PROTOCOL)

print()
print("==========================================")
print(" DUCKBOT LIVE SKATING MONITOR")
print("==========================================")
print()

if not port.openPort():
    raise RuntimeError("U2D2 port open failed")

if not port.setBaudRate(BAUD):
    port.closePort()
    raise RuntimeError("Baudrate setting failed")

print("PORT :", PORT)
print("BAUD :", BAUD)
print()


# ============================================================
# Ping
# ============================================================

for dxl_id in [LEFT_ID, RIGHT_ID]:

    model, result, error = packet.ping(port, dxl_id)

    if result != 0:
        port.closePort()
        raise RuntimeError(
            f"DYNAMIXEL ID {dxl_id} communication failed"
        )

    print(
        f"DYNAMIXEL ID {dxl_id} OK   MODEL={model}"
    )


# ============================================================
# Setup motors
# ============================================================

for dxl_id in [LEFT_ID, RIGHT_ID]:

    packet.write1ByteTxRx(
        port,
        dxl_id,
        ADDR_TORQUE_ENABLE,
        TORQUE_DISABLE
    )

    packet.write4ByteTxRx(
        port,
        dxl_id,
        ADDR_PROFILE_VELOCITY,
        PROFILE_VELOCITY
    )

    packet.write1ByteTxRx(
        port,
        dxl_id,
        ADDR_TORQUE_ENABLE,
        TORQUE_ENABLE
    )


# ============================================================
# Move center
# ============================================================

packet.write4ByteTxRx(
    port,
    LEFT_ID,
    ADDR_GOAL_POSITION,
    LEFT_CENTER
)

packet.write4ByteTxRx(
    port,
    RIGHT_ID,
    ADDR_GOAL_POSITION,
    RIGHT_CENTER
)

print()
print("Moving to CENTER...")
time.sleep(2)


# ============================================================
# CSV
# ============================================================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

csv_name = f"duckbot_skating_live_{timestamp}.csv"

csv_file = open(csv_name, "w", newline="")

writer = csv.writer(csv_file)

writer.writerow([
    "time_sec",

    "left_goal_deg",
    "left_position_deg",
    "left_velocity_raw",
    "left_current_raw",

    "right_goal_deg",
    "right_position_deg",
    "right_velocity_raw",
    "right_current_raw"
])

print("CSV :", csv_name)


# ============================================================
# Live graph buffer
# ============================================================

times = deque()

left_goal_data = deque()
right_goal_data = deque()

left_position_data = deque()
right_position_data = deque()


# ============================================================
# Matplotlib
# ============================================================

plt.ion()

fig, ax = plt.subplots(figsize=(11, 6))

left_goal_line, = ax.plot(
    [],
    [],
    "--",
    label="LEFT Goal"
)

left_actual_line, = ax.plot(
    [],
    [],
    label="LEFT Actual"
)

right_goal_line, = ax.plot(
    [],
    [],
    "--",
    label="RIGHT Goal"
)

right_actual_line, = ax.plot(
    [],
    [],
    label="RIGHT Actual"
)

ax.set_title(
    "DUCKBOT Roller Skating - Live Joint Motion"
)

ax.set_xlabel("Time (sec)")
ax.set_ylabel("Motor Position (deg)")

ax.grid(True)
ax.legend()

plt.show(block=False)


# ============================================================
# Start
# ============================================================

print()
print("==========================================")
print(" LIVE SKATING START")
print(" Ctrl+C = STOP")
print("==========================================")
print()

start_time = time.time()

sample = 0


try:

    while True:

        now = time.time()

        elapsed = now - start_time

        # ----------------------------------------------------
        # skating phase
        # ----------------------------------------------------

        phase = (
            2.0
            * math.pi
            * elapsed
            / CYCLE_TIME
        )

        swing = int(
            AMPLITUDE * math.sin(phase)
        )

        # 반대 위상
        left_goal = LEFT_CENTER + swing
        right_goal = RIGHT_CENTER - swing


        # ----------------------------------------------------
        # Send command
        # ----------------------------------------------------

        packet.write4ByteTxRx(
            port,
            LEFT_ID,
            ADDR_GOAL_POSITION,
            left_goal
        )

        packet.write4ByteTxRx(
            port,
            RIGHT_ID,
            ADDR_GOAL_POSITION,
            right_goal
        )


        # ----------------------------------------------------
        # Read LEFT
        # ----------------------------------------------------

        left_pos, _, _ = packet.read4ByteTxRx(
            port,
            LEFT_ID,
            ADDR_PRESENT_POSITION
        )

        left_vel, _, _ = packet.read4ByteTxRx(
            port,
            LEFT_ID,
            ADDR_PRESENT_VELOCITY
        )

        left_cur, _, _ = packet.read2ByteTxRx(
            port,
            LEFT_ID,
            ADDR_PRESENT_CURRENT
        )


        # ----------------------------------------------------
        # Read RIGHT
        # ----------------------------------------------------

        right_pos, _, _ = packet.read4ByteTxRx(
            port,
            RIGHT_ID,
            ADDR_PRESENT_POSITION
        )

        right_vel, _, _ = packet.read4ByteTxRx(
            port,
            RIGHT_ID,
            ADDR_PRESENT_VELOCITY
        )

        right_cur, _, _ = packet.read2ByteTxRx(
            port,
            RIGHT_ID,
            ADDR_PRESENT_CURRENT
        )


        # ----------------------------------------------------
        # Convert
        # ----------------------------------------------------

        left_deg = raw_to_deg(left_pos)
        right_deg = raw_to_deg(right_pos)

        left_goal_deg = raw_to_deg(left_goal)
        right_goal_deg = raw_to_deg(right_goal)

        left_vel = signed32(left_vel)
        right_vel = signed32(right_vel)

        left_cur = signed16(left_cur)
        right_cur = signed16(right_cur)


        # ----------------------------------------------------
        # Save CSV
        # ----------------------------------------------------

        writer.writerow([
            elapsed,

            left_goal_deg,
            left_deg,
            left_vel,
            left_cur,

            right_goal_deg,
            right_deg,
            right_vel,
            right_cur
        ])

        csv_file.flush()


        # ----------------------------------------------------
        # Graph buffer
        # ----------------------------------------------------

        times.append(elapsed)

        left_goal_data.append(left_goal_deg)
        right_goal_data.append(right_goal_deg)

        left_position_data.append(left_deg)
        right_position_data.append(right_deg)


        # ----------------------------------------------------
        # Keep only recent GRAPH_WINDOW seconds
        # ----------------------------------------------------

        while (
            len(times) > 0
            and elapsed - times[0] > GRAPH_WINDOW
        ):

            times.popleft()

            left_goal_data.popleft()
            right_goal_data.popleft()

            left_position_data.popleft()
            right_position_data.popleft()


        # ----------------------------------------------------
        # Update graph
        # ----------------------------------------------------

        left_goal_line.set_data(
            times,
            left_goal_data
        )

        left_actual_line.set_data(
            times,
            left_position_data
        )

        right_goal_line.set_data(
            times,
            right_goal_data
        )

        right_actual_line.set_data(
            times,
            right_position_data
        )


        if len(times) > 1:

            ax.set_xlim(
                max(0, elapsed - GRAPH_WINDOW),
                elapsed + 0.2
            )

        # XL330 center ± motion range
        ax.set_ylim(
            raw_to_deg(LEFT_CENTER - AMPLITUDE - 100),
            raw_to_deg(LEFT_CENTER + AMPLITUDE + 100)
        )

        fig.canvas.draw_idle()
        fig.canvas.flush_events()

        plt.pause(0.001)


        # ----------------------------------------------------
        # Terminal monitor
        # ----------------------------------------------------

        if sample % 10 == 0:

            if swing > 30:
                motion = "LEFT PUSH"
            elif swing < -30:
                motion = "RIGHT PUSH"
            else:
                motion = "RECOVERY"

            print(
                f"{elapsed:6.2f}s | "
                f"{motion:12s} | "
                f"L={left_deg:7.2f}° "
                f"R={right_deg:7.2f}° | "
                f"Lcur={left_cur:5d} "
                f"Rcur={right_cur:5d}"
            )

        sample += 1

        time.sleep(DT)


except KeyboardInterrupt:

    print()
    print("STOP requested")


finally:

    print("Returning to CENTER...")

    packet.write4ByteTxRx(
        port,
        LEFT_ID,
        ADDR_GOAL_POSITION,
        LEFT_CENTER
    )

    packet.write4ByteTxRx(
        port,
        RIGHT_ID,
        ADDR_GOAL_POSITION,
        RIGHT_CENTER
    )

    time.sleep(1)

    for dxl_id in [LEFT_ID, RIGHT_ID]:

        packet.write1ByteTxRx(
            port,
            dxl_id,
            ADDR_TORQUE_ENABLE,
            TORQUE_DISABLE
        )

    port.closePort()

    csv_file.close()

    plt.ioff()
    plt.close()

    print()
    print("==========================================")
    print(" DUCKBOT STOP")
    print(" CSV SAVED :", csv_name)
    print("==========================================")
