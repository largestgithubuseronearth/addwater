# install.py
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

import shutil
import logging

from os import PathLike
from os.path import join, exists
from typing import Optional, Callable
from enum import Enum

from addwater.utils.paths import DOWNLOAD_DIR

log = logging.getLogger(__name__)

class InstallManager():

	_install_theme: callable
	_set_preferences: callable
	_uninstall_theme: callable

	def __init__(self, installer: callable, preference_handler: callable=None, uninstaller: callable=None):
		self._install_theme = installer

		if preference_handler:
			self._set_preferences = preferences_handler
		else:
			self._set_preferences = _set_theme_prefs

		if uninstaller:
			self._uninstall_theme = uninstaller
		self._uninstall_theme = _do_uninstall_theme


	"""PUBLIC METHODS"""
	# TODO reduce how many arguments need to be passed into the , it's so messy

	def begin_install(self, theme_path: PathLike, profile_path: PathLike, color_palette: str, app_options, gset_reader) -> Enum:
		# TODO make this decide whether to use the full or quick install based on an enum flag
		pass

	def full_install(self, theme_path: PathLike, profile_path: PathLike, color_palette: str, app_options, gset_reader) -> Enum:
		"""Kick off installing theme and setting its user.js preferences.

		Args:
			theme_path = full path to the folder that will be copied to the profile
			profile_path = full path to the profile.
			color_palette = name of the color palette to import
			gset_reader = gsettings object for the app
		"""
		log.info('Starting a full install...')
		log.debug(f'Color Palette: {color_palette}')

		color_palette = color_palette.lower()

		if not exists(profile_path):
			raise InstallException('Install failed. Profile folder doesn\'t exist.')

		# Run install script
		try:
			self._install_theme(
				profile_path=profile_path,
				theme_path=theme_path,
				color_palette=color_palette,
			)
			self._set_preferences(profile_path, app_options, gset_reader)
		except InstallException as err:
			log.critical(err)
			return InstallStatus.FAILURE

		log.info('Full install done.')
		return InstallStatus.SUCCESS


	def quick_install(self, theme_path: PathLike, profile_path: PathLike, color_palette: str,) -> Enum:
		"""Installs theme files but doesn't change any user preferences. This is
		useful for updating in the background."""

		log.info('Starting a quick install...')
		log.debug(f'Color Palette: {color_palette}')

		color_palette = color_palette.lower()

		if not exists(profile_path):
			raise InstallException('Install failed. Profile folder doesn\'t exist.')

		try:
			self._install_theme(
				profile_path=profile_path,
				color_palette=color_palette,
				theme_path=theme_path,
			)
		except (InstallException, FileNotFoundError) as err:
			log.critical(err)
			return InstallStatus.FAILURE

		log.info('Quick install done.')
		return InstallStatus.SUCCESS


	def uninstall(self, profile_path: str, folder_name: str) -> Enum:
		try:
			self._uninstall_theme(profile_path, folder_name)
		except InstallException as err:
			log.critical(err)
			return InstallStatus.FAILURE

		return InstallStatus.SUCCESS



"""PRIVATE FUNCTIONS"""

"""Default install handlers. Can be overridden by injecting functions at construction."""
def _set_theme_prefs(profile_path: str, options: list[dict], gset_reader) -> None:
	"""Update user preferences in user.js according to GSettings.

	Args:
		profile_path = full file path to the profile that the theme will be installed to
		options = the theme options list dicts
		gset_reader = Gio.Settings object preconfigured for the correct schema
						to read the values of the keys

	"""
	log.info('Setting theme preferences in profile data...')

	user_js = join(profile_path, "user.js")
	# FIXME If the user.js file is gone, the other required prefs won't be set here
	# and thus the theme will not work properly
	try:
		with open(file=user_js, mode="r", encoding='utf-8') as file:
			lines = file.readlines()
	except FileNotFoundError:
		lines = []
	with open(file=user_js, mode="w", encoding='utf-8') as file:
		for group in options:
			for option in group["options"]:
				pref_name = f'gnomeTheme.{option["js_key"]}'
				pref_value = str(gset_reader.get_boolean(option["key"])).lower()
				full_line = f"""user_pref("{pref_name}", {pref_value});\n"""

				# TODO simplify this section
				found = False
				for i, line in enumerate(lines):
					# This is easier than a for-each
					if pref_name in line:
						lines[i] = full_line
						found = True
						break
				if found is False:
					lines.append(full_line)
				log.debug(f'{pref_name} -> {pref_value}')

		file.writelines(lines)

	log.info("Done.")


def _do_uninstall_theme(profile_path: str, theme_folder: str) -> None:
	log.info('Uninstalling theme from profile...')
	log.debug(f'Profile path: {profile_path}')

	# Delete theme folder
	try:
		chrome_path = join(profile_path, "chrome", theme_folder)
		shutil.rmtree(chrome_path)
	except FileNotFoundError:
		pass

	# TODO remove css import lines

	# Set all user_prefs to false
	user_js = join(profile_path, "user.js")
	try:
		with open(file=user_js, mode="r", encoding='utf-8') as file:
			lines = file.readlines()
	except FileNotFoundError:
		log.info("Done.")
		return

	try:
		with open(file=user_js, mode="w", encoding='utf-8') as file:
			# TODO find a way to avoid using the index and just edit the line in the list directly
			for i, line in enumerate(lines):
				if "gnomeTheme" in line:
					lines[i] = line.replace('true', 'false')

			file.writelines(lines)
	except OSError as err:
		log.error(f'Resetting user.js prefs to false failed: {err}')
		raise InstallException('Uninstall failed')

	log.info('Done.')



class InstallTypeFlag(Enum):
	QUICK = 0
	FULL = 1

class InstallStatus(Enum):
	SUCCESS = 0
	FAILURE = 1

class InstallException(Exception):
	pass
