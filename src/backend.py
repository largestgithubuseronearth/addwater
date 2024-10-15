# backend.py
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
from os.path import exists, join
from typing import Callable, Optional

from addwater.components.install import InstallManager
from addwater.components.online import OnlineManager
from addwater.utils.mocks import mock_online
from addwater.utils.paths import DOWNLOAD_DIR

from addwater.apps.firefox.firefox_details import AppDetailsException

from addwater import info

log = logging.getLogger(__name__)

class AddWaterBackend:
    """The interface by which this app can complete important tasks like installing, updating, etc.
    Relies on injected components that manage those actual processes. This class
    just connects and abstracts those details into easy public methods that can be
    used anywhere.

    This class can live without a GUI frontend to allow for background updating.

    Args:
            app_details = object that stores and manages the state of important app details
                                            such as the app's name, available profiles, data paths, and what
                                            theme options are available. Will be passed into other managers
                                            for convenience.
            install_manager = object that manages processes related to installing,
                                                    uninstalling, and setting user's theme preferences in
                                                    configuration files.
            online_manager = object that makes internet requests, processes http responses,
                                                    handles network errors, downloads theme releases, and preps
                                                    those releases to be installed.
    """

    app_details: callable
    online_manager: callable
    install_manager: callable

    def __init__(self, app_details, install_manager, online_manager):
        self.app_details = app_details
        self.install_manager = install_manager
        self.online_manager = online_manager

        log.info(f"Backend created for {self.get_app_name()}")

    """PUBLIC METHODS

	For these methods, it's often impossible to avoid modifying object states. So it's
	important for these methods to be readable and concise, and modify as little
	as possible.
	"""

    """Install actions"""

    def begin_install(self, profile_id, color_palette, full_install=False) -> Enum:
        log.info("beginning installation...")
        result = self.app_details.get_download_path_info()
        (p1, p2, p3) = result # TODO is there a dynamic, easier way to unpack this tuple?
        theme_path = join(p1, p2, p3)

        app_path = self.app_details.get_data_path()
        profile_path = join(app_path, profile_id)

        # Prep options for pref handler if full install
        if full_install:
            option_request = {}
            gset = self.app_details.get_new_gsettings()
            options = self.app_details.get_options()

            for group in options:
                for option in group["options"]:
                    js_key = option["js_key"]
                    g_key = option["key"]
                    value = gset.get_boolean(g_key)

                    option_request[js_key] = value
        else:
            option_request = None

        # Call installer and return status to page
        status = self.install_manager.combined_install(
            theme_path=theme_path,
            profile_path=profile_path,
            color_palette=color_palette,
            options_results=option_request
        )

        log.info("install process completed")
        return status



    def remove_theme(self, profile_id) -> Enum:
        folder_name = self.app_details.get_theme_folder_name()

        app_path = self.get_data_path()
        profile_path = join(app_path, profile_id)

        install_status = self.install_manager.uninstall(profile_path, folder_name)
        return install_status

    """Online Actions"""

    def update_theme(self) -> Enum:
        path_info = self.app_details.get_download_path_info()
        version = self.get_installed_version()
        status = self.online_manager.get_updates_online(version, path_info)

        new_version = self.get_update_version()
        self.app_details.set_installed_version(new_version)

        return status

    """Info Getters"""

    # TODO make a new getter and setter here for installed version so you don't have to call appdetails directly
    def get_app_name(
        self
    ) -> str:
        return self.app_details.get_name()

    def get_app_settings(
        self
    ):
        return self.app_details.get_new_gsettings()

    def get_app_options(self) -> list[dict[str, any]]:
        return self.app_details.get_options()

    def get_data_path(
        self
    ) -> str:
        return self.app_details.get_data_path()

    def get_colors_list(self) -> list:
        return self.app_details.get_color_palettes()

    def get_installed_version(
        self
    ) -> int:
        return self.app_details.get_installed_version()

    def get_update_version(self) -> int:
        return self.online_manager.get_update_version()

    def get_profile_list(self) -> dict:
        return self.app_details.get_profiles()

    def get_package_formats(
        self
    ) -> dict:
        return self.app_details.package_formats

    """Info Setters"""

    def set_data_path(self, new_path: str) -> None:
        try:
            self.app_details.set_data_path(new_path)
        except AppDetailsException as err:
            log.error(err)
            raise InterfaceMisuseError(err)

    """Dangerous"""

    def reset_app(
        self
    ):
        app_name = self.get_app_name()
        log.warning(f"{app_name} is now being reset...")
        self._uninstall_all_profiles()
        self.app_details.reset_settings()
        log.info(f"done. {app_name} has been reset to default state")

    """PRIVATE METHODS"""

    def _uninstall_all_profiles(self):
        log.warning(f"uninstalling theme from all known profiles...")
        profiles = self.app_details.get_profiles()
        for each in profiles:
            profile_id = each["id"]
            self.remove_theme(profile_id)

        log.info("done. theme removed from all profiles")


class InterfaceMisuseError(Exception):
    pass


class FatalInterfaceError(Exception):
    pass


class BackendFactory:

    @staticmethod
    def new_from_appdetails(app_details):
        install_method = app_details.get_installer()
        install_manager = InstallManager(
            installer=install_method,
        )

        if info.MOCK_API == "True":
            online_manager = mock_online.MockOnlineManager(2)
        else:
            theme_url = app_details.get_info_url()
            online_manager = OnlineManager(
                theme_url=theme_url,
            )

        firefox_backend = AddWaterBackend(
            app_details=app_details,
            install_manager=install_manager,
            online_manager=online_manager,
        )
        return firefox_backend
