#!/usr/bin/env bash

# This program was originally written for Fractal.
# https://gitlab.gnome.org/World/fractal/-/blob/bca6fd7f67c5bc21d69cabf506ce012676478688/


export LC_ALL=C

# Usage info
show_help() {
cat << EOF
Run conformity checks on the current Rust project.

If a dependency is not found, helps the user to install it.

USAGE: ${0##*/} [OPTIONS]

OPTIONS:
    -s, --git-staged        Only check files staged to be committed
    -f, --force-install     Install missing dependencies without asking
    -v, --verbose           Use verbose output
    -h, --help              Display this help and exit

ERROR CODES:
    1                       Check failed
    2                       Missing dependency
EOF
}

# Style helpers
act="\e[1;32m"
err="\e[1;31m"
pos="\e[32m"
neg="\e[31m"
res="\e[0m"

# Common styled strings
Installing="${act}Installing${res}"
Checking="  ${act}Checking${res}"
Failed="    ${err}Failed${res}"
error="${err}error:${res}"
invalid="${neg}Invalid input${res}"
ok="${pos}ok${res}"
fail="${neg}fail${res}"

# Initialize variables
git_staged=0
force_install=0
verbose=0

# Helper functions
# Sort to_sort in natural order.
sort() {
    local size=${#to_sort[@]}
    local swapped=0;

    for (( i = 0; i < $size-1; i++ ))
    do
        swapped=0
        for ((j = 0; j < $size-1-$i; j++ ))
        do
            if [[ "${to_sort[$j]}" > "${to_sort[$j+1]}" ]]
            then
                temp="${to_sort[$j]}";
                to_sort[$j]="${to_sort[$j+1]}";
                to_sort[$j+1]="$temp";
                swapped=1;
            fi
        done

        if [[ $swapped -eq 0 ]]; then
            break;
        fi
    done
}

# Remove common entries in to_diff1 and to_diff2.
diff() {
    for i in ${!to_diff1[@]}; do
        for j in ${!to_diff2[@]}; do
            if [[ "${to_diff1[$i]}" == "${to_diff2[$j]}" ]]; then
                unset to_diff1[$i]
                unset to_diff2[$j]
                break
            fi
        done
    done
}

# Check if rustup is available.
# Argument:
#   '-i' to install if missing.
check_rustup() {
    if ! which rustup &> /dev/null; then
        if [[ "$1" == '-i' ]]; then
            echo -e "$Installing rustup…"
            curl https://sh.rustup.rs -sSf  | sh -s -- -y --default-toolchain nightly
            export PATH=$PATH:$HOME/.cargo/bin
            if ! which rustup &> /dev/null; then
                echo -e "Could not install rustup"
                exit 2
            fi
        else
            exit 2
        fi
    fi
}

# Install cargo via rustup.
install_cargo() {
    check_rustup -i
    if ! which cargo >/dev/null 2>&1; then
        echo -e "Could not install cargo"
        exit 2
    fi
}

# Check if cargo is available. If not, ask to install it.
check_cargo() {
    if ! which cargo >/dev/null 2>&1; then
        echo "Could not find cargo for pre-commit checks"

        if [[ $force_install -eq 1 ]]; then
            install_cargo
        elif [ ! -t 1 ]; then
            exit 2
        elif check_rustup; then
            echo -e "$error rustup is installed but the cargo command isn't available"
            exit 2
        else
            echo ""
            echo "y: Install cargo via rustup"
            echo "N: Don't install cargo and abort checks"
            echo ""
            while true; do
                echo -n "Install cargo? [y/N]: "; read yn < /dev/tty
                case $yn in
                    [Yy]* )
                        install_cargo
                        break
                        ;;
                    [Nn]* | "" )
                        exit 2
                        ;;
                    * )
                        echo $invalid
                        ;;
                esac
            done
        fi
    fi

    if [[ $verbose -eq 1 ]]; then
        echo ""
        rustc -Vv && cargo +nightly -Vv
    fi
}

