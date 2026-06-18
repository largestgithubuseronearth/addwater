/// This class is responsible for keeping the user.js file open and writing in the user prefs on the fly
/// when a user changes a choice switch in the UI
use adw::subclass::prelude::*;
use glib::{clone, Properties};
use gtk::prelude::*;
use gtk::{gio, glib};

use std::cell::{Cell, RefCell};

use crate::{
    model::{PackageFormat, WaterProfile},
    widgets::WaterBoolRow,
};

mod imp {
    use super::*;

    #[derive(Default, Debug)]
    pub struct WaterOptionTracker {
        pub(super) children: RefCell<Vec<WaterBoolRow>>,
    }

    #[glib::object_subclass]
    impl ObjectSubclass for WaterOptionTracker {
        const NAME: &'static str = "WaterOptionTracker";
        type Type = super::WaterOptionTracker;
    }

    impl ObjectImpl for WaterOptionTracker {}
}

glib::wrapper! {
    /// Tracks preferences in the user.js file for the selected profile and automatically
    /// updates them when they're changed in the Add Water GUI.
    pub struct WaterOptionTracker(ObjectSubclass<imp::WaterOptionTracker>);
}
