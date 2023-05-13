# ##### BEGIN LICENSE BLOCK #####
#
# "BakeMaster" Blender Add-on (version 3.0.0)
# Copyright (C) 2023 Kiril Strezikozin aka kemplerart
#
# This License permits you to use this software for any purpose including
# personal, educational, and commercial; You are allowed to modify it to suit
# your needs, and to redistribute the software or any modifications you make
# to it, as long as you follow the terms of this License and the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This License grants permission to redistribute this software to
# UNLIMITED END USER SEATS (OPEN SOURCE VARIANT) defined by the
# acquired License type. A redistributed copy of this software
# must follow and share similar rights of free software and usage
# specifications determined by the GNU General Public License.
#
# This program is free software and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License in
# GNU.txt file along with this program. If not,
# see <http://www.gnu.org/licenses/>.
#
# ##### END LICENSE BLOCK #####

# For run-py-tests: run tests package;
# For run-bpy-tests: run this __init__.py directly.

__package__ = "tests"

import sys
import unittest

from os import path as os_path

import bpy

sys.path.append(os_path.join(os_path.dirname(__file__), ".."))

from . import populate  # noqa: E402


# Test Cases

Test_ba_populate = populate.Test_ba_populate

###


if __name__ == '__main__':
    print("\n")
    print(f"Running tests from {__file__}.\nBlender version is {bpy.app.version}.\nPython version is {sys.version}")  # noqa: E501
    print("\n\n")

    argv = [__file__]

    if "--" in sys.argv:
        argv += sys.argv[sys.argv.index("--") + 1:]

    unittest.main(argv=argv)
