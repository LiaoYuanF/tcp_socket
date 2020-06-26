import get
import threading
import os
import socket

socket_server = socket(socket.AF_INET,socket.SOCK_STREAM)
users = {}

def forward_message(s,addr):
    while True:
        try:
            response = s.recv(1024).decode("gbk")
            msg = "{} user {} send the message：{}".format(get.get_time(),addr,response)
            for client in users.values():           # what is users.values ?
                client.send(msg.encode("gbk"))
        except ConnectionResetError:
            print("user{} quit the chat！".format(addr))
            users.pop(addr)
            break


def accept_connection(s):
    while True:
        s,addr =s.accept()                          # 接受到了socket连接
        users[addr]=s               
        number = len(users)
        print("user {} connect successfully".foramt(addr))
        # 开启一个新线程
        threadingThread(target=forward_message,args=(s,addr)).start()


def start_sever(s):
        server_addr = (get.get_ip(),10000)
        s.bind(server_addr)
        s.listen(5)
        print("sever is opening...")
        print("if you want to close the sever,please input: stop server")
        threading.Thread(target=self.accept_cont,args=(s)).start()

def close_sever(s):
    for client in users.values():
        client.close()
    s.close()
    os.exit(0)

if __name__=="__main__":
    socket_server = socket(socket.AF_INET,socket.SOCK_STREAM)
    users = {}
    start_sever(socket_server)
    while True:
        cmd = input()
        if cmd == "stop server":
            close_sever(socket_server)
