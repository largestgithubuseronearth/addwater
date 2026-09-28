from addwater.utils.background import BackgroundUpdater
from enum import Enum
from gi.repository import Gio, GLib
import logging
from addwater import Backend

log = logging.getLogger("cli-provider")

class CliProvider:
    _app: Gio.Application

    def __init__(self, app: Gio.Application) -> None:
        self._register_into_gapp(app)

        self._app = app

    def do_command_line(self, app: Gio.Application, cmdline: Gio.ApplicationCommandLine) -> int:
        """Run in your app's 'do_command_line' vfunc and return its value.
        Don't modify it; everything will be taken care of for you"""
        return self._run_command_line(cmdline).value

    # TODO should this be in control of starting the GUI? Probably not
    def _run_command_line(self, cmdline: Gio.ApplicationCommandLine) -> Enum:
        """Handles command line args and options if given, or starts the GUI
        window if none are provided."""
        options = cmdline.get_options_dict().end().unpack()

        if not options:
            self._app.activate()
            return CliStatus.SUCCESS

        if options.get("quick-update"):
            return self._update_firefox_gnome_theme(self._app.backends[0])
        else:
            log.error("use --help for proper usage notes")
            return CliStatus.FAILURE

    # TODO use AppTheme when available instead
    def _update_firefox_gnome_theme(self, theme_backend: Backend) -> Enum:
        if not theme_backend:
            log.error("no themes available")
            return CliStatus.FAILURE

        background_updater = BackgroundUpdater(theme_backend)
        background_updater.quick_update()

        notif = background_updater.get_status_notification()
        if notif:
            self._app.send_notification("addwater-bg-update-status", notif)

        return CliStatus.SUCCESS

    # TODO setup a real command tree here
    # TODO AppTheme should store a OptionGroup mapping
    #      OptionEntries to methods to define its CLI stuff
    def _register_into_gapp(self, app: Gio.Application) -> None:
        app.add_main_option(
            "quick-update",
            ord("q"),
            GLib.OptionFlags.IN_MAIN,
            GLib.OptionArg.NONE,
            "Quickly update and install theme with the last-used settings",
            None,
        )


class CliException(Exception):
    pass

class CliStatus(Enum):
    SUCCESS = 0
    FAILURE = 1
    # TODO add more cases here?

