# preferences.py
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

import gi

gi.require_version('Xdp', '1.0')
gi.require_version('XdpGtk4', '1.0')

from gi.repository import Adw, Gtk, Gio, GLib, Xdp, XdpGtk4

# TODO Make set_custom_firefox_path handler

@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/preferences.ui")
class AddWaterPreferences(Adw.PreferencesDialog):
    __gtype_name__ = "AddWaterPreferences"


    def __init__(self):
        super().__init__()
        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")
        log.info("Preferences Window activated")

        firefox_path = self.settings.get_string("firefox-path")

        # DEBUG
        self.notification_tester

        # Portal stuff
        self.parent = XdpGtk4.parent_new_gtk(Gtk.Window.new())
        self.portal = Xdp.Portal.initable_new()

        log.debug("Requesting autostart in background...")
        self.portal.request_background(
            None,
            "TESTING BACKGROUND STUFF",
            None, # terminal exec. Do i need to make my app use the terminal? Probably.
            Xdp.BackgroundFlags.AUTOSTART,
            None,
            self.background_handler,
            None
        )

    def background_handler(self, portal, result, _):
        if self.portal.request_background_finish(result) == True:
            log.debug("Success. Background request granted")
        else:
            log.debug("Failed. Background request rejected")

