import socket
import datetime

def get_ip():
    host =socket.gethostname()
    ip = socket.gethostbyname(host)
    return ip

def get_time():
    now = datetime.datetime.now()
    send_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return send_time

