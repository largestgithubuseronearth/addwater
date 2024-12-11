# TODO is there a simpler way to do this? .in files? json?

FIREFOX_OPTIONS = [
    {
        "group_name": _("Tab Position"),
        "options": [
            {
                "key": "hide-single-tab",
                "js_key": "hideSingleTab",
                "summary": _("Hide Single Tab"),
                "description": _("Hide Tab Bar when only one tab is open"),
                "tooltip": _("Consider placing the New Tab button near the Search Bar. Otherwise it may get lost when only one tab is open."),
            },
            {
                "key": "normal-width-tabs",
                "js_key": "normalWidthTabs",
                "summary": _("Standard Tab Width"),
                "description": _("Use same tab width as standard Firefox"),
                "tooltip": "",
            },
            {
                "key": "swap-tab-close",
                "js_key": "swapTabClose",
                "summary": _("Swap Tab Close Button"),
                "description": _("Place Close Tab button on opposite side from window controls"),
                "tooltip": "",
            },
            {
                "key": "bookmarks-toolbar-under-tabs",
                "js_key": "bookmarksToolbarUnderTabs",
                "summary": _("Bookmarks Toolbar Under Tabs"),
                "description": _("Place Bookmarks Bar underneath Tab Bar"),
                "tooltip": "",
            },
            {
                "key": "tabs-as-headerbar",
                "js_key": "tabsAsHeaderbar",
                "summary": _("Tabs as Headerbar"),
                "description": _("Place Tab Bar at top of window"),
                "tooltip": _('Enabling with "Hide Single Tab" will show a Title Bar when only one tab is open'),
            },
            {
                "key": "tab-align-left",
                "js_key": "tabAlignLeft",
                "summary": _("Left-Aligned Titles"),
                "description": _("Align tab title to left"),
                "tooltip": "",
            },
        ],
    },
    {
        "group_name": _("Tab Behavior"),
        "options": [
            {
                "key": "active-tab-contrast",
                "js_key": "activeTabContrast",
                "summary": _("Active Tab Contrast"),
                "description": _("Add more visual contrast to the active tab"),
                "tooltip": "",
            },
            {
                "key": "close-only-selected-tabs",
                "js_key": "closeOnlySelectedTabs",
                "summary": _("Close Only Selected Tabs"),
                "description": _("Only show the Close Tab button on the active tab"),
                "tooltip": "",
            },
            {
                "key": "symbolic-tab-icons",
                "js_key": "symbolicTabIcons",
                "summary": _("Symbolic Tab Icons"),
                "description": _("Make all tab icons appear similar to symbolic icons"),
                "tooltip": "",
            },
            {
                "key": "all-tabs-button",
                "js_key": "allTabsButton",
                "summary": _("Tab List Button"),
                "description": _("Show All Tabs button"),
                "tooltip": "",
            },
            {
                # TODO make this dependent on all-tabs-button being true
                "key": "all-tabs-button-on-overflow",
                "js_key": "allTabsButtonOnOverflow",
                "summary": _("Tab List Button on Overflow"),
                "description": _("Only show All Tabs button if not all tabs can fit on screen"),
                "tooltip": "",
            },
        ],
    },
    {
        "group_name": "Style",
        "options": [
            {
              "key": "bookmarks-on-fullscreen",
                "js_key": "bookmarksOnFullscreen",
                "summary": _("Fullscreen Bookmarks"),
                "description": _("Show Bookmarks bar while in fullscreen"),
                "tooltip": ""
            },
            {
                "key": "hide-webrtc-indicator",
                "js_key": "hideWebrtcIndicator",
                "summary": _("Hide Privacy Indicators"),
                "description": _("Hide microphone, screen share, and camera warnings"),
                "tooltip": _("GNOME will still show these privacy indicators in the Top Bar"),
            },
            {
                "key": "oled-black",
                "js_key": "oledBlack",
                "summary": _("True Black Dark Theme"),
                "description": _("Use an OLED-friendly, deep black when dark theme is enabled"),
                "tooltip": "",
            },
            {
                "key": "no-themed-icons",
                "js_key": "noThemedIcons",
                "summary": _("No Themed Icons"),
                "description": _("Use standard Firefox icons instead of Adwaita-styled icons"),
                "tooltip": "",
            },
        ],
    },
]
