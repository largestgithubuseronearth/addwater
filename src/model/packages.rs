use std::{
    fmt::Display,
    path::{Path, PathBuf},
};

#[repr(u32)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum PackageFormat {
    Firefox,
    FirefoxFlatpak,
    FirefoxSnap,
    Librewolf,
    LibrewolfFlatpak,
    Floorp,
    FloorpFlatpak,
    Waterfox,
    WaterfoxFlatpak,
    CachyOS,
}

impl Default for PackageFormat {
    fn default() -> Self {
        Self::Firefox
    }
}

// These shouldn't be translated since they're brand names
impl Display for PackageFormat {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let name: &str = match self {
            Self::Firefox => "Firefox",
            Self::FirefoxFlatpak => "Firefox: Flatpak",
            Self::FirefoxSnap => "Firefox: Snap",
            Self::Librewolf => "Librewolf",
            Self::LibrewolfFlatpak => "Librewolf: Flatpak",
            Self::Floorp => "Floorp",
            Self::FloorpFlatpak => "Floorp: Flatpak",
            Self::Waterfox => "Waterfox",
            Self::WaterfoxFlatpak => "Waterfox: Flatpak",
            Self::CachyOS => "CachyOS Browser",
        };

        write!(f, "{name}")
    }
}

impl From<PackageFormat> for PathBuf {
    fn from(value: PackageFormat) -> Self {
        use PackageFormat::*;
        let path: &str = match value {
            Firefox => "~/.mozilla/firefox/",
            FirefoxFlatpak => "~/.var/app/org.mozilla.firefox/.mozilla/firefox/",
            FirefoxSnap => "~/snap/firefox/common/.mozilla/firefox/",
            Librewolf => "~/.librewolf/",
            LibrewolfFlatpak => "~/.var/app/io.gitlab.librewolf-community/.librewolf/",
            Floorp => "~/.floorp/",
            FloorpFlatpak => "~/.var/app/one.ablaze.floorp/.floorp/",
            Waterfox => "~/.waterfox/",
            WaterfoxFlatpak => "~/.var/app/net.waterfox.waterfox/.waterfox/",
            CachyOS => "~/.cachy/",
        };

        Self::from(path)
    }
}
