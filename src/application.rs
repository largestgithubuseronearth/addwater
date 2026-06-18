/* application.rs
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

use adw::prelude::*;
use adw::subclass::prelude::*;
use gettextrs::gettext;
use gtk::{gio, glib};

use crate::config::{APP_ID, PROFILE, VERSION};
use crate::WaterWindow;

mod imp {
    use super::*;

    #[derive(Debug, Default)]
    pub struct WaterApplication {}

    #[glib::object_subclass]
    impl ObjectSubclass for WaterApplication {
        const NAME: &'static str = "WaterApplication";
        type Type = super::WaterApplication;
        type ParentType = adw::Application;
    }

    impl ObjectImpl for WaterApplication {
        fn constructed(&self) {
            self.parent_constructed();
            let obj = self.obj();
            obj.setup_gactions();
            obj.set_accels_for_action("app.quit", &["<primary>q"]);
            obj.set_accels_for_action("app.preferences", &["<primary>comma"]);
        }
    }

    impl ApplicationImpl for WaterApplication {
        // We connect to the activate callback to create a window when the application
        // has been launched. Additionally, this callback notifies us when the user
        // tries to launch a "second instance" of the application. When they try
        // to do that, we'll just present any existing window.
        fn activate(&self) {
            let application = self.obj();
            // Get the current window or create one if necessary
            let window = application
                .active_window()
                .unwrap_or(WaterWindow::new(&*application).upcast());

            if PROFILE == "development" {
                window.add_css_class("devel");
            }

            // Ask the window manager/compositor to present the window
            window.present();
        }
    }

    impl GtkApplicationImpl for WaterApplication {}
    impl AdwApplicationImpl for WaterApplication {}
}

glib::wrapper! {
    pub struct WaterApplication(ObjectSubclass<imp::WaterApplication>)
        @extends gio::Application, gtk::Application, adw::Application,
        @implements gio::ActionGroup, gio::ActionMap;
}

impl Default for WaterApplication {
    fn default() -> Self {
        glib::Object::builder()
            .property("application-id", APP_ID)
            .property("flags", gio::ApplicationFlags::empty())
            .property("resource-base-path", "/dev/qwery/AddWater")
            .build()
    }
}

impl WaterApplication {
    fn setup_gactions(&self) {
        let quit_action = gio::ActionEntry::builder("quit")
            .activate(move |app: &Self, _, _| app.quit())
            .build();
        let about_action = gio::ActionEntry::builder("about")
            .activate(move |app: &Self, _, _| app.show_about())
            .build();
        let pref_action = gio::ActionEntry::builder("preferences")
            .activate(move |app: &Self, _, _| app.show_prefs())
            .build();
        self.add_action_entries([quit_action, about_action, pref_action]);
    }

    fn show_prefs(&self) {
        // TODO make pref dialog
        println!("hi");
    }

    fn show_about(&self) {
        let window = self.active_window().unwrap();
        let about = adw::AboutDialog::builder()
            .application_name("Add Water")
            .application_icon(APP_ID)
            .developer_name("Claire")
            .version(VERSION)
            .developers(vec!["Claire"])
            // Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
            .translator_credits(gettext("translator-credits"))
            .copyright("© 2025 Claire")
            .build();

        about.present(Some(&window));
    }
}
