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
from addwater.profile import Profile
from addwater.backend import InterfaceMisuseError

log = logging.getLogger(__name__)

# TODO merge the package selector into this one combobox, and break them into
#      sections by package format

@Gtk.Template(resource_path=info.PREFIX + "/gtk/profile-selector.ui")
class ProfileSelector(Adw.ComboRow):
    __gtype_name__ = "AddWaterProfileSelector"

    # TODO store all profiles in the same model and the PackSelector
    #      changes the filter of visible ones; GtkFilter
    profiles: Gio.ListStore = Gtk.Template.Child()
    sort_model: Gtk.SortListModel = Gtk.Template.Child()
    sorter: Gtk.CustomSorter = Gtk.Template.Child()

    # Also GSettings needs this to store profile id
    selected_profile_id = GObject.Property(type=str, flags=(GObject.ParamFlags.READWRITE))

    def __init__(self):
        super().__init__()

        self.sorter.set_sort_func(sort_profiles)

    def setup_list(self, profile_list, selected_profile_id):
        self.profiles.splice(0, self.profiles.get_n_items(), profile_list)

        for i, profile in enumerate(self.sort_model):
            if profile.id == selected_profile_id:
                self.set_selected(i)
                return

        self.set_selected(0)

def sort_profiles(a: Profile, b: Profile, _data) -> int:
    if (res := b.favorite - a.favorite) != 0:
        return res

    return (a.name > b.name) - (b.name > a.name)
