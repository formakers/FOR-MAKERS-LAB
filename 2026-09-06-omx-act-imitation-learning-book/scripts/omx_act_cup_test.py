import threading, time
import cv2, numpy as np, torch
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors

MODEL_PATH="."
JOINT_TOPIC="/joint_states"
IMAGE_TOPIC="/camera/color/image_raw"
JOINT_ORDER=["joint1","joint2","joint3","joint4","joint5","gripper_joint_1"]
NUM_SAMPLES=10

class Diagnostic(Node):
    def __init__(self):
        super().__init__("omx_act_cup_diagnostic")
        self.lock=threading.Lock(); self.state=None; self.image=None; self.results={}
        self.create_subscription(JointState,JOINT_TOPIC,self.joint_cb,10)
        self.create_subscription(Image,IMAGE_TOPIC,self.image_cb,10)
        print("Loading ACT policy...")
        self.policy=ACTPolicy.from_pretrained(MODEL_PATH); self.policy.eval()
        self.pre,self.post=make_pre_post_processors(self.policy.config,pretrained_path=MODEL_PATH)
        print("ROBOT COMMAND DISABLED")
        print("[L]eft [C]enter [R]ight [S]how [Q]uit")

    def joint_cb(self,msg):
        d=dict(zip(msg.name,msg.position))
        if all(n in d for n in JOINT_ORDER):
            with self.lock: self.state=np.array([d[n] for n in JOINT_ORDER],dtype=np.float32)

    def image_cb(self,msg):
        try:
            e=msg.encoding.lower()
            if e not in ("rgb8","bgr8"): return
            im=np.frombuffer(msg.data,np.uint8).reshape(msg.height,msg.width,3)
            if e=="bgr8": im=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
            im=cv2.resize(im,(640,480),interpolation=cv2.INTER_AREA).astype(np.float32)/255.0
            with self.lock: self.image=np.transpose(im,(2,0,1))
        except Exception as ex: print("IMAGE ERROR:",ex)

    def measure(self,label):
        with self.lock:
            if self.state is None or self.image is None:
                print("Waiting for state/camera"); return
        self.policy.reset(); samples=[]; states=[]
        print("\nMEASURING:",label)
        for i in range(NUM_SAMPLES):
            with self.lock: s=self.state.copy(); im=self.image.copy()
            obs={"observation.state":torch.from_numpy(s),
                 "observation.images.camera":torch.from_numpy(im)}
            with torch.inference_mode(): a=self.policy.select_action(self.pre(obs))
            a=self.post(a).detach().cpu().numpy().reshape(-1)
            samples.append(a.copy()); states.append(s.copy())
            print(f"{i+1:02d}/{NUM_SAMPLES}",np.round(a,4)); time.sleep(.25)
        samples=np.array(samples); states=np.array(states)
        self.results[label]=(samples.mean(0),samples.std(0),states.mean(0))
        print("ROBOT STATE:",np.round(states.mean(0),4))
        print("ACT MEAN:",np.round(samples.mean(0),4))
        print("ACT STD:",np.round(samples.std(0),4))

    def show(self):
        print("\nLEFT / CENTER / RIGHT")
        for k,n in [("L","LEFT"),("C","CENTER"),("R","RIGHT")]:
            print(n, "NOT MEASURED" if k not in self.results else np.round(self.results[k][0],4))
        if all(k in self.results for k in "LCR"):
            L,C,R=(self.results[k][0] for k in "LCR")
            print("CENTER-LEFT :",np.round(C-L,4))
            print("RIGHT-CENTER:",np.round(R-C,4))
            print("RIGHT-LEFT  :",np.round(R-L,4))
            print("[joint1,joint2,joint3,joint4,joint5,gripper]")

def main():
    rclpy.init(); node=Diagnostic()
    threading.Thread(target=rclpy.spin,args=(node,),daemon=True).start()
    time.sleep(2)
    try:
        while True:
            c=input("[L]eft [C]enter [R]ight [S]how [Q]uit > ").strip().upper()
            if c in "LCR":
                print("컵 위치를 고정하고 2초 기다립니다..."); time.sleep(2); node.measure(c)
            elif c=="S": node.show()
            elif c=="Q": break
    except KeyboardInterrupt: pass
    finally:
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()
if __name__=="__main__": main()
