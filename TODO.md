## Front-facing improvements:
* Change backends list to a dict or have some way to identify what app each backend goes to
* Dialog prompt for user to select which package to install to when multiple package formats are detected simultaneously
* When user changes Package in prefs, refresh the interface automatically to apply to the new paths.
* Add a "Restart Firefox" button to install and uninstall toasts

## Under-the-hood Improvements:

 * Create AppDetails factory from which the firefox_details are constructed
 * Set up unit tests (surprisingly complicated)


## Accessibility Test Results:
<!-- TODO Retry all of these on Gnome 47. Orca was improved -->
- [ ] Large text
- [ ] Screen reader
- [ ] Full keyboard navigation
- [ ] Touchscreen support
- [ ] Accerciser test
- [ ] Contrast

## Translation
 - [X] Give translation credit in aboutdialog
 - [ ] Add a full translators list in credits
 - [ ] Make sure all translatables are not using fstrings. Reference Bassi's matrix msg
 - [ ] Reword any awkward descriptions for clarity
 - [ ] Mark all theme options for translation (requires the db rework)
 - [ ] Set up a system for users to easily translate. Weblate or similar platform.
