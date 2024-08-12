# TODO is there a simpler way to do this? .in files?

FIREFOX_OPTIONS = [
    {
    "group_name": "Tab Position",
    "options": [
          {
            "key": "hide-single-tab",
            "js_key": "hideSingleTab",
            "summary": "Hide Single Tab",
            "description": "Hide the tab bar when only one tab is open",
            "tooltip":'Consider moving New Tab button near the search bar. Otherwise it may get lost when only tab is open'
          },
          {
            "key": "normal-width-tabs",
            "js_key": "normalWidthTabs",
            "summary": "Standard Tab Width",
            "description": "Use the same tab width as standard Firefox"
          },
          {
            "key": "swap-tab-close",
            "js_key": "swapTabClose",
            "summary": "Swap Tab Close Button",
            "description": "Place Close Tab button on opposite side from window controls"
          },
          {
            "key": "bookmarks-toolbar-under-tabs",
            "js_key": "bookmarksToolbarUnderTabs",
            "summary": "Bookmarks Toolbar Under Tabs",
            "description": "Move the Bookmarks toolbar underneath tabs bar"
          },
          {
            "key": "tabs-as-headerbar",
            "js_key": "tabsAsHeaderbar",
            "summary": "Tabs as Headerbar",
            "description": "Place the tab bar at the top of the window, like Firefox's standard layout",
            "tooltip": 'Enabling with "Hide Single Tab" will replace the single tab with a title bar'
          }
        ]
    },
    {
    "group_name": "Tab Behavior",
    "options": [
          {
            "key": "active-tab-contrast",
            "js_key": "activeTabContrast",
            "summary": "Active Tab Contrast",
            "description": "Add more visual contrast to the active tab"
          },
          {
            "key": "close-only-selected-tabs",
            "js_key": "closeOnlySelectedTabs",
            "summary": "Close Only Selected Tabs",
            "description": "Only show the Close Tab button on the active tab"
          },
          {
            "key": "symbolic-tab-icons",
            "js_key": "symbolicTabIcons",
            "summary": "Symbolic Tab Icons",
            "description": "Make all tab icons look similar to symbolic icons"
          }
        ]
    },

  {
    "group_name": "Styling",
    "options": [
      {
        "key": "hide-webrtc-indicator",
        "js_key": "hideWebrtcIndicator",
        "summary": "Hide Privacy Indicators",
        "description": "Hide microphone, screen share, and camera indicators. GNOME provides privacy warnings in the top bar."
      },
      {
        "key": "oled-black",
        "js_key": "oledBlack",
        "summary": "True Black Dark Theme",
        "description": "Change dark theme into an OLED black variant"
      },
      {
        "key": "no-themed-icons",
        "js_key": "noThemedIcons",
        "summary": "No Themed Icons",
        "description": "Use standard Firefox icons instead of Adwaita-styled icons"
      }
    ]
  }

]

FIREFOX_COLORS = [
    "Adwaita",
    "Maia"
]
