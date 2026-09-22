import backend

Server = backend.Server(port=6567, debug=True, logpath="server.log", Pass="InputAPasswordMoron")

Server.Run()