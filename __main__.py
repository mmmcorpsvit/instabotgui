import sys
import wx

from components.ConsoleOutput import ConsoleOutput
from components.TrayIcon import TrayIcon

# ---------------------------------------------------------------------------
from core.bot import get_insta_actions_list


def WriteText(text):
    if text[-1:] == '\n':
        text = text[:-1]
    wx.LogMessage(text)


class Log:
    write = WriteText


# ---------------------------------------------------------------------------

class InstagramBox(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        sampleList = ['zero', 'one', 'two', 'three', 'four', 'five',
                      'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
                      'twelve', 'thirteen', 'fourteen']

        wx.StaticText(self, -1, "This example uses the wx.ListBox control.", (45, 10))
        wx.StaticText(self, -1, "Select one:", (15, 50))
        self.lb1 = wx.ListBox(self, 60, (100, 50), (90, 120), sampleList, wx.LB_SINGLE | wx.LB_OWNERDRAW)
        self.Bind(wx.EVT_LISTBOX, self.EvtListBox, self.lb1)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.EvtListBoxDClick, self.lb1)
        self.lb1.Bind(wx.EVT_RIGHT_UP, self.EvtRightButton)
        self.lb1.SetSelection(3)
        self.lb1.Append("with data", "This one has data")
        self.lb1.SetClientData(2, "This one has data")

        # These only work on Windows
        # self.lb1.SetItemBackgroundColour(1, "green")
        # self.lb1.SetItemForegroundColour(2, "red")

        wx.StaticText(self, -1, "Select many:", (220, 50))
        self.lb2 = wx.ListBox(self, 70, (320, 50), (90, 120), sampleList, wx.LB_EXTENDED)
        self.Bind(wx.EVT_LISTBOX, self.EvtMultiListBox, self.lb2)
        self.lb2.Bind(wx.EVT_RIGHT_UP, self.EvtRightButton)
        self.lb2.SetSelection(0)

        sampleList = sampleList + ['test a', 'test aa', 'test aab',
                                   'test ab', 'test abc', 'test abcc',
                                   'test abcd']
        sampleList.sort()
        wx.StaticText(self, -1, "Find Prefix:", (15, 250))

    def EvtListBox(self, event):
        self.log.WriteText('EvtListBox: %s, %s, %s\n' %
                           (event.GetString(),
                            event.IsSelection(),
                            event.GetSelection()
                            # event.GetClientData()
                            ))

        lb = event.GetEventObject()
        # data = lb.GetClientData(lb.GetSelection())

        # if data is not None:
        # self.log.WriteText('\tdata: %s\n' % data)

    def EvtListBoxDClick(self, event):
        self.log.WriteText('EvtListBoxDClick: %s\n' % self.lb1.GetSelection())
        self.lb1.Delete(self.lb1.GetSelection())

    def EvtMultiListBox(self, event):
        self.log.WriteText('EvtMultiListBox: %s\n' % str(self.lb2.GetSelections()))

    def EvtRightButton(self, event):
        self.log.WriteText('EvtRightButton: %s\n' % event.GetPosition())

        if event.GetEventObject().GetId() == 70:
            selections = list(self.lb2.GetSelections())
            selections.reverse()

            for index in selections:
                self.lb2.Delete(index)


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
