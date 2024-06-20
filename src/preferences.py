#preferences.py
# TODO make pref window close on Ctrl+W and allow close app with Ctrl+Q
# FIXME [Widget of type “AddWaterPreferences” already has an accessible role of type “GTK_ACCESSIBLE_ROLE_GENERIC”]



from gi.repository import Adw, Gtk, Gio, GLib

@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/preferences.ui")
class AddWaterPreferences(Adw.PreferencesDialog):
    __gtype_name__ = "AddWaterPreferences"

    def __init__(self):
        super().__init__()
        print("preferences is alive!")
