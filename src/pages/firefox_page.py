# firefox_page.py

from gi.repository import Gtk, Adw, Gio, GLib

from ..utils.profiles import find_profiles
from ..utils.install_firefox import install_firefox
from ..utils import paths
from ..utils import online

import logging
# TODO do I need to type this into every single module?
log = logging.getLogger(__name__)


@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/firefox-page.ui")
class FirefoxPage(Adw.Bin):
    __gtype_name__ = "FirefoxPage"
    # Firefox Attributes
    # TODO find dir automatically. Simply check if folder exists?
    firefox_dir = paths.FIREFOX_BASE

    transaction = {}
    all_settings = ["gnomeTheme.hideSingleTab"]

    # Widget controls
    profile_switcher_list = Gtk.Template.Child()
    profile_switcher = Gtk.Template.Child()

    def __init__(self):
        # TODO read schema's keys and set all preferences accordingly. Store this info in a dict.
        self.settings_firefox = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")

        # TODO Find firefox installation folder


        # TODO Once I can find the correct firefox install, replace moz_path with user_firefox_dir
        self.profiles = find_profiles(moz_path=self.firefox_dir)
        print(self.profiles)
        if self.profiles is None:
            log.critical("Could not find any Firefox profiles.")
        for each in self.profiles:
            self.profile_switcher_list.append(each["name"])





        # online.check_for_updates(app="firefox")
        # install_firefox(firefox_path=self.firefox_dir,
                        # TODO this profile
        #                 profile="xtg2dvxg.claire",
        #                 version=126)



