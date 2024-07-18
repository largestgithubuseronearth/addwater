# TODO is there a simpler way to do this? .in files?

FIREFOX_OPTIONS = [
    {
    "group_name": "Tab Position",
    "options": [
          {
            "key": "hide-single-tab",
            "js_key": "hideSingleTab",
            "summary": "Hide Single Tab",
            "description": "Hide the tab bar when only one tab is open"
          },
          {
            "key": "normal-width-tabs",
            "js_key": "normalWidthTabs",
            "summary": "Normal Width Tabs",
            "description": "Use the same tab width as default Firefox"
          },
          {
            "key": "swap-tab-close",
            "js_key": "swapTabClose",
            "summary": "Swap Tab Close Button",
            "description": "Prevent Tab Close button from following the position of the window controls"
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
            "description": "Place the tabs on the top of the window, and use the tabs bar to hold the window controls, like Firefox's standard tab bar.\n\nEnabling with \"Hide Single Tab\" will replace the single tab with a title bar"
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
            "description": "Add more contrast to the active tab"
          },
          {
            "key": "close-only-selected-tabs",
            "js_key": "closeOnlySelectedTabs",
            "summary": "Close Only Selected Tabs",
            "description": "Only show the close button on the selected tab"
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
        "summary": "Hide WebRTC Indicator",
        "description": "Hide redundant WebRTC indicator since GNOME provides their own privacy icons in the top right"
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
        "description": "Use default Firefox icons instead of the included Adwaita icons."
      }
    ]
  }

]

# TODO add thunderbird options
THUNDERBIRD_OPTIONS = [
    {
        "group_name": "Tab Position and Behavior",
        "options": [
            {
            "key": "hide-tabbar",
            "js_key": "hideTabbar",
            "summary": "Hide Tab Bar",
            # TODO fix this description
            "description": "Hides tabs and menu bar. Press Alt to present the tab bar or by enabling the menu bar."
            },
            {
            "key": "normal-width-tabs",
            "js_key": "normalWidthTabs",
            "summary": "Normal Width Tabs",
            "description": "Use the same tab width as default Firefox"
            },
            {
            "key": "active-tab-contrast",
            "js_key": "activeTabContrast",
            "summary": "Active Tab Contrast",
            "description": "Add more contrast to the active tab"
            }
        ]
    }

]
