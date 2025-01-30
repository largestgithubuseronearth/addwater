# window.py
#
# Copyright 2025 Qwery
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
        self.create_pages(self.backends)

    def create_pages(self, app_backends: list):
        """Create and present app pages, and connect them to their respective app backend"""
        log.info("resetting gui pages")
        self.main_toolbar_view.set_content(None)
        self.pages = []

        for each in app_backends:
            # Check data path for validity
            if exists(join(each.get_data_path(), "profiles.ini")):
                page = AddWaterPage(backend=each)
                log.debug("page created successfully")
            else:
                app_name = each.get_app_name()
                log.critical(
                    f"No data path for {app_name} available. Showing an error message"
                )
                page = self.create_error_page(app_name)

            self.pages.append(page)

        if len(self.pages) == 1:
            self.main_toolbar_view.set_content(self.pages[0])
            log.debug("1 page available")
        else:
            log.error("multiple pages available")
            # TODO else use a Viewstack
            raise NotImplementedError

    def create_error_page(self, app_name: str):
        """Create basic error status page when the app faces a fatal error
        that must be communicated to the user.
        """
        help_page_button = Adw.Clamp(
            hexpand=False,
            child=Gtk.Button(
                label=_("Open Help Page"),
                action_name="app.open-help-page",
                css_classes=["suggested-action", "pill"],
            ),
        )
        statuspage = Adw.StatusPage(
            # Translators: {} will be replaced with the app name ("Firefox" or "Thunderbird")
            title=_("{} Profile Data Not Found").format(app_name),
            # Translators: {} will be replaced with the app name ("Firefox" or "Thunderbird")
            description=_("Please ensure {} is installed and Add Water has permission to access your profiles").format(app_name),
            child=help_page_button,
        )
        return statuspage

    def create_action(self, name: str, callback, shortcuts: list[str]=None):
        """Add a window action and shortcut.

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

    """Dialogs"""

    def on_preferences_action(self, *_args):
        """Callback for the app.preferences action."""
        pref = AddWaterPreferences()
        # TODO improve this to only refresh the profiles combobox? It freezes the app for a second

        pref.present(self)

    def on_about_action(self, *_args):
        """Callback for the app.about action."""
        # Grab log info for debug info page
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        CURRENT_LOGFILE = join(paths.LOG_DIR, f"addwater_{now}.log")
        with open(file=CURRENT_LOGFILE, mode="r", encoding="utf-8") as f:
            db_info = f.read()

        # Setting up About dialog
        about = Adw.AboutDialog.new_from_appdata(
            (info.PREFIX + "/" + "dev.qwery.AddWater.metainfo"), info.VERSION
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
        # Translators: Replace this with "Your Name https://www.your-website.com" or "Your Name <your-email@example.com>"
        about.set_translator_credits( _("translator-credits") )
        about.set_copyright("© 2025 Qwery")
        about.set_license_type(Gtk.License.GPL_3_0)
        about.add_credit_section(
        # Translator: This is followed by a list of names
            name=_("Theme Created and Maintained by"),
            people=["Rafael Mardojai CM https://www.mardojai.com/"],
        )
        about.add_legal_section(
            "Other Wordmarks",
            "Firefox and Thunderbird are trademarks of the Mozilla Foundation in the U.S. and other countries.",
            Gtk.License.UNKNOWN,
            None,
        )

        about.present(self)