# Install rustfmt with rustup.
install_rustfmt() {
    check_rustup -i

    echo -e "$Installing rustfmt…"
    rustup component add --toolchain nightly rustfmt
    if ! cargo +nightly fmt --version >/dev/null 2>&1; then
        echo -e "Could not install rustfmt"
        exit 2
    fi
}

# Run rustfmt to enforce code style.
run_rustfmt() {
    if ! cargo +nightly fmt --version >/dev/null 2>&1; then
        if [[ $force_install -eq 1 ]]; then
            install_rustfmt
        elif [ ! -t 1 ]; then
            echo "Could not check code style, because rustfmt could not be run"
            exit 2
        else
            echo "Rustfmt is needed to check code style, but it isn’t available"
            echo ""
            echo "y: Install rustfmt via rustup"
            echo "N: Don't install rustfmt and abort checks"
            echo ""
            while true; do
                echo -n "Install rustfmt? [y/N]: "; read yn < /dev/tty
                case $yn in
                    [Yy]* )
                        install_rustfmt
                        break
                        ;;
                    [Nn]* | "" )
                        exit 2
                        ;;
                    * )
                        echo $invalid
                        ;;
                esac
            done
        fi
    fi

    echo -e "$Checking code style…"

    if [[ $verbose -eq 1 ]]; then
        echo ""
        cargo +nightly fmt --version
        echo ""
    fi


    if [[ $git_staged -eq 1 ]]; then
        staged_files=`git diff --name-only --cached | xargs ls -d 2>/dev/null | grep '.rs$'`
        result=0
        for file in ${staged_files[@]}; do
            if ! cargo +nightly fmt -- --unstable-features --skip-children --check $file; then
                result=1
            fi
        done

        if [[ $result -eq 1 ]]; then
            echo -e "  Checking code style result: $fail"
            echo "Please fix the above issues, either manually or by running: cargo fmt --all"
            exit 1
        else
            echo -e "  Checking code style result: $ok"
        fi
    else
        if ! cargo +nightly fmt --all -- --check; then
            echo -e "  Checking code style result: $fail"
            echo "Please fix the above issues, either manually or by running: cargo fmt --all"
            exit 1
        else
            echo -e "  Checking code style result: $ok"
        fi
    fi
}


# Install typos with cargo.
install_typos() {
    echo -e "$Installing typos…"
    cargo install typos-cli
    if ! typos --version >/dev/null 2>&1; then
        echo -e "Could not install typos"
        exit 2
    fi
}

# Run typos to check for spelling mistakes.
run_typos() {
    if ! typos --version >/dev/null 2>&1; then
        if [[ $force_install -eq 1 ]]; then
            install_typos
        elif [ ! -t 1 ]; then
            echo "Could not check spelling mistakes, because typos could not be run"
            exit 2
        else
            echo "Typos is needed to check spelling mistakes, but it isn’t available"
            echo ""
            echo "y: Install typos via cargo"
            echo "N: Don't install typos and abort checks"
            echo ""
            while true; do
                echo -n "Install typos? [y/N]: "; read yn < /dev/tty
                case $yn in
                    [Yy]* )
                        install_typos
                        break
                        ;;
                    [Nn]* | "" )
                        exit 2
                        ;;
                    * )
                        echo $invalid
                        ;;
                esac
            done
        fi
    fi

    echo -e "$Checking spelling mistakes…"

    if [[ $verbose -eq 1 ]]; then
        echo ""
        typos --version
        echo ""
    fi

    staged_files=`git diff --name-only --cached | xargs ls -d 2>/dev/null`

    if ! typos --color always ${staged_files}; then
        echo -e "  Checking spelling mistakes result: $fail"
        echo "Please fix the above issues, either manually or by running: typos -w"
        exit 1
    else
        echo -e "  Checking spelling mistakes result: $ok"
    fi
}

