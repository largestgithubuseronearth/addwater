# Add Water
### An Installer for the fantastic GNOME for Firefox theme by Rafael Mardojai (link)

## PRIMARY GOALS:
* Give app functionality to run at startup, in the background, and check for + install updates automatically
    * Is the manifest import okay? I copied from AdwSteamGtk 
* Pref: Allow user to choose a specific path from the list of commons ones, or auto to let me figure it out
* Make unit tests for app, especially in sections where data loss could occur
* Find a good formatting solution
    * Pylint
    * Black 
* Make Github issue template


## FLATHUB GOALS:
* Flatpak: Make sure Flatpak is configured properly
    * Ensure flatpak manifest permissions are correct
    * Allow permission to run in background to permissions
    * Is is okay to remove ipc permission? Doesn't seem necessary but idk.
    * Where does $FLATPAK_DEST go to?
* Write .desktop file
* Write appstream info
* Smooth out all accessibility issues


## Wrap up
* Make docstrings for the classes and methods
* Write help page for user troubleshooting


### Accessibility:
[X] Large Text
[~] Screen Reader.
    Could find everything except:
    * Can't find label for the bottom action bar
    * Some subtitles are not read aloud. Orca bug?
    * Toasts are not read out
[X] Full keyboard navigation
[X] Contrast
[] Touch screen support
[] Accerciser test (need to resolve imp issue; dnf has old version?)


### What needs to happen for Thunderbird support:
* Be able to clone the git repo in Python and self-set rate limits to avoid clogging Github after every minor change
* Set up AddWaterPage to work with both Firefox and Thunderbird


### Other Notes:
* I will not support Experimental options. Users must enable those manually.


