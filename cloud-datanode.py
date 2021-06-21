import socket
import json
import libvirt
import os
from random import randint


class Cloud:

    def __init__(self):
        self.xml = '''<domain type='kvm'> 
    <name>{name}</name>            
    <memory unit='MB'>{mostmemory}</memory>                
    <currentMemory unit='MB'>{memory}</currentMemory>   
    <vcpu>{cpu}</vcpu>                                               
    <os> 
      <type arch='x86_64' machine='pc'>hvm</type>
	  <boot dev='hd'/>
      <boot dev='cdrom'/>
   </os> 
   <features> 
     <acpi/> 
     <apic/> 
     <pae/> 
   </features> 
   <clock offset='localtime'/> 
   <on_poweroff>destroy</on_poweroff> 
   <on_reboot>restart</on_reboot>   
   <on_crash>destroy</on_crash> 
   <devices> 
     <emulator>/usr/libexec/qemu-kvm</emulator> 
     <disk type='file' device='disk'> 
      <driver name='qemu' type='qcow2'/>          
      <source file='/home/yaokx/cloud/{qcname}.qcow2'/>        
       <target dev='hda' bus='ide'/> 
     </disk> 
     <disk type='file' device='cdrom'> 
	     <source file='/home/yaokx/iso/ubuntu-18.04.5-desktop-amd64.iso'/>
       <target dev='hdb' bus='ide'/> 
     </disk> 
    <interface type='bridge'>                                           
      <source bridge='br0'/> 
      <mac address="{mac}"/>   
    </interface> 
    <input type='mouse' bus='ps2'/>    
        <graphics type='vnc' port='{vncport}' listen='0.0.0.0' keymap='en-us' passwd='{vncpwd}'/>
   </devices> 
</domain> '''
        self.conn = libvirt.open("qemu:///system")  # 链接
        try:
            with open("peizhi.json", "r") as f:  # 打开文件
                content = f.read()
                data = json.loads(content)
                self.vncport = int(data["vncport"])
                self.mac = data["mac"].split(" ")
        except:
            self.vncport = 5900
            self.mac = []

    # 随机生成一个mac地址
    def make_mac(self):
        # 随机创建一个mac地址
        while True:
            result = "52:" + ":".join(["%02x" % x for x in map(lambda x: randint(0, 255), range(5))])
            if result not in self.mac:
                self.mac.append(result)
                return result

    # 查看能否建立这个虚拟机
    def compare(self, data):
        nodeinfo = self.conn.getInfo()  # 获取虚拟化主机信息
        # 当主机内存小于创建的就退出
        if nodeinfo[1] < int(data["memory"]):
            return False
        # 当虚拟机cpu个数少于创建的就退出
        if nodeinfo[2] < int(data["cpu"]):
            return False
        # 当空闲内存小于300mb说明主机已经很繁忙了，所以不创建虚拟机退出
        if self.conn.getFreeMemory() / 1024 / 1024 < 300:
            return False
        # 获取磁盘剩余gb
        info = os.statvfs('/')
        free_size = info.f_bsize * info.f_bavail / 1024 / 1024 / 1024
        if free_size < int(data["hd"]):
            return False
        return True

    # 创建虚拟机
    def make_machine(self, data):
        nodeinfo = self.conn.getInfo()  # 获取虚拟化主机信息
        # 开始创建虚拟机
        hostname = data["webname"] + "-" + data["username"] + "-" + data["hostname"]
        os.popen("qemu-img create -f qcow2 /home/yaokx/cloud/{}.qcow2 {}G".format(hostname, data["hd"]))
        newxml = self.xml.format(name=hostname, mostmemory=nodeinfo[1], memory=data["memory"], cpu=data["cpu"],
                                 qcname=hostname,
                                 mac=self.make_mac(), vncport=self.vncport, vncpwd=data["username"])
        # 创建虚拟机
        self.conn.defineXML(newxml)
        f = open('/home/yaokx/cloud/{}.xml'.format(hostname), 'w')
        f.write(newxml)
        f.close()
        self.vncport += 1
        # 输出当前信息
        allmac = ""
        for i in self.mac:
            if i != "":
                allmac += i
                if i != self.mac[-1]:
                    allmac += " "
        dic = {"vncport": self.vncport, "mac": allmac}
        dic = json.dumps(dic)
        f = open('peizhi.json', 'w')
        f.write(dic)
        f.close()

    # 打开虚拟机
    def open_machine(self, hostname):
        # 获取全部虚拟机名称
        dom_list = cloud.conn.listAllDomains()
        dom_list = [dom.name() for dom in dom_list]
        # 如果主机有虚拟机就打开然后返回true 没有就返回false
        if hostname in dom_list:
            dom = cloud.conn.lookupByName(hostname)
            dom.create()
            return True
        else:
            False

    # 关闭虚拟机
    def close_machine(self, hostname):
        # 获取全部虚拟机名称
        dom_list = cloud.conn.listAllDomains()
        dom_list = [dom.name() for dom in dom_list]
        # 如果主机有虚拟机就关闭然后返回true 没有就返回false
        if hostname in dom_list:
            dom = cloud.conn.lookupByName(hostname)
            dom.destroy()
            return True
        else:
            False
    #删除虚拟机
    def del_machine(self,hostname):
        # 获取全部虚拟机名称
        dom_list = cloud.conn.listAllDomains()
        dom_list = [dom.name() for dom in dom_list]
        # 如果主机有虚拟机就删除然后返回true 没有就返回false
        if hostname in dom_list:
            dom = cloud.conn.lookupByName(hostname)
            dom.destroy()
            dom.undefine()
            os.system("rm /home/yaokx/cloud/{}.xml".format(hostname))
            os.system("rm /home/yaokx/cloud/{}.qcow2".format(hostname))
            return True
        else:
            False



