# build-aux/

# FIXME add test for flatpak builder manifest linter

manifest_user = 'dev.qwery.AddWater.json'

flatpakcli = find_program('flatpak', required: true, disabler: true)
test('Validate Flatpak manifest',
	flatpakcli,
	args: ['run', '--command=flatpak-builder-lint', 'org.flatpak.Builder', 'manifest', manifest_user]
)