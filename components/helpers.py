import wx


def WriteText(text):
    if text[-1:] == '\n':
        text = text[:-1]
    wx.LogMessage(text)


class Log:
    write = WriteText
