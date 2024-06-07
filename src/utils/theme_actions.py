# theme_actions.py

def install_firefox_theme(firefox_path):
    if type(firefox_path) not str or not in list:
        return Error

    # TODO prep installation cli command [firefox path] [profile] [theme]. How to do commands in python?

def uninstall_firefox_theme(firefox_path):
    # TODO delete chrome folder
    # TODO remove all prefs in user.js or set all that begin with "gnomeTheme." to false
