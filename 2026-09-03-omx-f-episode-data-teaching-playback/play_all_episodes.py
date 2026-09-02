#!/usr/bin/env python3

import csv
import glob
import os
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from control_msgs.action import GripperCommand


class OMXMultiEpisodePlayer(Node):

    def __init__(self):
        super().__init__('omx_multi_episode_player')

        self.arm_joint_names = [
            'joint1',
            'joint2',
            'joint3',
            'joint4',
            'joint5'
        ]

        self.arm_pub = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        self.gripper_client = ActionClient(
            self,
            GripperCommand,
            '/gripper_controller/gripper_cmd'
        )

        self.get_logger().info(
            'OMX-F Multi Episode Player Ready'
        )

    def send_arm(self, joint_positions, duration):

        msg = JointTrajectory()
        msg.joint_names = self.arm_joint_names

        point = JointTrajectoryPoint()
        point.positions = joint_positions

        duration = max(duration, 0.08)

        sec = int(duration)
        nanosec = int((duration - sec) * 1e9)

        point.time_from_start.sec = sec
        point.time_from_start.nanosec = nanosec

        msg.points.append(point)

        self.arm_pub.publish(msg)

    def send_gripper(self, position):

        if not self.gripper_client.wait_for_server(
            timeout_sec=0.2
        ):
            return

        goal = GripperCommand.Goal()

        goal.command.position = position
        goal.command.max_effort = 20.0

        self.gripper_client.send_goal_async(goal)


def load_episode(filename):

    data = []

    with open(filename, 'r', newline='') as f:

        reader = csv.DictReader(f)

        for row in reader:

            try:

                data.append({
                    'time': float(row['time']),

                    'joints': [
                        float(row['joint1']),
                        float(row['joint2']),
                        float(row['joint3']),
                        float(row['joint4']),
                        float(row['joint5'])
                    ],

                    'gripper': float(row['gripper'])
                })

            except (ValueError, KeyError) as e:

                print(
                    f'잘못된 데이터 건너뜀 : {e}'
                )

    return data


def play_episode(
    node,
    filename,
    speed_scale=0.5
):

    data = load_episode(filename)

    if not data:
        print(
            f'{os.path.basename(filename)} : 데이터 없음'
        )
        return

    print()
    print('========================================')
    print(
        f' PLAY START : {os.path.basename(filename)}'
    )
    print('========================================')
    print(f'Samples : {len(data)}')
    print(f'Speed   : {speed_scale}')
    print()

    previous_time = data[0]['time']

    for index, row in enumerate(data):

        current_time = row['time']

        dt = current_time - previous_time

        if dt < 0:
            dt = 0

        sleep_time = dt / speed_scale

        node.send_arm(
            row['joints'],
            max(0.08, sleep_time)
        )

        node.send_gripper(
            row['gripper']
        )

        rclpy.spin_once(
            node,
            timeout_sec=0.001
        )

        if sleep_time > 0:
            time.sleep(sleep_time)

        previous_time = current_time

        if index % 20 == 0:

            print(
                f'PLAY '
                f'{index}/{len(data)} '
                f'| time={current_time:.2f}'
            )

    print()
    print('----------------------------------------')
    print(
        f'{os.path.basename(filename)} COMPLETE'
    )
    print('----------------------------------------')


def main():

    rclpy.init()

    node = OMXMultiEpisodePlayer()

    dataset_dir = os.path.expanduser(
        '~/omx_dataset'
    )

    episode_files = sorted(
        glob.glob(
            os.path.join(
                dataset_dir,
                'episode_*.csv'
            )
        )
    )

    print()
    print('========================================')
    print(' OMX-F ALL EPISODES AUTO PLAYBACK')
    print('========================================')

    if not episode_files:

        print()
        print('Episode 파일이 없습니다.')
        print('~/omx_dataset/episode_*.csv')

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

        return

    print()
    print(
        f'발견된 Episode : '
        f'{len(episode_files)}개'
    )
    print()

    for filename in episode_files:

        print(
            ' -',
            os.path.basename(filename)
        )

    print()
    print('========================================')
    print('5초 후 자동 재생 시작')
    print('로봇 주변을 확인하세요.')
    print('========================================')
    print()

    time.sleep(5)

    speed_scale = 0.5
    episode_wait = 3.0

    for index, filename in enumerate(
        episode_files
    ):

        print()
        print(
            f'>>> Episode '
            f'{index + 1}/{len(episode_files)}'
        )

        play_episode(
            node,
            filename,
            speed_scale
        )

        if index < len(episode_files) - 1:

            print()
            print(
                f'다음 Episode까지 '
                f'{episode_wait:.0f}초 대기...'
            )

            time.sleep(
                episode_wait
            )

    print()
    print('========================================')
    print(' ALL EPISODES PLAYBACK COMPLETE')
    print('========================================')
    print()

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
