from tkinter import *
import socket
import time
from tkinter import messagebox
from threading import Thread
import re
import os
import struct
import sys
import pyaudio
import wave
class Audio:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 16000
        self.p = pyaudio.PyAudio()
    def record(self,WAVE_OUTPUT_FILENAME,RECORD_SECONDS):
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        print("开始录音,请说话......")
        frames = []
        for i in range(0, int(self.RATE / self.CHUNK * RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)
        print("录音结束,请闭嘴!")
        stream.stop_stream()
        stream.close()
        self.p.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    def play_record(self):
        f = wave.open(r"tem.wav", "rb")
        # instantiate PyAudio
        p = self.p
        # open stream
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)
        # read data
        data = f.readframes(self.CHUNK)
        # paly stream
        while data != '':
            stream.write(data)
            data = f.readframes(self.CHUNK)
        # stop stream
        stream.stop_stream()
        stream.close()
        # close PyAudio
        p.terminate()
        os.remove("tem.wav")
class Client:
    """创建客户端的模板类"""
    def __init__(self):
        print("初始化tcp多人聊天室客户端")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.client_socket.connect(('127.0.0.1', 7890))
        addr = ("60.205.247.173", 10000)
        self.client_socket .connect(addr)
    def send_login_info(self, username, password):
        """
        发送登录用户的用户名和密码给服务器验证，并return验证结果
        :param username: 待验证的用户名
        :param password: 待验证的密码
        :return: 验证结果
        """
        # 告诉服务器本次请求的类型，“1” 是验证登录
        self.client_socket.sendall("1".encode("utf-8"))
        # 将用户名和密码按照一定规律组合后一起发送给服务器
        username_psw = username + "#!#!" + password
        self.client_socket.sendall(username_psw.encode("utf-8"))
        # 获取服务器的返回值，"1"代表通过，“0”代表不通过，再放回True or False
        check_result = self.client_socket.recv(1024).decode("utf-8")
        return check_result

    def send_register_info(self, username, password, confirm):
        """
        发送用户注册的用户名和密码给服务器，并返回注册结果
        :param username: 待注册的用户名
        :param password: 待注册的密码
        :param confirm: 确认密码
        :return: 注册结果
        """
        # 判断两次输入的密码是否一致
        if not password == confirm:
            return "密码不一致，请重新输入！"
        # 告诉服务器本次请求类型，“2” 是注册用户
        self.client_socket.sendall("2".encode("utf-8"))

        # 将用户名和密码按一定规律组装后发送给服务器
        username_psw = username + "#!#!" + password
        self.client_socket.sendall(username_psw.encode("utf-8"))

        # 获取服务器返回的结果
        check_result = self.client_socket.recv(1024).decode("utf-8")
        return check_result
    def upload_file(self,filepath):
        filepath=filepath.strip()
        if os.path.isfile(filepath):
            self.client_socket.sendall("4".encode("utf-8"))
            fileinfo_size=struct.calcsize('128sl') #定义打包规则,受linux与window操作系统的位数差异影响.使用128sl会越界
            #定义文件头信息，包含文件名和文件大小
            fhead = struct.pack(b'128sl',bytes(os.path.basename(filepath), encoding='utf-8'),os.stat(filepath).st_size)
            self.client_socket.send(fhead) 
            print ("client filepath: ",filepath)
            #断点续传的实现
            #print(self.client_socket.recv(1024).decode())
            #received_size = int(float(self.client_socket.recv(1024).decode()))
            fo = open(filepath,'rb')
            #fo.seek(received_size)
            while True:
                filedata = fo.read(1024)
                if not filedata:
                    break
                self.client_socket.send(filedata)
            fo.close()
            print ("send over...")
        else:
            print("can't find the file")
    def download_file(self,filename):
    #while True:
        self.client_socket.sendall("5".encode("utf-8"))
        time.sleep(2)
        #self.client_socket.sendall(filename.encode("utf-8"))
        fileinfo_size=struct.calcsize('128sl') #定义打包规则,受linux与window操作系统的位数差异影响.使用128sl会越界
            #定义文件头信息，包含文件名和文件大小
        fhead = struct.pack(b'128sl',bytes(os.path.basename(filename), encoding='utf-8'),os.stat("jamon_client.py").st_size)
        self.client_socket.send(fhead)
            
     
    def send_msg(self, content):
        """
        向服务器发送数据
        :param content: 待发送的内容
        """
        # 告诉服务器本次请求类型，“3” 是发送消息
        self.client_socket.sendall("3".encode("utf-8"))
        self.client_socket.sendall(content.encode("utf-8"))

    def recv_data(self, size=1024):
        """
        客户端向服务器接收数据
        :return: 接收到的数据
        """
        return self.client_socket.recv(size).decode("utf-8")

    def close(self):
        """
        关闭客户端与服务器连接的套接字
        """
        self.client_socket.close()


