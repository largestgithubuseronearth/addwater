#![allow(dead_code)]

use adw::subclass::prelude::*;
use glib::Properties;
use gtk::prelude::*;
use gtk::{gio, glib};

use std::{
    cell::{Cell, RefCell},
    path::Path,
};

use super::PackageFormat;

mod imp {
    use super::*;

    #[derive(Debug, Default, Properties)]
    #[properties(wrapper_type = super::WaterProfile)]
    pub struct WaterProfile {
        #[property(get, construct_only)]
        pub(super) name: RefCell<String>,
        #[property(get, construct_only)]
        pub(super) id: RefCell<String>,
        #[property(name = "format-name", type = String, get = Self::format_name)]
        #[property(get, construct_only)]
        pub(super) favorite: Cell<bool>,

        pub(super) format: Cell<PackageFormat>,
        pub(super) filepath: RefCell<Option<Box<Path>>>,
    }

    #[glib::object_subclass]
    impl ObjectSubclass for WaterProfile {
        const NAME: &'static str = "WaterProfile";
        type Type = super::WaterProfile;
    }

    #[glib::derived_properties]
    impl ObjectImpl for WaterProfile {}
    impl WaterProfile {
        pub fn format_name(&self) -> String {
            format!("{}", self.format.get())
        }
    }
}

glib::wrapper! {
    pub struct WaterProfile(ObjectSubclass<imp::WaterProfile>);
}

impl WaterProfile {
    pub fn new(
        name: &str,
        id: &str,
        favorite: bool,
        filepath: Option<Box<Path>>,
        package_format: PackageFormat,
    ) -> Self {
        let this: Self = glib::Object::builder()
            .property("name", name)
            .property("id", id)
            .property("favorite", favorite)
            .build();
        this.imp().filepath.replace(filepath);
        this.imp().format.set(package_format);

        this
    }

    pub fn package_format(&self) -> PackageFormat {
        self.imp().format.get()
    }
}
