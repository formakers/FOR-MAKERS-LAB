import json, threading, time
from pathlib import Path
import cv2, numpy as np, torch
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from sensor_msgs.msg import Image, JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import GripperCommand
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors

MODEL_PATH="."
JOINT_TOPIC="/joint_states"; IMAGE_TOPIC="/camera/color/image_raw"
ARM_TOPIC="/arm_controller/joint_trajectory"; GRIPPER_ACTION="/gripper_controller/gripper_cmd"
JOINT_ORDER=["joint1","joint2","joint3","joint4","joint5","gripper_joint_1"]
DEFAULT_FPS=10.0
ARM_MAX_STEP=.05; GRIPPER_MAX_STEP=.02
ACTION_MIN=np.array([-1.0216312,-2.1184275,-.86823314,.12885438,-.877437,.0076699],np.float32)
ACTION_MAX=np.array([.22396119,.95567006,1.7364663,1.8131653,.4325826,.720971],np.float32)

def find_fps():
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k.lower()=="fps":
                    try:
                        f=float(v)
                        if 1<=f<=120:return f
                    except: pass
                r=walk(v)
                if r:return r
        elif isinstance(x,list):
            for v in x:
                r=walk(v)
                if r:return r
    for fn in ["info.json","meta/info.json","metadata/info.json","train_config.json","config.json"]:
        p=Path(fn)
        if p.exists():
            try:
                f=walk(json.loads(p.read_text()))
                if f:
                    print("Dataset FPS found:",f); return f
            except: pass
    print("Dataset FPS metadata not found; fallback:",DEFAULT_FPS)
    return DEFAULT_FPS

HZ=min(find_fps(),20.0); PERIOD=1/HZ; TRAJ_TIME=PERIOD*1.2

class Control(Node):
    def __init__(self):
        super().__init__("omx_act_fps_control")
        self.lock=threading.Lock(); self.state=None; self.image=None; self.steps=0; self.busy=False
        self.last_grip_t=0.; self.last_grip=None
        self.create_subscription(JointState,JOINT_TOPIC,self.joint_cb,10)
        self.create_subscription(Image,IMAGE_TOPIC,self.image_cb,10)
        self.arm=self.create_publisher(JointTrajectory,ARM_TOPIC,10)
        self.grip=ActionClient(self,GripperCommand,GRIPPER_ACTION)
        print("Loading ACT policy...")
        self.policy=ACTPolicy.from_pretrained(MODEL_PATH); self.policy.eval(); self.policy.reset()
        self.pre,self.post=make_pre_post_processors(self.policy.config,pretrained_path=MODEL_PATH)
        print(f"ACT READY | {HZ:.1f} Hz | period={PERIOD:.3f}s | trajectory={TRAJ_TIME:.3f}s")
        print("Ctrl+C = STOP")
        self.create_timer(PERIOD,self.step)

    def joint_cb(self,msg):
        d=dict(zip(msg.name,msg.position))
        if all(n in d for n in JOINT_ORDER):
            with self.lock:self.state=np.array([d[n] for n in JOINT_ORDER],np.float32)

    def image_cb(self,msg):
        try:
            e=msg.encoding.lower()
            if e not in ("rgb8","bgr8"):return
            im=np.frombuffer(msg.data,np.uint8).reshape(msg.height,msg.width,3)
            if e=="bgr8":im=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
            im=cv2.resize(im,(640,480),interpolation=cv2.INTER_AREA).astype(np.float32)/255.
            with self.lock:self.image=np.transpose(im,(2,0,1))
        except Exception as ex:print("IMAGE ERROR:",ex)

    def send_grip(self,x):
        now=time.monotonic()
        if now-self.last_grip_t<max(.1,PERIOD):return
        if self.last_grip is not None and abs(x-self.last_grip)<.002:return
        if not self.grip.server_is_ready():return
        g=GripperCommand.Goal(); g.command.position=float(x); g.command.max_effort=0.
        self.grip.send_goal_async(g); self.last_grip_t=now; self.last_grip=x

    def step(self):
        if self.busy:return
        self.busy=True
        try:
            with self.lock:
                if self.state is None or self.image is None:return
                s=self.state.copy(); im=self.image.copy()
            obs={"observation.state":torch.from_numpy(s),
                 "observation.images.camera":torch.from_numpy(im)}
            with torch.inference_mode():a=self.policy.select_action(self.pre(obs))
            a=self.post(a).detach().cpu().numpy().reshape(-1)
            target=np.clip(a,ACTION_MIN,ACTION_MAX)
            arm=s[:5]+np.clip(target[:5]-s[:5],-ARM_MAX_STEP,ARM_MAX_STEP)
            grip=float(np.clip(s[5]+np.clip(target[5]-s[5],-GRIPPER_MAX_STEP,GRIPPER_MAX_STEP),
                               ACTION_MIN[5],ACTION_MAX[5]))
            m=JointTrajectory(); m.joint_names=JOINT_ORDER[:5]; p=JointTrajectoryPoint()
            p.positions=arm.tolist(); sec=int(TRAJ_TIME)
            p.time_from_start.sec=sec
            p.time_from_start.nanosec=int((TRAJ_TIME-sec)*1_000_000_000)
            m.points=[p]; self.arm.publish(m); self.send_grip(grip)
            self.steps+=1
            if self.steps%max(1,int(HZ))==0:
                print("STEP",self.steps,"STATE",np.round(s,4),"ACT",np.round(a,4),
                      "SAFE ARM",np.round(arm,4),"GRIP",round(grip,4))
        except Exception as ex:print("CONTROL ERROR:",type(ex).__name__,ex)
        finally:self.busy=False

def main():
    rclpy.init(); n=Control()
    try:rclpy.spin(n)
    except KeyboardInterrupt:print("\nACT CONTROL STOPPED")
    finally:
        n.destroy_node()
        if rclpy.ok():rclpy.shutdown()
if __name__=="__main__":main()
