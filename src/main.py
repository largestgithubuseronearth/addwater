# main.py
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
import shutil
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from addwater import info
from addwater.apps.firefox import FirefoxAppDetails
from addwater.backend import Backend
from gi.repository import Adw, Gio, GLib
from .cli import CliProvider

from .utils import paths
from .utils.logs import init_logs
from .window import Window
from typing import Any

log = logging.getLogger("application")

# TODO create a CLI class to handle commands instead

class Application(Adw.Application):
    """The main application singleton class."""
    _cli_provider: CliProvider

    def __init__(self) -> None:
        super().__init__(
            application_id=info.APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            resource_base_path=info.PREFIX,
        )

        paths.init_paths()
        init_logs()

        self.init_actions()

        self.backends = self.construct_backends()

        self._cli_provider = CliProvider(self)

    def do_command_line(self, cmdline: Gio.ApplicationCommandLine) -> int:
        return self._cli_provider.do_command_line(self, cmdline)

    def do_activate(self) -> None:
        if not (win := self.props.active_window):
            win = Window(application=self, backends=self.backends)

        win.present()

    def construct_backends(self) -> None:
        # TODO make this dynamic to find all available app details
        backends = []
        ff_app_detail = FirefoxAppDetails()
        backends.append(Backend.new_from_appdetails(ff_app_detail))

        return backends

    def on_reset_app_action(self, *_args) -> None:
        log.warning("resetting the entire app...")

        settings = Gio.Settings(info.APP_ID)
        settings.reset("background-update")

        for each in self.backends:
            each.reset_app()

        try:
            shutil.rmtree(paths.DOWNLOAD_DIR)
        except FileNotFoundError:
            pass
        log.info("deleted download folder")

        log.info("app has been reset and will now exit")
        self.quit()

    def init_actions(self) -> None:
        actions = {
            "quit"     : (lambda *_a: self.quit(),
                          ["<primary>q", "<primary>w"]),
            "reset-app": (self.on_reset_app_action, None)
        }

        for name, details in actions.items():
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", details[0])
            self.add_action(action)
            if shortcuts := details[1]:
                self.set_accels_for_action(f"app.{name}", shortcuts)

def main(version: str) -> int:
    app = Application()
    return app.run(sys.argv)

