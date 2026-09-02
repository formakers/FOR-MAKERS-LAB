# COMMANDS.md

## Terminal 1
```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

ros2 launch open_manipulator_bringup omx_f.launch.py \
port_name:=/dev/ttyACM1
```

## Terminal 2
```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

ros2 run open_manipulator_teleop omx_f_teleop
```

## Terminal 3
```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

cd ~/omx_dataset
python3 record_joint_data.py
```

R + Enter = 기록 시작  
S + Enter = 저장  
Q + Enter = 종료

## Terminal 4
```bash
cd ~/Robotics/ros2_ws
source install/setup.bash

cd ~/omx_dataset
python3 play_all_episodes.py
```
