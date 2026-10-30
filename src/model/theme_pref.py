from typing import ReadOnly, TypedDict


# TODO pass this into the PrefSwitch GUI class
class ThemePref(TypedDict):
    """Defines how theme-specific user preferences should be laid out

    :key: GSettings key
    :js_key: Javascript key used in user.js
    :summary: Name of the option; title-case
    :description: Brief description of behavior; sentence-case
    :tooltip: Extra information that appears in a popover button. button is hidden if None
    :depends: other keys that this pref relies upon to be enabled
    """
    key:         ReadOnly[str]
    js_key:      ReadOnly[str]
    summary:     ReadOnly[str]
    description: ReadOnly[str]
    tooltip:     ReadOnly[str] | None
    depends:     ReadOnly[dict] | None

# TODO remove this and just add a "group" key to ThemePref
class ThemePrefGroup(TypedDict):
    """Grouping for [ThemePref]. This will be used to organize prefs in UI and
    CLI `--help`."""
    group_name: ReadOnly[str]
    prefs:      ReadOnly[list[ThemePref]]