class LoginPanel:
    """登录界面模板类，只需另外传入其他对象的方法"""
    def __init__(self):
        self.login_frame = Tk()
        self.username = None
        self.password = None

    def set_panel_position(self):
        """
        设置登陆界面在屏幕中的位置和大小
        """
        screen_width = self.login_frame.winfo_screenwidth()    # 获取屏幕宽度
        screen_height = self.login_frame.winfo_screenheight()  # 获取屏幕高度
        width = 400
        height = 300
        gm_str = "%dx%d+%d+%d" % (width, height, (screen_width - width) / 2,
                                  (screen_height - 1.2 * height) / 2)
        self.login_frame.geometry(gm_str)

    def config_for_reg_panel(self):
        """
        给登陆界面设置其他配置
        """
        self.login_frame.configure(background="lightblue")
        self.login_frame.resizable(width=False, height=False)  # 设置界面大小可调
        self.login_frame.title("Login")

    def set_title(self):
        """
        放置界面标题
        """
        title_lable = Label(self.login_frame, text="MyChat - Login", font=("Microsoft Yahei", 16),
                            fg="black", bg="lightblue")
        title_lable.pack(ipady=10, fill=X)

    def set_form(self):
        """
        放置登陆表单
        """
        # 1、创建框架
        form_frame = Frame(self.login_frame, bg="lightblue")
        form_frame.pack(fill=X, padx=20, pady=10)

        # 2、添加用户名、密码标签，并设置字体、背景色、前景色并用grid布局
        Label(form_frame, text="username：", font=("Microsoft Yahei", 12), bg="lightblue", fg="black").grid(row=0, column=3, pady=20)
        Label(form_frame, text="password：", font=("Microsoft Yahei", 12), bg="lightblue", fg="black").grid(row=1, column=3, pady=20)

        # 3、设置输入框，储存用户输入的用户名和密码
        self.username = StringVar()
        self.password = StringVar()
        Entry(form_frame, textvariable=self.username, bg="#e3e3e3", width=30).grid(row=0, column=4, ipady=1)
        Entry(form_frame, textvariable=self.password, show="*", bg="#e3e3e3", width=30).grid(row=1, column=4, ipady=1)

    def set_btn(self):
        """
        放置注册和登陆按钮
        """
        btn_frame = Frame(self.login_frame, bg="lightblue")
        btn_reg = Button(btn_frame, text="Register", bg="lightblue", fg="black", width=15,
                              font=('Microsoft Yahei', 12), command=self.reg_func)
        btn_reg.pack(side=LEFT, ipady=3)

        btn_login = Button(btn_frame, text="Login", bg="lightblue", fg="black", width=15,
                                font=('Microsoft Yahei', 12), command=self.login_func)
        btn_login.pack(side=RIGHT, ipady=3)
        btn_frame.pack(fill=X, padx=20, pady=20)

    def show(self):
        """
        调用实例方法给登录界面做整体布局
        """
        self.set_panel_position()
        self.config_for_reg_panel()
        self.set_title()
        self.set_form()
        self.set_btn()
        self.login_frame.mainloop()

    def close(self):
        """
        实现对界面的关闭
        """
        # 先判断是否有界面
        if self.login_frame == None:
            print("未显示界面")
        else:
            self.login_frame.destroy()

    def get_input(self):
        """
        获取用户输入的用户名和密码
        :return: 返回获得的用户名和密码
        """
        return self.username.get(), self.password.get()

    def login_func(self):
        """
        封装到登陆界面中的登录按钮的功能。
        """
        username, password = self.get_input()
        client = Client()
        check_result = client.send_login_info(username, password)
        if check_result == "登录成功！":
            messagebox.showinfo(title="Success", message="登陆成功！")
            self.close()
            main_panel = MainPanel(username, client)
            Thread(target=main_panel.handle_msg).start()
            # print("线程创建成功...")
            main_panel.show()
        elif check_result == "密码输入有误，请重新输入！":
            messagebox.showerror(title="Error", message="密码输入有误，请重新输入！")
        elif check_result == "不存在该用户，请先注册！":
            messagebox.showerror(title="Error", message="不存在该用户，请先注册！")

    def reg_func(self):
        """
        封装到登录界面的注册按钮中，实现从登录界面跳转到注册界面
        """
        self.close()
        reg_panel = RegPanel()
        reg_panel.show()


