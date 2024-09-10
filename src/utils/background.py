# background.py
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

from enum import Enum

from gi.repository import Gio

log = logging.getLogger(__name__)

class BackgroundUpdater():
	def __init__(self, backend: list):
		app_name = backend.get_app_name()
		log.debug(f'BackgroundUpdater created for {app_name}')
		self.backend = backend
		self.settings = self.backend.get_app_settings()



	def quick_update(self,):
		update_status = self.backend.update_theme()
		match update_status:
			case update_status.UPDATED:
				status = self.silent_install()
			case update_status.NO_UPDATE:
				log.info('no update')
				status = SilentUpdateStatus.NO_UPDATE
			case update_status.DISCONNECTED:
				log.info('online failed, disconnected')
				status = SilentUpdateStatus.ONLINE_FAIL
			case update_status.RATELIMITED:
				log.info('online failed, rate limited')
				status = SilentUpdateStatus.ONLINE_FAIL

		self.bg_status = status

	def silent_install(self,):
		log.info('Update available. Silently installing')
		color_palette = self.settings.get_string('palette-selected')
		profile_id = self.settings.get_string('profile-selected')
		# TODO Move this check into backend.get_selected_profile()?
		if not profile_id:
			profiles = self.backend.get_profile_list()
			profile_id = profiles[0]['id']

		install_status = self.backend.quick_install(profile_id, color_palette)

		if install_status.SUCCESS:
			log.info('Silent install succeeded')
			return SilentUpdateStatus.UPDATED
		else:
			log.info('Silent install failed')
			return SilentUpdateStatus.INSTALL_FAIL


	def get_update_status(self,):
		return self.bg_status

	def get_status_notification(self,):
		log.debug('prepping a desktop notification for the bg update/install status')
		status = self.bg_status

		match status:
			case status.UPDATED:
				title = 'Theme updated'
				msg = 'Firefox GNOME Theme Updated'
			case status.ONLINE_FAIL:
				title= 'Theme Update Failed'
				msg = 'Could not check for theme updates due to a network issue'
			case status.INSTALL_FAIL:
				title = 'Theme Installation failed'
				msg = 'A theme update was downloaded but the installation failed'
			case _:
				msg = None

		if msg:
			log.debug(f'notification text: {msg}')
			notif = Gio.Notification.new(title)
			notif.set_body(msg)
			notif.set_priority(Gio.NotificationPriority.LOW)
			return notif

		log.debug(f'nothing to report thus no notification sent')
		return None




class UpdaterException(Exception):
	pass

class SilentUpdateStatus(Enum):
	NO_UPDATE = 0
	UPDATED = 1
	ONLINE_FAIL = 2
	INSTALL_FAIL = 3
