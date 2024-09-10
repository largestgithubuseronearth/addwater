# tests/

moduledir = pkgdatadir / 'tests'

test_sources = [
	'__init__.py',

	'test_page.py',
	'test_online_manager.py',
	'test_install_manager.py',
	'test_backend.py'
]

install_data(test_sources, install_dir: moduledir)

# FIXME no module named pytest
# interpreter = python.find_installation('python3')
# test('Test Online Provider', interpreter, args: ['-m', 'pytest', 'tests'])