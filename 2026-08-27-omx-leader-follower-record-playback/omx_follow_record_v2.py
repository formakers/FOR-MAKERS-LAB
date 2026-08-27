#!/usr/bin/env python3
import csv
import sys
import time
import termios
import tty
import select

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

UPDATE_INTERVAL = 0.05
TRAJECTORY_TIME = 0.10

# Follower 집게 OPEN 보정값.
# 조금 더 벌리고 싶으면 0.05 -> 0.06 -> 0.07처럼 조금씩 올려 테스트하세요.
OPEN_OFFSET = 0.05


def map_value(value, input_open, input_close, output_open, output_close):
    if abs(input_close - input_open) < 1e-9:
        return output_open

    low = min(input_open, input_close)
    high = max(input_open, input_close)
    value = max(low, min(high, value))

    ratio = (value - input_open) / (input_close - input_open)
    return output_open + ratio * (output_close - output_open)


class OMXFollowRecordV2(Node):
    def __init__(self):
        super().__init__("omx_follow_record_v2")

        self.subscription = self.create_subscription(
            JointState,
            "/leader/joint_states",
            self.joint_callback,
            10,
        )

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

        self.latest_joint_map = {}
        self.leader_open = None
        self.leader_close = None
        self.follow_enabled = False
        self.start_time = None
        self.last_publish_time = 0.0

        self.csv_file = open("omx_motion_v2.csv", "w", newline="")
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow([
            "time",
            "joint1",
            "joint2",
            "joint3",
            "joint4",
            "joint5",
            "leader_gripper",
            "follower_gripper",
        ])

        self.stdin_fd = sys.stdin.fileno()
        self.old_terminal_settings = termios.tcgetattr(self.stdin_fd)
        tty.setcbreak(self.stdin_fd)

        self.keyboard_timer = self.create_timer(0.05, self.keyboard_callback)
        self.print_help()

    def print_help(self):
        print()
        print("==============================================")
        print(" OMX Leader -> Follower V2")
        print("==============================================")
        print(" O : Leader OPEN 위치 저장")
        print(" C : Leader CLOSE 위치 저장")
        print(" G : FOLLOW + RECORD 시작")
        print(" S : FOLLOW 정지")
        print(" Q : 종료")
        print(f" OPEN_OFFSET = {OPEN_OFFSET:+.3f}")
        print(" 저장 파일: omx_motion_v2.csv")
        print("==============================================")
        print()

    def joint_callback(self, msg):
        now = time.time()

        self.latest_joint_map = {
            name: position
            for name, position in zip(msg.name, msg.position)
        }

        if not self.follow_enabled:
            return

        if now - self.last_publish_time < UPDATE_INTERVAL:
            return
        self.last_publish_time = now

        for name in self.joint_names:
            if name not in self.latest_joint_map:
                self.get_logger().warning(f"Missing joint: {name}")
                return

        j1 = self.latest_joint_map["joint1"]
        j2 = self.latest_joint_map["joint2"]
        j3 = self.latest_joint_map["joint3"]
        j4 = self.latest_joint_map["joint4"]
        j5 = self.latest_joint_map["joint5"]
        leader_grip = self.latest_joint_map["gripper_joint_1"]

        # O/C에서 측정한 Leader 범위를 반전하여 Follower에 매핑
        follower_open = self.leader_close + OPEN_OFFSET
        follower_close = self.leader_open

        follower_grip = map_value(
            leader_grip,
            self.leader_open,
            self.leader_close,
            follower_open,
            follower_close,
        )

        trajectory = JointTrajectory()
        trajectory.header.stamp = self.get_clock().now().to_msg()
        trajectory.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = [j1, j2, j3, j4, j5, follower_grip]

        total_ns = int(TRAJECTORY_TIME * 1_000_000_000)
        point.time_from_start.sec = total_ns // 1_000_000_000
        point.time_from_start.nanosec = total_ns % 1_000_000_000

        trajectory.points.append(point)
        self.publisher.publish(trajectory)

        elapsed = time.time() - self.start_time
        self.writer.writerow([
            round(elapsed, 4),
            j1, j2, j3, j4, j5,
            leader_grip,
            follower_grip,
        ])
        self.csv_file.flush()

    def current_gripper(self):
        return self.latest_joint_map.get("gripper_joint_1")

    def keyboard_callback(self):
        readable, _, _ = select.select([sys.stdin], [], [], 0)
        if not readable:
            return

        key = sys.stdin.read(1).lower()

        if key == "o":
            grip = self.current_gripper()
            if grip is None:
                print("\nLeader gripper 값을 아직 받지 못했습니다.\n")
                return
            self.leader_open = grip
            print(f"\n[O] Leader OPEN = {grip:.6f}\n")

        elif key == "c":
            grip = self.current_gripper()
            if grip is None:
                print("\nLeader gripper 값을 아직 받지 못했습니다.\n")
                return
            self.leader_close = grip
            print(f"\n[C] Leader CLOSE = {grip:.6f}\n")

        elif key == "g":
            if self.leader_open is None:
                print("\n먼저 OPEN 상태에서 O를 누르세요.\n")
                return
            if self.leader_close is None:
                print("\n먼저 CLOSE 상태에서 C를 누르세요.\n")
                return
            if abs(self.leader_close - self.leader_open) < 0.01:
                print("\nOPEN/CLOSE 값 차이가 너무 작습니다.\n")
                return

            follower_open = self.leader_close + OPEN_OFFSET
            follower_close = self.leader_open

            self.start_time = time.time()
            self.follow_enabled = True

            print()
            print("==============================================")
            print(" FOLLOW + RECORD START")
            print("==============================================")
            print(f"Leader OPEN    : {self.leader_open:.6f}")
            print(f"Leader CLOSE   : {self.leader_close:.6f}")
            print(f"Follower OPEN  : {follower_open:.6f}")
            print(f"Follower CLOSE : {follower_close:.6f}")
            print("CSV : omx_motion_v2.csv")
            print("==============================================")
            print()

        elif key == "s":
            self.follow_enabled = False
            print("\nFOLLOW STOP\n")

        elif key == "q":
            raise KeyboardInterrupt

    def cleanup(self):
        self.follow_enabled = False

        try:
            termios.tcsetattr(
                self.stdin_fd,
                termios.TCSADRAIN,
                self.old_terminal_settings,
            )
        except Exception:
            pass

        if not self.csv_file.closed:
            self.csv_file.flush()
            self.csv_file.close()

        print("\nCSV 저장 완료: omx_motion_v2.csv\n")


def main(args=None):
    rclpy.init(args=args)
    node = OMXFollowRecordV2()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cleanup()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