class RegPanel:
    """注册界面模板类，只需另外传入其他对象的方法"""
    def __init__(self):
        self.reg_frame = Tk()
        self.username = None
        self.password = None
        self.confirm = None

    def set_panel_position(self):
        """设置注册界面在屏幕中的位置和大小"""
        screen_width = self.reg_frame.winfo_screenwidth()
        screen_height = self.reg_frame.winfo_screenheight()
        width = 400
        height = 360
        gm_str = "%dx%d+%d+%d" % (width, height, (screen_width - width) / 2, (screen_height - 1.2 * height) / 2)
        self.reg_frame.geometry(gm_str)

    def config_for_reg_panel(self):
        """给注册界面设置其他配置"""
        self.reg_frame.configure(background="lightblue")

        # 设置窗口关闭按钮时，调用方法，用于退出时关闭socket连接
        self.reg_frame.protocol("WM_DELETE_WINDOW", self.close_callback)

        # 界面可调整大小
        self.reg_frame.resizable(width=False, height=False)
        self.reg_frame.title("Register")

    def set_title(self):
        """放置界面标题"""
        title_lable = Label(self.reg_frame, text="MyChat - Register", font=("Microsoft Yahei", 16), fg="black", bg="lightblue")
        title_lable.pack(ipady=10, fill=X)

    def set_form(self):
        """放置注册表单"""
        form_frame = Frame(self.reg_frame, bg="lightblue")
        form_frame.pack(fill=X, padx=20, pady=10)

        # 设置用户名、密码标签
        Label(form_frame, text="username：", font=("Microsoft Yahei", 12), bg="lightblue", fg="black").grid(row=0, column=1, pady=20)
        Label(form_frame, text="password：", font=("Microsoft Yahei", 12), bg="lightblue", fg="black").grid(row=1, column=1, pady=20)
        Label(form_frame, text=" confirm：", font=("Microsoft", 12), bg="lightblue", fg="black").grid(row=2, column=1, pady=20)

        # 设置变量，存储用户名和密码
        self.username = StringVar()
        self.password = StringVar()
        self.confirm = StringVar()

        # 设置输入框
        Entry(form_frame, textvariable=self.username, bg="#e3e3e3", width=30).grid(row=0, column=2, ipady=1)
        Entry(form_frame, textvariable=self.password, show="*", bg="#e3e3e3", width=30) \
            .grid(row=1, column=2, ipady=1)
        Entry(form_frame, textvariable=self.confirm, show="*", bg="#e3e3e3", width=30) \
            .grid(row=2, column=2, ipady=1)

    def set_btn(self):
        """放置取消和注册按钮"""
        btn_frame = Frame(self.reg_frame, bg="lightblue")
        btn_quit = Button(btn_frame, text="Cancel", bg="lightblue", fg="black", width=15,
                          font=('Microsoft Yahei', 12), command=self.quit_func)
        btn_quit.pack(side=LEFT, ipady=3)

        btn_reg = Button(btn_frame, text="Register", bg="lightblue", fg="black", width=15,
                         font=('Microsoft Yahei', 12), command=self.reg_func)
        btn_reg.pack(side=RIGHT, ipady=3)
        btn_frame.pack(fill=X, padx=20, pady=20)

    def show(self):
        """注册界面布局"""
        self.set_panel_position()
        self.config_for_reg_panel()
        self.set_title()
        self.set_form()
        self.set_btn()

        # 启动注册界面，让其显示
        self.reg_frame.mainloop()

    def close(self):
        if self.reg_frame == None:
            print("未显示界面")
        else:
            self.reg_frame.destroy()

    def get_input(self):
        """
        获取输入的用户名、密码、确认密码
        :return: 获取得到的用户名、密码和确认密码
        """
        return self.username.get(), self.password.get(), self.confirm.get()

    def quit_func(self):
        """
        封装到注册界面中的取消按钮中，实现从注册界面跳转到登陆界面
        """
        self.close()
        login_panel = LoginPanel()
        login_panel.show()

    def reg_func(self):
        """
        封装到注册界面的注册按钮中
        """
        username, password, confirm = self.get_input()
        client = Client()
        ret = client.send_register_info(username, password, confirm)
        print(ret)
        if ret == "密码不一致，请重新输入！":
            messagebox.showerror(title="Error", message="密码不一致，请重新输入！")
        else:
            if ret == "抱歉，用户名已存在！":
                messagebox.showerror(title="Error", message="抱歉，用户名已存在！")
            elif ret == "注册成功！":
                # 注册成功后提示，然后跳回登录界面
                messagebox.showinfo(title="Success", message="注册成功！")
                self.close()
                login_panel = LoginPanel()
                login_panel.show()
            else:
                messagebox.showerror(title="Error", message="发生未知错误！")

    def close_callback(self):
        self.close()
        login_panel = LoginPanel()
        login_panel.show()


