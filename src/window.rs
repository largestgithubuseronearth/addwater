/* window.rs
 *
 * Copyright 2025 Claire
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

use adw::subclass::prelude::*;
use gtk::prelude::*;
use gtk::{gio, glib};

use crate::pages::WaterFirefoxPage;

mod imp {
    use super::*;

    #[derive(Debug, Default, gtk::CompositeTemplate)]
    #[template(resource = "/dev/qwery/AddWater/window.ui")]
    pub struct WaterWindow {}

    #[glib::object_subclass]
    impl ObjectSubclass for WaterWindow {
        const NAME: &'static str = "WaterWindow";
        type Type = super::WaterWindow;
        type ParentType = adw::ApplicationWindow;

        fn class_init(klass: &mut Self::Class) {
            klass.bind_template();

            WaterFirefoxPage::ensure_type();
        }

        fn instance_init(obj: &glib::subclass::InitializingObject<Self>) {
            obj.init_template();
        }
    }

    impl ObjectImpl for WaterWindow {}
    impl WidgetImpl for WaterWindow {}
    impl WindowImpl for WaterWindow {}
    impl ApplicationWindowImpl for WaterWindow {}
    impl AdwApplicationWindowImpl for WaterWindow {}
}

glib::wrapper! {
    pub struct WaterWindow(ObjectSubclass<imp::WaterWindow>)
        @extends gtk::Widget, gtk::Window, gtk::ApplicationWindow, adw::ApplicationWindow,
        @implements gio::ActionGroup, gio::ActionMap;
}

impl WaterWindow {
    pub fn new<P: IsA<gtk::Application>>(application: &P) -> Self {
        glib::Object::builder()
            .property("application", application)
            .build()
    }
}
