# firefox_page.py

from gi.repository import Gtk, Adw, GObject

@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/firefox-page.ui")
class FirefoxPage(Adw.ViewStackPage):
    __gtype_name__ = "FirefoxPage"

    def __init__(self, **kwargs):
        super().__init__()

        print("firefox page loaded")
