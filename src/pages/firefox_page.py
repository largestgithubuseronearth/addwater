# firefox_page.py
# TODO once this is working properly turn this class into a generic parent class and spin off Firefox and Thunderbird Pages into their own subclasses

import logging, json
from gi.repository import Gtk, Adw, Gio, GLib
from .firefox_prefs import final
from ..utils.profiles import find_profiles, find_install
from ..utils import install
from ..utils import paths
from ..utils import online

log = logging.getLogger(__name__)


@Gtk.Template(resource_path="/dev/qwery/AddWater/pages/firefox-page.ui")
class FirefoxPage(Adw.Bin):
    """Firefox ViewStackPage. Must be converted into a generalized """
    __gtype_name__ = "FirefoxPage"

    # Firefox Attributes
    install_dir = find_install()
    selected_profile = None
    current_theme_version = None
    desired_theme_version = None


    transaction = {}

    # Widget controls
    preferences_page = Gtk.Template.Child()
    profile_list = Gtk.Template.Child()

     # = Gtk.Template.Child()

    def __init__(self):
        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")
        self.settings.delay()
        self.init_prefs()

        print(json.dumps(final, indent=2))
        for each in final:
            print(each["group_name"])
            for option in each["options"]:
                print(option)
            print("\n\n\n")


        self.profiles = find_profiles(moz_path=self.install_dir)
        for each in self.profiles:
            self.profile_list.append(each["name"])


        # Apply Changes action
        # TODO Should this be None? What does the parameter refer to?
        self.install_action(
            "water.apply-changes",
            None,
            self.apply_changes
            )


        online.check_for_updates(app="firefox")

    def init_prefs(self):
    # TODO Add Unstable features
        for each in final:
            group = Adw.PreferencesGroup(title=each["group_name"])

            for option in each["options"]:
                button = Adw.SwitchRow(
                    title=option["summary"],
                    tooltip_text=option["description"]
                )
                self.settings.bind(
                    option["key"],
                    button,
                    "active",
                    # TODO should I use GET flag instead to grab the setting first?
                    Gio.SettingsBindFlags.DEFAULT
                )
                # TODO bind buttons to the gschema keys
                group.add(button)
            self.preferences_page.add(group)


    def apply_changes(self, one, two, three):
        print(one)
        print(two)
        print(three)
        self.settings.apply()
        # TODO use self.settings_firefox.apply() to apply all stored changes
        # TODO can I still bind the switches to the keys and have it work before applying?

    def add_change(self, switch, state):
        pass

    def begin_install(self):

        install.install_firefox(firefox_path=self.install_dir,
                        profile=self.selected_profile,
                        version=self.desired_theme_version)
