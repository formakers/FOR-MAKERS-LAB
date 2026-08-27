#!/usr/bin/env python3
import csv
import sys
import time
import termios
import tty
import select

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

CSV_FILE = "omx_motion_v2.csv"

PLAYBACK_SPEED = 1.0
RETURN_TIME = 2.0
LOOP_PAUSE = 0.5
SMOOTH_WINDOW = 5


def smooth_values(values, window):
    if window <= 1:
        return values[:]

    result = []
    half = window // 2

    for i in range(len(values)):
        start = max(0, i - half)
        end = min(len(values), i + half + 1)
        section = values[start:end]
        result.append(sum(section) / len(section))

    return result


class OMXPlaybackSmoothV2(Node):
    def __init__(self):
        super().__init__("omx_playback_smooth_v2")

        self.publisher = self.create_publisher(
            JointTrajectory,
            "/leader/joint_trajectory",
            10,
        )

        self.joint_names = [
            "joint1",
            "joint2",
            "joint3",
            "joint4",
            "joint5",
            "gripper_joint_1",
        ]

        self.motion = []
        self.stop_requested = False
        self.quit_requested = False

        self.stdin_fd = sys.stdin.fileno()
        self.old_terminal_settings = termios.tcgetattr(self.stdin_fd)
        tty.setcbreak(self.stdin_fd)

        self.load_csv()
        self.smooth_motion()
        self.print_help()

    def load_csv(self):
        with open(CSV_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.motion.append({
                    "time": float(row["time"]),
                    "joint1": float(row["joint1"]),
                    "joint2": float(row["joint2"]),
                    "joint3": float(row["joint3"]),
                    "joint4": float(row["joint4"]),
                    "joint5": float(row["joint5"]),
                    "gripper": float(row["follower_gripper"]),
                })

        if len(self.motion) < 2:
            raise RuntimeError("CSV에 재생할 동작이 없습니다.")

        print(f"\nCSV: {CSV_FILE}")
        print(f"Points: {len(self.motion)}")
        print(f"Duration: {self.motion[-1]['time']:.2f} sec\n")

    def smooth_motion(self):
        keys = [
            "joint1", "joint2", "joint3",
            "joint4", "joint5", "gripper",
        ]

        for key in keys:
            values = [row[key] for row in self.motion]
            values = smooth_values(values, SMOOTH_WINDOW)
            for i, value in enumerate(values):
                self.motion[i][key] = value

    def print_help(self):
        print("============================================")
        print(" OMX-F SMOOTH PLAYBACK V2")
        print("============================================")
        print(" 1 : 1회 재생")
        print(" 5 : 5회 반복")
        print(" 0 : 무한 반복")
        print(" S : 반복 정지")
        print(" Q : 종료")
        print(f" Speed       : {PLAYBACK_SPEED:.2f}x")
        print(f" Smoothing   : {SMOOTH_WINDOW}")
        print(f" Return time : {RETURN_TIME:.1f}s")
        print("============================================")
        print()

    def set_duration(self, point, seconds):
        seconds = max(seconds, 0.02)
        total_ns = int(seconds * 1_000_000_000)
        point.time_from_start.sec = total_ns // 1_000_000_000
        point.time_from_start.nanosec = total_ns % 1_000_000_000

    def move_to_start(self):
        first = self.motion[0]

        trajectory = JointTrajectory()
        trajectory.header.stamp = self.get_clock().now().to_msg()
        trajectory.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = [
            first["joint1"],
            first["joint2"],
            first["joint3"],
            first["joint4"],
            first["joint5"],
            first["gripper"],
        ]
        self.set_duration(point, RETURN_TIME)

        trajectory.points.append(point)
        self.publisher.publish(trajectory)

        print(f"시작 자세로 이동 ({RETURN_TIME:.1f}s)")
        time.sleep(RETURN_TIME + 0.2)

    def make_trajectory(self):
        trajectory = JointTrajectory()
        trajectory.header.stamp = self.get_clock().now().to_msg()
        trajectory.joint_names = self.joint_names

        start_time = self.motion[0]["time"]
        previous_time = 0.0

        for index, row in enumerate(self.motion):
            t = (row["time"] - start_time) / PLAYBACK_SPEED

            if index == 0:
                t = 0.05

            if t <= previous_time:
                t = previous_time + 0.02
            previous_time = t

            point = JointTrajectoryPoint()
            point.positions = [
                row["joint1"],
                row["joint2"],
                row["joint3"],
                row["joint4"],
                row["joint5"],
                row["gripper"],
            ]
            self.set_duration(point, t)
            trajectory.points.append(point)

        return trajectory

    def get_key(self):
        readable, _, _ = select.select([sys.stdin], [], [], 0)
        if not readable:
            return None
        return sys.stdin.read(1).lower()

    def play_once(self):
        self.move_to_start()

        trajectory = self.make_trajectory()
        self.publisher.publish(trajectory)

        total_time = (
            self.motion[-1]["time"] - self.motion[0]["time"]
        ) / PLAYBACK_SPEED

        print(
            f"Trajectory sent: {len(trajectory.points)} points / "
            f"{total_time:.2f}s"
        )

        start = time.time()
        while time.time() - start < total_time + 0.3:
            key = self.get_key()

            if key == "s":
                self.stop_requested = True
                print("\nSTOP\n")
                return False

            if key == "q":
                self.quit_requested = True
                return False

            rclpy.spin_once(self, timeout_sec=0.01)
            time.sleep(0.01)

        print("PLAY COMPLETE")
        return True

    def repeat(self, count=None):
        self.stop_requested = False
        number = 0

        while rclpy.ok():
            if self.stop_requested or self.quit_requested:
                break

            if count is not None and number >= count:
                break

            number += 1
            print(
                f"\n===== LOOP {number}"
                + (f"/{count}" if count is not None else "")
                + " ====="
            )

            if not self.play_once():
                break

            pause_start = time.time()
            while time.time() - pause_start < LOOP_PAUSE:
                key = self.get_key()

                if key == "s":
                    self.stop_requested = True
                    break

                if key == "q":
                    self.quit_requested = True
                    break

                time.sleep(0.02)

    def run(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.02)
            key = self.get_key()

            if key is None:
                continue
            elif key == "1":
                self.repeat(count=1)
            elif key == "5":
                self.repeat(count=5)
            elif key == "0":
                self.repeat(count=None)
            elif key == "q":
                break

    def cleanup(self):
        try:
            termios.tcsetattr(
                self.stdin_fd,
                termios.TCSADRAIN,
                self.old_terminal_settings,
            )
        except Exception:
            pass

        print("\nSmooth Playback V2 종료\n")


def main(args=None):
    rclpy.init(args=args)
    node = OMXPlaybackSmoothV2()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.cleanup()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
