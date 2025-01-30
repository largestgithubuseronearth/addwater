# preferences.py
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

import gi

gi.require_version("Xdp", "1.0")

from gi.repository import Adw, Gio, Gtk, Xdp, GObject

from addwater import info
from addwater.backend import InterfaceMisuseError

log = logging.getLogger(__name__)


@Gtk.Template(resource_path=info.PREFIX + "/gtk/preferences.ui")
class AddWaterPreferences(Adw.PreferencesDialog):
    """Home to all options that are strictly related to Add Water functionality.
     No theme-specific options should be presented in this dialog.
     """
    __gtype_name__ = "AddWaterPreferences"

    background_update_switch = Gtk.Template.Child()


    def __init__(self):
        super().__init__()
        log.info("Preferences Window activated")
        self.settings_app = Gio.Settings(schema_id=info.APP_ID)
        self.portal = Xdp.Portal()

        try:
            self.settings_app.bind(
                "background-update",
                self.background_update_switch,
                "active",
                Gio.SettingsBindFlags.DEFAULT,
            )
            self.background_update_switch.connect(
                "activated", self._do_background_request
            )
        except Exception as err:
            log.error(err)



    # TODO is there a better way to handle this? copied from adwsteamgtk
    def _do_background_request(self, *_blah):
        """Request permission from portals to launch at login time"""
        bg_enabled = self.settings_app.get_boolean("background-update")
        if bg_enabled:
            flag = Xdp.BackgroundFlags.AUTOSTART
        else:
            flag = Xdp.BackgroundFlags.NONE

        self.portal.request_background(
            None,
            _("Checking for theme updates"),
            ["addwater", "--quick-update"],
            flag,
            None,
            None,
            None,
        )
