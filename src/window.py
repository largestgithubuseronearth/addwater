# window.py
#
# Copyright 2024 Claire
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
from gi.repository import Adw, Gtk, GLib, Gio, Gdk, GObject
from .pages.firefox_page import FirefoxPage

@Gtk.Template(resource_path='/dev/qwery/AddWater/gtk/window.ui')
class AddwaterWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AddwaterWindow'

    toast_overlay = Gtk.Template.Child()

    firefox_page = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings(schema_id="dev.qwery.AddWater")



