# Lint Flatpak Manifest

# FIXME set unnecessary libportal build options to false

flatpak = find_program('flatpak', required: false)

# Docs: https://docs.flathub.org/docs/for-app-authors/linter
manifest = files('dev.qwery.AddWater.Devel.json')[0]
lint_command = ['run', '--command=flatpak-builder-lint', 'org.flatpak.Builder',
		'--exceptions', '--appid', 'dev.qwery.AddWater',
		'manifest', manifest]

# If we're in a flatpak, we need to use this instead
if not flatpak.found()
	flatpak = find_program('flatpak-spawn', required: true)
	lint_command = ['--host', 'flatpak'] + lint_command
endif

test('Lint Flatpak manifest',
	flatpak,
	args: lint_command,
	is_parallel: true
)
