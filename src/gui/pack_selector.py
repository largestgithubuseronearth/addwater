# page.py
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

from gi.repository import Adw, Gio, GObject, Gtk

from addwater import info
from addwater.backend import InterfaceMisuseError
from addwater.apps.firefox.firefox_paths import FirefoxPack

log = logging.getLogger(__name__)


@Gtk.Template(resource_path=info.PREFIX + "/gtk/pack-selector.ui")
class PackSelector(Adw.ComboRow):
    __gtype_name__ = "WaterPackSelector"

    backend = None
    # TODO this shouldn't touch settings or backend at all
    package: FirefoxPack
    inner_valid_path: bool
    autofind_paths: bool = GObject.Property(type=bool, default=True, flags=GObject.ParamFlags.READWRITE)

    def __init__(self):
        super().__init__()
        # TODO use a full bind instead of connect to signal
        # FIXME this causes an error during GObject construction since
        #       settings isn't in place yet
        self.notify('selected-item')
        self.connect('notify::selected-item', lambda *args: self.set_package())


    # TODO this should be done in constructor; shouldn't need Page's help to do this
    def setup_list(self, pack, backend):
        self.backend = backend

        self.get_model().splice(1, 0, [p.pack_name for p in FirefoxPack])

        if pack and not self.autofind_paths:
            self.package = pack
            # Offset 1 since Auto Discover is first
            i = list(FirefoxPack).index(pack) + 1
            self.set_selected(i)

    def set_package(self):
        selected_index = self.get_selected()
        AUTO = 0

        if selected_index == AUTO:
            self.autofind_paths = True
            log.info("Autofind paths enabled")
            self.valid_path = True
            self.emit("package-changed")
            return

        self.autofind_paths = False
        log.info("Autofind paths disabled")

        packstr = self.get_selected_item().get_string()
        new_pack = FirefoxPack.new_from_name(packstr)
        if new_pack:
            try:
                self.backend.set_package(new_pack)
            except InterfaceMisuseError as err:
                log.error(err)
                self.valid_path = False
            else:
                self.valid_path = True
                self.package = new_pack
                self.emit("package-changed")

        return

    @GObject.Property(type=bool, default=False)
    def valid_path(self) -> bool:
        return self.inner_valid_path

    @valid_path.setter
    def set_valid_path(self, is_valid: bool):
        if is_valid:
            self.remove_css_class("error")
        else:
            self.add_css_class("error")

        self.inner_valid_path = is_valid

    @GObject.Signal(name="package-changed")
    def package_changed(self):
        pass
