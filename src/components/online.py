# download.py
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


import os
import tarfile
import logging
import requests
import json

from enum import Enum
from os.path import join, exists
from addwater.utils.paths import DOWNLOAD_DIR
from typing import Optional

log = logging.getLogger(__name__)

class OnlineManager():

	# TODO should online manager keep these details or AppDetails?
	installed_version: int
	update_version: int
	theme_url: str

	def __init__(self, theme_url: str):
		log.debug('online manager is now alive')
		self.theme_url = theme_url
		pass


	"""PUBLIC METHODS"""

	def get_updates_online(self, app_details: callable) -> Enum:
		log.info('Checking for updates...')

		installed_version = app_details.get_installed_version()
		try:
			update_info = self._get_release_info(self.theme_url)
		except NetworkException as err:
			self.update_version = installed_version
			return OnlineStatus.DISCONNECTED

		calls_left = update_info["ratelimit_remaining"]
		if self._is_ratelimit_exceeded(calls_left):
			log.warning('rate limiting self to avoid angering Github')
			return OnlineStatus.RATELIMITED

		update_version = update_info["version"]
		self.update_version = update_version
		tarball_url=update_info["tarball_url"]
		app_name = app_details.get_name().lower()

		files_downloaded = exists(app_details.get_theme_download_path())
		update_available = self._is_update_available(new=update_version, current=installed_version)
		if update_available or not files_downloaded:
			log.info('update available. getting it now...')
			# TODO find a way for appdetails to store this path so it's easy to stay consistent between managers. Is that even worth it?
			base_name = f'{app_name}-{update_version}'
			final_name = app_details.final_theme_name
			try:
				self.get_release(
					base_name=base_name, final_name=final_name, tarball_url=tarball_url
				)
			except NetworkException as err:
				return OnlineStatus.DISCONNECTED
			except ExtractionException as err:
				log.error(err)
				# TODO recover from this more cleanly
				raise OnlineManagerError('could not extract theme release tarball')

			return OnlineStatus.UPDATED

		log.info('No update available.')
		return OnlineStatus.NO_UPDATE


	# TODO improve to allow files to be downloaded that aren't necessarily zipped or are of different ziptypes
	def get_release(self, base_name: str, final_name: str, tarball_url: str):
		"""Download and prep a theme release for installation
		Args:
			base_name = the naming convention for the download zipfile and extracted path
			final_path = naming convention for the resulting theme files. As of now,
				this is '{app_name}-gnome-theme'. This means you can find the theme
				folder at "{base-name}-extracted/{final_path}"
		"""
		zipfile = join(DOWNLOAD_DIR, f'{base_name}.tar.gz')
		extract_path = join(DOWNLOAD_DIR, f'{base_name}-extracted')
		final_path = join(extract_path, final_name.lower())
		if exists(final_path):
			log.info(f"{base_name} already ready to install. Skipping.")
			return


		log.info(f'Getting release: {base_name}...')

		if not exists(zipfile) or not exists(extract_path):
			try:
				self._download_tarball(tarball_url, zipfile)
			except (requests.RequestException, requests.ConnectionError) as err:
				log.error(err)
				raise NetworkException(err)

		if not exists(extract_path):
			try:
				self._extract_tarball(zipfile, extract_path)
			except (FileNotFoundError, tarfile.TarError) as err:
				# TODO find a better error to throw
				raise ExtractionException('Theme files failed to extract')

		# rename inner folder
		self._rename_theme_folder(extract_path, final_name)
		log.info('Update files downloaded and ready to install.')

	def get_update_version(self,):
		return self.update_version



	"""PRIVATE FUNCTIONS"""
	# TODO how to make download asynchronous?
	@staticmethod
	def _download_tarball(dl_url: str, result: str) -> None:
		"""Download file and write to a file

		Args:
			dl_url = url to the file to download
			result = path to write the contents of the downloaded file
		"""
		if exists(result):
			log.debug('Already downloaded this release. Skipping download.')
			return

		headers = {
			'X-Github-Api-Version': '2022-11-28',
			'User-Agent' : 'dev.qwery.AddWater/pre-alpha',
			# TODO is this the proper accept header?
			'Accept' : 'application/vnd.github.x-gzip+json'
		}
		# TODO test with the streaming feature
		response = requests.get(dl_url, headers=headers)

		with open(file=result, mode="wb") as file:
			file.write(response.content)

		log.debug("Successfully downloaded release from Github")


	@staticmethod
	def _extract_tarball(zipfile_path: str, result_path: str) -> None:
		"""Extracts tar.gz files. It's important to know that this destroys the tar after the extraction is done.

		Args:
			zipfile_path = input tar.gz file to unzip
			result_path = resulting extracted directory
		"""

		if not exists(zipfile_path):
			raise FileNotFoundError('Zipfile does not exist to be extracted. It must have been lost since downloading it')
		if exists(result_path):
			log.debug('Unzipped directory already exists. Skipping extraction.')
			return

		with tarfile.open(zipfile_path) as tf:
			tf.extractall(path=result_path, filter="data")
		log.debug(f'Successfully unzipped the file to {result_path}')

		os.remove(zipfile_path)
		log.debug(f'Deleted {zipfile_path}')


	@staticmethod
	def _rename_theme_folder(parent_dir: str, new_name: str) -> None:
		"""Renames the inner folder of the release to be easy to find later."""
		final_path = join(parent_dir, new_name)
		if not exists(parent_dir):
			raise FileNotFoundError('Rename failed. Parent folder does not exist.')
		if exists(final_path):
			log.debug('Inner file is already properly named. Skipping rename step.')
			return

		with os.scandir(path=parent_dir) as scan:
			for each in scan:
				if each.name.startswith(f"rafaelmardojai"):
					old_path = join(parent_dir, each.name)
					os.rename(old_path, final_path)
		log.debug('Successfully renamed inner folder')


	@staticmethod
	def _get_release_info(gh_url: str) -> dict[str, [int,str]]:
		"""Poll Github url and check if a new release of the theme is available

		Args:
			gh_url = fully-qualified url to a github releases api call (https://api.github.com/...)

		Returns:
			release_info = dict including "version" as int, "ratelimit_remaining" as int, and "tarball_url" as str
		"""
		# TODO If you can check Firefox version easily, check that before requesting from GH

		# TODO make sure this request is complaint with github's specification
		# Include all the applicable headers
		headers = {
			'X-Github-Api-Version': '2022-11-28',
			'User-Agent' : 'dev.qwery.AddWater/pre-alpha',
			'Accept': 'application/vnd.github+json'
		}
		try:
			response = requests.get(gh_url, headers=headers)
		except requests.RequestException as err:
			log.error(f'Could not connect to Github to grab release info: {err}')
			raise NetworkException(err)

		api_calls_left = int(response.headers["x-ratelimit-remaining"])
		try:
			latest_release = response.json()[0]
			version = int(latest_release["tag_name"].lstrip("v"))
			tarball_url = latest_release["tarball_url"]
		# TODO make sure this error is correct
		except request.JSONDecodeError as err:
			log.err(err)
			version = None
			tarball_url = None

		release_info = {
			"version" : version,
			"ratelimit_remaining" : api_calls_left,
			"tarball_url" : tarball_url,
		}
		return release_info


	@staticmethod
	def _is_ratelimit_exceeded(api_calls_left: int) -> bool:
		# TODO Set API limit more robust and strict before flathub release
		# Maybe set the time and api calls remaining in gsettings
		CHOSEN_LIMIT = 10
		log.debug(f'Remaining Github API calls for the next hour: {api_calls_left}')
		return bool(api_calls_left < CHOSEN_LIMIT)


	@staticmethod
	def _is_update_available(current: int, new: int) -> bool:
		if type(current) is not int or type(new) is not int:
			raise ValueError

		# TODO consider making this handle special cases like minor updates or maybe rollbacks
		# This could work by parsing a string and separating them by the dots. MAJOR.MINOR.MICRO
		# And if any of them are higher, then the release is downloaded
		return bool(new > current)


class OnlineStatus(Enum):
	NO_UPDATE = 0
	UPDATED = 1
	DISCONNECTED = 2
	RATELIMITED = 3


class NetworkException(Exception):
	pass

class OnlineManagerError(Exception):
	pass

class ExtractionException(Exception):
	pass

