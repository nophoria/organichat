import socket as Sock
import time
import hashlib
import threading


def HashDat(Hash, Dat):
    return bytes(Byte ^ Hash[i % len(Hash)] for i, Byte in enumerate(Dat))


class BackendHandler:
    def __init__(self, ServerIP="localhost", Port=6567, Pass="InputAPasswordMoron", Username="User"):
        self.ServerIP = ServerIP
        self.Port = Port
        self.Pass = Pass
        self.Username = Username
        self.Hash = (hashlib.sha512(Pass.encode('utf-32'))).digest()
        self.ClientSocket = None
        self.RecipentsList = []
        self.IncomingMessages = []
        self.PendingConnRequests = []
        self.ConnectedTo = None
        self.Running = False
        self.PollThread = None
        self.RecvThread = None
        self.ConnWaitResult = {}

    def SendMsg(self, Text):
        Payload = Text.encode('utf-8')
        Encoded = HashDat(self.Hash, Payload)
        Header = len(Encoded).to_bytes(4, 'big')
        self.ClientSocket.sendall(Header + Encoded)

    def RecvMsg(self):
        Header = self.RecvExact(4)
        if Header is None:
            return None
        MsgLen = int.from_bytes(Header, 'big')
        Body = self.RecvExact(MsgLen)
        if Body is None:
            return None
        Decoded = HashDat(self.Hash, Body)
        try:
            return Decoded.decode('utf-8')
        except Exception:
            return None

    def RecvExact(self, NumBytes):
        Buf = b""
        while len(Buf) < NumBytes:
            Chunk = self.ClientSocket.recv(NumBytes - len(Buf))
            if not Chunk:
                return None
            Buf += Chunk
        return Buf

    def Conn(self):
        try:
            self.ClientSocket = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
            self.ClientSocket.connect((self.ServerIP, self.Port))
            self.SendMsg(self.Username)
            self.Running = True

            self.PollThread = threading.Thread(target=self.PollLoop, daemon=True)
            self.PollThread.start()

            self.RecvThread = threading.Thread(target=self.RecieveConn, daemon=True)
            self.RecvThread.start()

            return True

        except Exception as e:
            print(f"Error Connecting To Server: {e}")
            self.ClientSocket = None
            return False

    def PollLoop(self):
        while self.Running:
            try:
                self.SendMsg("!List")
            except Exception as e:
                print(f"Error Polling Server: {e}")
                self.Running = False
                break
            time.sleep(1)

    def ConnToOther(self, FriendlyName):
        if FriendlyName not in self.RecipentsList:
            return False

        self.ConnWaitResult.pop(FriendlyName, None)
        self.SendMsg(f"!Conn:{FriendlyName}")

        Deadline = time.time() + 5
        while time.time() < Deadline:
            if FriendlyName in self.ConnWaitResult:
                Accepted = self.ConnWaitResult.pop(FriendlyName)
                if Accepted:
                    self.ConnectedTo = FriendlyName
                return Accepted
            time.sleep(0.05)

        return False

    def AcceptConn(self, FriendlyName):
        self.SendMsg(f"!ConnYes:{FriendlyName}")
        self.ConnectedTo = FriendlyName
        if FriendlyName in self.PendingConnRequests:
            self.PendingConnRequests.remove(FriendlyName)

    def RejectConn(self, FriendlyName):
        self.SendMsg(f"!ConnNo:{FriendlyName}")
        if FriendlyName in self.PendingConnRequests:
            self.PendingConnRequests.remove(FriendlyName)

    def Leave(self):
        if self.ConnectedTo:
            self.SendMsg("!Leave")
        self.ConnectedTo = None

    def RecieveConn(self):
        while self.Running:
            try:
                Msg = self.RecvMsg()
                if Msg is None:
                    self.Running = False
                    break

                if Msg.startswith("!"):
                    self.HandleCommand(Msg)
                else:
                    self.IncomingMessages.append(Msg)

            except Exception as e:
                print(f"Error Receiving Conn: {e}")
                self.Running = False
                break
            time.sleep(0.1)

    def HandleCommand(self, Msg):
        Command, _, Arg = Msg.partition(":")

        if Command == "!List":
            self.RecipentsList = Arg.split(",") if Arg else []

        elif Command == "!Conn":
            if Arg and Arg not in self.PendingConnRequests:
                self.PendingConnRequests.append(Arg)

        elif Command == "!ConnYes":
            self.ConnWaitResult[Arg] = True

        elif Command == "!ConnNo":
            self.ConnWaitResult[Arg] = False

        elif Command == "!Leave":
            self.ConnectedTo = None

        else:
            print(f"Unknown Command From Server: {Msg}")

    def SendChatMsg(self, Body):
        self.SendMsg(Body)

    def Close(self):
        self.Running = False
        if self.ClientSocket:
            self.ClientSocket.close()


