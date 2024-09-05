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
import shutil

from gi.repository import Adw, Gtk, GLib, Gio, Gdk, GObject
from .utils import logs, paths

from addwater import info
from addwater.page import AddWaterPage

log = logging.getLogger(__name__)

@Gtk.Template(resource_path=info.PREFIX + '/gtk/window.ui')
class AddWaterWindow(Adw.ApplicationWindow):
	__gtype_name__ = 'AddWaterWindow'


	# Use when only one page is available
	# TODO make it dynamically use a ViewStack when there are multiple pages/app plugins to display
	main_toolbar_view = Gtk.Template.Child()

	def __init__(self, backends: list, **kwargs):
		super().__init__(**kwargs)
		if info.PROFILE == 'developer':
			self.add_css_class('devel')

		self.set_size_request(375, 425) # Minimum size of window Width x Height

		self.settings = Gio.Settings(schema_id=info.APP_ID)
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
		for each in backends:
			self.create_firefox_page(each)


	# TODO refactor to support as many pages as possible
	def create_firefox_page(self, firefox_backend):
		self.main_toolbar_view.set_content(None)

		firefox_page = AddWaterPage(
			backend=firefox_backend
		)

		self.main_toolbar_view.set_content(firefox_page)


	# TODO redo this to accept multiple types of errors
	def error_status_page(self, app_name):
		help_page_button = Adw.Clamp(
			# maximum_size=300,
			hexpand=False,
			child=Gtk.Button(
				label="Open Help Page",
				action_name="app.open-help-page",
				css_classes=["suggested-action", "pill"],
			)
		)
		statuspage = Adw.StatusPage(
			title=f"Can't Find {app_name} Data",
			description=f'Please ensure that [Preferences > {app_name}: Package Type] is correctly set to the type of {app_name} you have (Snap, Flatpak, etc.) or to Auto.\n\nFor more troubleshooting support, click the button below.',
			child=help_page_button
		)
		return statuspage

