# -*- coding:utf-8 -*-
import socket
import time
import socketserver
import struct
import os
import threading

def get_ip():
    host =socket.gethostname()
    ip = socket.gethostbyname(host)
    return ip

def recvFile(connection,address):
    while True:
        try:
            connection.settimeout(600)
            fileinfo_size=struct.calcsize('128sq')
            buf = connection.recv(fileinfo_size)
            if buf: #如果不加这个if，第一个文件传输完成后会自动走到下一句
                filename,filesize =struct.unpack('128sq',buf)
                filename_f = filename.decode().strip('\x00')
                filenewname = os.path.join('new_'+ filename_f)
                 #print ('file new name is %s, filesize is %s' %(filenewname,filesize))
                recvd_size = 0 #定义接收了的文件大小
                #断点续传
                if os.path.exists(filenewname):
                    recvd_size = os.path.getsize(filenewname)
                connection.send(str(recvd_size).encode())
                file = open(filenewname,'ab')
                print ('stat receiving...')
                while not recvd_size == filesize:
                    if filesize - recvd_size > 1024:
                        rdata = connection.recv(1024)
                        recvd_size += len(rdata)
                    else:
                        rdata = connection.recv(filesize - recvd_size)
                        recvd_size = filesize
                    file.write(rdata)
                file.close()
                print ('receive done')
                         #connection.close()
        except socket.timeout:
            connection.close()

#addr = (get.get_ip(),10000)
#s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#s.bind(addr)
#s.listen(10)
#while True:
#    connection,address=s.accept()
#    print('Connected by ',address)
#    thread = threading.Thread(target=recvFile,args=(connection,address)) #使用threading也可以
#    thread.start()
#s.close()

