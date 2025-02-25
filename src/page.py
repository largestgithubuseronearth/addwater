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

from addwater.gui.option_factory import (create_option_group,
                                         create_option_switch)
from gi.repository import Adw, Gio, GObject, Gtk
from packaging.version import Version

from addwater import info
from addwater.gui.profile_selector import ProfileSelector

from .backend import InterfaceMisuseError

log = logging.getLogger(__name__)


# TODO grey out enable theme switch when there's no package to install (first launch, no internet)
@Gtk.Template(resource_path=info.PREFIX + "/gtk/addwater-page.ui")
class AddWaterPage(Adw.Bin):
    """The container that holds the GUI that allows the user to configure the
    theme.

    Args:
        backend: an AddWaterBackend interface object
    """

    __gtype_name__ = "AddWaterPage"

    # Widget controls
    toast_overlay = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    change_confirm_bar = Gtk.Template.Child()

    general_pref_group = Gtk.Template.Child()

    enable_button = Gtk.Template.Child()
    profile_combobox = Gtk.Template.Child()
    firefox_package_combobox = Gtk.Template.Child()
    firefox_package_combobox_list = Gtk.Template.Child()

    # Class Attributes
    app_name: str  # Proper, capitalized name of the app, 'Firefox' or 'Thunderbird'

    profile_list: list[dict[str, str]]

    current_toast = None

    def __init__(self, backend):
        super().__init__()

        self.backend = backend
        self.app_name = self.backend.get_app_name()

        # Stores changes as a transaction to apply all opts at once
        self.settings = self.backend.get_app_settings()
        self.settings.delay()


        # Profiles
        self.profile_combobox.setup_settings(self.backend.get_app_settings())
        self.profile_list = self.backend.get_profile_list()

        # General GUI
        options = self.backend.get_app_options()
        self.init_gui(options, self.profile_list)

        # Package selector
        self.settings_instant = backend.get_app_settings()
        self.FIREFOX_FORMATS = backend.get_package_formats()
        self.firefox_path = self.backend.get_data_path()
        self._init_firefox_combobox()

        self._set_actions_signals()

        self.send_toast(_("Checking for updates..."), 10)
        self.request_update_status()

    """PUBLIC METHODS"""

    # TODO turn this into an async callback
    def request_update_status(self):
        update_status = self.backend.update_theme()
        match update_status:
            case update_status.UPDATED:
                if self.settings.get_boolean("theme-enabled"):
                    self.activate_action("apply-changes")

                version = str(self.backend.get_update_version()).rstrip(".0")
                version = f"v{version}"
                # Translators: {} will be replaced by a version number (example: "v126.5.65")
                msg = _("Updated theme to {}").format(version)
            case update_status.DISCONNECTED:
                msg = _("Failed to check for updates due to a network issue")
            case update_status.RATELIMITED:
                msg = _("Failed to check for updates. Please try again later.")
            case update_status.OTHER_ERROR:
                msg = _("Unknown error has occurred. Please report this to developer.")
            case update_status.NO_UPDATE:
                msg = None

        self._display_version()
        self.send_toast(msg)

    # TODO make this a stateful action?
    def on_apply_action(self, *_args):
        """Apply changes to GSettings and call the proper install or uninstall method"""
        log.debug("Applied changes")

        self.settings.apply()

        theme_enabled = self.settings.get_boolean("theme-enabled")
        if theme_enabled:
            log.debug("GUI calling for install..")
            install_status = self.backend.begin_install(
                self.profile_combobox.selected_profile, True
            )
            toast_msg = _("Installed Theme. Restart Firefox to see changes.")
        else:
            log.debug("GUI calling for uninstall...")
            install_status = self.backend.remove_theme(
                self.profile_combobox.selected_profile
            )
            toast_msg = _("Removed Theme. Restart Firefox to see changes.")

        match install_status:
            case install_status.FAILURE:
                toast_msg = _("Installation failed")
            case _:
                pass

        self.send_toast(toast_msg, 3, 1)

    def on_discard_action(self):
        """Revert all temporary changes and notify user"""
        log.info("Discarded unapplied changes")

        # Revert must ALWAYS be first
        self.settings.revert()

        # TODO Reset to prior selected profile

        self.send_toast(_("Changes reverted"))

    def send_toast(
        self, msg: Optional[str] = None, timeout_seconds: int = 2, priority: int = 0
    ) -> None:
        """Convenience method to send an AdwToast quickly.

        Args:
            msg: Toast message as string. If none, it will still withdraw the
                 currently displayed toast.
            timeout_seconds: Default is 2 seconds.
            priority: default is Normal Priority (0). Use 1 to skip the toast queue
                and immediately present this toast.

        """
        # FIXME When a toast is displayed at the app launch, it still stays on screen forever
        if self.current_toast:
            self.current_toast.dismiss()

        if not msg:
            return

        self.current_toast = Adw.Toast(
            title=msg, timeout=timeout_seconds, priority=priority
        )

        self.toast_overlay.add_toast(self.current_toast)

        # Hack - Adw: Toasts don't timeout properly
        # details: https://gitlab.gnome.org/GNOME/libadwaita/-/issues/440
        self.enable_button.grab_focus()

    def init_gui(self, options, profile_list):
        """Create and bind all SwitchRows according to their respective GSettings keys

        Args:
            options: a json-style list of dictionaries which include all option groups
                    and options that the theme supports.
            profile_list: list of dicts with "name" and "id"
        """
        # App options
        self.settings.bind(
            "theme-enabled", self.enable_button, "active", Gio.SettingsBindFlags.DEFAULT
        )
        # Theme options
        for each_group in options:
            group = create_option_group(
                group_schematic=each_group,
                gui_switch_factory=create_option_switch,
                settings=self.settings,
                enable_button=self.enable_button,
            )
            self.preferences_page.add(group)

        self.profile_combobox.setup_list(
            self.backend.get_profile_list(),
            self.settings.get_string("profile-selected")
        )

    """PRIVATE METHODS"""

    def _set_actions_signals(self):
        # Change Confirmation bar
        self.settings.bind_property(
            "has-unapplied",
            self.change_confirm_bar,
            "revealed",
            GObject.BindingFlags.SYNC_CREATE,
        )

        action_group = Gio.SimpleActionGroup.new()

        apply_action = Gio.SimpleAction(name="apply-changes")
        apply_action.connect("activate", lambda *blah: self.on_apply_action())
        apply_action.connect("activate", lambda *blah: self._set_profile())
        action_group.add_action(apply_action)

        discard_action = Gio.SimpleAction(name="discard-changes")
        discard_action.connect("activate", lambda *blah: self.on_discard_action())
        action_group.add_action(discard_action)

        self.insert_action_group("water", action_group)

        # Combobox setup
        self.profile_combobox.notify("selected-item")
        self.profile_combobox.connect("notify::selected-item", lambda *blah: self._set_profile())

        self.firefox_package_combobox.notify("selected-item")
        self.firefox_package_combobox.connect(
            "notify::selected-item", lambda row, *blah: self._set_firefox_package(row)
        )
        self.connect(
            "package-changed",
            lambda *_blah: self.profile_combobox.setup_list(
                self.backend.get_profile_list(),
                self.settings.get_string("profile-selected")
            )
        )

    def _display_version(self):
        version = self.backend.get_update_version()
        if version == Version("0.0.0"):
            v_str = _("Not installed")
        else:
            v_str = f"v{str(version).rstrip(".0")}"
        # Translators: {} will be replaced with a version number (example: v132) or a status message
        self.general_pref_group.set_title(_("Firefox GNOME Theme — {}").format(v_str))

    # TODO get this out of this class and let the selector class handle it entirely
    # This would be a lot easier with some way to track profiles cleanly
    def _set_profile(self) -> None:
        self.profile_combobox.set_profile()
        if self.profile_combobox.selected_profile != self.settings.get_string("profile-selected"):
            self.settings.set_string("profile-selected", self.profile_combobox.selected_profile)


    # TODO break package combobox and later its dialog into its own module

    # TODO make labels insensitive if the path doesn't exist
    # this would require keeping a model of which are available atm

    # Alternative: Mark ones that are valid so they're easier to find
    def _init_firefox_combobox(self):
        for each in self.FIREFOX_FORMATS:
            self.firefox_package_combobox_list.append(each["name"])

        if self.settings_instant.get_boolean("autofind-paths") is False:
            user_path = self.firefox_path

            for each in self.FIREFOX_FORMATS:
                if each["path"] == user_path:
                    i = self.FIREFOX_FORMATS.index(each) + 1
                    self.firefox_package_combobox.set_selected(i)

    # TODO integrate cleanly with existing objects e.g. settings reader
    def _set_firefox_package(self, row):
        # TODO rework all of this to be stateful to reduce the duplication
        selected_index = row.get_selected()
        AUTO = 0

        if selected_index == AUTO:
            self.settings_instant.set_boolean("autofind-paths", True)
            log.info("Autofind paths enabled")
            row.remove_css_class("error")
            self.profile_combobox.set_sensitive(True)
            row.set_has_tooltip(False)
            self.action_set_enabled("water.apply-changes", True)
            self.emit("package-changed")
            return

        self.settings_instant.set_boolean("autofind-paths", False)
        log.warning("Autofind paths disabled")

        selected = row.get_selected_item().get_string()
        for each in self.FIREFOX_FORMATS:
            if selected == each["name"]:
                path = each["path"]
                log.info(f'User specified path: {each["path"]}')

                try:
                    self.backend.set_data_path(path)
                except InterfaceMisuseError as err:  # invalid path provided
                    log.error(err)
                    self.profile_combobox.set_sensitive(False)
                    row.add_css_class("error")
                    row.set_has_tooltip(True)
                    self.action_set_enabled("water.apply-changes", False)
                else:
                    self.profile_combobox.set_sensitive(True)
                    row.remove_css_class("error")
                    row.set_has_tooltip(False)
                    self.action_set_enabled("water.apply-changes", True)
                    self.firefox_path = path
                    self.emit("package-changed")
                    break

    @GObject.Signal(name="package-changed")
    def package_changed(self):
        pass
