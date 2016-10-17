# -*- coding: cp936 -*-
# ==========================================================
# $Name: ssh_manage.py
# $Revision: 0.1.1
# $Function: server manager tool
# $Author: LiCaiRong
# $Email: xglcr@163.com
# $Create Date: 2009-12-25 12:30
# $Modify Date: 2009-12-25 12:30
# ==========================================================

import wx,threading,os,glob,paramiko,time
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

TIMEOUT = 5
historycmd = []
textdata = []
lock = threading.RLock()
for x in range(1000):
    textdata.append(x)

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, (15, 50), (890, 360), style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        CheckListCtrlMixin.__init__(self)

class InsertFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'SSH批量连接工具', pos=(100, 50),
                size=(930, 690), style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetIcon(wx.Icon("fish.ico", wx.BITMAP_TYPE_ICO))
        font=wx.Font(9,wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.panel = wx.Panel(self)
        self.button1 = wx.Button(self.panel, label="执行命令", pos=(15, 15), size=(80, 25))
        self.porttext = wx.TextCtrl(self.panel, -1, "22", pos=(110,17), size=(50, 21))
        self.usertext = wx.TextCtrl(self.panel, -1, "root", pos=(170,17), size=(50, 21))
        self.pwdtext = wx.TextCtrl(self.panel, -1, "", pos=(230,17), size=(70, 21), style=wx.TE_PASSWORD)
        self.pwdtext.SetFont(font)
        self.cmdtext = wx.TextCtrl(self.panel, -1, "uptime", pos=(310,17), size=(550, 21))
        self.cmdtext.SetFont(font)
        self.list1 = CheckListCtrl(self.panel)
        self.list1.SetBackgroundColour('#B0C4DE')
        sizedata = [25,34,120,120,490,80]
        labelname = ['','id','服务器名称','服务器IP','执行结果','备注']
        for i in range(6):
            if i != 1:
                self.list1.InsertColumn(i, labelname[i], format=wx.LIST_FORMAT_LEFT, width=int(sizedata[i]))
            else:
                self.list1.InsertColumn(i, labelname[i], format=wx.LIST_FORMAT_CENTRE, width=int(sizedata[i]))
        button2 = wx.Button(self.panel, label="全选", pos=(15, 420), size=(60, 25))
        button3 = wx.Button(self.panel, label="全清", pos=(80, 420), size=(60, 25))
        button4 = wx.Button(self.panel, label="反选", pos=(145, 420), size=(60, 25))
        button5 = wx.Button(self.panel, label="批量选择", pos=(210, 420), size=(60, 25))
        self.cmbox = wx.ComboBox(self.panel, -1, "关键字", pos=(275, 422), size=(70, 30), choices=["错误"])
        button7 = wx.Button(self.panel, label="配置文件", pos=(350, 420), size=(60, 25))
        ipfile = glob.glob('*.txt')
        self.cmbox2 = wx.ComboBox(self.panel, -1, "重载配置", pos=(415, 422), size=(70, 30), choices=ipfile)
        button9 = wx.Button(self.panel, label="历史命令", pos=(490, 420), size=(60, 25))
        label = wx.StaticText(self.panel, -1, "状态：", pos=(565, 425))
        self.multitext = wx.TextCtrl(self.panel, -1, pos=(15, 455), size=(890, 175), style=wx.TE_MULTILINE)
        self.msg = wx.StaticText(self.panel, -1, label="", pos=(610, 425))
        self.Bind(wx.EVT_BUTTON, self.run, self.button1)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.printtext, self.list1)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.listadd, self.list1)
        self.Bind(wx.EVT_BUTTON, self.select_all, button2)
        self.Bind(wx.EVT_BUTTON, self.clear_all, button3)
        self.Bind(wx.EVT_BUTTON, self.inverse, button4)
        self.Bind(wx.EVT_BUTTON, self.batch_select, button5)
        self.Bind(wx.EVT_COMBOBOX, self.type, self.cmbox)
        self.Bind(wx.EVT_BUTTON, self.profile, button7)
        self.Bind(wx.EVT_COMBOBOX, self.reload, self.cmbox2)
        self.Bind(wx.EVT_BUTTON, self.history, button9)
        self.multitext.SetFont(font)
        wx.StaticText(self.panel, -1, "此程序为服务器批量管理工具，如果您在使用中发现问题或是有什么建议，请联系作者：xglcr@163.com", pos=(100, 635))
        self.openfile(self,'iplist.txt')

    def run(self,event):
        self.indexip = []
        curselection = []
        self.done_count = []
        self.fail_count = []
        self.port = int(self.porttext.GetValue())
        self.username = self.usertext.GetValue()
        self.password = self.pwdtext.GetValue()
        cmd = self.cmdtext.GetValue()
        num = self.list1.GetItemCount()
        for x in range(num):
            if self.list1.IsChecked(x):
                tmpdata = "%s %s" % (x,iplist[x].rstrip().split()[0])
                self.indexip.append(tmpdata)
                curselection.append(x)
        if (len(self.indexip) == 0):
            self.update_msg("没有选择执行命令的服务器，请选择！")
        elif not self.port or not self.username or not self.password or not cmd:
            self.update_msg("请输入端口、用户名、密码以及命令！")
        else:
            self.button1.Enable(False)
            historycmd.append("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),cmd))
            threads=[]
            loops=range(len(self.indexip))
            for i in loops:
                t = threading.Thread(target=self.sockets,args=(self,self.indexip[i],cmd))
                threads.append(t)
            for i in loops:
                threads[i].start()
            self.update_msg("[ 0/%3d]个连接线程已完成, [%3d]个错误" % (len(self.indexip), len(self.fail_count)))
            
    def sockets(self,event,index,data):
        try:
            HOST = index.split()[1]
            idx = index.split()[0]
            self.list1.SetStringItem(int(idx), 5, "正在执行...")
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(HOST, self.port, username=self.username, password=self.password)
            stdin, stdout , stderr = s.exec_command(data, timeout=TIMEOUT)
            if data.strip().split()[-1] == "&":
                return_data = "no return values"
            else:
                return_data = stdout.read()
            dataline = return_data.split('\n')[0]
            self.list1.SetStringItem(int(idx), 4, unicode(dataline,"gbk"))
            self.list1.SetStringItem(int(idx), 5, "完成")
            svrname = unicode(iplist[int(idx)].rstrip().split()[1],'gbk')
            value = unicode("执行结果","gbk")
            memo = unicode("备注：完成","gbk")
            textdata[int(idx)] = "%s %s %s:\n%s\n%s" % (svrname,HOST,value,unicode(return_data,"gbk"),memo)
            lock.acquire()
            self.multitext.SetValue("%s" % textdata[int(idx)])
            lock.release()
            s.close()
            self.done_count.append(HOST)
            self.update_msg("[%3d/%3d]个连接线程已完成, [%3d]个错误" % (len(self.done_count)+len(self.fail_count),len(self.indexip), len(self.fail_count)))
            if len(self.done_count) + len(self.fail_count) == len(self.indexip):
                self.button1.Enable(True)
        except Exception, e:
            dataline = "%s" % e
            self.list1.SetStringItem(int(idx), 4, dataline)
            self.list1.SetStringItem(int(index.split()[0]), 5, "错误")
            svrname = unicode(iplist[int(idx)].rstrip().split()[1],'gbk')
            value = unicode("执行结果","gbk")
            memo = unicode("备注：错误","gbk")
            textdata[int(idx)] = "%s %s %s:\n%s\n%s" % (svrname,HOST,value,dataline,memo)
            s.close()
            self.fail_count.append(index.split()[0])
            self.update_msg("[%3d/%3d]个连接线程已完成, [%3d]个错误" % (len(self.done_count)+len(self.fail_count),len(self.indexip), len(self.fail_count)))
            if len(self.done_count) + len(self.fail_count) == len(self.indexip):
                self.button1.Enable(True)

    def update_msg(self, msg):
        self.msg.SetLabel(msg)
        
    def printtext(self,event):
        cur = self.list1.GetFirstSelected()
        self.multitext.SetValue("%s" % textdata[int(cur)])

    def reload(self,event):
        IPLIST = self.cmbox2.GetValue()
        self.openfile(self,IPLIST)

    def openfile(self,event,IP):
        num = self.list1.GetItemCount()
        if (num != 0):
            self.list1.DeleteAllItems()
        f = open(IP,'r')
        global iplist
        iplist = []
        row = 0
        for line in f:
            iplist.append(line)
            ip,notes = line.split()
            self.list1.InsertStringItem(row,'')
            self.list1.SetStringItem(row, 1, str(row))
            self.list1.SetStringItem(row, 2, notes)
            self.list1.SetStringItem(row, 3, ip)
            row += 1
        f.close()
    
    def listadd(self,event):
        self.cmbox.Clear()
        self.cmbox.Append("错误")
        cur = self.list1.GetFirstSelected()
        notes = unicode(iplist[cur].rstrip().split()[1],'gbk')
        for i in range(len(notes.split('_'))):
            self.cmbox.Append(notes.split('_')[i])
            self.cmbox.Append(notes.split('_')[i][0:-1])
            self.cmbox.Append(notes.split('_')[i][0:-2])
    
    def type(self,event):
        selection = []
        match = self.cmbox.GetValue()
        num = self.list1.GetItemCount()
        if match == u"错误":
            self.clear_all(self)
            for i in self.fail_count:
                self.list1.CheckItem(int(i))
                selection.append(int(i))
        else:
            for i in range(num):
                tmp = (unicode(iplist[i],"gbk").rstrip().split()[1].lower()).find(match.lower())
                if (tmp != -1):
                    self.list1.CheckItem(i)
                    selection.append(i)
        self.update_msg("已勾选符合条件的服务器[ %s ]台！" % len(selection))
    
    def select_all(self,event):
        num = self.list1.GetItemCount()
        for i in range(num):
            self.list1.CheckItem(i)
        self.update_msg("当前已选择服务器[ %s ]台！" % num)

    def clear_all(self,event):
        num = self.list1.GetItemCount()
        for i in range(num):
            self.list1.CheckItem(i,False)
        self.update_msg("当前未选择任何服务器！")

    def inverse(self,event):
        selection = []
        num = self.list1.GetItemCount()
        for i in range(num):
            if self.list1.IsChecked(i):
                self.list1.CheckItem(i,False)
            else:
                self.list1.CheckItem(i)
                selection.append(i)
        self.update_msg("当前已选择服务器[ %s ]台！" % len(selection))

    def batch_select(self,event):
        selection = []
        i = self.list1.GetFirstSelected()
        while i != -1:
            self.list1.CheckItem(i)
            i = self.list1.GetNextSelected(i)
            selection.append(i)
        self.update_msg("已勾选高亮的服务器[ %s ]台！" % len(selection))

    def profile(self,event):
        wx.Execute('notepad admin.ini')

    def history(self,event):
        self.multitext.Clear()
        for i in historycmd:
            self.multitext.AppendText(i)
        self.update_msg("总共[ %s ]条历史命令！" % len(historycmd))


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = InsertFrame(parent=None, id=-1)
    frame.Show()
    app.MainLoop()