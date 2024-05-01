import socket
import os
import ubx

# Set the path for the Unix socket
socket_path = "/tmp/gps"

# Create the Unix socket client
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect to the server
client.connect(socket_path)
def update_gnss(n):
    print("hi")
    msg = client.recv(1024)
    print("to here?")
    print(msg)
    data = ubx.parse.nav.ubx_nav_pvt(b"\x00\x00" + msg)

    date = "%04d-%02d-%02d" % (data["year"], data["month"], data["day"])
    time = "%02d:%02d:%02d" % (data["hour"], data["min"], data["sec"])

    fixDict = {
        0: "no ﬁx",
        1: "dead reckoning only",
        2: "2D-ﬁx",
        3: "3D-ﬁx",
        4: "GNSS + dead reckoning combined",
        5: "time only ﬁx",
    }

    fix = fixDict[data["fixType"]]

    style = {
        "width": "400px",
        "height": "456px",
        "left": "1480px",
        "top": "464px",
        "position": "absolute",
        "background": "#00FF00",
    }

    if data["fixType"] == 0:
        style["background"] = "#FF0000"

    print(data)

update_gnss(1)

# Close the connection
client.close()
