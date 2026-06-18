use adw::subclass::prelude::*;
use glib::{clone, Properties};
use gtk::prelude::*;
use gtk::{gio, glib};

use std::cell::{Cell, RefCell};

use crate::model::{PackageFormat, WaterProfile};

mod imp {
    use super::*;

    #[derive(Default, Debug, Properties, gtk::CompositeTemplate)]
    #[properties(wrapper_type = super::WaterBoolRow)]
    #[template(resource = "/dev/qwery/AddWater/widgets/bool_row.ui")]
    pub struct WaterBoolRow {
        /// This is the line that gets added & removed from user.js
        #[property(get, construct_only)]
        pub(super) pref_id: RefCell<String>,
        /// Whether the preference is enabled in
        #[property(get, set)]
        pub(super) enabled: Cell<bool>,
        #[property(name = "extra-info-available", type = bool, get = Self::extra_info_available)]
        /// Extra text to show in the info button. If empty, button will be hidden
        #[property(get, set)]
        pub(super) extra_info: RefCell<String>,
    }

    #[glib::object_subclass]
    impl ObjectSubclass for WaterBoolRow {
        const NAME: &'static str = "WaterBoolRow";
        type Type = super::WaterBoolRow;
        type ParentType = adw::ActionRow;

        fn class_init(klass: &mut Self::Class) {
            klass.bind_template();
        }

        fn instance_init(obj: &glib::subclass::InitializingObject<Self>) {
            obj.init_template();
        }
    }

    #[glib::derived_properties]
    impl ObjectImpl for WaterBoolRow {
        fn constructed(&self) {
            self.parent_constructed();

            self.obj().connect_extra_info_notify(clone!(
                #[weak(rename_to = this)]
                self,
                move |_| this.obj().notify_extra_info_available()
            ));
        }
    }
    impl WidgetImpl for WaterBoolRow {}
    impl ListBoxRowImpl for WaterBoolRow {}
    impl PreferencesRowImpl for WaterBoolRow {}
    impl ActionRowImpl for WaterBoolRow {}

    impl WaterBoolRow {
        pub(super) fn extra_info_available(&self) -> bool {
            !self.extra_info.borrow().is_empty()
        }
    }
}

glib::wrapper! {
    pub struct WaterBoolRow(ObjectSubclass<imp::WaterBoolRow>)
        @extends adw::ActionRow, adw::PreferencesRow, gtk::ListBoxRow, gtk::Widget,
        @implements gtk::Accessible, gtk::Actionable, gtk::Buildable, gtk::ConstraintTarget;
}
