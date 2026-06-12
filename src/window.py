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
from datetime import datetime, timezone
from os.path import exists, join

from addwater.page import Page
from gi.repository import Adw, Gio, Gtk

from addwater import info

from addwater.gui import Preferences
from .utils.paths import LOG_DIR

log = logging.getLogger("window")


@Gtk.Template(resource_path=info.PREFIX + "/gtk/window.ui")
class Window(Adw.ApplicationWindow):
    __gtype_name__ = "WaterWindow"

    view_switcher = Gtk.Template.Child()
    view_stack = Gtk.Template.Child()
    error_page = Gtk.Template.Child()

    def __init__(self, backends: list, **kwargs):
        super().__init__(**kwargs)

        if info.PROFILE == "development":
            self.add_css_class("devel")

        self.set_size_request(360, 294)

        self.init_settings()
        self.init_actions()

        self.backends = backends
        self.create_pages(self.backends)

    def create_pages(self, app_backends: list):
        """Create and present app pages, and connect them to their respective app backend"""
        # TODO completely redo this. May just give the page its backend directly
        for backend in app_backends:
            # Check data path for validity
            try:
                backend.get_package().get_profile_ini()
                page = Page(backend=backend)
                log.debug("page created successfully")
            except FileNotFoundError as e:
                app_name = backend.get_app_name()
                self.view_stack.set_visible_child_name("error")
                log.critical(e)

            setup_error_page(self.error_page, "Firefox")
            self.view_stack.add_titled(page, "firefox", "Firefox")
            self.view_stack.get_page(
                self.view_stack.get_child_by_name("firefox")
            ).set_icon_name("globe-symbolic")
            self.view_stack.set_visible_child_name("firefox")

        self.view_switcher.set_visible(len(self.view_stack.get_pages()) > 2)

    def init_settings(self):
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

    def init_actions(self):
        actions = {
            "preferences": (lambda *_args: Preferences().present(self), ["<Ctrl>comma"]),
                  "about": (self.on_about_action, None)
        }

        for name, details in actions.items():
            action = Gio.SimpleAction.new(name)
            action.connect("activate", details[0])
            self.add_action(action)
            if shortcuts := details[1]:
                app = self.get_application()
                app.set_accels_for_action(f"win.{name}", shortcuts)

    """Dialogs"""

    def on_about_action(self, *_args):
        """Callback for the app.about action."""
        # Grab log info for debug info page
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        CURRENT_LOGFILE = join(LOG_DIR, f"addwater_{now}.log")
        with open(file=CURRENT_LOGFILE, mode="r", encoding="utf-8") as f:
            db_info = f.read()

        # Setting up About dialog
        about = Adw.AboutDialog.new_from_appdata(
            (info.PREFIX + "/" + "dev.qwery.AddWater.metainfo"), info.VERSION
        )
        about.set_application_icon(info.APP_ID)
        about.set_developers(["Qwery"])
        about.set_copyright("© 2025 Qwery")

        about.set_debug_info(db_info)
        about.set_debug_info_filename(f"addwater_{now}.log")

        # Translators: Replace this with "Your Name https://www.your-website.com" or "Your Name <your-email@example.com>"
        about.set_translator_credits(_("translator-credits"))
        about.add_credit_section(
            # Translator: This is followed by a list of names
            name=_("Theme Created and Maintained by"),
            people=["Rafael Mardojai CM https://www.mardojai.com/"],
        )
        about.add_legal_section(
            "Other Wordmarks",
            "Firefox and Thunderbird are trademarks of the Mozilla Foundation" 
            "in the U.S. and other countries.",
            Gtk.License.UNKNOWN,
            None,
        )

        about.present(self)
        
def setup_error_page(page: Adw.StatusPage, app_name: str):
    """Create basic error status page when the app faces a fatal error
    that must be communicated to the user.
    """
    # Translators: {} will be replaced with the app name ("Firefox" or "Thunderbird")
    title=_("{} Profile Data Not Found").format(app_name)
    # Translators: {} will be replaced with the app name ("Firefox" or "Thunderbird")
    description=_(
        "Please ensure {} is installed and Add Water has permission to access your profiles"
    ).format(app_name)
    
    page.set_title(title)
    page.set_description(description)
