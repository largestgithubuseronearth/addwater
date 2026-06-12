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
import os.path
import shutil
import sys
from datetime import datetime, timezone

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from addwater.apps.firefox import FirefoxAppDetails
from addwater.backend import Backend
from gi.repository import Adw, Gio, GLib, Gtk

from addwater import info

from .utils import paths
from .utils.background import BackgroundUpdater
from .utils.logs import init_logs
from .window import Window

log = logging.getLogger("application")


class Application(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id=info.APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            resource_base_path=info.PREFIX,
        )

        self.init_actions()

        paths.init_paths()
        init_logs()

        self.backends = self.construct_backends()

        self.add_main_option(
            "quick-update",
            ord("q"),
            GLib.OptionFlags.IN_MAIN,
            GLib.OptionArg.NONE,
            "Quickly update and install theme with the last-used settings",
            None,
        )

    def do_command_line(self, command_line):
        """Handles command line args and options if given, or starts the GUI
        window if none are provided.
        """
        options = command_line.get_options_dict()
        options = options.end().unpack()

        if options or info.FORCE_BG == "True":
            try:
                self.handle_background_update(options)
                return 0
            except CommandMisuseException as err:
                log.error(f"Use --help for proper usage notes: {err}")
                return 1

        self.activate()
        return 0

    def do_activate(self):
        if not (win := self.props.active_window):
            win = Window(application=self, backends=self.backends)

        win.present()

    def handle_background_update(self, options):
        if info.FORCE_BG == "True":
            options = {"quick-update": True}

        # TODO add flag to reset app from CLI
        # TODO handle the option better and handle the error better
        if "quick-update" in options and options["quick-update"]:
            if not self.backends:
                log.error("Cannot find any Firefox ")
                return

            background_updater = BackgroundUpdater(self.backends[0])
            background_updater.quick_update()

            notif = background_updater.get_status_notification()
            if notif:
                self.send_notification("addwater-bg-update-status", notif)
            return

        raise CommandMisuseException(f"Unknown options: {options}")

    def construct_backends(self):
        # TODO make this dynamic to find all available app details
        backends = []
        ff_app_detail = FirefoxAppDetails()
        backends.append(Backend.new_from_appdetails(ff_app_detail))

        return backends

    def on_reset_app_action(self, *_args):
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

    def init_actions(self):
        actions = {
                 "quit": (lambda *_a: self.quit(), ["<primary>q", "<primary>w"]),
            "reset-app": (self.on_reset_app_action, None)
        }

        for name, details in actions.items():
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", details[0])
            self.add_action(action)
            if shortcuts := details[1]:
                self.set_accels_for_action(f"app.{name}", shortcuts)

def main(version):
    app = Application()
    return app.run(sys.argv)


class CommandMisuseException(Exception):
    pass
