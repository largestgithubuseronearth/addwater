# data/icons/

# application_id = 'dev.qwery.AddWater'
application_id = app_id

scalable_dir = 'hicolor' / 'scalable' / 'apps'
install_data(
  scalable_dir / ('@0@.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

# Need to override here bc I don't have a "devel" variant of the symbolic icon.
application_id = 'dev.qwery.AddWater'
symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
install_data(
  symbolic_dir / ('@0@-symbolic.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir / 'apps'
)
