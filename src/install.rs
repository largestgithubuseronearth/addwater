use adw::subclass::prelude::*;
use glib::{Properties, clone};
use gtk::prelude::*;
use gtk::{gio, glib};

use std::{
    cell::{RefCell, OnceCell}, 
    path::{PathBuf, Path},
    sync::OnceLock,
    error::Error,
};
use crate::model::WaterProfile;

use git2::Repository;

/// Get the path to the theme repo files, or create the path if necessary.
fn theme_dir() -> &'static PathBuf {
    static THEME_DIR: OnceLock<PathBuf> = OnceLock::new();
    THEME_DIR.get_or_init(|| {
        // TODO remove old cache dir
        xdg::BaseDirectories::new()
            .create_cache_directory("addwater/firefox")
            .expect("xdg-cache should be set and available")
    })
}

const FIREFOX_THEME_URL: &'static str = "https://github.com/rafaelmardojai/firefox-gnome-theme.git";

mod imp {
    use super::*;

    #[derive(Default, Debug, Properties)]
    #[properties(wrapper_type = super::WaterInstaller)]
    pub struct WaterInstaller {
        /// Profile to install theme to
        #[property(get, set, construct)]
        pub(super) profile: RefCell<Option<WaterProfile>>,
    }
    // TODO handle to the file
    // path to git repo

    #[glib::object_subclass]
    impl ObjectSubclass for WaterInstaller {
        const NAME: &'static str = "WaterInstaller";
        type Type = super::WaterInstaller;
    }

    #[glib::derived_properties]
    impl ObjectImpl for WaterInstaller {
        fn constructed(&self) {
            self.parent_constructed();
            
            // TODO remove old dir
            
            // FIXME
            // gio::spawn_blocking(clone!(
            //     #[weak(rename_to = this)] self,
            //     move || {
            //         glib::spawn_future(async {
            //             this.setup_repo().await.unwrap();
            //         });
            //     }
            // ));
        }
    }
    impl WaterInstaller {
        async fn setup_repo(&self) -> Result<Repository, Box<dyn Error>> {
            if let Ok(repo) = Repository::open(theme_dir()) {
                Ok(repo)
            } else {
                // FIXME coerce the errors
                Ok(Repository::clone(FIREFOX_THEME_URL, theme_dir()).unwrap())
            }
            
            
        }
    }
}

glib::wrapper! {
    /// Manages the theme's local Git repo — checking for and downloading updates, and installing to the profile
    pub struct WaterInstaller(ObjectSubclass<imp::WaterInstaller>);
}

// TODO
// list of tags
// pre-defined update strategies (latest, master, etc.)


impl WaterInstaller {
    // TODO
    pub async fn install_theme(&self) -> Result<(), Box<dyn Error>> {
        let profile_path = self.profile().ok_or("no profile set for installer");
        
        
        // TODO copy files from theme_dir to "profile.path / chrome"

        // TODO add import lines to userChrome.css and userContent.css, creating them if necessary

        // TODO create a user.js file if one does not exist
        
        Ok(())
    }
    
    // TODO uninstall theme
}

impl Default for WaterInstaller {
    fn default() -> Self {
        glib::Object::new()
    }
}
