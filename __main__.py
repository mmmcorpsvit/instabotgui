import sys
import wx

from components.ConsoleOutput import ConsoleOutput
from components.PropertyEditor import PropertyEditor
from components.TrayIcon import TrayIcon

from core.bot import get_insta_actions_list


class MainFrame(wx.Frame):
    """"""

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="InstaBot v0.1")

        # Добавляем панель так, чтобы она выглядела корректно на всех платформах
        panel = wx.Panel(self, wx.ID_ANY)

        # TrayIcon
        self.tbIcon = TrayIcon(self)

        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # ConsoleLog
        # https://python-scripts.com/wxpython-redirecting-stdout-stderr
        # https://python-scripts.com/wxpython-redirect-pythons-logging-module-to-a-textctrl
        # https://python-scripts.com/textctrl-wxpython
        # panel = wx.Panel(self, wx.ID_ANY)
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        log = ConsoleOutput(panel, wx.ID_ANY, size=(300, 100), style=style)
        btn = wx.Button(panel, wx.ID_ANY, 'Test!')
        self.Bind(wx.EVT_BUTTON, self.onConsoleOutputButton, btn)

        # Добавляем виджеты в сайзер
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

        # Перенаправляем текст сюда
        sys.stdout = log

        # Actions list
        actions_list = wx.ListBox(panel)
        actions_list.Append(get_insta_actions_list())
        actions_list.SetSelection(0)
        sizer.Add(actions_list, 2, wx.ALL | wx.EXPAND, 5)

        # propertyeditor
        property_editor = PropertyEditor(panel)
        # sizer.Add(property_editor, 3, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)
        self.Show()

    def onConsoleOutputButton(self, event):
        print("You pressed the button!")

    def onClose(self, evt):
        """
        Уничтожает иконку панели задач и рамку
        """
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()

    def onMinimize(self, event):
        """
        Во время сворачивания, делаем так, чтобы приложение оставило иконку в трее
        """
        if self.IsIconized():
            self.Hide()


def main(argv):
    app = wx.App(False)
    frame = MainFrame()
    frame.SetSize(1200, 900)
    frame.Centre()

    app.MainLoop()


if __name__ == '__main__':
    main(sys.argv)
