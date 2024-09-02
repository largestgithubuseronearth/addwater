# Add Water
### An installer for the fantastic GNOME for Firefox theme by [Rafael Mardojai CM](https://github.com/rafaelmardojai/firefox-gnome-theme)

## PRIMARY GOALS:
* Give app functionality to run at startup, in the background, and check for + install updates automatically
* Find a good auto linter/formatter
    * Pylint
    * Black 
* Improve implementation of AppDetails and make a generic factory for this
* Properly set up Meson
    * Set up options to enable mocks and easy tests, but disable ALL of these when profile == user
        * Integrate these in the real code cleaner. Like with the force_bg and use_api 
    * Set up properly use my basic unit tests. Kept hitting an error


## SECONDARY GOALS:
* Find good documentation solution
    * doxygen
    * sphinx
    * read the docs
* Change all type hints to use pathlike when needed

## FLATHUB GOALS:
* Make sure Flatpak is configured properly
    * Ensure flatpak manifest permissions are correct
    * Give permission to run in background at login time
    * Where does $FLATPAK_DEST go to?
    * Is the libportal manifest import okay? I copied from AdwSteamGtk 
* Write .desktop file
* Write appstream info
    * Finish preview images to look nicer
* Smooth out all accessibility issues


## Wrap up
* Set up project for i18n work
* Write better docstrings for the classes and methods
* Write help page for user troubleshooting


## Accessibility Test Results:
<!-- TODO redo these tests! -->
[X] Large Text
[~] Screen Reader tests
    Could find everything except:
    * Can't find label for the bottom action bar
    * Some SwitchRow subtitles are not read aloud. Orca bug?
    * Toasts are not read out
[X] Full keyboard navigation
[X] Contrast
[] Touch screen support
[] Accerciser test (need to resolve imp issue)


### What needs to happen for Thunderbird support:
* Be able to clone the Github repo in Python easily
* Set up self-restricting limits and timings on when to clone to avoid Github api ratelimits
* Make another pass through all modules to ensure they can support multiple pages and backends at a single time
* Set up Thunderbird AppDetails(paths, options, url, etc)
* Set up Thunderbird GSettings schema and keys 


### Other Notes:
* I will not support Experimental options at this time. Users must enable those manually.

