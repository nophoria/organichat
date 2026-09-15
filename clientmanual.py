import backend
import time

Backend = backend.BackendHandler(ServerIP="localhost", Port=6567)
time.sleep(0.1)

while True:
    time.sleep(0.1)
    Backend.SendMsg(input())
    print("Sent")
    time.sleep(1)
    print(Backend.PullMsgs())
    print("Waiting For Next Msg")

