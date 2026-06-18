use adw::subclass::prelude::*;
use gtk::prelude::*;
use gtk::{gio, glib};

use crate::{
    model::{PackageFormat, WaterProfile},
    widgets::WaterBoolRow,
};

mod imp {
    use super::*;

    #[derive(Default, Debug, gtk::CompositeTemplate)]
    #[template(resource = "/dev/qwery/AddWater/widgets/profile_selector.ui")]
    pub struct WaterProfileSelector {
        #[template_child]
        pub(super) profile_model: TemplateChild<gio::ListStore>,
        #[template_child]
        pub(super) sorter: TemplateChild<gtk::CustomSorter>,
        #[template_child]
        pub(super) section_sorter: TemplateChild<gtk::CustomSorter>,
    }

    #[glib::object_subclass]
    impl ObjectSubclass for WaterProfileSelector {
        const NAME: &'static str = "WaterProfileSelector";
        type Type = super::WaterProfileSelector;
        type ParentType = adw::ComboRow;

        fn class_init(klass: &mut Self::Class) {
            klass.bind_template()
        }

        fn instance_init(obj: &glib::subclass::InitializingObject<Self>) {
            obj.init_template();
        }
    }

    impl ObjectImpl for WaterProfileSelector {
        fn constructed(&self) {
            use std::cmp::Ordering;

            self.parent_constructed();

            // Sort by favorited, then alphabetically
            self.sorter.set_sort_func(move |a, b| {
                let a = a
                    .downcast_ref::<WaterProfile>()
                    .expect("this must be a profile");
                let b = b
                    .downcast_ref::<WaterProfile>()
                    .expect("this must be a profile");

                let order = b.favorite().cmp(&a.favorite());
                if order == Ordering::Equal {
                    a.name().cmp(&b.name()).into()
                } else {
                    order.into()
                }
            });

            // Group by package format
            self.section_sorter.set_sort_func(move |a, b| {
                let a = a
                    .downcast_ref::<WaterProfile>()
                    .expect("this must be a profile")
                    .package_format() as u32;
                let b = b
                    .downcast_ref::<WaterProfile>()
                    .expect("this must be a profile")
                    .package_format() as u32;

                a.cmp(&b).into()
            });

            // TODO temp values
            let tempprofs = vec![
                WaterProfile::new("bark", "1", false, None, PackageFormat::Firefox),
                WaterProfile::new("awiooo", "1", true, None, PackageFormat::Firefox),
                WaterProfile::new("5isrky", "1", false, None, PackageFormat::FirefoxFlatpak),
                WaterProfile::new(
                    "wjfnfyhjmn",
                    "1",
                    false,
                    None,
                    PackageFormat::FirefoxFlatpak,
                ),
                WaterProfile::new("pewgno", "1", true, None, PackageFormat::Librewolf),
                WaterProfile::new("zubufb", "1", true, None, PackageFormat::CachyOS),
                WaterProfile::new("gubbb", "1", false, None, PackageFormat::Firefox),
                WaterProfile::new("lasdiojf", "1", false, None, PackageFormat::CachyOS),
            ];

            self.profile_model.extend_from_slice(&tempprofs);
        }
    }
    impl WidgetImpl for WaterProfileSelector {}
    impl ListBoxRowImpl for WaterProfileSelector {}
    impl PreferencesRowImpl for WaterProfileSelector {}
    impl ActionRowImpl for WaterProfileSelector {}
    impl ComboRowImpl for WaterProfileSelector {}
}

glib::wrapper! {
    pub struct WaterProfileSelector(ObjectSubclass<imp::WaterProfileSelector>)
        @extends gtk::Widget, gtk::ListBoxRow, adw::PreferencesRow, adw::ActionRow, adw::ComboRow,
        @implements gtk::Accessible, gtk::Actionable, gtk::Buildable, gtk::ConstraintTarget;
}
