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


# TODO separate (binding switches and applying/discard) from all other GSet use cases.
# In other cases, they can just create their own temp settings object


import logging
from typing import Optional, Callable
from gi.repository import Adw, Gio, GObject, Gtk

from addwater import info

log = logging.getLogger(__name__)


# TODO give ability to refresh page OR refresh the profile switcher on a datapath change
# TODO grey out enable theme switch when there's no package to install (first launch, no internet)
@Gtk.Template(resource_path=info.PREFIX + "/gtk/addwater-page.ui")
class AddWaterPage(Adw.Bin):
    """The container that holds the GUI that allows the user to configure the
    theme.

    args:
            backend = an addwaterbackend interface object
    """

    __gtype_name__ = "AddWaterPage"

    # Widget controls
    toast_overlay = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    change_confirm_bar = Gtk.Template.Child()

    general_pref_group = Gtk.Template.Child()

    enable_button = Gtk.Template.Child()
    profile_combobox = Gtk.Template.Child()
    profile_combobox_list = Gtk.Template.Child()

    # Class Attributes
    app_name: str  # Proper, capitalized name of the app, 'Firefox' or 'Thunderbird'
    selected_profile: str  # User's chosen profile to install theme to

    profile_list: list[dict[str, str]]

    current_toast = None

    def __init__(self, backend):
        super().__init__()

        self.backend = backend

        self.app_name = self.backend.get_app_name()

        self.settings = self.backend.get_app_settings()
        self.settings.delay()

        # Profiles
        self.selected_profile = self.settings.get_string("profile-selected")
        self.profile_list = self.backend.get_profile_list()

        options = self.backend.get_app_options()
        self.init_gui(options, self.profile_list)

        self.profile_combobox.notify("selected-item")
        self.profile_combobox.connect("notify::selected-item", self._set_profile)

        # Change Confirmation bar
        self.install_action("water.apply-changes", None, self.on_apply_action)
        self.install_action("water.discard-changes", None, self.on_discard_action)
        self.settings.bind_property(
            "has-unapplied",
            self.change_confirm_bar,
            "revealed",
            GObject.BindingFlags.SYNC_CREATE,
        )
        self.send_toast(_("Checking for updates..."), 10)
        # TODO add callback instead when async updates are finished
        self.request_update_status()

    """PUBLIC METHODS"""

    def request_update_status(self):
        update_status = self.backend.update_theme()
        match update_status:
            case update_status.UPDATED:
                version = self.backend.get_update_version(pretty=True)
                # Translators: {} will be replaced by a version number
                msg = (_("Updated theme to v{}").format(version))
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

    def on_apply_action(self, *_args):
        """Apply changes to GSettings and call the proper install or uninstall method"""
        log.debug("Applied changes")

        self._set_profile(self.profile_combobox)

        self.settings.apply()

        theme_enabled = self.settings.get_boolean("theme-enabled")

        if theme_enabled:
            log.debug("GUI calling for install..")
            install_status = self.backend.begin_install(
                self.selected_profile, True
            )
            toast_msg = _("Installed Theme. Restart Firefox to see changes.")
        else:
            log.debug("GUI calling for uninstall...")
            install_status = self.backend.remove_theme(self.selected_profile)
            toast_msg = _("Removed Theme. Restart Firefox to see changes.")

        match install_status:
            case install_status.FAILURE:
                toast_msg = _("Installation failed")
            case _:
                pass

        self.send_toast(toast_msg, 3, 1)

    def on_discard_action(self, *_args):
        """Revert changes made to GSettings and notify user"""
        log.info("Discarded unapplied changes")

        # Revert must ALWAYS be first
        self.settings.revert()

        try:
            self._reset_profile_combobox()
        except PageException as err:
            log.error(err)
            self.send_toast(
                _("The interface had an error. Please report if this occurs multiple times.")
            )

        self.send_toast(_("Changes reverted"))

    def send_toast(
        self, msg: Optional[str] = None, timeout_seconds: int = 2, priority: int = 0
    ):
        # FIXME When a toast is displayed at the app launch, it still stays on screen forever
        if self.current_toast:
            self.current_toast.dismiss()

        # Pass None as msg to withdraw any toasts already on screen
        if not msg:
            return

        self.current_toast = Adw.Toast(
            title=msg, timeout=timeout_seconds, priority=priority
        )

        self.toast_overlay.add_toast(self.current_toast)

        # Workaround for Adw bug which cause toasts to display forever
        # issue: https://gitlab.gnome.org/GNOME/libadwaita/-/issues/440
        self.enable_button.grab_focus()

    def init_gui(self, options, profile_list):
        """Create and bind all SwitchRows according to their respective GSettings keys

        Args:
                options: a json-style list of dictionaries which include all option groups
                        and options that the theme supports.
                profile_list = list of dicts with "name" and "id"
        """
        # App options
        self.settings.bind(
            "theme-enabled", self.enable_button, "active", Gio.SettingsBindFlags.DEFAULT
        )
        # Theme options
        for each_group in options:
            group = self._create_option_group(
                group_schematic=each_group,
                gui_switch_factory=self._create_option_switch,
                settings=self.settings,
                enable_button=self.enable_button,
            )
            self.preferences_page.add(group)

        # Profile list
        for each in profile_list:
            self.profile_combobox_list.append(each["name"])
        try:
            self._reset_profile_combobox()
        except PageException as err:
            log.error(err)
            self.send_toast(
                _("The interface had an error. Please report if this occurs often.")
            )

    """PRIVATE METHODS"""

    def _display_version(self):
        # TODO clean this up a bit
        version = self.backend.get_update_version(pretty=True)
        if not version:
            version = _("Not installed")
        else:
            version = f"v{version}"
        # Translators: {} will be replaced with a version number (example: v132) or a status message
        self.general_pref_group.set_title(_("Firefox GNOME Theme — {}").format(version))

    def _set_profile(self, row, _=None) -> None:
        profile_display_name = row.get_selected_item().get_string()
        for each in self.profile_list:
            if each["name"] == profile_display_name:
                self.selected_profile = each["id"]
                log.debug("set profile to %s", each["id"])
                break

        # This compare avoids triggering "has-unapplied" too often
        if self.selected_profile != self.settings.get_string("profile-selected"):
            self.settings.set_string("profile-selected", self.selected_profile)

    @staticmethod
    def _create_option_group(
        group_schematic: dict[str, list[dict]],
        gui_switch_factory: Callable,
        settings,
        enable_button
    ):
        """Creates a PreferencesGroup with the included switch options, and
        binds all the switches to gsettings
        """

        group = Adw.PreferencesGroup(
            title=group_schematic["group_name"], margin_start=20, margin_end=20
        )

        for option in group_schematic["options"]:
            row = gui_switch_factory(
                title=option["summary"],
                subtitle=option["description"],
                extra_info=option["tooltip"],
            )

            row_switch = row.get_activatable_widget()
            settings.bind(
                option["key"], row_switch, "active", Gio.SettingsBindFlags.DEFAULT
            )
            # Grey-out row if theme isn't enabled.
            enable_button.bind_property(
                "active", row, "sensitive", GObject.BindingFlags.SYNC_CREATE
            )

            # Handle dependencies on other options
            if option["depends"]:
                for prereq, b in option["depends"]:
                    match b:
                        case True:
                            flag = Gio.SettingsBindFlags.DEFAULT
                        case False:
                            flag = Gio.SettingsBindFlags.INVERT_BOOLEAN
                    settings.bind(
                        prereq, row, "sensitive", flag
                    )


            group.add(row)

        return group

    @staticmethod
    def _create_option_switch(
        title: str, subtitle: str, extra_info: Optional[str] = None
    ):
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        # This styling was borrowed from GNOME settings > Mouse Acceleration option
        if extra_info:
            label = Gtk.Label(
                label=extra_info,
                margin_top=6,
                margin_bottom=6,
                margin_start=6,
                margin_end=6,
                max_width_chars=50,
                wrap=True,
            )
            info_popup = Gtk.Popover(autohide=True, child=label, hexpand=False)
            info_button = Gtk.MenuButton(
                has_frame=False,
                icon_name="info-outline-symbolic",
                valign="center",
                vexpand=False,
                tooltip_text="More Information",
                popover=info_popup,
            )
            row.add_suffix(info_button)

        switch = Gtk.Switch(
            valign="center",
            vexpand=False,
        )
        row.add_suffix(switch)
        row.set_activatable_widget(switch)

        return row

    def _reset_profile_combobox(self):
        last_profile = self.settings.get_string("profile-selected")
        if not last_profile:
            return
        for each in self.profile_list:
            if each["id"] == last_profile:
                self.profile_combobox.set_selected(self.profile_list.index(each))
                return

        log.error("Profile combo box reset failed")
        log.debug(f"last_profile: {last_profile}")
        raise PageException("Profile combo box reset failed")


# Generic to use for any basic GUI failure
# TODO re-evaluate whether these are necessary
class PageException(Exception):
    pass


class FatalPageException(Exception):
    pass
