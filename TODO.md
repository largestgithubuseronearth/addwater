## Front-facing improvements:

* Dialog prompt for user to select which package to install to when multiple package formats are detected simultaneously
* Add a function to easily get the log files for GitHub issues.
* Add a "Restart Firefox" button to install and uninstall toasts
* Get Flathub verification
* Improve screenshots
* Set up app for i18n work

## Under-the-hood Improvements:

 * Find a documentation solution
    * doxygen
    * sphinx
    * read the docs
 * Add more docstrings 
 * Create AppDetails factory from which the firefox_details are constructed
 * Set up unit tests (surprisingly difficult)


## Accessibility Test Results:
<!-- TODO Retry all of these on Gnome 47 since Orca was improved -->
- [ ] Large text
- [ ] Screen reader
- [ ] Full keyboard navigation
- [ ] Touchscreen support
- [ ] Accerciser test
- [ ] Contrast
