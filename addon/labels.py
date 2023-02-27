# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on (version 3.0.0)
# Copyright (C) 2023 Kiril Strezikozin aka kemplerart
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

class BM_LABELS_Props():
    labels = {
    }

    def __init__(self, property_group: str, property_name: str,
                 property_arg: str):
        self.property_group = property_group
        self.property_name = property_name
        self.property_arg = property_arg

    def get(self):
        try:
            label = self.labels[self.property_group][self.property_name][
                    self.property_arg]
        except KeyError:
            label = None
        return label


class BM_LABELS_Operators():
    labels = {
        'BM_OT_BakeJobs': {
            "description": "Add/remove/trash/move order of bake jobs in the table on the left"  # noqa: E501
        }
    }

    def __init__(self, operator_name: str, property_name: str):
        self.operator_name = operator_name
        self.property_name = property_name

    def get(self):
        try:
            label = self.labels[self.operator_name][self.property_name]
        except KeyError:
            label = None
        return label
