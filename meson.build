project('addwater', 'rust', 
          version: '0.1.0',
    meson_version: '>= 1.0.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

profile = get_option('profile')
if profile == 'default'
	app_id = 'dev.qwery.AddWater'
elif profile == 'development'
	app_id = 'dev.qwery.AddWater.Devel'

  # Setup pre-commit hook for ensuring coding style is always consistent
  message('Setting up git pre-commit hook..')
  run_command('cp', '-f', 'hooks/pre-commit.hook', '.git/hooks/pre-commit', check: false)
endif

conf = configuration_data()
conf.set_quoted('APP_ID', app_id)
conf.set_quoted('PROFILE', profile)
conf.set_quoted('VERSION', meson.project_version())
conf.set_quoted('GETTEXT_PACKAGE', 'addwater')
conf.set_quoted('LOCALEDIR', get_option('prefix') / get_option('localedir'))
conf.set_quoted('PKGDATADIR', pkgdatadir)

subdir('data')
subdir('src')
subdir('po')

meson.add_dist_script(
	'build-aux/dist-vendor.sh',
	meson.project_build_root() / 'meson-dist' / meson.project_name() + '-' + meson.project_version(),
	meson.project_source_root()
)

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
