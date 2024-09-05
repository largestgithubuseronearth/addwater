# data/

# Desktop file
desktop_file = i18n.merge_file(
				input: 'dev.qwery.AddWater.desktop.in',
			 output: 'dev.qwery.AddWater.desktop',
				 type: 'desktop',
			 po_dir: '../po',
			install: true,
	install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
	test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

# Appstream
appstream_file = configure_file(
	input: 'dev.qwery.AddWater.metainfo.xml.in',
	output: 'dev.qwery.AddWater.metainfo.xml.in',
	configuration: conf
)
appstream_file = i18n.merge_file(
	input: appstream_file,
	output: app_id + '.metainfo.xml',
	po_dir: '../po',
	install: true,
	install_dir: get_option('datadir') / 'metainfo'
)
appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
	args: ['validate', '--no-net', '--explain', appstream_file])


# GSchema
gschema_file = configure_file(
	input: 'dev.qwery.AddWater.gschema.xml.in',
	output: app_id + '.gschema.xml',
	configuration: conf
)

install_data(gschema_file,
	install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
	compile_schemas,
	args: ['--strict', '--dry-run', meson.current_source_dir()])

subdir('icons')
