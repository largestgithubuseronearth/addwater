use adw::subclass::prelude::*;
use gtk::prelude::*;
use gtk::{gio, glib};

use crate::{
    install::WaterInstaller,
    model::{PackageFormat, WaterProfile},
    widgets::{WaterBoolRow, WaterProfileSelector},
};

use std::cell::RefCell;

mod imp {
    use super::*;

    #[derive(Default, Debug, gtk::CompositeTemplate)]
    #[template(resource = "/dev/qwery/AddWater/pages/firefox.ui")]
    pub struct WaterFirefoxPage {
        pub(super) installer: RefCell<WaterInstaller>,
        
        #[template_child]
        pub(super) enable_toggle: TemplateChild<adw::SwitchRow>,
    }

    #[glib::object_subclass]
    impl ObjectSubclass for WaterFirefoxPage {
        const NAME: &'static str = "WaterFirefoxPage";
        type Type = super::WaterFirefoxPage;
        type ParentType = adw::Bin;

        fn class_init(klass: &mut Self::Class) {
            klass.bind_template();
            WaterProfile::ensure_type();
            WaterProfileSelector::ensure_type();
            WaterBoolRow::ensure_type();
        }

        fn instance_init(obj: &glib::subclass::InitializingObject<Self>) {
            obj.init_template();
        }
    }

    impl ObjectImpl for WaterFirefoxPage {}
    impl WidgetImpl for WaterFirefoxPage {}
    impl BinImpl for WaterFirefoxPage {}
}

glib::wrapper! {
    pub struct WaterFirefoxPage(ObjectSubclass<imp::WaterFirefoxPage>)
        @extends gtk::Widget, adw::Bin,
        @implements gtk::Accessible, gtk::Buildable, gtk::ConstraintTarget;
}