def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    return ip


if __name__ == "__main__":
    # 主机ip
    localIp = get_ip()
    # 服务器实际对象
    cloud = Cloud()
    # 创建UDP监听窗口
    PORT = 50000
    # 字节流获取大小
    BUFSIZE = 1024
    # 监听ip和端口，因为监听广播信息所以没有绑定ip
    ADDR = ("", PORT)
    # 创建监听对象 udp模式
    udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口
    udpSerSock.bind(ADDR)
    # 设置过期时间
    udpSerSock.settimeout(3)  # 设置一个时间提示，如果10秒钟没接到数据进行提示
    # 创建udp发送端口
    udpCliSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 可复用端口
    udpCliSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        try:
            data, addr = udpSerSock.recvfrom(BUFSIZE)
            data = data.decode('utf8').replace("'", '"')
            data = json.loads(data)
            if data["type"] == "new":
                print("newing")
                if cloud.compare(data):
                    re_addr = (str(addr[0]), int(data["port"]))
                    re = "ok"
                    re = str.encode(re)
                    udpCliSock.sendto(re, re_addr)
                    try:
                        data, addr = udpSerSock.recvfrom(BUFSIZE)
                        data = data.decode('utf8').replace("'", '"')
                        data = json.loads(data)
                        cloud.make_machine(data)
                        re_addr = (str(addr[0]), int(data["port"]))
                        re = str(localIp) + ":" + str(cloud.vncport - 1)
                        re = str.encode(re)
                        udpCliSock.sendto(re, re_addr)
                        print("new complate")
                    except socket.timeout:  # 如果10秒钟没有接收数据进行提示（打印 "time out"）
                        continue
            if data["type"] == "open":
                print("opening")
                hostname = data["webname"] + "-" + data["username"] + "-" + data["hostname"]
                if cloud.open_machine(hostname):
                    re_addr = (str(addr[0]), int(data["port"]))
                    re = "open"
                    re = str.encode(re)
                    udpCliSock.sendto(re, re_addr)
                    print("open complate")
            if data["type"] == "close":
                print("closeing")
                hostname = data["webname"] + "-" + data["username"] + "-" + data["hostname"]
                if cloud.close_machine(hostname):
                    re_addr = (str(addr[0]), int(data["port"]))
                    re = "close"
                    re = str.encode(re)
                    udpCliSock.sendto(re, re_addr)
                    print("close complate")
            if data["type"] == "del":
                print("deling")
                hostname = data["webname"] + "-" + data["username"] + "-" + data["hostname"]
                if cloud.del_machine(hostname):
                    re_addr = (str(addr[0]), int(data["port"]))
                    re = "del"
                    re = str.encode(re)
                    udpCliSock.sendto(re, re_addr)
                    print("del complate")

        except socket.timeout:  # 如果10秒钟没有接收数据
            print("waiting")
            continue