I'm sorry you're having issues with Add Water (AW from here on). Here you can find some potential advice for your issue in case I'm not around to help.

If your issue isn't resolved by these steps, please [open an issue on GitHub](https://github.com/largestgithubuseronearth/addwater/issues/new/choose).

## When asking for help, please bring the log file
If you don't know what the cause might be, AW stores logs of its behavior that you can reference and attach to your GitHub issue. You can find the logs by clicking on [About Add Water > Troubleshooting > Debugging Information > Save As...].

When creating a GitHub issue, those who bring the relevant log file will probably get their issue resolved much faster than those who don't.

## General advice
1. _My `user.js` configs/hardening are no longer applied to my profile._
If you had a custom `user.js` file in your profile, AW has renamed it to `user.js.bak` at the time of installation to avoid overwriting it. Simply remove the `.bak` suffix from the filename and it'll work like normal. 

You can also move your custom changes into the new file but be aware that this may lead to undefined behavior and issues that you need to resolve on your own. Only the `user.js` template provided is supported but AW was built to avoid overwriting your custom one. If you ever find that it has, open an issue on GitHub.


# Troubleshooting
The two common points of failure are with the code sections that manage online connections and manage installing the theme files to your profile since there's so many edge cases I can't reasonably account for.

When errors occur, AW will show a popup notification at the bottom of the window that should clue you in to whether the issue stems from an internet or installation error.

## Online issues
1. _Make sure AW has internet access._

Make sure you're connected to the internet at least once while using AW so it can download the necessary files. Additionally, make sure it has the Network permission enabled.


2. _Make sure you're not rate-limited_

GitHub has a limit on how many requests you can send per hour. AW will warn you when you're being rate-limited when the app launches. This is unlikely to occur because AW can only send a maximum of three requests in a single session. It isn't impossible though; extenuating circumstances like a script, or a user opening and closing the app very often could trigger this.

Ultimately the solution is to let it rest for a few hours. If you continue to spam while rate-limited, GitHub may ban your IP, and I bear no responsibility for that. A good-faith user of AW will never come anywhere close to that limit.

## Install issues
1. _Make sure AW is set to use the correct package of Firefox_

If you have multiple packages (Flatpak, Snap, binaries, etc.) of Firefox installed, make sure you've selected the correct one in the "Packages Format" menu on the front page.

Every package format of Firefox stores its profile data in a different directory, and if you have multiple package types installed simultaneously then AW may have been installing the theme files to the wrong one.

2. _Make sure AW has permission to access your profile files_

AW needs read and write permissions to your Firefox data folder to be able to apply the theme files — this is the folder which includes all your profiles and the `profiles.ini` file. AW is pre-configured to have the minimum amount of permissions but still have access to the most common data paths out-of-the-box.

If you've changed your Flatpak permissions for AW, you may have removed the path from the permissions and will need to re-add it with a tool like [Flatseal](https://flathub.org/apps/com.github.tchx84.Flatseal). Click reset in top right-hand corner and it will store all necessary file permissions.



# Conclusion
If you didn't find a solution to your problem, please [open an issue on GitHub](https://github.com/largestgithubuseronearth/addwater/issues/new/choose) and I will respond as soon as possible.

If applicable, please bring the log file from the day the issue occurred as I noted earlier.


Thank you for your time and patience. I hope that, despite of your issues, Add Water has been helpful for you.
