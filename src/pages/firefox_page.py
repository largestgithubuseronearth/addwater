# firefox_page.py

from gi.repository import Gtk, Adw, Gio, GLib

from ..utils.profiles import find_profiles
from ..utils import install
from ..utils import paths
from ..utils import online

import logging
log = logging.getLogger(__name__)

# TEMP move to another module and import
gsettings_keys = [
    "hide-single-tab",
    "normal-width-tabs",
    "swap-tab-close",
    "bookmarks-toolbar-under-tabs",
    "tabs-as-headerbar",
    "active-tab-contrast",
    "close-only-selected-tabs",
    "symbolic-tab-icons",
    "hide-webrtc-indicator"
]


@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/firefox-page.ui")
class FirefoxPage(Adw.Bin):
    __gtype_name__ = "FirefoxPage"
    # Firefox Attributes
    # TODO find dir automatically. Simply check if folder exists?
    firefox_dir = paths.FIREFOX_BASE
    firefox_profile = None
    firefox_version = None


    transaction = {}
    all_settings = ["gnomeTheme.hideSingleTab"]

    # Widget controls
    profile_switcher_list = Gtk.Template.Child()
    profile_switcher = Gtk.Template.Child()

    def __init__(self):
        # TODO read schema's keys and set all preferences accordingly. Store this info in a dict.
        self.settings_firefox = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")
        self.settings_firefox.delay()
        self.init_prefs()

        # TODO Find firefox installation folder


        self.profiles = find_profiles(moz_path=self.firefox_dir)
        for each in self.profiles:
            self.profile_switcher_list.append(each["name"])


        # online.check_for_updates(app="firefox")

    def init_prefs(self):

        pass


    def apply_changes(self):
        # TODO use self.settings_firefox.apply() to apply all stored changes
        # TODO can I still bind the switches to the keys and have it work before applying?
        pass

    def begin_install(self):

        install.install_firefox(firefox_path=self.firefox_dir,
                        profile=self.firefox_profile,
                        version=self.firefox_version)
