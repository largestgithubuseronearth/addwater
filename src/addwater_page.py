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


# TODO separate binding switches and applying/discard from all other GSet use cases.
# In other cases, they can just create their own temp settings object


import logging

from datetime import timedelta
from typing import Optional
from gi.repository import Gtk, Adw, Gio, GLib, GObject
from .utils import paths
from .utils import exceptions as exc
from .theme_options import FIREFOX_COLORS
from .backend import AddWaterBackend

log = logging.getLogger(__name__)

# TODO add variable to count number of errors. After a threshold, ask the user to report the issue.
@Gtk.Template(resource_path="/dev/qwery/AddWater/gtk/addwater-page.ui")
class AddWaterPage(Adw.Bin):
    __gtype_name__ = "AddWaterPage"

    # Widget controls
    toast_overlay = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    change_confirm_bar = Gtk.Template.Child()

    enable_button = Gtk.Template.Child()
    profile_combobox = Gtk.Template.Child()
    profile_combobox_list = Gtk.Template.Child()
    color_combobox = Gtk.Template.Child()
    color_combobox_list = Gtk.Template.Child()


    # Class Attributes
    app_name: str     # Proper, capitalized name of the app, 'Firefox' or 'Thunderbird'
    selected_profile: str        # User's chosen profile to install theme to

    profile_list: list[dict[str,str]]

    def __init__(self, app_name: str, backend=None):
        super().__init__()
        try:
            self.backend = backend
        except:
            log.critical("Backend initialization failed")
            raise exc.FatalPageException('Backend failed to init')

        self.app_name = app_name

        self.settings = Gio.Settings(schema_id=f"dev.qwery.AddWater.{self.app_name}")
        self.settings.delay()

        # Profiles
        self.selected_profile = self.settings.get_string("last-profile")
        self.profile_list = self.backend.get_profile_list()

        options = self.backend.get_app_options()
        self._init_gui(options, self.profile_list)

        self.profile_combobox.notify("selected-item")
        self.profile_combobox.connect("notify::selected-item", self._set_profile)
        self.color_combobox.notify("selected-item")
        self.color_combobox.connect("notify::selected-item", self._set_colors_gsettingss)

        # Change Confirmation bar
        # TODO try using an action group instead. Would that make actions easier?
        self.install_action(
            "water.apply-changes", None, self.on_apply_action
        )
        self.install_action(
            "water.discard-changes", None, self.on_discard_action
        )
        self.settings.bind_property(
            "has-unapplied",
            self.change_confirm_bar,
            "revealed",
            GObject.BindingFlags.SYNC_CREATE
        )

        self.request_update_status()



    """PUBLIC METHODS"""

    def request_update_status(self):
        update_status = self.backend.get_updates()
        match update_status:
            case update_status.UPDATED:
                version = self.backend.update_version
                msg = f'Updated theme to v{version}'
            case update_status.DISCONNECTED:
                msg = 'Updated failed due to a network issue'
            case update_status.RATELIMITED:
                msg = 'Update failed due to Github rate limits. Please try again later.'
            case _:
                msg = None
        if msg:
            self.send_toast(msg)


    def on_apply_action(self, *_):
        """Apply changes to GSettings and call the proper install or uninstall method"""
        log.info('Applied changes')

        self.settings.apply()

        theme_enabled = self.settings.get_boolean('theme-enabled')
        color_palette = self.settings.get_string('color-theme')
        if theme_enabled:
            log.info(f'GUI calling for install..')
            install_status = self.backend.full_install(
                self.selected_profile, color_palette
            )
            toast_msg = "Installed Theme. Restart Firefox to see changes."
        else:
            log.info(f'GUI calling for uninstall...')
            install_status = self.backend.remove_theme(self.selected_profile)
            toast_msg = "Removed Theme. Restart Firefox to see changes."

        match install_status:
            case install_status.FAILURE:
                toast_msg = 'Installation failed. Please report issue in About Menu'
            case _:
                pass

        self.send_toast(toast_msg, 3, 1)


    def on_discard_action(self, *_):
        """Revert changes made to GSettings and notify user"""
        log.info('Discarded unapplied changes')

        # Revert must ALWAYS be first
        self.settings.revert()

        try:
            self._reset_color_combobox()
            self._reset_profile_combobox()
        except PageException as err:
            log.error(err)
            self.send_toast('The interface had an error. Please report if this occurs multiple times.')

        self.send_toast("Changes reverted")


    def send_toast(self, msg: str, timeout_seconds: int=2, priority: int=0):
        # Workaround for libadwaita bug which cause toasts to display forever
        if not msg:
            log.error("Tried to send a toast of None")
            return

        self.toast_overlay.add_toast(
            Adw.Toast(title=msg, timeout=timeout_seconds, priority=priority)
        )
        self.enable_button.grab_focus()



    """PRIVATE METHODS"""

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


    def _set_colors_gsettingss(self, row, _=None):
        selected_color = row.get_selected_item().get_string().lower()

        # This compare check avoids triggering "has-unapplied" at app launch
        if selected_color != self.settings.get_string("color-theme"):
            self.settings.set_string("color-theme", selected_color)


    def _init_gui(self, options, profile_list):
        """Create and bind all SwitchRows according to their respective GSettings keys

        Args:
            options: a json-style list of dictionaries which include all option groups
                and options that the theme supports. Included in theme_options.py
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
                enable_button=self.enable_button
            )
            self.preferences_page.add(group)

        # Colors list
        for each in FIREFOX_COLORS:
            self.color_combobox_list.append(each)

        # Profile list
        for each in profile_list:
            self.profile_combobox_list.append(each["name"])
        try:
            self._reset_color_combobox()
            self._reset_profile_combobox()
        except PageException as err:
            log.error(err)
            self.send_toast('The interface had an error. Please report if this occurs often.')


    @staticmethod
    def _create_option_group(group_schematic: dict[str,list[dict]], gui_switch_factory: callable, settings, enable_button) -> None:
        """Creates a PreferencesGroup with the included switch options, and binds all the switches to gsettings"""
        # TODO these margins are arbitrary. Toy & try to find a better margin value.
        group = Adw.PreferencesGroup(
            title=group_schematic["group_name"], margin_start=20, margin_end=20
        )

        for option in group_schematic["options"]:
            row = gui_switch_factory(
                title=option["summary"], subtitle=option["description"], extra_info=option["tooltip"]
            )

            row_switch = row.get_activatable_widget()
            settings.bind(
                option["key"], row_switch, "active", Gio.SettingsBindFlags.DEFAULT
            )
            # disable row if theme isn't enabled.
            enable_button.bind_property(
                "active", row, "sensitive", GObject.BindingFlags.SYNC_CREATE
            )

            group.add(row)

        return group


    @staticmethod
    def _create_option_switch(title: str, subtitle: str, extra_info: str=None):
        # Everything about this seems to work perfect. Just need to fix the info button
        row = Adw.ActionRow(
            title=title,
            subtitle=subtitle,
        )
        # TODO make this popover appear when clicking the info button
        if extra_info:
            info_popup = Gtk.Popover(
                autohide=True,
                child=Gtk.Label(label=extra_info),
            )
            info_button = Gtk.Button(
                has_frame=False,
                icon_name='info-outline-symbolic',
                valign="center",
                vexpand=False,
            )
            row.add_suffix(info_button)


        switch = Gtk.Switch(
            valign="center",
            vexpand=False,
        )
        row.add_suffix(switch)
        row.set_activatable_widget(switch)

        return row


    def _reset_profile_combobox(self,):
        last_profile = self.settings.get_string("last-profile")
        for each in self.profile_list:
            if each["id"] == last_profile:
                self.profile_combobox.set_selected(self.profile_list.index(each))
                return
        raise PageException('Profile combo box reset failed')


    def _reset_color_combobox(self,):
        selected = self.settings.get_string("color-theme").title()
        for each in FIREFOX_COLORS:
            if each == selected:
                self.color_combobox.set_selected(FIREFOX_COLORS.index(each))
                return

        raise PageException('Color combo box reset failed')



# Generic to use for any basic GUI failure
class PageException(Exception):
    pass

class FatalPageException(Exception):
    pass
