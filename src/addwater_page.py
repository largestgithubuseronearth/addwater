# addwater_page.py
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

# TODO make app_path a class property that can be edited easily
# FIXME If the app updates but the user doesn't install it, then the theme update is downloaded in full repeatedly until user manually installs it


import logging, json, os.path, shutil
from typing import Optional
from gi.repository import Gtk, Adw, Gio, GLib, GObject
from .utils import paths
from .utils import exceptions as err
from .theme_options import FIREFOX_COLORS
from .backend import AddWaterBackend

log = logging.getLogger(__name__)


@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/addwater-page.ui")
class AddWaterPage(Adw.Bin):
    __gtype_name__ = "AddWaterPage"

    # Class Attributes
    app_name: str     # Proper, capitalized name of the app, 'Firefox' or 'Thunderbird'
    selected_color: str       # User's chosen color theme
    selected_profile: str        # User's chosen profile to install theme to

    profile_list: list[dict[str,str]]

    # Widget controls
    toast_overlay = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    change_confirm_bar = Gtk.Template.Child()

    enable_button = Gtk.Template.Child()
    profile_combobox = Gtk.Template.Child()
    profile_combobox_list = Gtk.Template.Child()
    color_combobox = Gtk.Template.Child()
    color_combobox_list = Gtk.Template.Child()

    def __init__(self, app_name: str, backend=None):
        super().__init__()
        try:
            self.backend = backend
        except:
            print("CRITICAL: Backend initialization FAILED")

        self.app_name = app_name

        self.settings = Gio.Settings(schema_id=f"dev.qwery.AddWater.{self.app_name}")
        self.settings.delay()

        # Profiles and Colors lists
        self.selected_color = self.settings.get_string("color-theme")
        self.selected_profile = self.settings.get_string("last-profile")
        self.profile_list = self.backend.get_profiles()

        self._init_gui(self.backend.get_app_options(), self.profile_list)

        self.profile_combobox.notify("selected-item")
        self.profile_combobox.connect("notify::selected-item", self._set_profile)
        self.color_combobox.notify("selected-item")
        self.color_combobox.connect("notify::selected-item", self._set_colors)

        # Change Confirmation bar
        # TODO try using an action group instead
        self.install_action(
            "water.apply-changes", None, self.apply_changes
        )
        self.install_action(
            "water.discard-changes", None, self.discard_changes
        )

        self.settings.bind_property(
            "has-unapplied",
            self.change_confirm_bar,
            "revealed",
            GObject.BindingFlags.SYNC_CREATE
        )

        # Check for updates and install if new available and theme is already enabled
        value = self.backend.get_update_available()

        if value and self.settings.get_boolean("theme-enabled"):
            self.apply_changes()
            self.send_toast(f"Updated to v{self.backend.update_version}")


    def _init_gui(self, option_list, profile_list):
        """Create and bind all SwitchRows according to their respective GSettings keys

        Args:
            option_list: a json-style list of dictionaries which include all option groups
                and options that the theme supports. Included in theme_options.py
        """
        # App options
        self.settings.bind(
            "theme-enabled", self.enable_button, "active", Gio.SettingsBindFlags.DEFAULT
        )
        # Theme options
        for each in option_list:
            group = Adw.PreferencesGroup(
                title=each["group_name"], margin_start=30, margin_end=30
            )

            for option in each["options"]:
                button = Adw.SwitchRow(
                    title=option["summary"], subtitle=option["description"]
                )
                # TODO If possible, make this tooltip an actual info suffix button (i)
                try:
                    button.set_tooltip_text(option["tooltip"])
                except KeyError:
                    pass
                self.settings.bind(
                    option["key"], button, "active", Gio.SettingsBindFlags.DEFAULT
                )
                # Disables theme-specific options if theme isn't enabled.
                self.enable_button.bind_property(
                    "active", button, "sensitive", GObject.BindingFlags.SYNC_CREATE
                )

                group.add(button)
            self.preferences_page.add(group)

        # Colors list
        for each in FIREFOX_COLORS:
            self.color_combobox_list.append(each)
        self.reset_color_combobox()

        # Profile list
        for each in profile_list:
            self.profile_combobox_list.append(each["name"])
        self.reset_profile_combobox()


    def apply_changes(self, *_):
        """FRONT: Apply changes to GSettings and call the proper install or uninstall method"""
        self.settings.apply()

        try:
            if self.settings.get_boolean("theme-enabled"):
                log.info(f'Installing theme to {self.selected_profile}...')
                self.backend.full_install()
                msg = "Installed Theme. Restart Firefox to see changes."
            else:
                log.info(f'Uninstalling theme from {self.selected_profile}...')
                self.backend.remove_theme()
                msg = "Removed Theme. Restart Firefox to see changes."
        except err.FatalPageException as e:
            log.critical(e)
            raise err.FatalPageException(e)
        except err.InstallException as e:
            log.critical(e)
            msg = e.user_msg
        else:
            log.info('SUCCESS')

        self.send_toast(msg, 3, 1)


    def discard_changes(self, *_):
        """FRONT: Revert changes made to GSettings and notify user"""
        # Revert must ALWAYS be first
        self.settings.revert()

        self.reset_color_combobox()
        self.reset_profile_combobox()

        self.send_toast("Changes reverted")


    def _set_profile(self, row, _=None):
        profile_display_name = row.get_selected_item().get_string()
        for each in self.profile_list:
            if each["name"] == profile_display_name:
                self.selected_profile = each["id"]
                log.debug('set profile to %s', each["id"])
                break

        # This compare check avoids triggering "has-unapplied" at app launch
        if self.selected_profile != self.settings.get_string("last-profile"):
            self.settings.set_string("last-profile", self.selected_profile)


    def _set_colors(self, row, _):
        self.selected_color = row.get_selected_item().get_string().lower()

        # This compare check avoids triggering "has-unapplied" at app launch
        if self.selected_color != self.settings.get_string("color-theme"):
            self.settings.set_string("color-theme", self.selected_color)


    # TODO consider using timedelta on timeout arg
    def send_toast(self, msg: str, timeout: int=2, priority: int=0):
        # Workaround for libadwaita bug which cause toasts to display forever
        if not msg:
            log.error("Tried to send a toast of None")
            print("Tried to send a toast of None")
            return

        self.toast_overlay.add_toast(
            Adw.Toast(
                title=msg, timeout=timeout, priority=priority
            )
        )
        self.enable_button.grab_focus()


    def reset_profile_combobox(self,):
        last_profile = self.settings.get_string("last-profile")
        for each in self.profile_list:
            if each["id"] == last_profile:
                self.profile_combobox.set_selected(self.profile_list.index(each))
                return

        raise FileNotFoundError('Profile combo box reset failed')


    def reset_color_combobox(self,):
        selected = self.settings.get_string("color-theme").title()
        for each in FIREFOX_COLORS:
            if each == selected:
                self.color_combobox.set_selected(FIREFOX_COLORS.index(each))
                return

        raise FileNotFoundError('Profile combo box reset failed')
