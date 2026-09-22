import sys
import time
import threading
from backend import BackendHandler

Username = sys.argv[1] if len(sys.argv) > 1 else input("Username: ")

Backend = BackendHandler(ServerIP="localhost", Port=6567, Pass="InputAPasswordMoron", Username=Username)

if not Backend.Conn():
    print("Couldn't Connect, Exiting")
    sys.exit()

print(f"Connected As {Username}")

Shown = set()

def WatcherLoop():
    while Backend.Running:
        while Backend.IncomingMessages:
            print("\n" + Backend.IncomingMessages.pop(0))
        for Requester in Backend.PendingConnRequests:
            if Requester not in Shown:
                print(f"\n{Requester} Wants To Talk, Type !Accept:{Requester} Or !Reject:{Requester}")
                Shown.add(Requester)
        time.sleep(0.1)

WatcherThread = threading.Thread(target=WatcherLoop, daemon=True)
WatcherThread.start()

while True:
    Cmd = input("> ").strip()

    if Cmd == "!List":
        print(Backend.RecipentsList)

    elif Cmd.startswith("!Conn:"):
        Target = Cmd.split(":", 1)[1]
        if Backend.ConnToOther(Target):
            print(f"Connected To {Target}")
        else:
            print(f"{Target} Didn't Accept Or Wasn't Found")

    elif Cmd.startswith("!Accept:"):
        Target = Cmd.split(":", 1)[1]
        Backend.AcceptConn(Target)
        Shown.discard(Target)
        print(f"Connected To {Target}")

    elif Cmd.startswith("!Reject:"):
        Target = Cmd.split(":", 1)[1]
        Backend.RejectConn(Target)
        Shown.discard(Target)

    elif Cmd == "!Leave":
        Backend.Leave()
        print("Left Conversation")

    elif Cmd == "!Quit":
        Backend.Close()
        break

    else:
        if Backend.ConnectedTo:
            Backend.SendChatMsg(Cmd)
        else:
            print("Not Connected To Anyone, Use !Conn:Name First")