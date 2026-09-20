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

    def Conn(self):
        try:
            # Create Socket
            ClientSocket = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
            ClientSocket.connect((self.ServerIP, self.Port))
            ClientSocket.send(HashDat(self.Hash, Username))

        except Exception as e:
            print(f"Error Connecting To Server: {e}")
            return None

class Server:
    def __init__(self, port=6567, debug=False, logpath="server.log", Pass="InputAPasswordMoron"):
        # Copy From Init
        self.port = port
        self.running = True
        self.debug = debug
        self.logpath = logpath
        self.Pass = Pass
        self.Hash = (hashlib.sha512(Pass.encode('utf-32'))).digest()

        # Init Globals
        self.UserList = []

    def HandleClient(self, ClientSock, ClientAddrSanitised):
        Connected = True
        while Connected:
            try:
                Dat = ClientSock.recv(1024)
                DecodedDat = str(HashDat(self.Hash, Dat))
                self.UserList.append((ClientAddrSanitised, DecodedDat))
                ReturnUserList = str(self.UserList).encode("utf-32")
                ClientSock.send(HashDat(self.Hash, ReturnUserList))

            except Exception as e:
                self.Log(f"TCP Conn Err {ClientAddrSanitised}: {e}", ErrLevel=2)
                Connected = False
            finally:
                ClientSock.close()

    def Run(self, MaxPeople=8):
        # Setup Socket
        ServerSocket = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
        ServerSocket.setsockopt(Sock.SOL_SOCKET, Sock.SO_REUSEADDR, 1)
        ServerSocket.bind(("localhost", self.port))
        ServerSocket.listen(MaxPeople)
        self.Log("Server Started Waiting For Conn", ErrLevel=0)
        
        while self.running:
            ClientSock, ClientAddr = ServerSocket.accept()
            ClientAddrSanitised = '{}:{}'.format(ClientAddr[0], ClientAddr[1])
            self.Log(f"Client Connected From {ClientAddrSanitised}", ErrLevel=0)
            
            # Create New Thread Per Conn
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