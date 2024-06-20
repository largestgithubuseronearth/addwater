# logs.py

import logging
import os.path
from gi.repository import Gtk, Adw
from . import paths

log = logging.getLogger(__name__)
# TODO include datetime into logs
def init_logs():
    try:
        LOGFILE = os.path.join(paths.LOG_DIR, "add-water.log")
        logging.basicConfig(filename=LOGFILE,
                            filemode="w",
                            level=logging.DEBUG)
    except:
        print("Couldn't initialize log file")


    # TODO remove the oldest logs after ten-ish logs




    # TODO Add to top of log file information about system and dependencies such as:
    # distro
    # time that the app was started
    # desktop environment
    # flatpak or not?
    info = f"""System Info:
    Add Water — An installer for the GNOME theme for Firefox and Thunderbird
    GTK version: {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}
    ADW version: {Adw.MAJOR_VERSION}.{Adw.MINOR_VERSION}.{Adw.MICRO_VERSION}
    -------------------------------------------------------------------
    """
    log.debug(info)




