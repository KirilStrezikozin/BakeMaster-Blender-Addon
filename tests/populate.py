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

__all__ = ["Test_ba_populate"]

import sys
import unittest

import bpy

from bpy.types import Object, PropertyGroup


class Test_ba_populate(unittest.TestCase):
    """
    Default BakeMaster population to test Add, Remove, and Trash OTs.
    """

    obs = []

    def get_bm(self) -> PropertyGroup:
        return bpy.context.scene.bakemaster

    def bm_trash(self, data_name: str) -> None:

        attr = "%s_trash" % data_name[:-1]
        self.assertTrue(hasattr(bpy.ops.bakemaster, attr))

        trash_ot = getattr(bpy.ops.bakemaster, attr)
        trash_ot('INVOKE_DEFAULT')

    def get_c_active_object(self) -> Object:
        ob = bpy.context.active_object

        if ob is None:
            raise ValueError("Testing encountared None active_object")

        return bpy.context.active_object

    def ob_populate(self) -> None:
        print("Populating the Scene...")

        bpy.ops.object.text_add()
        ob = self.get_c_active_object()
        ob.name = "Text"
        self.obs.append(ob)

        bpy.ops.object.metaball_add()
        ob = self.get_c_active_object()
        ob.name = "Meta"
        self.obs.append(ob)

        bpy.ops.object.empty_add()
        ob = self.get_c_active_object()
        ob.name = "Image"
        ob.empty_display_type = 'IMAGE'
        self.obs.append(ob)

        bpy.ops.object.light_add()
        ob = self.get_c_active_object()
        ob.name = "Light"
        self.obs.append(ob)

        bpy.ops.curve.primitive_bezier_curve_add()
        ob = self.get_c_active_object()
        ob.name = "BezierCurve"
        self.obs.append(ob)

        bpy.ops.mesh.primitive_cube_add()
        ob = self.get_c_active_object()
        ob.name = "Cube"
        self.obs.append(ob)

        bpy.ops.mesh.primitive_cube_add()
        ob = self.get_c_active_object()
        ob.name = "Plane"
        self.obs.append(ob)

    def setUp(self) -> None:
        print("Starting.")
        print("--------------------------------------------------------------")

        self.ob_populate()

        print("\nFinished.")

    def test_bm_trash_bakejobs(self) -> None:
        print("--------------------------------------------------------------")
        print(f"Testing {self.test_bm_trash_bakejobs.__name__}")

        bm = self.get_bm()

        self.bm_trash("bakejobs")

        self.assertEqual(bm.bakejobs_len, 0)
        self.assertEqual(bm.bakejobs_active_index, -1)
        self.assertEqual(len(bm.bakejobs), 0)

        print("\nFinished.")

    def tearDown(self) -> None:
        print("--------------------------------------------------------------")
        print("Tearing down.\n")


if __name__ == '__main__':
    print("\n")
    print(f"Running tests from {__file__}.\nBlender version is {bpy.app.version}.\nPython version is {sys.version}")  # noqa: E501
    print("\n\n")

    argv = [__file__]

    if "--" in sys.argv:
        argv += sys.argv[sys.argv.index("--") + 1:]

    unittest.main(argv=argv)
