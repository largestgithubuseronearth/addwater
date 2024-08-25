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


import logging
import os.path
import shutil

from gi.repository import Adw, Gtk, GLib, Gio, Gdk, GObject
from .page import AddWaterPage
from .theme_options import FIREFOX_OPTIONS
from .utils import logs, paths

from addwater import info
from .backend import AddWaterBackend
from .components.details import AppDetails
from .components.install import InstallManager
from .components.apps.firefox.firefox_install import install_for_firefox
from .components.online import OnlineManager

log = logging.getLogger(__name__)

firefox_url = "https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases"

# TODO refactor this whole class to only focus on the GUI
@Gtk.Template(resource_path='/dev/qwery/AddWater/gtk/window.ui')
class AddWaterWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AddWaterWindow'

    firefox_page = None     # Keep a reference to the page to call it in case of reset app.
    firefox_backend = None

    # Use when only one page is available
    main_toolbar_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if info.PROFILE == 'developer':
            self.add_css_class('devel')

        self.set_size_request(375, 425) # Minimum size of window Width x Height

        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")
        if info.PROFILE == 'user':
            self.settings.bind(
                'window-height', self, 'default-height', Gio.SettingsBindFlags.DEFAULT
            )
            self.settings.bind(
                'window-width', self, 'default-width', Gio.SettingsBindFlags.DEFAULT
            )
            self.settings.bind(
                'window-maximized', self, 'maximized', Gio.SettingsBindFlags.DEFAULT
            )

        # TODO bind window size to GSettings

        reset_action = Gio.SimpleAction.new("reset-app")
        reset_action.connect("activate", self.on_reset_action)
        self.add_action(reset_action)

        self.create_firefox_page()


    def create_firefox_page(self):
        self.main_toolbar_view.set_content(None)

        # Find Firefox Profile Path
        firefox_path = os.path.expanduser(self.settings.get_string("firefox-path"))
        if os.path.exists(firefox_path) is False:
            log.warning(f"Prior Firefox path no longer exists {firefox_path}")
            if self.settings.get_boolean("autofind-paths") is True:
                log.warning("Automatically finding a new one...")
                firefox_path = self.find_app_path(paths.FIREFOX_PATHS)
            else:
                log.warning("User has autofind disabled.")
                firefox_path = None
        log.info(f"Found Firefox Path: {firefox_path}")

        # Add page to window
        self.settings.set_string("firefox-path", firefox_path)

        # TODO extract this whole step into main or elsewhere
        firefox_settings = Gio.Settings(schema_id='dev.qwery.AddWater.Firefox')
        installed_version = firefox_settings.get_int('installed-version')
        self.firefox_backend = self._construct_backend(
            theme_url=firefox_url,
            app_name='Firefox',
            app_options=FIREFOX_OPTIONS,
            app_path=firefox_path,
            installed_version=installed_version,
        )

        self.firefox_page = AddWaterPage(
            app_name='Firefox',
            backend=self.firefox_backend
        )


        self.main_toolbar_view.set_content(self.firefox_page)

    # TODO move into AppDetails
    def find_app_path(self, path_list):
        """Iterates over all common Firefox config directories and returns which one exists.

        Args:
            path_list = Either of the list of dicts from the paths module to make it easy to iterate over
        """
        for each in path_list:
            p = each["path"]
            if os.path.exists(p):
                n = each["name"]
                log.info(f"Found new Firefox path: {n} — {p}")
                return p
        log.error("Could not find any of the common Firefox paths")
        return None

    # TODO extract this into main or somewhere else
    def on_reset_action(self, action, _):
        # TODO refactor this to actually close the app completely. It's awkward to ask the user to relaunch the app.

        # Delete Download cache. Always keep the logs!
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
        self.settings.reset("autofind-paths")
        log.info("Reset AddWater GSettings")

        self.firefox_backend._reset_full_uninstall()

        self.main_toolbar_view.set_content(
            Adw.StatusPage(title="Please close and reopen Add Water")
        )

        log.info("Reset done")

    # TODO redo this to accept multiple types of errors
    def error_status_page(self, app_name):
        statuspage = Adw.StatusPage(
            title=f"Can't Find {app_name} Data",
            description=f'Please ensure that [Preferences > {app_name}: Package Type] is correctly set to the type of {app_name} you have (Snap, Flatpak, etc.) or to Auto.\n\nFor more troubleshooting support, click the button below.',
            child=Adw.Clamp(
                maximum_size=300,
                child=Gtk.Button(
                    label="Open Help Page",
                    action_name="app.open-help-page",
                    css_classes=["suggested-action", "pill"],
                )
            )
        )
        return statuspage


    """PRIVATE METHODS"""
    # TODO extract this process somewhere else
    @staticmethod
    def _construct_backend(theme_url, app_name, app_options, app_path, installed_version):
        install_manager = InstallManager(
            installer=install_for_firefox,
        )

        online_manager = OnlineManager(
            theme_url=theme_url,
        )

        app_details = AppDetails(
            name=app_name,
            options=app_options,
            data_path=app_path,
            installed_version=installed_version,
        )

        firefox_backend = AddWaterBackend(
            app_details=app_details,
            install_manager=install_manager,
            online_manager=online_manager,
        )
        return firefox_backend
