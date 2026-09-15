import socket as Sock
import asyncio
import time

class BackendHandler:
    def __init__(self, serverip="localhost", port=6567):
        self.serverip = serverip
        self.port = port

    def Conn():
        pass

    def SendMsg():
        pass

    def PullMsgs():
        return Server.MsgHistory

class Server:
    def __init__(self, port=6567, debug=False, logpath="server.log"):
        self.port = port
        self.running = True
        self.debug = debug
        self.logpath = logpath

        self.MsgHistory = []
    
    async def Run():
        ServerSocket = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
        ServerSocket.setsockopt(Sock.SOL_SOCKET, Sock.SO_REUSEADDR, 1)
        ServerSocket.bind(("localhost", self.port))

        print(f"Server Started On Port {self.port}, Waiting For Client Conn")

        ClientSock, ClientAddr = ServerSocket.accept()
        print(f"Client Connected: {ClientAddr} At Time [{time.strftime('%H:%M:%S')}]")

    def Stop():
        self.running = False

    def Log(self, Msg, ErrLevel=0):
        # 0 = Info, 1 = Warning, 2 = Error, 3 = Fatal, 4 = Debug
        with open(self.logpath, "a") as LogFile:
            if ErrLevel == 0:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [INFO ], {Msg}\n")
            elif ErrLevel == 1:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [WARN ], {Msg}\n")
            elif ErrLevel == 2:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [ERROR], {Msg}\n")
            elif ErrLevel == 3:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [FATAL], {Msg}\n")
            elif ErrLevel == 4:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [DEBUG], {Msg}\n")