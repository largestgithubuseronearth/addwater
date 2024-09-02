# main.py
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

import sys
import gi
import logging
import shutil
import os, os.path

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, Gdk, GLib

from .window import AddWaterWindow
from .preferences import AddWaterPreferences

from addwater import info
from .utils import paths
from .utils.logs import init_logs
from .utils.background import BackgroundUpdater

from addwater.backend import BackendFactory
from addwater.apps.firefox.firefox_details import FirefoxAppDetails, FatalAppDetailsError


log = logging.getLogger(__name__)


class AddWaterApplication(Adw.Application):
	"""The main application singleton class."""

	def __init__(self):
		super().__init__(application_id='dev.qwery.AddWater',
						 flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
		self.create_action('quit', lambda *_: self.quit(), ['<primary>q', '<primary>w'])
		self.create_action('about', self.on_about_action)
		self.create_action('preferences', self.on_preferences_action, ['<Ctrl>comma'])
		self.create_action('open-help-page', self.on_help_action)
		self.create_action('reset-app', self.on_reset_app_action)

		paths.init_paths()
		init_logs()

		self.add_main_option(
			'quick-update',
			ord('q'),
			GLib.OptionFlags.IN_MAIN,
			GLib.OptionArg.NONE,
			'Quickly update and install theme with the last-used settings',
			None,
		)


	def do_command_line(self, command_line):
		options = command_line.get_options_dict()
		options = options.end().unpack()
		# GUI Route
		if not options:
			self.activate()
			return 0

		# CLI Route
		self.backends = []
		firefox_backend = self._setup_logic_part()
		self.backends.append(firefox_backend)

		background_updater = BackgroundUpdater(self.backends[0])
		background_updater.quick_update()
		notif = background_updater.get_update_status()
		self.send_notification(notif)


		log.info('background updater finished. exiting now.')
		return 0


	def do_activate(self):
		"""Called when the application is activated.

		We raise the application's main window, creating it if
		necessary.
		"""

		# Create logic backend
		self.backends = []
		firefox_backend = self._setup_logic_part()
		self.backends.append(firefox_backend)

		# Create window with the logic it needs
		win = self.props.active_window
		if not win:
			win = AddWaterWindow(application=self, backends=self.backends)
		win.present()

###################################################################################

	# TODO rename this is a terrible name
	def _setup_logic_part(self):
		# TODO This needs to eventually allow for multiple apps.
		# How would it check for which to add? Would this be manual?
		return BackendFactory.new_from_appdetails(FirefoxAppDetails())


	def on_reset_app_action(self, *_):
		log.warning('resetting the entire app...')

		# TODO temporarily indexing until app can support multiple backends
		backend = self.backends[0]
		backend.reset_app()

		shutil.rmtree(paths.DOWNLOAD_DIR)

		log.info('app has been reset and will now exit')
		self.quit()

###################################################################################



	def on_about_action(self, widget, _):
		"""Callback for the app.about action."""
		# TODO info.py.in seems like a good model for how to do this. But requires meson tinkering
		about = Adw.AboutDialog(application_name='Add Water',
								application_icon='dev.qwery.AddWater',
								developer_name='qwery',
								version=info.VERSION,
								developers=['Qwery'],
								copyright='© 2024 Qwery',
								license_type=Gtk.License.GPL_3_0)
		about.add_credit_section(
			name="Theme Created and Maintained by",
			people=["Rafael Mardojai CM https://www.mardojai.com/"])
		about.add_legal_section(
			"Other Wordmarks",
			"Firefox and Thunderbird are trademarks of the Mozilla Foundation in the U.S. and other countries.",
			Gtk.License.UNKNOWN,
			None
		)
		about.present(self.props.active_window)


	def on_preferences_action(self, widget, _):
		"""Callback for the app.preferences action."""
		pref = AddWaterPreferences()
		pref.present(self.props.active_window)
		log.info('preferences action activated')


	def create_action(self, name, callback, shortcuts=None):
		"""Add an application action.

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
			self.set_accels_for_action(f"app.{name}", shortcuts)


	def on_help_action(self, action, _):
		log.info("help page action activated")
		# TODO is there a better link than this?
		weblaunch = Gtk.UriLauncher.new("https://github.com/largestgithubuseronearth/addwater/blob/7b405a417356346fd1d93d3d2090a090cf27ecbf/docs/user-help.md")
		weblaunch.launch(None, None, None, None)


def main(version):
	"""The application's entry point."""
	app = AddWaterApplication()
	return app.run(sys.argv)

