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

from os.path import exists, join
from datetime import datetime, timezone

from addwater.page import AddWaterPage
from gi.repository import Adw, Gio, Gtk

from addwater import info
from .preferences import AddWaterPreferences
from .utils import paths

log = logging.getLogger(__name__)


@Gtk.Template(resource_path=info.PREFIX + "/gtk/window.ui")
class AddWaterWindow(Adw.ApplicationWindow):
    __gtype_name__ = "AddWaterWindow"

    main_menu = Gtk.Template.Child()
    # Use when only one page is available
    # TODO make it dynamically use a ViewStack when there are multiple pages/app plugins to display
    main_toolbar_view = Gtk.Template.Child()

    def __init__(self, backends: list, **kwargs):
        super().__init__(**kwargs)

        if info.PROFILE == "developer":
            self.add_css_class("devel")

        self.set_size_request(360, 294)  # Minimum size of window Width x Height

        self.settings = Gio.Settings(schema_id=info.APP_ID)
        if info.PROFILE == "user":
            self.settings.bind(
                "window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT
            )
            self.settings.bind(
                "window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT
            )
            self.settings.bind(
                "window-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT
            )
        self.create_action("preferences", self.on_preferences_action, ["<Ctrl>comma"])
        self.create_action("about", self.on_about_action)

        self.backends = backends
        for each in backends:
            data_path = each.get_data_path()
            if exists(data_path):
                self.create_firefox_page(each)
            else:
                log.critical("Data path has failed. App can't continue. Displaying error status page")
                self.error_page()

    # TODO refactor to support as many pages as possible. only supports a single page rn
    def create_firefox_page(self, firefox_backend):
        self.main_toolbar_view.set_content(None)

        firefox_page = AddWaterPage(backend=firefox_backend)

        self.main_toolbar_view.set_content(firefox_page)

    """These are only called if no profile data is found"""

    def error_page(self):
        page = self.create_error_page()
        self.main_toolbar_view.set_content(page)

    def create_error_page(self):
        help_page_button = Adw.Clamp(
            hexpand=False,
            child=Gtk.Button(
                label="Open Help Page",
                action_name="app.open-help-page",
                css_classes=["suggested-action", "pill"],
            ),
        )
        statuspage = Adw.StatusPage(
            title="Firefox Profile Data Not Found",
            description="Please ensure Firefox is installed and Add Water has permission to access your profiles.",
            child=help_page_button,
        )
        return statuspage


    # TODO clean up this class because it's sloppy
    def on_preferences_action(self, *_):
        """Callback for the app.preferences action."""
        pref = AddWaterPreferences(self.backends[0])
        pref.present(self)


    def on_about_action(self, *_):
        """Callback for the app.about action."""

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        CURRENT_LOGFILE = join(paths.LOG_DIR, f"addwater_{now}.log")

        with open(file=CURRENT_LOGFILE, mode="r", encoding="utf-8") as f:
            db_info = f.read()

        about = Adw.AboutDialog.new_from_appdata(
            resource_path=(info.PREFIX + "/" + "dev.qwery.AddWater.metainfo"),
            release_notes_version=info.VERSION
        )
        about.set_application_name("Add Water")
        about.set_application_icon(info.APP_ID)
        about.set_developer_name("qwery")
        about.set_version(info.VERSION)

        about.set_issue_url(info.ISSUE_TRACKER)
        about.set_website(info.WEBSITE)
        about.set_debug_info(db_info)
        about.set_debug_info_filename(f"addwater_{now}.log")
        about.set_support_url(info.TROUBLESHOOT_HELP)

        about.set_developers(["Qwery"])
        about.set_copyright("© 2024 Qwery",)
        about.set_license_type(Gtk.License.GPL_3_0)

        about.add_credit_section(
            name="Theme Created and Maintained by",
            people=["Rafael Mardojai CM https://www.mardojai.com/"],
        )
        about.add_legal_section(
            "Other Wordmarks",
            "Firefox and Thunderbird are trademarks of the Mozilla Foundation in the U.S. and other countries.",
            Gtk.License.UNKNOWN,
            None,
        )
        about.present(self)



    def create_action(self, name, callback, shortcuts=None):
        """Add a window action.

        Args:
                name: the name of the action
                callback: the function to be called when the action is
                  activated
                shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            app = self.get_application()
            app.set_accels_for_action(f"win.{name}", shortcuts)
