# custTray_phoenix.py

import wx
import wx.adv


class TrayIcon(wx.adv.TaskBarIcon):
    """"""

    def __init__(self, frame):
        """Constructor"""
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame

        icon = wx.Icon('assets/app.ico', wx.BITMAP_TYPE_ICO)

        self.SetIcon(icon, "Restore")

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarLeftClick)

    def OnTaskBarActivate(self, evt):
        """"""
        pass

    def OnTaskBarClose(self, evt):
        """
        Уничтожает иконку панели задач и рамку в самой иконке панели задач
        """
        self.frame.Close()

    def OnTaskBarLeftClick(self, evt):
        """
        Создаёт меню, которое появляется при нажатии правой кнопки мыши.
        """
        self.frame.Show()
        self.frame.Restore()
