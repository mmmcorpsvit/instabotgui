import wx
import wx.adv
# import wx.propgrid as pg
import wx.propgrid as wxpg


class PropertyEditor(wxpg.PropertyGridManager):
    """"""

    def __init__(self, frame, *args, **kw):
        """Constructor"""
        super().__init__(frame, style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_AUTO_SORT | wxpg.PG_TOOLBAR)
        # self.pg = wxpg.PropertyGridManager(frame, style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_AUTO_SORT | wxpg.PG_TOOLBAR)

        # Show help as tooltips
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)

# pg = pg.PropertyGrid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE)