# Install machete with cargo.
install_machete() {
    echo -e "$Installing cargo-machete…"
    cargo install cargo-machete
    if ! cargo machete --version>/dev/null 2>&1; then
        echo -e "Could not install cargo-machete"
        exit 2
    fi
}

# Run machete to check for unused dependencies.
run_machete() {
    if ! cargo machete --version >/dev/null 2>&1; then
        if [[ $force_install -eq 1 ]]; then
            install_machete
        elif [ ! -t 1 ]; then
            echo "Could not check for unused dependencies, because cargo-machete could not be run"
            exit 2
        else
            echo "cargo-machete is needed to check for unused dependencies, but it isn’t available"
            echo ""
            echo "y: Install cargo-machete via cargo"
            echo "N: Don't install cargo-machete and abort checks"
            echo ""
            while true; do
                echo -n "Install cargo-machete? [y/N]: "; read yn < /dev/tty
                case $yn in
                    [Yy]* )
                        install_machete
                        break
                        ;;
                    [Nn]* | "" )
                        exit 2
                        ;;
                    * )
                        echo $invalid
                        ;;
                esac
            done
        fi
    fi

    echo -e "$Checking for unused dependencies…"

    if [[ $verbose -eq 1 ]]; then
        echo ""
        cargo machete --version
        echo ""
    fi

    if ! cargo machete --with-metadata; then
        echo -e "  Checking for unused dependencies result: $fail"
        echo "Please fix the above issues, either by removing the dependencies, or by adding the necessary configuration option in Cargo.toml (see cargo-machete documentation)"
        exit 1
    else
        echo -e "  Checking for unused dependencies result: $ok"
    fi
}

