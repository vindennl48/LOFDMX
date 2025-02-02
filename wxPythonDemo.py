import wx

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Control Panel", size=(800, 600))
        
        # Main panel with sizer
        main_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Create sidebar
        self.sidebar = wx.Panel(main_panel, size=(150, -1))
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create navigation buttons
        nav_items = [
            ("Pedalboard", "pedalboard"),
            ("DMX Lighting", "dmx"),
            ("Reaper", "reaper"),
            ("Settings", "settings")
        ]
        
        self.buttons = []
        for label, tag in nav_items:
            btn = wx.Button(self.sidebar, label=label, style=wx.BU_LEFT)
            btn.Bind(wx.EVT_BUTTON, lambda evt, t=tag: self.switch_panel(evt, t))
            sidebar_sizer.Add(btn, 0, wx.EXPAND|wx.ALL, 5)
            self.buttons.append(btn)
        
        # Add spacer to push settings to bottom
        sidebar_sizer.AddStretchSpacer()
        settings_btn = wx.Button(self.sidebar, label="Settings")
        settings_btn.Bind(wx.EVT_BUTTON, lambda e: self.switch_panel(e, "settings"))
        sidebar_sizer.Add(settings_btn, 0, wx.EXPAND|wx.ALL, 5)
        
        self.sidebar.SetSizer(sidebar_sizer)
        
        # Create content panel
        self.content_panel = wx.Panel(main_panel)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create different views
        self.panels = {
            "pedalboard": self.create_pedalboard_panel(),
            "dmx": self.create_dmx_panel(),
            "reaper": self.create_reaper_panel(),
            "settings": self.create_settings_panel()
        }
        
        # Show initial panel
        self.current_panel = None
        self.switch_panel(None, "pedalboard")
        
        self.content_panel.SetSizer(self.content_sizer)
        
        # Add to main sizer
        sizer.Add(self.sidebar, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self.content_panel, 1, wx.EXPAND|wx.ALL, 5)
        main_panel.SetSizer(sizer)
        
        # macOS-specific styling
        self.sidebar.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        
    def switch_panel(self, event, panel_name):
        if self.current_panel:
            self.current_panel.Hide()
        self.current_panel = self.panels[panel_name]
        self.current_panel.Show()
        self.content_sizer.Layout()
        
    def create_pedalboard_panel(self):
        panel = wx.Panel(self.content_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add pedalboard-specific controls
        title = wx.StaticText(panel, label="Pedalboard Configuration")
        title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(title, 0, wx.ALL, 10)
        
        # Add more controls here...
        sizer.Add(wx.CheckBox(panel, label="Enable MIDI Routing"), 0, wx.ALL, 5)
        sizer.Add(wx.CheckBox(panel, label="Enable Audio Loopback"), 0, wx.ALL, 5)
        
        panel.SetSizer(sizer)
        panel.Hide()
        return panel
        
    def create_dmx_panel(self):
        panel = wx.Panel(self.content_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(panel, label="DMX Lighting Control")
        title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(title, 0, wx.ALL, 10)
        
        # Add DMX controls...
        sizer.Add(wx.StaticText(panel, label="Universe Configuration:"), 0, wx.ALL, 5)
        sizer.Add(wx.SpinCtrl(panel, min=1, max=8), 0, wx.ALL, 5)
        sizer.Add(wx.Button(panel, label="Test Lights"), 0, wx.ALL, 5)
        
        panel.SetSizer(sizer)
        panel.Hide()
        return panel
        
    def create_reaper_panel(self):
        panel = wx.Panel(self.content_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(panel, label="Reaper Integration")
        title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(title, 0, wx.ALL, 10)
        
        # Reaper controls...
        sizer.Add(wx.StaticText(panel, label="Reaper API Key:"), 0, wx.ALL, 5)
        sizer.Add(wx.TextCtrl(panel), 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(wx.Button(panel, label="Connect to Reaper"), 0, wx.ALL, 5)
        
        panel.SetSizer(sizer)
        panel.Hide()
        return panel
        
    def create_settings_panel(self):
        panel = wx.Panel(self.content_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(panel, label="Application Settings")
        title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(title, 0, wx.ALL, 10)
        
        # Settings controls...
        sizer.Add(wx.CheckBox(panel, label="Start with system"), 0, wx.ALL, 5)
        sizer.Add(wx.CheckBox(panel, label="Enable Auto-Updates"), 0, wx.ALL, 5)
        sizer.Add(wx.StaticText(panel, label="Theme:"), 0, wx.ALL, 5)
        sizer.Add(wx.Choice(panel, choices=["System Default", "Light", "Dark"]), 0, wx.ALL, 5)
        
        panel.SetSizer(sizer)
        panel.Hide()
        return panel

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
