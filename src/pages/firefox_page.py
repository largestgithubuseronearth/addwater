# firefox_page.py

from gi.repository import Gtk, Adw, Gio, GLib

from ..utils.profiles import find_profiles
from ..utils.install_firefox import install_firefox
from ..utils import paths


@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/firefox-page.ui")
class FirefoxPage(Adw.Bin):
    __gtype_name__ = "FirefoxPage"

    app_main_path = None

    transaction = {}
    all_settings = ["gnomeTheme.hideSingleTab"]

    profile_list = Gtk.Template.Child()
    profile_switcher = Gtk.Template.Child()

    def __init__(self):
        install_firefox(firefox_path=paths.FIREFOX_BASE,
                        profile=None,
                        version=126)
        # TODO read schema's keys and set all preferences accordingly. Store this info in a dict.
        self.settings_firefox = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")

        # TODO Find firefox installation folder


        # TODO redo this to give correct moz_path based on installation
        # self.profiles = find_profiles(moz_path=(GLib.get_user_data_dir() + "/temp/"))
        # for each in self.profiles:
        #     self.profile_list.append(each["name"])


