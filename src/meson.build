pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'addwater'
gnome = import('gnome')

gnome.compile_resources('addwater',
  'addwater.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

# TODO set up app_id and everything else to make it easier
profile = get_option('profile')
if profile == 'user'
	app_id = 'dev.qwery.AddWater'
elif profile =='developer'
	app_id = 'dev.qwery.AddWater.devel'
endif


conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('APP_ID', 'dev.qwery.AddWater')
conf.set('PROFILE', profile)
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'addwater.in',
  output: 'addwater',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)
install_subdir('components', install_dir: moduledir)
install_subdir('utils', install_dir: moduledir)

addwater_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'preferences.py',
  'theme_options.py',
  'page.py',
  'backend.py',

  'components/apps/firefox/firefox_install.py',
  'components/apps/firefox/firefox_details.py',
  # 'components/details.py',
  'components/install.py',
  'components/online.py',

  'utils/paths.py',
  'utils/logs.py',

  configure_file(input: 'info.py.in', output: 'info.py', configuration: conf),
]

install_data(addwater_sources, install_dir: moduledir)
