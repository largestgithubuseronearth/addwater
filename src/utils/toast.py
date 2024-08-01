# toast.py
# TODO hopefully find a way to make this without creating a ui template

from gi.repository import Adw, Gtk

class AddWaterToaster(Adw.ToastOverlay):
    __gtype_name__ = AddWaterToaster

    def __init__(self):
        super().__init__()
        print("Toaster is alive!")
