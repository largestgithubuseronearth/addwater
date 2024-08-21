

class InstallManager():

    install: callable
    set_preferences: callable
    uninstall: callable

    def __init__(self, installer: callable, preference_setter: callable, uninstall: callable)
    pass


    @staticmethod
    def _set_theme_prefs(profile_path: str, options: list[dict], settings) -> None:
        # Set all user.js options according to gsettings
        user_js = join(profile_path, "user.js")
        with open(file=user_js, mode="r", encoding='utf-8') as file:
            lines = file.readlines()

        with open(file=user_js, mode="w", encoding='utf-8') as file:
            for group in options:
                for option in group["options"]:
                    pref_name = f'gnomeTheme.{option["js_key"]}'
                    pref_value = str(settings.get_boolean(option["key"])).lower()
                    full_line = f"""user_pref("{pref_name}", {pref_value});\n"""

                    found = False
                    for i in range(len(lines)):
                        # This is easier than a for-each
                        if pref_name in lines[i]:
                            lines[i] = full_line
                            found = True
                            break
                    if found is False:
                        lines.append(full_line)

            file.writelines(lines)

        log.info("Theme preferences set")


    @staticmethod
    def _do_uninstall_theme(profile_path: str) -> None:
        # Delete theme folder
        try:
            chrome_path = join(profile_path, "chrome", "firefox-gnome-theme")
            shutil.rmtree(chrome_path)
        except FileNotFoundError:
            pass

        # TODO remove css import lines

        # Set all user_prefs to false
        user_js = join(profile_path, "user.js")
        try:
            with open(file=user_js, mode="r", encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            log.info("Theme uninstalled successfully.")
            return

        with open(file=user_js, mode="w", encoding='utf-8') as file:
            # This is easier than a foreach
            for i in range(len(lines)):
                if "gnomeTheme" in lines[i]:
                    lines[i] = lines[i].replace("true", "false")

            file.writelines(lines)

        log.info("Theme uninstalled successfully.")"
