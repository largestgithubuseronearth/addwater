# thunderbird_page.py
# TODO Create thunder page logic

from gi.repository import Gtk, Adw

@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/thunderbird-page.ui")
class ThunderbirdPage(Adw.Bin):
    __gtype_name__ = "ThunderbirdPage"

    def __init__(self):
        print("thunderbird")
