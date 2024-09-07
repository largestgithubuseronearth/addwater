# firefox_details.py
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

from os.path import join, exists
from typing import Optional
from enum import Enum
from configparser import ConfigParser

from gi.repository import Gio

from addwater.utils import paths
from addwater import info
from .firefox_options import FIREFOX_OPTIONS, FIREFOX_COLORS
from .firefox_paths import FIREFOX_PATHS
from .firefox_install import install_for_firefox

log = logging.getLogger(__name__)

# TODO would it make sense to create "tickets" that are a copy of the original
# instance — only without ability to be modified — rather than passing in the
# original object? This would allow for only passing part of the app and worrying
# less about modifying the state.


# TODO specialize this into Firefox first and then make it an injectible,
# dynamic class in the future once the app's core logic has settled and it's
# clearer what exact variables and roles AppDetails should take responsibility
# for.


class FirefoxAppDetails():
	"""Conveniently stores important app info to reduce how many arguments
	need to be passed around. If a method requires more than three pieces of info,
	just pass this object into managers and let them find what they need.

	Please avoid altering the state of an AppDetails instance outside of
	construction or dedicated setter methods in the backend interface.


	Args:
		name = proper, capitalized name of the app. i.e. 'Firefox' or 'Thunderbird
		options = theme options that the user can modify from the page GUI
		data_path = full path to the directory which includes all profile folders
						as well as profiles.ini and installs.ini
	"""

	package_formats: list[dict[str,str]] = FIREFOX_PATHS

	# primary
	name: str = 'Firefox'
	installed_version: int

	# install
	installer: callable = install_for_firefox
	options: list[dict[any]] = FIREFOX_OPTIONS
	color_palettes: list = FIREFOX_COLORS
	autofind_data_path: bool
	data_path: str
	profiles_list: list[dict[str,str]]

	# online
	theme_gh_url: str = 'https://api.github.com/repos/rafaelmardojai/firefox-gnome-theme/releases'

	theme_parent_folder = join(paths.DOWNLOAD_DIR, 'firefox')
	theme_folder = 'firefox-gnome-theme'
	full_theme_path = join(theme_parent_folder, theme_folder)


	def __init__(self,):
		self.settings = self.get_new_gsettings()

		version = self.settings.get_int('installed-version')
		self.set_installed_version(version)

		self.autofind_data_path = self.settings.get_boolean('autofind-paths')
		# TODO ensure this handles autofind paths
		data_paths = self._find_data_paths(self.package_formats)
		# TODO make this handle having multiple available paths
		self.set_data_path(data_paths[0]["path"])

		try:
			self.profiles_list = self._find_profiles(self.data_path)
		except FileNotFoundError as err:
			log.critical(err)
			raise FatalAppDetailsError(f'App cannot continue without profile data: {err}')



	"""PUBLIC METHODS"""
	def _reset_settings(self,):
		log.info(f'Resetting all gsettings for {self.name}')
		self.settings.reset('theme-enabled')
		self.settings.reset("data-path")
		self.settings.reset("autofind-paths")
		self.settings.reset("installed-version")
		self.settings.reset("profile-selected")
		self.settings.reset("palette-selected")

		for group in self.options:
			for option in group['options']:
				gset_key = option['key']
				self.settings.reset(gset_key)
		log.info('done. gsettings reset')


	"""Getters"""
	def get_new_gsettings(self,):
		# TODO make sure this is safe
		schema_id = (info.APP_ID + '.' + self.get_name())
		return Gio.Settings(schema_id=schema_id)

	def get_theme_folder_name(self,):
		return self.theme_folder

	def get_theme_download_path(self,):
		return self.full_theme_path

	def get_color_palettes(self,):
		return self.color_palettes

	def get_name(self,):
		return self.name

	def get_data_path(self,):
		return self.data_path

	def get_installer(self,):
		return self.installer

	def get_installed_version(self,):
		return self.installed_version

	def get_options(self,):
		return self.options

	def get_profiles(self,):
		return self.profiles_list

	def get_info_url(self,):
		return self.theme_gh_url


	"""Setters"""
	def set_data_path(self, new_path: str):
		log.info(f'Setting {self.name} data path: {new_path}')
		if exists(new_path):
			self.data_path = new_path
			self.settings.set_string('data-path', self.data_path)
			log.info(f'Valid path. Done.')
			return

		log.error(f'Tried to set app_path to non-existant path. Path given: {new_path}')
		raise AppDetailsException('Data path given does not exist')


	def set_installed_version(self, new_version: int,) -> None:
		log.debug(f'Set installed version number to {new_version}')
		self.settings.set_int('installed-version', new_version)
		self.installed_version = new_version



	"""PRIVATE METHODS"""
	@staticmethod
	def _find_profiles(app_path: str) -> list[dict[str,str]]:
		"""Reads the app profile data files and returns a list of known profiles.
		The user's preferred profiles are always first in the list.

		Args:
		app_path : The full path to where the app stores its profiles and the profiles.ini files

		Returns:
		A list of dicts with all profiles. Each dict includes the full ID path of the profile ["id"], and a display name to present in the UI ["name"].
		"""
		cfg = ConfigParser()
		defaults = []
		profiles = []

		install_file = join(app_path, "installs.ini")
		profiles_file = join(app_path, "profiles.ini")

		if not exists(install_file):
			raise FileNotFoundError('installs.ini file not found')
		if not exists(profiles_file):
			raise FileNotFoundError('profiles.ini file not found')

		# Find preferred profile paths
		cfg.read(install_file)
		for each in cfg.sections():
			default_profile = cfg[each]["Default"]
			defaults.append(default_profile)
			log.debug(f"Preferred profile: {default_profile}")

		# Find all paths and names
		cfg.read(profiles_file)
		for each in cfg.sections():
			try:
				path = cfg[each]["path"]
				name = cfg[each]["name"]
				if path in defaults:
					name = name + ' (Preferred)'
					pass

				profiles.append({"id" : path, "name" : name})
			except KeyError:
				pass

		# Sort so preferred names are first
		# TODO also sort alphabetically
		profiles.sort(reverse=True, key=_sort_profile_by_preferred)

		if profiles is None:
			raise FatalAppDetailsError('installs.ini and profiles.ini exist but do not have any profiles available.')
		return profiles


	@staticmethod
	def _find_data_paths(path_list: list[dict[str,str]]) -> list[dict[str,str]]:
		"""Iterates over all common Firefox config directories and returns which one exists.

		Args:
			path_list = Either of the list of dicts from the paths module to make it easy to iterate over
		"""
		found = []
		for each in path_list:
			path = each["path"]
			if exists(path):
				name = each["name"]
				log.debug(f"Found Firefox path: {name} — {path}")
				found.append(each)
		if not found:
			log.error('Could not find any valid data paths. App cannot function.')
			raise FatalAppDetailsError('Could not find any valid data paths')

		return found


def _sort_profile_by_preferred(item: str) -> bool:
	return item["name"].endswith(" (Preferred)")



class AppDetailsException(Exception):
	pass

class FatalAppDetailsError(Exception):
	pass

