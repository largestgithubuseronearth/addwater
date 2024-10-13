project('addwater',
	version: 'rc1',
	meson_version: '>= 0.62.0',
	default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

# TODO try copying this to make the unit tests package
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
# TODO move these types of testing options into their own dedicated file that doesn't get made if profile == 'user'
# I want to avoid cluttering the code if these options aren't necessary for
# the user but that may not be possible since it would likely break the Python
# code and imports. Any way to disable those errors and just ignore it?
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
