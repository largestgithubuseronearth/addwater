# src/

moduledir = pkgdatadir / 'addwater'

configure_file(
	input: 'addwater.in',
	output: 'addwater',
	configuration: conf,
	install: true,
	install_dir: get_option('bindir'),
	install_mode: 'r-xr-xr-x'
)

install_subdir('apps', install_dir: moduledir)
install_subdir('components', install_dir: moduledir)
install_subdir('utils', install_dir: moduledir)
install_subdir('gui', install_dir: moduledir)

addwater_sources = [
	'__init__.py',
	'main.py',
	'window.py',
	'preferences.py',
	'page.py',
	'backend.py',

	'apps/firefox/firefox_install.py',
	'apps/firefox/firefox_details.py',
	'apps/firefox/firefox_options.py',
	'apps/firefox/firefox_paths.py',

	'components/install.py',
	'components/online.py',

	'gui/option_factory.py',

	'utils/paths.py',
	'utils/logs.py',
	'utils/background.py',
	'utils/versioning.py',

	configure_file(input: 'info.py.in', output: 'info.py', configuration: conf),
]
install_data(addwater_sources, install_dir: moduledir)