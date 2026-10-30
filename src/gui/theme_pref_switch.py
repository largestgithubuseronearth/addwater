import logging

from addwater import info
from addwater.model import ThemePref, ThemePrefGroup
from gi.repository import Adw, Gio, GObject, Gtk
from gi.repository.GObject import ParamFlags as GParamFlags

log = logging.getLogger("theme-pref-switch")

@Gtk.Template(resource_path=info.PREFIX + "/gtk/theme-pref-switch.ui")
class ThemePrefSwitch(Adw.ActionRow):
    """A toggle switch dedicated to Theme prefs.

    :pref: ThemePref this switch is in control of """
    __gtype_name__ = "WaterThemePrefSwitch"

    tooltip_button: Gtk.MenuButton = Gtk.Template.Child()
    tooltip_label: Gtk.Label = Gtk.Template.Child()
    switch: Gtk.Switch = Gtk.Template.Child()

    _pref: ThemePref

    disclaimer_text = GObject.Property(
            type=str,
            flags=(GParamFlags.READWRITE | GParamFlags.CONSTRUCT_ONLY))

    def __init__(self, pref: ThemePref) -> None:
        super().__init__(
            title=pref["summary"],
            subtitle=pref["description"],
            disclaimer_text=pref["tooltip"]
        )
        self._pref = pref
        self.notify("has-disclaimer")
        self.connect("activated",
                     lambda *a: log.debug(f"toggled pref {self.get_title()}"))


    @GObject.Property(type=bool, default=False)
    def has_disclaimer(self) -> bool:
        return bool(self.disclaimer_text)



@Gtk.Template(resource_path=info.PREFIX + "/gtk/theme-pref-group.ui")
class ThemePrefGrouping(Adw.PreferencesGroup):
    __gtype_name__ = "WaterThemePrefGroup"

    _pref_group: ThemePrefGroup
    _settings: Gio.Settings

    _name: str

    def __init__(self, name: str, pref_groups: ThemePrefGroup, settings: Gio.Settings) -> None:
        super().__init__()

        self._name = name
        self._pref_group = pref_groups
        self._settings = settings
        self.notify("group-name")

        for pref in pref_groups["prefs"]:
            row = ThemePrefSwitch(pref)

            row_switch = row.get_activatable_widget()
            settings.bind(
                pref["key"], row_switch, "active", Gio.SettingsBindFlags.DEFAULT
            )

            # FIXME bind to the "active" property of the row it depends on.
            # requires holding a reference to that row which I don't atm

            # Handle dependencies on other prefs
            if pref["depends"]:
                for prereq, b in pref["depends"]:
                    match b:
                        case True:
                            flag = Gio.SettingsBindFlags.DEFAULT
                        case False:
                            flag = Gio.SettingsBindFlags.INVERT_BOOLEAN
                    settings.bind(prereq, row, "sensitive", flag)

            self.add(row)

    @GObject.Property(type=str, flags=GParamFlags.READABLE)
    def group_name(self) -> str:
        return self._name
