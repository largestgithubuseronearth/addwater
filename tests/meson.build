# TODO setup / teardown data to simulate profiles
# TODO test: background updater
# TODO test: installer
# TODO test: find old profiles
# TODO test: finding new profiles
# TODO test: translations with podebug

configure_file(
  input: 'suite.py.in',
  output: 'suite.py',
  configuration: conf,
)

test_src = [
  '__init__.py',
  'test_paths.py',
]

foreach testfile: test_src
  configure_file(input: testfile, output: testfile, copy: true)
endforeach

test('pytest', find_program('pytest', disabler: true),
     args: [meson.current_build_dir(), '--quiet'])
