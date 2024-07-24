# logs.py

import logging
from datetime import datetime, timezone, timedelta
import os, os.path
from gi.repository import Gtk, Adw
from . import paths

log = logging.getLogger(__name__)
def init_logs():
    LOG_DIR = paths.LOG_DIR
    try:
        # TODO consider making the file append per day and show time in the log messages
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
        LOGFILE = os.path.join(LOG_DIR, f"addwater_{now}.log")
        logging.basicConfig(filename=LOGFILE,
                            filemode="w",
                            style="{",
                            format="[{levelname}] {name} — {message} {asctime}",
                            # TODO make this format so it's easy to read the logs
                            level=logging.DEBUG)
    except:
        print("Couldn't initialize log file")


    # Delete logs that are over two weeks old
    with os.scandir(path=LOG_DIR) as scan:
        oldest = ""
        for each in scan:
            time = datetime.strptime(
                each.name,
                "addwater_%Y-%m-%d_%H-%M.log",
            )
            time = time.replace(tzinfo=timezone.utc)
            difference = datetime.now(timezone.utc) - time
            if difference.days > 14:
                os.remove(os.path.join(LOG_DIR, each.name))
                log.info(each.name, "removed")




    # TODO Add to top of log file information about system and dependencies such as:
    # distro
    # desktop environment
    # flatpak or not?
    info = f"""System Info:
    Add Water — An installer for the GNOME theme for Firefox and Thunderbird
    Time: {datetime.now(timezone.utc)}
    GTK version: {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}
    ADW version: {Adw.MAJOR_VERSION}.{Adw.MINOR_VERSION}.{Adw.MICRO_VERSION}
    -------------------------------------------------------------------
    """
    log.debug(info)




