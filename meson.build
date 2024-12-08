project('addwater',
	version: '1.2',
	meson_version: '>= 1.1',
	default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

# Get profile and if user release, disable ALL testing options
profile = get_option('profile')
if profile == 'user'
	app_id = 'dev.qwery.AddWater'
	prefix = '/dev/qwery/AddWater'
	mock_api = false
	force_bg = false
elif profile =='developer'
	app_id = 'dev.qwery.AddWater.Devel'
	prefix = '/dev/qwery/AddWater/Devel'
	mock_api = get_option('use-mock-api')
	force_bg = get_option('force-background')
endif


conf = configuration_data({
	'PYTHON' : python.find_installation('python3').full_path(),
	'VERSION' : meson.project_version(),
	'APP_ID' : app_id,
	'PREFIX' : prefix,
	'PROFILE': profile,
	'localedir' : get_option('prefix') / get_option('localedir'),
	'pkgdatadir': pkgdatadir
})
conf.set('MOCK_API', mock_api)
conf.set('FORCE_BG', force_bg)


subdir('data')
subdir('po')
subdir('src')
# subdir('build-aux')



gnome.post_install(
	glib_compile_schemas: true,
	gtk_update_icon_cache: true,
	update_desktop_database: true,
)
