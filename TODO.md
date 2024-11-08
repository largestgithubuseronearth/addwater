## Front-facing improvements:
* Change backends list to a dict or have some way to identify what app each backend goes to
* Dialog prompt for user to select which package to install to when multiple package formats are detected simultaneously
* When user changes Package in prefs, refresh the interface automatically to apply to the new paths.
* Add a "Restart Firefox" button to install and uninstall toasts

## Under-the-hood Improvements:

 * Find a documentation solution
    * doxygen
    * sphinx
    * read the docs
 * Add more docstrings 
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
