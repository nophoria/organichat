import socket as Sock
import time
import hashlib
import threading

def HashDat(Hash, Dat): 
    return bytes(Byte ^ Hash[i % len(Hash)] for i, Byte in enumerate(Dat))

class BackendHandler:
    def __init__(self, ServerIP="localhost", Port=6567, Pass="InputAPasswordMoron"):
        self.ServerIP = ServerIP
        self.Port = Port
        self.Pass = Pass
        self.Hash = (hashlib.sha512(Pass.encode('utf-32'))).digest()

#     def SendMsg(self, Msg, MaxRetries=5):
#         for Attempt in range(MaxRetries):
#             try:
#                 ClientSock = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
#                 ClientSock.connect((self.ServerIP, self.Port))
#                 EncodedMsg = Msg.encode("utf-32")
#                 if len(EncodedMsg) > 8188:
#                     return False
#                 Header = bytearray(1)
#                 Header[0] = 0
#                 Payload = Header + EncodedMsg
#                 ClientSock.send(HashDat(self.Hash, Payload))
#                 ClientSock.close()
#                 return True
#             except Exception as e:
#                 if hasattr(ClientSock, 'close'):
#                     ClientSock.close()
#                 if Attempt < MaxRetries - 1:
#                     time.sleep(1)
#                 continue
#         return False

#     def PullMsgs(self):
#         try:
#             ClientSock = Sock.socket(Sock.AF_INET, Sock.SOCK_STREAM)
#             ClientSock.connect((self.ServerIP, self.Port))
#             Header = bytearray(1)
#             Header[0] = 128
#             ClientSock.send(Header)

#             Response = b""
#             while True:
#                 chunk = ClientSock.recv(8192)
#                 if not chunk:
#                     break
#                 Response += chunk
                
#             ClientSock.close()

#             MsgList = HashDat(self.Hash, (Response))
#             MsgList = MsgList.decode("utf-32")
#             MsgList = MsgList.split(",[NewMsg] ")
#             return MsgList

#         except Exception as e:
#             return False

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

    def HandleClient(ClientSock, ClientAddrSanitised):
        Connected = True
        while Connected:
            try:
                Dat = ClientSock.recv(1024)
                DecodedDat = HashDat(self.Hash, Dat)
                self.UserList.append((ClientAddrSanitised, DecodedDat))
                

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
            client_thread = threading.Thread(
                target=self.HandleClient,
                args=(ClientSock, ClientAddrSanitised)
            )
            client_thread.daemon = True
            client_thread.start()
#             try:
#                 Dat = ClientSock.recv(8193)
#                 DecodedDat = HashDat(self.Hash, Dat)
#                 HeaderDat = bytes([Dat[0]])
#                 HeaderDat = HashDat(self.Hash, HeaderDat)

#                 if len(HeaderDat) == 0:
#                     ClientSock.close()
#                     continue
#                 HeaderByte = HeaderDat[0]
#                 IsPull = bool(HeaderByte & 128)

#                 if IsPull:
#                     self.Log("Client Requested Msg History", ErrLevel=0)
#                     ClientSock.send(HashDat(self.Hash, ((",[NewMsg] ".join(self.MsgHistory)).encode("utf-32"))))
                
#                 else:
#                     self.Log("Client Sent New Msg", ErrLevel=0)
#                     Message = DecodedDat[1:8193].decode("utf-32")
#                     if len(Message) > 0:
#                         if self.debug:
#                             self.Log(f"Message Received From {ClientAddrSanitised} [{Message}]", ErrLevel=0)
#                         else:
#                             self.Log(f"Message Received From {ClientAddrSanitised}", ErrLevel=0)

#                         self.MsgHistory.append(Message)
#                         self.Log(self.MsgHistory, ErrLevel=4)

#             except Exception as e:
#                 self.Log(f"TCP Conn Err {ClientAddrSanitised}: {e}", ErrLevel=2)
#             finally:
#                 ClientSock.close()

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