# data/icons/

scalable_dir = 'hicolor' / 'scalable' / 'apps'
install_data(
  scalable_dir / ('@0@.svg').format(app_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

# Need to override app_id here bc I don't have a "devel" variant of the symbolic icon.
symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
install_data(
  symbolic_dir / ('@0@-symbolic.svg').format('dev.qwery.AddWater'),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)
