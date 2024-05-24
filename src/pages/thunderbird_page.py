
from gi.repository import Adw, Gtk, Gio, GLib

@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/thunderbird-page.ui")
class ThunderbirdPage(Adw.ViewStackPage):
    __gtype_name__ = "ThunderbirdPage"

    def __init__(self, **kwargs):
        super().__init__()

        print("thundy page!")
