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
from addwater.profile import Profile
from addwater.gui.profile_selector import ProfileSelector
from addwater.gui.pack_selector import PackSelector
from addwater.apps.firefox.firefox_paths import FirefoxPack

from .backend import InterfaceMisuseError

log = logging.getLogger(__name__)

@Gtk.Template(resource_path=info.PREFIX + "/gtk/addwater-page.ui")
class AddWaterPage(Adw.Bin):
    __gtype_name__ = "AddWaterPage"

    # Widget controls
    toast_overlay = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    change_confirm_bar = Gtk.Template.Child()

    general_pref_group = Gtk.Template.Child()

    enable_button = Gtk.Template.Child()
    profile_combobox = Gtk.Template.Child()
    package_combobox = Gtk.Template.Child()

    # TODO bind this to a prop that checks if the theme is installed
    theme_enabled = GObject.Property(
        type=bool,
        default=False,
        flags=(GObject.ParamFlags.READWRITE | GObject.ParamFlags.CONSTRUCT)
    )

    app_name = GObject.Property(
        type=str,
        flags=(GObject.ParamFlags.READWRITE)
    )

    current_toast = None

    def __init__(self, backend):
        super().__init__()

        self.backend = backend

        # Stores changes as a transaction to apply all opts at once
        self.settings = self.backend.get_app_settings()
        self.settings.delay()

        self.init_gui(self.backend.get_app_options())
        self.init_actions()
        self.bind_settings()

        self.send_toast(_("Checking for updates..."), 10)
        self.request_update_status()

    """PUBLIC METHODS"""

    # TODO turn this into an async callback
    def request_update_status(self):
        update_status = self.backend.update_theme()
        match update_status:
            case update_status.UPDATED:
                if self.theme_enabled:
                    self.activate_action("apply-changes")

                v = self.backend.get_update_version()
                # Translators: {} will be replaced by a version number (example: "v126.5.65")
                msg = _("Updated theme to {}").format(str(v))
            case update_status.DISCONNECTED:
                msg = _("Failed to check for updates due to a network issue")
            case update_status.RATELIMITED:
                msg = _("Failed to check for updates. Please try again later.")
            case update_status.OTHER_ERROR:
                msg = _("Unknown error has occurred. Please report this to developer.")
            case update_status.NO_UPDATE:
                msg = None

        self.update_version_title()
        self.send_toast(msg)

    def on_apply_action(self, *_args):
        """Apply changes to GSettings and call the proper install or uninstall method"""
        log.debug("Applied changes")

        self.settings.apply()

        if self.theme_enabled:
            log.debug("GUI calling for install..")
            install_status = self.backend.begin_install(
                self.profile_combobox.get_selected_item(), True
            )
            toast_msg = _("Installed Theme. Restart Firefox to see changes.")
        else:
            log.debug("GUI calling for uninstall...")
            install_status = self.backend.remove_theme(
                self.profile_combobox.get_selected_item()
            )
            toast_msg = _("Removed Theme. Restart Firefox to see changes.")

        if install_status == install_status.FAILURE:
            toast_msg = _("Installation failed")

        self.send_toast(toast_msg, 3, 1)

    def on_discard_action(self):
        self.settings.revert()
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
        if self.current_toast:
            self.current_toast.dismiss()

        if not msg:
            return

        self.current_toast = Adw.Toast(
            title=msg, timeout=timeout_seconds, priority=priority
        )

        self.toast_overlay.add_toast(self.current_toast)

        # Hack - AdwToasts don't timeout properly
        # details: https://gitlab.gnome.org/GNOME/libadwaita/-/issues/440
        self.enable_button.grab_focus()

    # TODO reduce all of this as much as possible using props and constructors
    def init_gui(self, options):
        """Create and bind all SwitchRows according to their respective GSettings keys

        Args:
            options: a json-style list of dictionaries which include all option groups
                    and options that the theme supports.
        """
        # Theme options
        for group_definition in options:
            group = create_option_group(
                group_schematic=group_definition,
                gui_switch_factory=create_option_switch,
                settings=self.settings,
            )
            self.bind_property(
                "theme-enabled",
                group, "sensitive",
                GObject.BindingFlags.DEFAULT | GObject.BindingFlags.SYNC_CREATE
            )
            self.preferences_page.add(group)

        pack = self.backend.get_package()
        self.package_combobox.setup_list(pack, self.backend)
        self.profile_combobox.setup_list(
            self.backend.get_profiles(),
            self.settings.get_string("profile-selected"),
            pack,
        )

    def bind_settings(self):
        # Primary Options
        self.settings.bind(
            "theme-enabled",
            self, "theme-enabled",
            Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind("profile-selected", self.profile_combobox, "selected-profile-id", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("autofind-paths", self.package_combobox, "autofind-paths", Gio.SettingsBindFlags.DEFAULT)

        # Change Confirmation bar
        self.settings.bind_property(
            "has-unapplied",
            self.change_confirm_bar,
            "revealed",
            GObject.BindingFlags.SYNC_CREATE,
        )

    def init_actions(self):
        action_group = Gio.SimpleActionGroup.new()

        apply_action = Gio.SimpleAction(name="apply-changes")
        apply_action.connect("activate", lambda *blah: self.on_apply_action())
        self.package_combobox.bind_property("valid-path", apply_action, "enabled", GObject.BindingFlags.SYNC_CREATE)
        action_group.add_action(apply_action)

        discard_action = Gio.SimpleAction(name="discard-changes")
        discard_action.connect("activate", lambda *blah: self.on_discard_action())
        action_group.add_action(discard_action)

        self.insert_action_group("water", action_group)

        # Combobox setup
        # TODO try to connect this in ui
        self.package_combobox.connect("package-changed", self.package_changed_cb)

    def package_changed_cb(self, pack_selector):
        if (pack := pack_selector.package):
            self.profile_combobox.update_package_filter(pack)

    def update_version_title(self):
        v = self.backend.get_update_version()
        version_str = parse_version_str(v)

        # Translators: {} will be replaced with a version number (example: v132) or a status message
        self.general_pref_group.set_title(_("Firefox GNOME Theme — {}").format(version_str))

def parse_version_str(version: Version):
    if version == Version("0.0.0"):
        return _("Not installed")

    return "v{}".format(str(version).removesuffix(".0"))

