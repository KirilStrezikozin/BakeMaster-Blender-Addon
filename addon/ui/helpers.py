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

import typing


class BM_UI_ml_draw():
    """
    BakeMaster custom UI props draw methods specifically for drawing props of
    items in a multi selection.

    Case 1. If no valid multi selection, default prop draw is used.

    Case 2. If props of propname are equal in a multi selection, default prop
    draw is used.

    Case 3. If props of prop_name aren't equal in a multi selection, a custom
    draw is used depending on a prop_type with an operator to
    'relinquish' the props = make them equal as such the default
    prop draw will be used.

    Use by inheriting.

    data_name is an identifier of walk_data_name for an instance.

    Example:
    ...

    self.draw_prop(bakemaster, layout, "IntProperty", container, "use_bake",
                   None, text="Bake Visibility", icon='RENDER_STILL',
                   emboss=False)

    self.draw_prop(bakemaster, layout, "Operator", None, None,
                   "bakemaster.bakejobs_add", text="Add", icon='ADD')

    ...
    """

    def draw_prop(self, bakemaster: not None, data_name: str,
                  layout: typing.Any, prop_type: str, data: not None,
                  property: str, operator: typing.Union[str, None],
                  *args, **kwargs):

        if data_name == "":
            data_name = self.data_name

        # Case 1
        if data is None or any([not self.has_multi_selection(bakemaster, data,
                                                             data_name),
                                not data.is_selected]):
            return self.default_draw_prop(layout, prop_type, data, property,
                                          operator, *args, **kwargs)

        _, containers, _ = getattr(
            bakemaster, "get_active_%s" % data_name)(bakemaster)

        props_equal = True
        old_prop_val = getattr(data, property)
        for container in containers:
            if not container.is_selected or container.has_drop_prompt:
                continue

            # skip checking group prop value if container isn't a group
            elif property.find("group") == 0 and not container.is_group:
                continue
            # skip checking decorator groups
            elif container.is_group and container.group_type == 'DECORATOR':
                continue

            if getattr(container, property) != old_prop_val:
                props_equal = False
                break

        # Case 2
        if props_equal:
            return self.default_draw_prop(layout, prop_type, data, property,
                                          operator, *args, **kwargs)

        # Case 3
        icon_value = bakemaster.get_icon('FLOATING_VALUE')

        if prop_type != "Operator":
            relinquish_operator = layout.operator(
                'bakemaster.global_ui_prop_relinquish',
                text=kwargs.get("text", ""),
                icon_value=icon_value)
            relinquish_operator.data_name = data_name
            relinquish_operator.prop_name = property
            return

        if kwargs.get("icon") is not None:
            _ = kwargs.pop("icon")
        kwargs["icon_value"] = icon_value
        return layout.operator(operator, *args, **kwargs)

    def default_draw_prop(self, layout: typing.Any, prop_type: str,
                          data: not None, property: str, operator: str,
                          *args, **kwargs):
        if prop_type == "Operator":
            return layout.operator(operator, *args, **kwargs)

        layout.prop(data, property, *args, **kwargs)

    def has_multi_selection(self, bakemaster, data: not None, data_name=""):
        """
        Return True if there is a visualized multi selection
        in the iterable attribute of data_name name inside the givne data.

        If data_name is not given (empty), self.data_name will be used.
        """
        if data_name == "":
            data_name = self.data_name

        return bakemaster.wh_has_ms(data, data_name)
