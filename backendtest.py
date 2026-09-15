import backend
import sys
import os

def ClearLog():
    if os.path.exists("test.log"): os.remove("test.log")

ClearLog()
Server = backend.Server(port=6567, debug=True, logpath="test.log")


def ReadLogs():
    LogList = []
    try:
        with open("test.log", "r") as LogFile:
            LogContents = LogFile.readlines()

            LineNum = 0
            for Line in LogContents:
                LineNum += 1
                CleanLine = Line.strip()
                if not CleanLine:
                    raise ValueError("Empty Line Found In Log File")
                    
                LineData = CleanLine.split(", ", 3)
                if len(LineData) == 3:
                    LogList.append(
                        {
                            "line": LineNum,
                            "time": LineData[0],
                            "loglevel": LineData[1],
                            "data": LineData[2]
                        }
                    )
                else:
                    raise ValueError("Invalid Log Format")

    except Exception as e:
        print(f"Error reading logs: {e}")
        return []
    
    return LogList

ClearLog()
LoopTestNum = 100
for i in range(100):
    Server.Log(f"TestingLine{i+1}", ErrLevel=4)
LogList = ReadLogs()

if (len(LogList) != 100):
    sys.exit(f"Log Test Failed, Log File Does Not Contain {LoopTestNum} Entries When {LoopTestNum} Entries Logged")

for i in range(100):
    if (LogList[i]["loglevel"] != "[DEBUG]"):
        sys.exit(f"Log Test Failed, Log Level For Line {i+1} Entry Is Not [DEBUG]")

    Expected = f"TestingLine{i+1}"
    Actual = str(LogList[i]["data"])
    
    if (Actual != Expected):
        sys.exit(f"Log Test Failed, Log Data For Line {i+1} Does Not Match Expected Data")

print("Log Tests Passed")