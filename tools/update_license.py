#!/usr/bin/env python3
# BEGIN LICENSE & COPYRIGHT BLOCK.
#
# Copyright (C) 2022-2024 Kiril Strezikozin
# BakeMaster Blender Add-on (version 2.6.0)
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

# This script is a tool for updating the license block in each file.
# Intended to be run directly or by $ make update_license LICENSE=LICENSE.txt

import sys
import pathlib
from typing import List


def prepare_license(license_path: pathlib.PurePath) -> List[str]:
    license_lines = []

    with license_path.open('r') as license_file:
        for line in license_file.readlines():
            license_lines.append(line)

    return license_lines


def update_dir(dir: pathlib.PurePath, LICENSE: pathlib.PurePath,
               license_lines: List[str]) -> None:

    info_start = "BEGIN LICENSE"
    info_end = "END LICENSE"

    if not dir.exists() or not dir.is_dir():
        return

    for src in dir.iterdir():
        if src.is_dir():

            if src.name.find(".") == -1 and src.name != "venv":
                update_dir(src, LICENSE, license_lines)
            continue

        elif (src.absolute() == LICENSE.absolute() or src.name == "GNU.txt"
              or "readme" in src.name.lower()):
            continue

        elif src.name.split('.')[-1] not in ['py', 'txt', 'c', 'h', 'cpp']:
            continue

        src_lines = []
        src_license_line = -1
        with src.open('r') as src_file:
            is_license_block = False

            for i, line in enumerate(src_file.readlines()):
                line_s = line.strip()

                if (len(line_s) and line_s[0] == "#"
                        and line.find(info_start) != -1):
                    src_license_line = i
                    is_license_block = True

                elif not is_license_block:
                    src_lines.append(line)

                elif (len(line_s) and line_s[0] == "#"
                      and line.find(info_end) != -1):
                    is_license_block = False

        if src_license_line == -1:
            continue

        with src.open('w') as src_file:
            src_file.seek(0)  # jump to the first byte position

            for i, line in enumerate(src_lines):
                if i == src_license_line:
                    for l_line in license_lines:
                        src_file.write(l_line)
                src_file.write(line)

            if len(src_lines) == 0:
                for l_line in license_lines:
                    src_file.write(l_line)


def main() -> None:
    print('"BakeMaster" Blender Add-on')
    print("Copyright (C) 2022-2023 Kiril Strezikozin")
    print("License update tool")
    print("=========================================")
    print("\n")

    PACKAGE = pathlib.Path(__file__).parent.parent

    if len(sys.argv) > 1 and sys.argv[1]:
        LICENSE = PACKAGE.joinpath(sys.argv[1])
    else:
        LICENSE = PACKAGE.joinpath(
            input("Enter path to license file (LICENSE): ")
            or "LICENSE")

    if not LICENSE.exists():
        print("%s does not exist. Aborting." % LICENSE.name)
        return

    license_lines = prepare_license(LICENSE)
    update_dir(PACKAGE, LICENSE, license_lines)

    print("License has been updated. Exiting.")


if __name__ == "__main__":
    main()
