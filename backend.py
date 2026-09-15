import socket as Sock
import time

class BackendHandler:
    def __init__(self, ServerIP="localhost", Port=6567):
        self.ServerIP = ServerIP
        self.Port = Port

    def SendMsg(self, Msg, MaxRetries=5):
        for Attempt in range(MaxRetries):
            try:
                ClientSock = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
                ClientSock.connect((self.ServerIP, self.Port))
                EncodedMsg = Msg.encode("utf-32")
                if len(EncodedMsg) > 8188:
                    return False
                Header = bytearray(1)
                Header[0] = 0
                ClientSock.send(Header + EncodedMsg)
                ClientSock.close()
                return True
            except Exception as e:
                if hasattr(ClientSock, 'close'):
                    ClientSock.close()
                if Attempt < MaxRetries - 1:
                    time.sleep(1)
                continue
        return False

    def PullMsgs(self):
        try:
            ClientSock = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
            ClientSock.connect((self.ServerIP, self.Port))
            Header = bytearray(1)
            Header[0] = 128
            ClientSock.send(Header)

            Response = b""
            while True:
                chunk = ClientSock.recv(8192)
                if not chunk:
                    break
                Response += chunk
                
            ClientSock.close()

            MsgList = Response.decode("utf-32").split(",[NewMsg] ")
            return MsgList

        except Exception as e:
            return False

class Server:
    def __init__(self, port=6567, debug=False, logpath="server.log"):
        # Copy From Init
        self.port = port
        self.running = True
        self.debug = debug
        self.logpath = logpath

        # Init Globals
        self.MsgHistory = []

    def Run(self):
        # Setup Socket
        ServerSocket = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
        ServerSocket.setsockopt(Sock.SOL_SOCKET, Sock.SO_REUSEADDR, 1)
        ServerSocket.bind(("localhost", self.port))
        ServerSocket.listen(1)

        self.Log("Server Started Waiting For Conn", ErrLevel=0)
        while self.running:
            ClientSock, ClientAddr = ServerSocket.accept()
            self.Log(f"Client Connected From {ClientAddr}", ErrLevel=0)

            try:
                HeaderDat = ClientSock.recv(1)

                if len(HeaderDat) == 0:
                    ClientSock.close()
                    continue
                HeaderByte = HeaderDat[0]
                IsPull = bool(HeaderByte & 128)

                if IsPull:
                    self.Log("Client Requested Msg History", ErrLevel=0)
                    ClientSock.send((",[NewMsg] ".join(self.MsgHistory)).encode("utf-32"))
                else:
                    self.Log("Client Sent New Msg", ErrLevel=0)
                    Message = ClientSock.recv(8188)
                    if len(Message) > 0:
                        DecodedMessage = Message.decode("utf-32")
                        self.MsgHistory.append(DecodedMessage)
                        if self.debug:
                            self.Log(f"Message Received From {ClientAddr}: {DecodedMessage}", ErrLevel=0)
                        else:
                            self.Log(f"Message Received From {ClientAddr}", ErrLevel=0)

            except Exception as e:
                self.Log(f"TCP Conn Err {ClientAddr}: {e}", ErrLevel=2)
            finally:
                ClientSock.close()

    def Stop(self):
        self.running = False

    def Log(self, Msg, ErrLevel=0):
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