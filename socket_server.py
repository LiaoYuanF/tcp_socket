###################################################################
#*-                                                             -*#
#*- function    : server                                        -*#
#*- serverhost  : 60.205.247.173                                -*#
#*- port    : 10000                                             -*#
#*- author  : fly                                               -*#
#*-                                                             -*#
###################################################################
# -*- coding:utf-8 -*-
import get
import threading
import os
import socket
import struct
def each_client(s,addr):
    while True:
        try:
            response = s.recv(1024).decode('utf-8')
            cmd,data = response.split(" ")
            if cmd == "chat":
                chat(addr,data)
            elif cmd == "upload":
                upload(s)
                print("upload is finished")
            elif cmd == "download":
                download(s,addr,data)
            else:
                print("An unknown command!")
            #msg = "{} user {} send the message：{}".format(get.get_time(),addr,response)
            #for client in users.values():   # what is users.values ?
            #   client.send(msg.encode("gbk"))
        except ConnectionResetError:
            print("user{} quit the chat！".format(addr))
            users.pop(addr)
            break


def accept_connection(s):
    while True:
        c,addr =s.accept()  # 接受到了socket连接
        users[addr]=c
        number = len(users)
        print("user {} connect successfully".format(addr))
                # 开启一个新线程
        threading.Thread(target=each_client,args=(c,addr)).start()


def start_sever(s):
    server_addr = (get.get_ip(),10000)
    s.bind(server_addr)
    s.listen(10)
    print("sever is opening...")
    print("if you want to close the sever,please input: stop server")
    threading.Thread(target=accept_connection,args=(s,)).start()

def chat(addr,data):
    msg = "{} user {} send the message：{}".format(get.get_time(),addr,data)
    print(msg)
    for client in users.values():   # what is users.values ?
        client.send(msg.encode('utf-8'))

def upload(s):
    #print ('Accept the file {} from {}'.format(data,addr))
    while True:
        fileinfo_size = struct.calcsize('128sl')
        buf = s.recv(fileinfo_size)
        if buf:
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(str.encode('\00'))
            new_filename = os.path.join(str.encode('./'), str.encode('new_') + fn)
            print ('file new name is {0}, filesize if {1}'.format(new_filename, filesize))
            recvd_size = 0  # 定义已接收文件的大小
            fp = open(new_filename, 'wb')
            print ("start receiving...")
            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = s.recv(1024)
                    recvd_size += len(data)
                else:
                    data = s.recv(filesize - recvd_size)
                    recvd_size = filesize
                    print("################################################################")
                fp.write(data)
            print("end")
            fp.close()
            print ("end receive...")
        #s.close()
        break

def download(s,addr,data):
    filename = data
    if os.path.isfile(filename):
        # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
        fileinfo_size = struct.calcsize('128sl')
        # 定义文件头信息，包含文件名和文件大小
        fhead = struct.pack('128sl', bytes(os.path.basename(filename).encode('utf-8')),os.stat(filename).st_size)
        s.send(fhead)
        print ('client filename: {0}'.format(filename))
        fp = open(filename, 'rb')
        while True:
            data = fp.read(1024)
            if not data:
                print ('{0} file send over...'.format(filename))
                break
            s.send(data)



def close_sever(s):
    for client in users.values():
        client.close()
    s.close()
    os._exit(0)

if __name__=="__main__":
    socket_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    users = {}
    start_sever(socket_server)
    while True:
        cmd = input()
        if cmd == "stop server":
            close_sever(socket_server)