class MainPanel:
    """主界面模板类，只需另外传入其他对象的方法"""
    def __init__(self, username, client):
        """初始化实例属性，用户名、在线列表、消息框、消息输入框等"""
        print("初始化主界面")
        self.main_frame = Tk()
        self.client = client
        self.username = username
        self.record_num=0
        self.online_list_box = None
        self.msg_box = None
        self.input_box = None
        self.audio=Audio()
    def set_panel_position(self):
        """
        设置聊天主界面在屏幕的位置和大小
        """
        width = 800
        height = 500
        screen_width = self.main_frame.winfo_screenwidth()
        screen_height = self.main_frame.winfo_screenheight()
        gm_str = "%dx%d+%d+%d" % (width, height, (screen_width - width) / 2,
                                  (screen_height - 1.2 * height) / 2)
        self.main_frame.geometry(gm_str)
        self.main_frame.minsize(width, height)  # 设置最小尺寸

    def config_for_mian_panel(self):
        """
        给主界面设置其他配置
        """
        self.main_frame.title("MyChat")
        self.main_frame.configure(background="lightblue")

        # 设置窗口关闭按钮时，调用方法，用于退出时关闭socket连接
        self.main_frame.protocol("WM_DELETE_WINDOW", self.close_callback)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

    def set_online_list(self):
        """
        设置在线用户列表
        """
        online_list_var = StringVar()  # 设置变量，储存在线列表中的值
        self.online_list_box = Listbox(self.main_frame, selectmode=NO, listvariable=online_list_var, bg="lightblue", fg="black", font=("Microsoft Yahei", 14), highlightcolor="white")
        self.online_list_box.grid(row=1, column=0, rowspan=3, sticky=N + S, padx=10, pady=(0, 5))

        # 给在线列表设置滚动栏
        list_sr_bar = Scrollbar(self.main_frame)
        list_sr_bar.grid(row=1, column=0, sticky=N + S + E, rowspan=3, pady=(0, 5))

        # 设置滚动效果命令，即下拉滚动条和鼠标滚动
        list_sr_bar['command'] = self.online_list_box.yview
        self.online_list_box['yscrollcommand'] = list_sr_bar.set

    def set_msg_box(self):
        """
        设置聊天消息显示框
        """
        # 设置消息滚动栏
        msg_sr_bar = Scrollbar(self.main_frame)
        msg_sr_bar.grid(row=1, column=1, sticky=E + N + S, padx=(0, 10))

        # 创建消息框
        self.msg_box = Text(self.main_frame, bg="lightblue", height=1, highlightcolor="white", highlightthickness=1)

        # 显示消息的文本框不可编辑，当需要修改内容时再修改版为可以编辑模式 NORMAL
        # 消息框的其他设置，以及位置摆放
        self.msg_box.config(state=DISABLED)
        self.msg_box.tag_configure('greencolor', foreground='green')
        self.msg_box.tag_configure('bluecolor', foreground='blue')
        self.msg_box.grid(row=1, column=1, sticky=W + E + N + S, padx=(10, 30))

        msg_sr_bar["command"] = self.msg_box.yview
        self.msg_box["yscrollcommand"] = msg_sr_bar.set

    def set_input_box(self):
        """
        设置聊天输入窗口
        """
        # 设置聊天输入窗口滚动栏
        send_sr_bar = Scrollbar(self.main_frame)
        send_sr_bar.grid(row=2, column=1, sticky=E + N + S, padx=(0, 10), pady=10)

        # 设置聊天输入窗口
        self.input_box = Text(self.main_frame, bg="lightblue", height=11, highlightcolor="white", highlightbackground="#444444", highlightthickness=3)
        self.input_box.see(END)
        self.input_box.grid(row=2, column=1, sticky=W + E + N + S, padx=(10, 30), pady=10)

        send_sr_bar["command"] = self.input_box.yview
        self.input_box["yscrollcommand"] = send_sr_bar.set

    def set_btn(self):
        """
        设置发送和清空按钮
        """
        Button(self.main_frame, text="Send", bg="lightblue", font=("Microsoft Yahei", 9), fg="black", command=self.send_func).grid(row=3, column=1, pady=5, padx=10, sticky=W, ipady=3, ipadx=10)
        Button(self.main_frame, text="Clear", bg="lightblue", font=("Microsoft Yahei", 9), fg="black", command=self.clear_input_box).grid(row=3, column=1, pady=5, sticky=W, padx=(90, 0), ipady=3, ipadx=10)
        Button(self.main_frame, text="Upload", bg="lightblue", font=("Microsoft Yahei", 9), fg="black", command=self.upload_func).grid(row=3, column=1, pady=5, padx=180, sticky=W, ipady=3, ipadx=10)
        Button(self.main_frame, text="dnload", bg="lightblue", font=("Microsoft Yahei", 9), fg="black", command=self.download_func).grid(row=3, column=1, pady=5, padx=(270,0), sticky=W, ipady=3, ipadx=10)
        Button(self.main_frame, text="sd_aud", bg="lightblue", font=("Microsoft Yahei", 9), fg="black",command=self.sd_aud).grid(row=3, column=1, pady=5, padx=(360, 0), sticky=W, ipady=3, ipadx=10)
        Button(self.main_frame, text="play", bg="lightblue", font=("Microsoft Yahei", 9), fg="black",command=self.play).grid(row=3, column=1, pady=5, padx=(450, 0), sticky=W, ipady=3, ipadx=10)
    def show(self):
        """主界面布局"""
        self.set_panel_position()
        self.config_for_mian_panel()

        # 设置标题
        Label(self.main_frame, text="MyChat：" + self.username, font=("Microsoft Yahei", 13), bg="lightblue", fg="black").grid(row=0, column=0, ipady=10, padx=10, columnspan=2, sticky=W)
        self.set_online_list()
        self.set_msg_box()
        self.set_input_box()
        self.set_btn()

        # 启动
        self.main_frame.mainloop()

    def handle_msg(self):
        """
        处理关于在线用户列表和消息框中内容的信息
        """
        time.sleep(2)  # 暂停一下，等待主界面渲染完毕
        while True:
            try:
                # 获取数据类型：在线用户列表、消息内容
                recv_data = self.client.recv_data()
                if recv_data:
                    ret = re.match(r"(#![\w]{7}#!)([\s\S]+)", recv_data)
                    option = ret.group(1)
                    print("recieved type: " + option)
                    print(recv_data)
                    if option == "#!onlines#!":
                        print("获取在线用户列表数据")
                        # 将一次性获取得到的用户名以 “#!”为标记分隔成一个列表
                        online_usernames = ret.group(2).split("#!")
                        online_usernames.remove("")  # 去除列表中的空字符串
                        print(online_usernames)
                        self.update_online_list(online_usernames)
                        print(online_usernames)
                    elif option == "#!message#!":  # 正则区分用户名和消息内容
                        print("获取新消息")
                        username_content = ret.group(2)
                        ret = re.match(r"(.*)#!([\s\S]*)", username_content)
                        username = ret.group(1)
                        content = ret.group(2)
                        self.set_msg_show_format(username, content)
                    elif option == "#!notices#!":
                        print("获取用户上下线通知")
                        notice = ret.group(2)  # 将通知提取出来
                        self.show_notice(notice)
                    elif option == "#!downlod#!":
                        print("Begin download file")
                        notice = ret.group(2)  # 将通知提取出来
                        self.show_notice(notice)
                        fileinfo_size=struct.calcsize('128sl')
                        buf = self.client.client_socket.recv(fileinfo_size)
                        if buf: #如果不加这个if，第一个文件传输完成后会自动走到下一句
                            filename,filesize =struct.unpack('128sl',buf)
                            filename_f = filename.decode().strip('\x00')
                            filenewname = filename_f
                            if filenewname[-1:]=="a":
                                filenewname="tem.wav"
                            #print ('file new name is %s, filesize is %s' %(filenewname,filesize))
                            recvd_size = 0 #定义接收了的文件大小
                            #断点续传
                            #if os.path.exists(filenewname):
                            #    recvd_size = os.path.getsize(filenewname)
                            #self.client.client_socket.send(str(recvd_size).encode())
                            file = open(filenewname,'ab')
                            print ('stat receiving...')
                            while not recvd_size == filesize:
                                if filesize - recvd_size > 1024:
                                    rdata = self.client.client_socket.recv(1024)
                                    recvd_size += len(rdata)
                                else:
                                    rdata = self.client.client_socket.recv(filesize - recvd_size)
                                    recvd_size = filesize
                                file.write(rdata)
                            file.close()
                            if filenewname[-3:]=="wav":
                                self.audio.play_record()
                        print ('receive done')
                         #connection.close()
            except Exception as ret:
                print("接受服务器消息出错，消息接受子线程结束。" + str(ret))
                break

    def update_online_list(self, online_usernames):
        """刷新在线列表 -- 一遍又一遍地清空，再回填到列表中"""
        print("正在更新列表...")
        self.online_list_box.delete(0, END)  # 全部清空
        print("**********")
        for username in online_usernames:
            self.online_list_box.insert(0, username)

    def show_notice(self, notice):
        """
        在消息文本框中显示用户的上下线通知
        :param notice: 待显示的通知
        """
        self.msg_box.config(state=NORMAL)  # 文本框设置为可改变，实现文本插入
        self.msg_box.insert(END, notice, "red")
        self.msg_box.insert(END, "\n", "red")
        self.msg_box.config(state=DISABLED)  # 文本框设置为不可改变
        self.msg_box.see(END)  # 滚动到文本框的最底部

    def set_msg_show_format(self, username, content):
        """
        将接受到的消息显示在消息文本框中，自己的消息用蓝色的，别人的消息用黑色
        :param username: 发送消息的用户的用户名
        :param content: 待显示的消息内容
        """
        self.msg_box.config(state=NORMAL)
        title = username + " " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n"
        if username == self.username:
            self.msg_box.insert(END, title, "blue")
        else:
            self.msg_box.insert(END, title, "black")
        self.msg_box.insert(END, content + "\n")
        self.msg_box.config(state=DISABLED)
        self.msg_box.see(END)

    def clear_input_box(self):
        """清空消息输入框"""
        self.input_box.delete('0.0', END)

    def get_input_box_content(self):
        return self.input_box.get('0.0', END)

    def send_func(self):
        """
        封装到主界面中的发送消息按钮中
        """
        content = self.get_input_box_content()
        self.client.send_msg(content)
        self.clear_input_box()
    def upload_func(self):
        """
        封装到主界面中的发送消息按钮中
        """
        content = self.get_input_box_content()
        self.client.upload_file(content)
        time.sleep(2)
        self.client.send_msg("Upload "+content)
        self.clear_input_box()
    def download_func(self):
        """
        封装到主界面中的发送消息按钮中
        """
        content = self.get_input_box_content()
        content=content.strip()
        self.client.download_file(content)
        self.clear_input_box()
    def sd_aud(self):
        """
        封装到主界面中的发送消息按钮中
        """
        content = self.get_input_box_content()
        file_name=str(self.username)+str(self.record_num)+".a"
        self.audio.record(file_name,int(content))
        time.sleep(2)
        self.client.send_msg("record " + file_name)
        time.sleep(2)
        self.clear_input_box()
    def play(self):
        """
        封装到主界面中的发送消息按钮中
        """
        content = self.get_input_box_content()
        content=content.strip()
        self.client.download_file(content)
        # while True:
        #     if os.path.exists("tem.wav"):
        #         break
        # self.audio.play_record()
        self.clear_input_box()
    def close(self):
        if self.main_frame == None:
            print("未显示界面")
        else:
            self.main_frame.destroy()

    def close_callback(self):
        self.client.close()
        self.close()


if __name__ == "__main__":
    login_panel = LoginPanel()
    login_panel.show()
