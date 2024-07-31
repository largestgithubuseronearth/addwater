# toast.py

from gi.repository import Adw, Gtk

class AddWaterToaster(Adw.ToastOverlay):
    __gtype_name__ = AddWaterToaster

    def __init__(self):
        super().__init__()
        print("Toaster is alive!")
