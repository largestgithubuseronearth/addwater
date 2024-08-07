# window.py
#
# Copyright 2024 Qwery
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging, os.path, shutil
from gi.repository import Adw, Gtk, GLib, Gio, Gdk, GObject
from .addwater_page import AddWaterPage
from .theme_options import FIREFOX_OPTIONS, THUNDERBIRD_OPTIONS
from .utils import logs, paths

log = logging.getLogger(__name__)

firefox_url = "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases"
# thunderbird_url = "https://api.github.com/repos/rafaelmardojai/thunderbird-gnome-theme/releases"

@Gtk.Template(resource_path='/dev/qwery/AddWater/gtk/window.ui')
class AddWaterWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AddWaterWindow'

    firefox_page = None     # Keep a reference to the page to call it in case of reset app.

    # Use when only one page is available
    main_toolbar_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")

        reset_action = Gio.SimpleAction.new("reset-app")
        reset_action.connect("activate", self.on_reset_action)
        self.add_action(reset_action)

        self.create_firefox_page()


    def create_firefox_page(self):
        # Firefox Page set up
        # Find Firefox profiles path
        self.main_toolbar_view.set_content(None)
        firefox_path = os.path.expanduser(self.settings.get_string("firefox-path"))
        if os.path.exists(firefox_path) is False:
            log.warning("Prior Firefox path no longer exists. Searching for a new one...")
            firefox_path = self.find_firefox_path()
            if firefox_path is None:
                log.error("Could not find Firefox path automatically. User must set it manually.")
            else:
                self.settings.set_string("firefox-path", firefox_path)
                log.info(f"Found Firefox path: {firefox_path}")

        # Add page to window
        if firefox_path == None:
            self.firefox_page = Adw.StatusPage(
                title="Can't Find Firefox Profiles",
                # TODO Redo this description. Is this status page even necessary?
                description="""Add Water is preconfigured to automatically find the common Firefox data locations. Please ensure Add Water has permission to access the directory in which Firefox stores the `profiles.ini` file.\n\nClick the button below to find more troubleshooting help.""",
                child=Adw.Clamp(
                    maximum_size=300,
                    child=Gtk.Button(
                        label="Open Help Page",
                        action_name="app.open-help-page",
                        css_classes=["suggested-action", "pill"],
                    )
                )
            )
        else:
            self.firefox_page = AddWaterPage(
                app_path=firefox_path,
                app_options=FIREFOX_OPTIONS,
                app_name="Firefox",
                theme_url=firefox_url
            )
        self.main_toolbar_view.set_content(self.firefox_page)


    def find_firefox_path(self):
        """Iterates over all common Firefox config directories and returns which one exists.
        """
        path_list = [
            paths.FIREFOX_BASE,
            paths.FIREFOX_FLATPAK,
            paths.FIREFOX_SNAP,
            paths.FIREFOX_LIBREWOLF_BASE,
            paths.FIREFOX_LIBREWOLF_FLATPAK,
            paths.FIREFOX_LIBREWOLF_SNAP,
            paths.FIREFOX_FLOORP_BASE,
            paths.FIREFOX_FLOORP_FLATPAK
        ]
        for each in path_list:
            if os.path.exists(each):
                return each

        return None


    def set_custom_firefox(self):
        # TODO
        pass

    def on_reset_action(self, action, _):
        # Delete Download cache. Always keep the logs! Users may try this to troubleshoot and if it does not work, they'll need logs.
        log.warning("App is being reset...")
        try:
            shutil.rmtree(paths.DOWNLOAD_DIR)
        except FileNotFoundError:
            pass
        log.info(f"Deleted path: {paths.DOWNLOAD_DIR}")

        # # Reset GSettings
        firefox_settings = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")
        firefox_settings.reset("installed-version")
        firefox_settings.reset("theme-enabled")
        firefox_settings.reset("color-theme")
        for group in FIREFOX_OPTIONS:
            for each in group["options"]:
                firefox_settings.reset(each["key"])
        log.info("Reset all Firefox GSettings")

        self.settings.reset("firefox-path")
        log.info("Reset AddWater GSettings")

        self.firefox_page.full_uninstall()

        self.main_toolbar_view.set_content(
            Adw.StatusPage(
                title="Please close and reopen Add Water"
            )
        )
        log.info("Reset done")
        print("reset action activated")
