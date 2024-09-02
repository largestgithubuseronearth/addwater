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
import logging

gi.require_version('Xdp', '1.0')
gi.require_version('XdpGtk4', '1.0')

from gi.repository import Adw, Gtk, Gio, GLib, Xdp, XdpGtk4

# TODO migrate this to use the appdetail class paths
from .utils.paths import FIREFOX_PATHS


log = logging.getLogger(__name__)

@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/preferences.ui")
class AddWaterPreferences(Adw.PreferencesDialog):
	__gtype_name__ = "AddWaterPreferences"

	FIREFOX_FORMATS = FIREFOX_PATHS

	firefox_package_combobox = Gtk.Template.Child()
	firefox_package_combobox_list = Gtk.Template.Child()

	def __init__(self):
		super().__init__()
		log.info("Preferences Window activated")

		self.settings_firefox = Gio.Settings(schema_id="dev.qwery.AddWater.Firefox")

		self.firefox_path = self.settings_firefox.get_string("data-path")
		self._init_firefox_combobox()

		self.firefox_package_combobox.notify("selected-item")
		self.firefox_package_combobox.connect("notify::selected-item", self._set_firefox_package)


	def _init_firefox_combobox(self):
		for each in self.FIREFOX_FORMATS:
			self.firefox_package_combobox_list.append(each["name"])

		if self.settings_firefox.get_boolean("autofind-paths") is False:
			user_path = self.firefox_path

			for each in self.FIREFOX_FORMATS:
				if each["path"] == user_path:
					i = self.FIREFOX_FORMATS.index(each) + 1

			self.firefox_package_combobox.set_selected(i)


	def _set_firefox_package(self, row, _):
		selected_index = row.get_selected()
		# First option is always Automatically Discover
		if selected_index == 0:
			self.settings_firefox.set_boolean("autofind-paths", True)
			log.warning("Autofind paths enabled")
			return

		self.settings_firefox.set_boolean("autofind-paths", False)
		log.warning("Autofind paths disabled")
		selected = row.get_selected_item().get_string()

		for each in self.FIREFOX_FORMATS:
			if selected == each["name"]:
				log.info(f'User specified path: {each["path"]}')
				self.settings_firefox.set_string("data-path", each["path"])
				self.firefox_path = each["path"]

