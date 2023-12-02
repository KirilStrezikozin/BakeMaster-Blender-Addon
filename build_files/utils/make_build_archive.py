#!/usr/bin/env python3
# BEGIN LICENSE & COPYRIGHT BLOCK.
#
# Copyright (C) 2022-2023 Kiril Strezikozin
# BakeMaster Blender Add-on (version 2.6.0a3)
#
# This file is a part of BakeMaster Blender Add-on, a plugin for texture
# baking in open-source Blender 3d modelling software.
# The author can be contacted at <kirilstrezikozin@gmail.com>.
#
# Redistribution and use for any purpose including personal, educational, and
# commercial, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. The current acquired License allows copies/redistributions of this
#    software be made to UNLIMITED END USER SEATS (OPEN SOURCE LICENSE).
# 2. Redistributions of this source code or partial usage of this source code
#    must follow the terms of this license and retain the above copyright
#    notice, and the following disclaimer.
# 3. The name of the author may be used to endorse or promote products derived
#    from this software. In such a case, a prior written permission from the
#    author is required.
#
# This program is free software and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# You should have received a copy of the GNU General Public License in the
# GNU.txt file along with this program. If not,
# see <http://www.gnu.org/licenses/>.
#
# END LICENSE & COPYRIGHT BLOCK.

# This script is a utility for building an install archive.
# Intended to be run by $ make build or $ make build VERSION=3.0.0

import os
import sys
import shutil
import pathlib
from typing import List, Tuple, Union

bool_DIR = True
bool_NOTDIR = False


def print_msg(text: str, verbose: bool = True) -> None:
    if verbose:
        print(text)


def mk_build_dirs(*paths: Tuple[List[Union[bool, pathlib.PurePath]]],
                  verbose=True) -> bool:
    for is_dir, path in list(paths):
        if not path.exists():
            if not is_dir:
                print_msg("File does not exist: %s" % path.name, verbose)
                continue
        elif not is_dir:
            continue

        try:
            path.mkdir()
        except OSError as error:
            print_msg("Directory not created:\n%s" % error, verbose)
        else:
            print_msg("Directory created: %s" % path.name, verbose)


def rm_dir(dir: pathlib.PurePath) -> None:
    if not dir.exists() or not dir.is_dir():
        return

    clean_dir(dir)

    try:
        dir.rmdir()
    except OSError:
        pass


def clean_dir(dir: pathlib.PurePath) -> None:
    if not dir.exists() or not dir.is_dir():
        return

    for path in dir.iterdir():
        if path.is_dir():
            rm_dir(path)
            continue
        try:
            os.remove(path.absolute())
        except OSError:
            pass


def prepare_license(license_path: pathlib.PurePath, licenses: List[str]
                    ) -> Tuple[int, int, List[str]]:
    license_type_line = -1
    license_version_line = -1
    license_lines = []

    with license_path.open('r') as license_file:
        for i, line in enumerate(license_file.readlines()):
            license_lines.append(line)

            if license_version_line == -1 and "Copyright (C)" in line:
                license_version_line = i + 1

            if license_type_line != -1:
                continue

            for license_name in licenses:
                if license_name in line:
                    license_type_line = i
                    break

    return license_type_line, license_version_line, license_lines


def get_addon_version() -> str:
    if len(sys.argv) > 1 and sys.argv[1]:
        VERSION = sys.argv[1]
    else:
        VERSION = input("Enter BakeMaster version (latest): ") or "latest"

    return VERSION


def make_zips() -> None:
    print('"BakeMaster" Blender Add-on')
    print("Copyright (C) 2022-2023 Kiril Strezikozin")
    print("Install archive build tool")
    print("=========================================")
    print("\n")

    VERSION = get_addon_version()

    PACKAGE = pathlib.Path(__file__).parent.parent.parent
    LICENSE = PACKAGE.joinpath("LICENSE.txt")
    INSTALL_DIR = PACKAGE.joinpath("install")
    ARCHIVE_DIR = INSTALL_DIR.joinpath("BakeMaster")

    write_version = VERSION.replace(".", "_")

    clean_dir(INSTALL_DIR)

    mk_build_dirs(
        [bool_DIR, INSTALL_DIR],
        [bool_DIR, ARCHIVE_DIR],
        [bool_DIR, ARCHIVE_DIR.joinpath("BakeMaster")],
        [bool_NOTDIR, LICENSE]
    )

    files = [
        "LICENSE.txt",
        "README.txt",
        "__init__.py",
        "labels.py",
        "operator_bake.py",
        "operators.py",
        "presets.py",
        "properties.py",
        "ui_panel.py",
        "ui_panel_base.py",
        "utils.py",
    ]

    licenses = [
        "1 END USER SEAT (SOLO LICENSE)",
        "2-5 END USER SEATS (SMALL STUDIO LICENSE)",
        "6-10 END USER SEATS (BIG STUDIO LICENSE)",
        "UNLIMITED END USER SEATS (OPEN SOURCE LICENSE)"
    ]

    info_start = "BEGIN LICENSE"
    info_end = "END LICENSE"

    suffixes = [
        "full_single",
        "full_2-5_users",
        "full_6-10_users",
        "full_opensource"
    ]

    license_type_line, license_version_line, license_lines = prepare_license(
        LICENSE, licenses)

    if license_version_line != -1:
        license_lines[license_version_line] = (
            "# BakeMaster Blender Add-on (version %s)\n" % VERSION)

    for i in range(len(licenses)):

        if license_type_line != -1:
            replace_with = licenses[i - 1] if i > 0 else licenses[-1]
            license_lines[license_type_line] = license_lines[
                license_type_line].replace(replace_with, licenses[i])

        for src_name in files:
            src = PACKAGE.joinpath(src_name)
            dst = ARCHIVE_DIR.joinpath("BakeMaster", src_name)

            if not src.exists():
                print("File does not exist: %s" % src_name)
                continue

            shutil.copyfile(src.absolute(), dst.absolute())

            if src_name == "README.txt":
                continue

            dst_license_line = -1
            dst_lines = []
            with dst.open('r') as dst_file:
                is_info_block = False

                for l_i, line in enumerate(dst_file.readlines()):
                    line_s = line.strip()

                    if (len(line_s) and line_s[0] == "#"
                            and line.find(info_start) != -1):
                        is_info_block = True
                        dst_license_line = l_i

                    elif not is_info_block:
                        dst_lines.append(line)

                    elif (len(line_s) and line_s[0] == "#"
                            and line.find(info_end) != -1):
                        is_info_block = False

            if dst_license_line == -1:
                continue

            with dst.open('w') as dst_file:
                dst_file.seek(0)  # jump to the first byte position

                for l_i, line in enumerate(dst_lines):
                    if l_i == dst_license_line:
                        for l_line in license_lines:
                            dst_file.write(l_line)
                    dst_file.write(line)

                if len(dst_lines) == 0:
                    for l_line in license_lines:
                        dst_file.write(l_line)

        archive_name = "bakemaster_blender_addon_%s_%s" % (write_version,
                                                           suffixes[i])
        archive_file = shutil.make_archive(archive_name, 'zip',
                                           ARCHIVE_DIR)
        shutil.move(archive_file, INSTALL_DIR)
        print("Build archive created: %s" % pathlib.Path(archive_file).name)
        clean_dir(ARCHIVE_DIR.joinpath("BakeMaster"))

    rm_dir(ARCHIVE_DIR)
    print("Build is completed. Exiting.")


if __name__ == "__main__":
    make_zips()
