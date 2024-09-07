## PRIMARY GOALS:
* Find a good auto linter/formatter
    * Pylint
    * Black 
* Improve implementation of AppDetails and/or make a generic factory for this
* Set up workflow actions to easily separate dev and user builds
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
* Consider possibility of a "Restart Firefox" button
* Is there a built-in GTK logging tool? How do cartridges and others do the debugging page?

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
[/] Large Text
[~] Screen Reader tests
    * When selecting a row, it wouldn't say the control type for my custom switch rows or the state of the switch. Doesn't notify when you change activate the switch from here.
    * Wouldn't mention the info button exists.
    * The info button's popover label isn't read
    * Label for Changes Bottom Bar isn't read
    The GNOME settings page I took these styles from also has these same issues. Any fix?
[/] Full keyboard navigation
    * Must press esc to exist info button
[/] Contrast
[] Touch screen support. Can't test this myself.
[] Accerciser test (need to resolve imp issue)


### What needs to happen for Thunderbird support:
* Be able to clone the Github repo in Python easily OR dev finishes it and makes actual releases
    * Set up self-restricting limits and timings on when to clone to avoid Github api ratelimits
* Make another pass through all modules to ensure they can support multiple pages and backends at a single time
* Set up Thunderbird AppDetails(paths, options, url, etc)
* Set up Thunderbird GSettings schema and keys 
