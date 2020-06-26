import socket
import threading
import os
import get

def recv_msg(s):    
    while True:
        try:         # 测试发现，当服务器率先关闭时，这边也会报ConnectionResetError
            response = s.recv(1024)
            print(response.decode("gbk"))
        except ConnectionResetError:
            print("服务器关闭，聊天已结束！")
            s.close()
            break
    os._exit(0)

def send_msg(s):
    print("连接成功！现在可以发送消息！\n")
    print("输入消息按回车来发送")
    print("输入esc来退出聊天")
    while True:
        msg = input()
        if msg == "esc":
            print("你退出了聊天")
            s.close()
            break
        s.send(msg.encode("gbk"))
    os._exit(0)


threads = [threading.Thread(target=recv_msg,args=(socket_client,)), 
           threading.Thread(target=send_msg,args=(socket_client,))]
for t in threads:
    t.start()

if __name__ == '__main__':
    socket_client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ("60.205.247.173", 10000)
    socket_client.connect(addr)
    print("连接成功！现在可以接收消息！\n")
    threads = [threading.Thread(target=recv_msg,args=(socket_client,)), 
               threading.Thread(target=send_msg,args=(socket_client,))]
    for t in threads:
        t.start()