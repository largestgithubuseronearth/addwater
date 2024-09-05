project('addwater',
	version: 'Pre-Alpha',
	meson_version: '>= 0.62.0',
	default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()


# TODO set up app_id and everything else to make it easier
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


conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('APP_ID', app_id)
conf.set('PREFIX', prefix)

# TODO move these types of testing checks into their own dedicated file that doesn't get made if profile == 'user'
conf.set('MOCK_API', mock_api)
conf.set('FORCE_BG', force_bg)
############################

conf.set('PROFILE', profile)
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)


subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
	glib_compile_schemas: true,
	gtk_update_icon_cache: true,
	update_desktop_database: true,
)
