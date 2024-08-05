# addwater

An app to automatically download and update the GNOME style theme for Firefox made by Rafael Mardojai (link).

MINIMUM FEATURES:
* Check for new releases of the firefox theme
* Automatically download the new release and install it
* Let the user uninstall the theme
* Ability to revert to the previous version in case the current one doesn't work

<!-- TODO Configure flatpak manifest properly -->
* Ensure flatpak manifest permissions are correct
* Allow permission to run in background to permissions
* Is is okay to remove ipc permission? Doesn't seem necessary but idk.
* Where does $FLATPAK_DEST go to?

<!-- TODO build preferences window for advanced users -->
* Allow user-specified path for Firefox
* Allow user to remove the theme from all profiles inside their firefox directory

<!-- TODO write .desktop file -->
<!-- TODO Write docstrings for the classes and methods -->
<!-- TODO Write unit tests for the majority of the app, especially critical sections where data loss may occur -->
<!-- TODO consider pylint -->
<!-- TODO format all code -->
<!-- TODO Find workaround for toasts staying on screen -->

<!-- TODO make help page -->


What needs to happen for Thunderbird support:
* Be able to clone the git repo in Python and self-set rate limits to avoid clogging Github after every minor change
* Set up AddWaterPage to work with both Firefox and Thunderbird

Notes:
* I will not support Experimental options. Users must enable those manually.

