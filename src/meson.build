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

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
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
install_subdir('pages', install_dir: moduledir)

addwater_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'pages/thunderbird_page.py'
]

install_data(addwater_sources, install_dir: moduledir)
