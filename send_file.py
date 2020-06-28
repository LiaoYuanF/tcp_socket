# -*- coding:utf-8 -*-
import struct
import socket
import os
import sys

#s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#s.connect(("60.205.247.173", 10000))

def sendFile(s):
    while True:
        filepath = input('Please Enter chars:\n')
        if os.path.isfile(filepath):
            fileinfo_size=struct.calcsize('128sq') #定义打包规则,受linux与window操作系统的位数差异影响.使用128sl会越界
            #定义文件头信息，包含文件名和文件大小
            fhead = struct.pack(b'128sq',bytes(os.path.basename(filepath), encoding='utf-8'),os.stat(filepath).st_size)
            s.send(fhead) 
            print ("client filepath: ",filepath)
            #断点续传的实现
            received_size = int(s.recv(1024).decode())
            fo = open(filepath,'rb')
            fo.seek(received_size)
            while True:
                filedata = fo.read(1024)
                if not filedata:
                    break
                s.send(filedata)
            fo.close()
            print ("send over...")
            #s.close()
