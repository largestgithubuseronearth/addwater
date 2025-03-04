# profile_selector.py
#
# Copyright 2025 Qwery
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
from typing import Callable, Optional

from gi.repository import GObject, Gtk, Adw, Gio
from packaging.version import Version

from addwater import info

from addwater.backend import InterfaceMisuseError

log = logging.getLogger(__name__)


@Gtk.Template(resource_path=info.PREFIX + "/gtk/profile-selector.ui")
class ProfileSelector(Adw.ComboRow):
    __gtype_name__ = "AddWaterProfileSelector"

    selected_profile = None
    strlist = Gtk.Template.Child()

    settings = None

    # TODO Make a simple profile data object to represent profiles instead of a dict

    # TODO redo this using ListStore and factories instead.

    # TODO reimplement resetting profile combobox cursor after I can track
    # profiles across firefox installs via sql

    # FIXME if a profile is removed, it's still selected in GSettings and causes an install fail

    def __init__(self):
        super().__init__()

    def setup_settings(self, settings):
        if self.settings:
            raise LogicError("ProfileSelector already has a settings reader")

        self.settings = settings

    # TODO add an icon to the preferred profile and set "Preferred profile" as tooltip?
    def setup_list(self, profile_list, selected_profile_id):
        """Initialize internal profile list model"""
        self.profile_list = profile_list
        names = [each["name"] for each in profile_list]

        self.strlist.splice(
            0, self.strlist.get_n_items(), names
        )

        # TODO Do this cleaner
        for i, each in enumerate(profile_list):
            if each["id"] == selected_profile_id:
                self.set_selected(i)
                return

        self.set_selected(0)

    def set_profile(self) -> None:
        with self.freeze_notify():
            profile_display_name = self.get_selected_item().get_string()
            for each in self.profile_list:
                if each["name"] == profile_display_name:
                    self.selected_profile = each["id"]
                    log.debug("set profile to %s", each["id"])
                    break

        # TODO make unapplied work with this
        # if self.selected_profile != self.ProfileGSet:
        #     self.ProfileGSet = self.selected_profile

    @GObject.Property
    def ProfileGSet(self) -> str:
        return self.settings.get_string("profile-selected")

    @ProfileGSet.setter
    def ProfileGSet(self, profile_id: str) -> None:
        self.settings.set_string("profile-selected", profile_id)
        # TODO emit a notify here?