# Check if files in POTFILES.in are correct.
#
# This checks, in that order:
#   - All files exist
#   - All files with translatable strings are present and only those
#   - Files are sorted alphabetically
#
# This assumes the following:
#   - POTFILES is located at 'po/POTFILES.in'
#   - UI (Glade) files are located in 'src' and use 'translatable="yes"'
#   - Rust files are located in 'src' and use '*gettext' methods or macros
check_potfiles() {
    echo -e "$Checking po/POTFILES.in…"

    local ret=0

    # Check that files in POTFILES.in exist.
    while read -r line; do
        if [[ -n $line &&  ${line::1} != '#' ]]; then
            if [[ ! -f $line ]]; then
                echo -e "$error File '$line' in POTFILES.in does not exist"
                ret=1
            fi
            if [[ ${line:(-3):3} == '.ui' ]]; then
                ui_potfiles+=($line)
            elif [[ ${line:(-3):3} == '.rs' ]]; then
                rs_potfiles+=($line)
            fi
        fi
    done < po/POTFILES.in

    if [[ ret -eq 1 ]]; then
        echo -e "  Checking po/POTFILES.in result: $fail"
        echo "Please fix the above issues"
        exit 1
    fi

    # Check that files in POTFILES.skip exist.
    while read -r line; do
        if [[ -n $line &&  ${line::1} != '#' ]]; then
            if [[ ! -f $line ]]; then
                echo -e "$error File '$line' in POTFILES.skip does not exist"
                ret=1
            fi
            if [[ ${line:(-3):3} == '.ui' ]]; then
                ui_skip+=($line)
            elif [[ ${line:(-3):3} == '.rs' ]]; then
                rs_skip+=($line)
            fi
        fi
    done < po/POTFILES.skip

    if [[ ret -eq 1 ]]; then
        echo -e "  Checking po/POTFILES.skip result: $fail"
        echo "Please fix the above issues"
        exit 1
    fi

    # Get UI files with 'translatable="yes"'.
    ui_files=(`grep -lIr 'translatable="yes"' src/*`)

    # Get Rust files with regex 'gettext(_f)?\('.
    rs_files=(`grep -lIrE 'gettext(_f)?\(' src/*`)

    # Get Rust files with macros, regex 'gettext!\('.
    rs_macro_files=(`grep -lIrE 'gettext!\(' src/*`)

    # Remove common files
    to_diff1=("${ui_skip[@]}")
    to_diff2=("${ui_files[@]}")
    diff
    ui_skip=("${to_diff1[@]}")
    ui_files=("${to_diff2[@]}")

    to_diff1=("${ui_potfiles[@]}")
    to_diff2=("${ui_files[@]}")
    diff
    ui_potfiles=("${to_diff1[@]}")
    ui_files=("${to_diff2[@]}")

    to_diff1=("${rs_skip[@]}")
    to_diff2=("${rs_files[@]}")
    diff
    rs_skip=("${to_diff1[@]}")
    rs_files=("${to_diff2[@]}")

    to_diff1=("${rs_potfiles[@]}")
    to_diff2=("${rs_files[@]}")
    diff
    rs_potfiles=("${to_diff1[@]}")
    rs_files=("${to_diff2[@]}")

    potfiles_count=$((${#ui_potfiles[@]} + ${#rs_potfiles[@]}))
    if [[ $potfiles_count -eq 1 ]]; then
        echo ""
        echo -e "$error Found 1 file in POTFILES.in without translatable strings:"
        ret=1
    elif [[ $potfiles_count -ne 0 ]]; then
        echo ""
        echo -e "$error Found $potfiles_count files in POTFILES.in without translatable strings:"
        ret=1
    fi
    for file in ${ui_potfiles[@]}; do
        echo $file
    done
    for file in ${rs_potfiles[@]}; do
        echo $file
    done

    let files_count=$((${#ui_files[@]} + ${#rs_files[@]}))
    if [[ $files_count -eq 1 ]]; then
        echo ""
        echo -e "$error Found 1 file with translatable strings not present in POTFILES.in:"
        ret=1
    elif [[ $files_count -ne 0 ]]; then
        echo ""
        echo -e "$error Found $files_count files with translatable strings not present in POTFILES.in:"
        ret=1
    fi
    for file in ${ui_files[@]}; do
        echo $file
    done
    for file in ${rs_files[@]}; do
        echo $file
    done

    let rs_macro_count=$((${#rs_macro_files[@]}))
    if [[ $rs_macro_count -eq 1 ]]; then
        echo ""
        echo -e "$error Found 1 Rust file that uses a gettext-rs macro, use the corresponding i18n method instead:"
        ret=1
    elif [[ $rs_macro_count -ne 0 ]]; then
        echo ""
        echo -e "$error Found $rs_macro_count Rust files that use a gettext-rs macro, use the corresponding i18n method instead:"
        ret=1
    fi
    for file in ${rs_macro_files[@]}; do
        echo $file
    done

    if [[ ret -eq 1 ]]; then
        echo ""
        echo -e "  Checking po/POTFILES.in result: $fail"
        echo "Please fix the above issues"
        exit 1
    fi

    # Check sorted alphabetically
    to_sort=("${potfiles[@]}")
    sort
    for i in ${!potfiles[@]}; do
        if [[ "${potfiles[$i]}" != "${to_sort[$i]}" ]]; then
            echo -e "$error Found file '${potfiles[$i]}' before '${to_sort[$i]}' in POTFILES.in"
            ret=1
            break
        fi
    done

    if [[ ret -eq 1 ]]; then
        echo ""
        echo -e "  Checking po/POTFILES.in result: $fail"
        echo "Please fix the above issues"
        exit 1
    else
        echo -e "  Checking po/POTFILES.in result: $ok"
    fi
}

# Check if files in resource files are sorted alphabetically.
check_resources() {
    echo -e "$Checking $1…"

    local ret=0
    local files=()

    # Get files.
    regex="<file .*>(.*)</file>"
    while read -r line; do
        if [[ $line =~ $regex ]]; then
            files+=("${BASH_REMATCH[1]}")
        fi
    done < $1

    # Check sorted alphabetically
    local to_sort=("${files[@]}")
    sort
    for i in ${!files[@]}; do
        if [[ "${files[$i]}" != "${to_sort[$i]}" ]]; then
            echo -e "$error Found file '${files[$i]#src/}' before '${to_sort[$i]#src/}' in $1"
            ret=1
            break
        fi
    done

    if [[ ret -eq 1 ]]; then
        echo ""
        echo -e "  Checking $1 result: $fail"
        echo "Please fix the above issues"
        exit 1
    else
        echo -e "  Checking $1 result: $ok"
    fi
}

# Install cargo-sort with cargo.
install_cargo_sort() {
    echo -e "$Installing cargo-sort…"
    cargo install cargo-sort
    if ! cargo-sort --version >/dev/null 2>&1; then
        echo -e "Could not install cargo-sort"
        exit 2
    fi
}

# Run cargo-sort to check if Cargo.toml is sorted.
run_cargo_sort() {
    if ! cargo-sort --version >/dev/null 2>&1; then
        if [[ $force_install -eq 1 ]]; then
            install_cargo_sort
        elif [ ! -t 1 ]; then
            echo "Could not check Cargo.toml sorting, because cargo-sort could not be run"
            exit 2
        else
            echo "Cargo-sort is needed to check the sorting in Cargo.toml, but it isn’t available"
            echo ""
            echo "y: Install cargo-sort via cargo"
            echo "N: Don't install cargo-sort and abort checks"
            echo ""
            while true; do
                echo -n "Install cargo-sort? [y/N]: "; read yn < /dev/tty
                case $yn in
                    [Yy]* )
                        install_cargo_sort
                        break
                        ;;
                    [Nn]* | "" )
                        exit 2
                        ;;
                    * )
                        echo $invalid
                        ;;
                esac
            done
        fi
    fi

    echo -e "$Checking Cargo.toml sorting…"

    if [[ $verbose -eq 1 ]]; then
        echo ""
        cargo-sort --version
        echo ""
    fi

    if ! cargo-sort --check --grouped --order package,lib,profile,features,dependencies,target,dev-dependencies,build-dependencies; then
        echo -e "  Cargo.toml sorting result: $fail"
        echo "Please fix the Cargo.toml file, either manually or by running: cargo-sort --grouped --order package,lib,profile,features,dependencies,target,dev-dependencies,build-dependencies"
        exit 1
    else
        echo -e "  Cargo.toml sorting result: $ok"
    fi
}

# Check arguments
while [[ "$1" ]]; do case $1 in
    -s | --git-staged )
        git_staged=1
        ;;
    -f | --force-install )
        force_install=1
        ;;
    -v | --verbose )
        verbose=1
        ;;
    -h | --help )
        show_help
        exit 0
        ;;
    *)
        show_help >&2
        exit 1
esac; shift; done

if [[ $git_staged -eq 1 ]]; then
   staged_files=`git diff --name-only --cached`
   if [[ -z $staged_files ]]; then
      echo -e "Could not check files because none were staged"
      exit 1
   fi
else
   staged_files=""
fi


# Run
check_cargo
echo ""
run_rustfmt
echo ""
run_typos
echo ""
run_machete
echo ""
check_potfiles
echo ""
if [[ $git_staged -eq 1 ]]; then
   staged_files=`git diff --name-only --cached | xargs ls -d 2>/dev/null | grep data/resources/resources.gresource.xml`
   if [[ -z $staged_files ]]; then
        check_resources "data/resources/resources.gresource.xml"
   fi
else
   check_resources "data/resources/resources.gresource.xml"
fi
echo ""
if [[ $git_staged -eq 1 ]]; then
   staged_files=`git diff --name-only --cached | xargs ls -d 2>/dev/null | grep src/ui-resources.gresource.xml`
   if [[ -z $staged_files ]]; then
        check_resources "src/ui-resources.gresource.xml"
   fi
else
   check_resources "src/ui-resources.gresource.xml"
fi
echo ""
run_cargo_sort
echo ""
