###################################################################
#*- 								                            -*#
#*- function	: client                                 	    -*#
#*- serverhost	: 60.205.247.173				                -*#
#*- port	: 10000 						                    -*#
#*- author	: fly		        		                        -*#
#*-			 					                                -*#
###################################################################

# -*- coding:utf-8 -*-
import socket
import threading
import os
import get
import struct

def recv_msg(s):    
    while True:
        try:         # 测试发现，当服务器率先关闭时，这边也会报ConnectionResetError
            response = s.recv(1024)
            print(response.decode('utf-8'))
        except ConnectionResetError:
            print("服务器关闭，聊天已结束！")
            s.close()
            break
    os._exit(0)

def upload(s,data):
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


def download(s,data):
    print ('Accept the file {}'.format(data))
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
                fp.write(data)
            fp.close()
            print ("end receive...")
        #s.close()
        break
if __name__ == '__main__':
    socket_client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ("60.205.247.173", 10000)
    socket_client.connect(addr)
    threading.Thread(target=recv_msg,args=(socket_client,)).start()
    print("连接成功！现在可以接受消息并通过输入指令进行操作！\n")
    #threading.Thread(target=send_msg,args=(socket_client,)).start()
    while True:
        request = input()
        socket_client.send(request.encode('utf-8'))
        cmd,data = request.split(" ")
        if cmd == 'upload':
            upload(socket_client,data)
            print("upload is finished")
        elif cmd == 'download':
            download(socket_client,data)
        elif cmd == 'chat':
            pass
        elif cmd == 'esc':
            os._exit(0)
        else:
            print("An unknown command!")
