## PRIMARY GOALS:
* Find a good auto linter/formatter
    * Pylint
    * Black 
* Improve implementation of AppDetails and/or make a generic factory for this
* Create install and online manager factories that take AppDetails as input. When something in appdetails changes, it will remake those factories with the new details they need
* Improve logging
* Move to Adw 1.6 🥹
* Add some sort of verification method to check that the installation was successful, and the files now exist in the profile directory.


## SECONDARY GOALS:
* Find good documentation solution
    * doxygen
    * sphinx
    * read the docs
* Change all type hints to use pathlike when needed
* Set up unit testing in meson. This is surprisingly difficult.
* Consider possibility of a "Restart Firefox" button
* Is there a built-in GTK logging tool? How do cartridges and others do the debugging page?

## FLATHUB GOALS:
* Make sure Flatpak is configured properly
    * Ensure flatpak manifest permissions are correct
* Write .desktop file
* Write appstream info
    * Finish preview images to look nicer
* Create app icon & brand colors
* Smooth out all accessibility issues


## Wrap up
* Set up project for i18n work
* Write better docstrings for the classes and methods
* Write help page for user troubleshooting


## Accessibility Test Results:

Note: Try all of these on Gnome 47 since Orca was improved

[/] Large Text
[~] Screen Reader tests
    * When selecting a row, it wouldn't say the control type for my custom switch rows or the state of the switch. Doesn't notify when you change activate the switch from here.
    * Wouldn't mention the info button exists.
    * The info button's popover label isn't read
    * Label for Changes Bottom Bar isn't read
    The GNOME settings page I took these styles from also has these same issues. Any fix?
[/] Full keyboard navigation
    * Must press esc to exit info button
[/] Contrast
[] Touch screen support. Can't test this myself.
[] Accerciser test (need to resolve imp issue)

