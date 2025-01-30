import logging

from gi.repository import Gtk, Adw, Gio, GObject

from typing import Optional, Callable

def create_option_group(
    group_schematic: dict[str, list[dict]],
    gui_switch_factory: Callable,
    settings,
    enable_button
):
    """Creates AdwPreferencesGroup with the included switch options, and
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

        # FIXME bind to the "active" property of the row it depends on
        # requires holding a reference to that row which I don't atm

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

def create_option_switch(
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
            tooltip_text=_("More Information"),
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