class Server:
    def __init__(self, port=6567, debug=False, logpath="server.log", Pass="InputAPasswordMoron"):
        self.port = port
        self.running = True
        self.debug = debug
        self.logpath = logpath
        self.Pass = Pass
        self.Hash = (hashlib.sha512(Pass.encode('utf-32'))).digest()

        self.UserList = {}
        self.Pairs = {}
        self.Lock = threading.Lock()

    def SendMsg(self, ClientSock, Text):
        Payload = Text.encode('utf-8')
        Encoded = HashDat(self.Hash, Payload)
        Header = len(Encoded).to_bytes(4, 'big')
        ClientSock.sendall(Header + Encoded)

    def RecvExact(self, ClientSock, NumBytes):
        Buf = b""
        while len(Buf) < NumBytes:
            Chunk = ClientSock.recv(NumBytes - len(Buf))
            if not Chunk:
                return None
            Buf += Chunk
        return Buf

    def RecvMsg(self, ClientSock):
        Header = self.RecvExact(ClientSock, 4)
        if Header is None:
            return None
        MsgLen = int.from_bytes(Header, 'big')
        Body = self.RecvExact(ClientSock, MsgLen)
        if Body is None:
            return None
        Decoded = HashDat(self.Hash, Body)
        try:
            return Decoded.decode('utf-8')
        except Exception:
            return None

    def HandleClient(self, ClientSock, ClientAddrSanitised):
        Connected = True
        Username = None

        try:
            Username = self.RecvMsg(ClientSock)
        except Exception as e:
            self.Log(f"TCP Conn Err {ClientAddrSanitised}: {e}", ErrLevel=2)
            ClientSock.close()
            return

        if not Username:
            ClientSock.close()
            return

        with self.Lock:
            self.UserList[Username] = ClientSock
        self.Log(f"{Username} Registered From {ClientAddrSanitised}", ErrLevel=0)

        while Connected:
            try:
                Msg = self.RecvMsg(ClientSock)
                if Msg is None:
                    Connected = False
                    break

                if Msg.startswith("!"):
                    Connected = self.HandleCommand(Username, ClientSock, Msg, ClientAddrSanitised)
                else:
                    with self.Lock:
                        PartnerName = self.Pairs.get(Username)
                        PartnerSock = self.UserList.get(PartnerName) if PartnerName else None
                    if PartnerSock:
                        self.SendMsg(PartnerSock, Msg)
                    else:
                        self.Log(f"{Username} Sent Msg With No Active Partner", ErrLevel=1)

            except Exception as e:
                self.Log(f"TCP Conn Err {ClientAddrSanitised}: {e}", ErrLevel=2)
                Connected = False

        with self.Lock:
            self.UserList.pop(Username, None)
            PartnerName = self.Pairs.pop(Username, None)
            if PartnerName:
                self.Pairs.pop(PartnerName, None)
        if PartnerName:
            PartnerSock = self.UserList.get(PartnerName)
            if PartnerSock:
                try:
                    self.SendMsg(PartnerSock, "!Leave")
                except Exception:
                    pass
        ClientSock.close()

    def HandleCommand(self, Username, ClientSock, Msg, ClientAddrSanitised):
        Command, _, Arg = Msg.partition(":")

        if Command == "!List":
            with self.Lock:
                Users = [U for U in self.UserList.keys() if U != Username and U not in self.Pairs]
            self.SendMsg(ClientSock, "!List:" + ",".join(Users))

        elif Command == "!Conn":
            Target = Arg
            with self.Lock:
                TargetSock = self.UserList.get(Target)
            if TargetSock:
                self.SendMsg(TargetSock, f"!Conn:{Username}")
            else:
                self.SendMsg(ClientSock, f"!ConnNo:{Target}")

        elif Command == "!ConnYes":
            Requester = Arg
            with self.Lock:
                RequesterSock = self.UserList.get(Requester)
                if RequesterSock:
                    self.Pairs[Username] = Requester
                    self.Pairs[Requester] = Username
            if RequesterSock:
                self.SendMsg(RequesterSock, f"!ConnYes:{Username}")

        elif Command == "!ConnNo":
            Requester = Arg
            with self.Lock:
                RequesterSock = self.UserList.get(Requester)
            if RequesterSock:
                self.SendMsg(RequesterSock, f"!ConnNo:{Username}")

        elif Command == "!Leave":
            with self.Lock:
                PartnerName = self.Pairs.pop(Username, None)
                if PartnerName:
                    self.Pairs.pop(PartnerName, None)
                    PartnerSock = self.UserList.get(PartnerName)
                else:
                    PartnerSock = None
            if PartnerSock:
                self.SendMsg(PartnerSock, "!Leave")

        else:
            self.Log(f"Unknown Command From {ClientAddrSanitised}: {Msg}", ErrLevel=1)

        return True

    def Run(self, MaxPeople=8):
        ServerSocket = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
        ServerSocket.setsockopt(Sock.SOL_SOCKET, Sock.SO_REUSEADDR, 1)
        ServerSocket.bind(("localhost", self.port))
        ServerSocket.listen(MaxPeople)
        self.Log("Server Started Waiting For Conn", ErrLevel=0)

        while self.running:
            ClientSock, ClientAddr = ServerSocket.accept()
            ClientAddrSanitised = '{}:{}'.format(ClientAddr[0], ClientAddr[1])
            self.Log(f"Client Connected From {ClientAddrSanitised}", ErrLevel=0)

            ClientThread = threading.Thread(
                target=self.HandleClient,
                args=(ClientSock, ClientAddrSanitised)
            )
            ClientThread.daemon = True
            ClientThread.start()

    def Stop(self):
        self.running = False

    def Log(self, Msg, ErrLevel=0):
        with open(self.logpath, "a") as LogFile:
            if ErrLevel == 0:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [INFO ], {Msg}\n")
                print(f"[{time.strftime('%H:%M:%S')}], [INFO ], {Msg}")
            elif ErrLevel == 1:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [WARN ], {Msg}\n")
                print(f"[{time.strftime('%H:%M:%S')}], [WARN ], {Msg}")
            elif ErrLevel == 2:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [ERROR], {Msg}\n")
                print(f"[{time.strftime('%H:%M:%S')}], [ERROR], {Msg}")
            elif ErrLevel == 3:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [FATAL], {Msg}\n")
                print(f"[{time.strftime('%H:%M:%S')}], [FATAL], {Msg}")
            elif ErrLevel == 4:
                LogFile.write(f"[{time.strftime('%H:%M:%S')}], [DEBUG], {Msg}\n")
                print(f"[{time.strftime('%H:%M:%S')}], [DEBUG], {Msg}")