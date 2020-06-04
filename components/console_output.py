import sys
import wx


class ConsoleOutput(wx.TextCtrl):

    def __init__(self, *args, **kwargs):
        """
        Инициируем текстовый контроль
        """
        wx.TextCtrl.__init__(self, *args, **kwargs)


    def write(self, text):
        self.WriteText(text)
