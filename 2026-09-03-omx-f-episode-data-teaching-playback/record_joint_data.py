#!/usr/bin/env python3

import os
import csv
import time
import threading

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class OMXEpisodeRecorder(Node):

    def __init__(self):
        super().__init__('omx_episode_recorder')

        self.save_dir = os.path.expanduser('~/omx_dataset')
        os.makedirs(self.save_dir, exist_ok=True)

        self.joint_names = [
            'joint1',
            'joint2',
            'joint3',
            'joint4',
            'joint5',
            'gripper_joint_1'
        ]

        self.recording = False
        self.rows = []
        self.start_time = None

        self.episode_number = self.find_next_episode()

        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

        print()
        print('========================================')
        print(' OMX-F EPISODE DATA RECORDER')
        print('========================================')
        print(' R + Enter : 기록 시작')
        print(' S + Enter : 저장')
        print(' Q + Enter : 종료')
        print('========================================')
        print(f'다음 Episode : {self.episode_number:03d}')
        print('========================================')
        print()

        self.keyboard_thread = threading.Thread(
            target=self.keyboard_loop,
            daemon=True
        )
        self.keyboard_thread.start()

    def find_next_episode(self):

        episode = 1

        while True:

            filename = os.path.join(
                self.save_dir,
                f'episode_{episode:03d}.csv'
            )

            if not os.path.exists(filename):
                return episode

            episode += 1

    def keyboard_loop(self):

        while rclpy.ok():

            try:
                command = input(
                    '명령 [R=기록 / S=저장 / Q=종료] > '
                )

            except EOFError:
                break

            command = command.strip().lower()

            if command == 'r':
                self.start_recording()

            elif command == 's':
                self.stop_and_save()

            elif command == 'q':

                if self.recording:
                    print()
                    print('현재 기록 중입니다.')
                    print('먼저 S + Enter로 저장하세요.')
                    continue

                print()
                print('프로그램 종료')

                rclpy.shutdown()
                break

            else:
                print()
                print('R, S 또는 Q를 입력하세요.')

    def start_recording(self):

        if self.recording:
            print()
            print('이미 기록 중입니다.')
            return

        self.rows = []
        self.start_time = time.time()
        self.recording = True

        print()
        print('========================================')
        print(f' EPISODE {self.episode_number:03d}')
        print(' RECORDING START')
        print('========================================')
        print('이제 터미널 2에서 로봇을 움직이세요.')
        print()

    def stop_and_save(self):

        if not self.recording:
            print()
            print('현재 기록 중인 Episode가 없습니다.')
            return

        self.recording = False

        filename = os.path.join(
            self.save_dir,
            f'episode_{self.episode_number:03d}.csv'
        )

        with open(filename, 'w', newline='') as f:

            writer = csv.writer(f)

            writer.writerow([
                'time',
                'joint1',
                'joint2',
                'joint3',
                'joint4',
                'joint5',
                'gripper'
            ])

            writer.writerows(self.rows)

        print()
        print('========================================')
        print(' EPISODE 저장 완료')
        print('========================================')
        print(f'파일 : {filename}')
        print(f'데이터 수 : {len(self.rows)} samples')
        print('========================================')

        self.episode_number += 1

        print()
        print(
            f'다음 Episode : '
            f'episode_{self.episode_number:03d}.csv'
        )
        print()

        self.rows = []

    def joint_callback(self, msg):

        if not self.recording:
            return

        joint_data = dict(
            zip(msg.name, msg.position)
        )

        elapsed = time.time() - self.start_time

        row = [elapsed]

        for name in self.joint_names:

            row.append(
                joint_data.get(
                    name,
                    float('nan')
                )
            )

        self.rows.append(row)

        count = len(self.rows)

        if count % 20 == 0:

            self.get_logger().info(
                f'Episode {self.episode_number:03d} '
                f'| {count} samples '
                f'| {elapsed:.2f} sec'
            )


def main(args=None):

    rclpy.init(args=args)

    node = OMXEpisodeRecorder()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        if node.recording:
            print()
            print(
                '기록 중 종료되었습니다. '
                '현재 Episode는 저장되지 않았습니다.'
            )

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
