project('addwater',
	version: '1.3',
	meson_version: '>= 1.4.0',
  default_options: ['warning_level=2', 'werror=true',
                    'buildtype=debugoptimized', 'python.install_env=auto'],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python').find_installation('python3',
  modules: [
    'packaging',
    'requests',
  ]
)

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

app_id = 'dev.qwery.AddWater'
if get_option('profile') == 'development'
	app_id = app_id + '.Devel'
endif


conf = configuration_data({
	'PYTHON'    : python.full_path(),
	'VERSION'   : meson.project_version(),
	'APP_ID'    : app_id,
	'PREFIX'    : '/dev/qwery/AddWater',
	'PROFILE'   : get_option('profile'),
	'localedir' : get_option('prefix') / get_option('localedir'),
	'pkgdatadir': pkgdatadir
})

dependency('gtk4',           version: '>=4.22')
dependency('libadwaita-1',   version: '>=1.9.0')
dependency('libportal',      version: '>=0.9.1',
           default_options: ['backend-gtk4=enabled',
                             'backend-gtk3=disabled',
                             'backend-qt5=disabled',
                             'backend-qt6=disabled',
                             'vapi=false',
                             'introspection=true',
                             'werror=false'])
dependency('libportal-gtk4', version: '>=0.9.1')

subdir('data')
subdir('po')
subdir('src')

if get_option('tests')
	subdir('build-aux')
  subdir('tests')
endif

gnome.post_install(
	glib_compile_schemas: true,
	gtk_update_icon_cache: true,
	update_desktop_database: true,
)
