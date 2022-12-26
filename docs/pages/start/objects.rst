.. |add_objects| image:: ../../_static/images/pages/start/objects/add_objects_350x320.gif
    :alt: How to add Objects

.. |how_nm_works| image:: ../../_static/images/pages/start/objects/how_nm_works_374x364.gif
    :alt: How Name Matching works

=============
Setup Objects
=============

Choose Objects
==============

To start settings up maps (image textures) for the mesh objects you want to bake, add these objects to the Table of Objects. Do it by pressing the ``Add`` button on the top:

|add_objects|

.. admonition:: Add Highpolies and Cages too
    :class: caution

    If you have highpolies or cages beside lowpoly models, add them to the Table too.

Name Matching
=============

| BakeMaster can automatically match all your lowpolies, highpolies, and cages with each other.
| To do so, press the ``ɑ`` button (`Containers <../advanced/nolimits.html#containers>`__ will form):

|how_nm_works|

Naming Conventions
------------------

| Objects get matched by the following suffixes:
| (can be customized in the `Addon Preferences <../advanced/nolimits.html#addon-preferences>`__)

.. cssclass:: table-with-borders

    +------------------------+----------+----------+----------+-----------+
    |                        | Lowpoly  | Highpoly | Cage     | Decal     |
    +------------------------+----------+----------+----------+-----------+
    | Default suffix         | ``low``  | ``high`` | ``cage`` | ``decal`` |
    +------------------------+----------+----------+----------+-----------+

.. cssclass:: table-with-borders

    +-----------------------------+------------------------------+
    | Lowpoly name example        | Gets matched to              |
    +-----------------------------+------------------------------+
    | ``tram_low``                | | ``tram_high``              |
    |                             | | ``tram_cage``              |
    |                             | | ``tram_high_decal``        |
    +-----------------------------+------------------------------+
    | ``Headlight_low_1``         | | ``Headlight_high_1``       |
    |                             | | ``Headlight_cage_1``       |
    +-----------------------------+------------------------------+
    | ``Headlight-back_low_55``   | | ``Headlight-back_high_55`` |
    |                             | | ``Headlight-back_cage_55`` |
    +-----------------------------+------------------------------+
    | ``monster_body``            | *Won't get matched*          |
    +-----------------------------+------------------------------+

.. caution::
    | BakeMaster determines naming suffixes between ``_`` (underscores) in the Object name.
    | Unmatched objects won't be grouped into containers.

Additional Controls
===================

The Table of Objects provides additional controls for the Objects in it:

.. raw:: html

    <div class="slideshow" id="slideshow-0">
        <div class="content-wrapper">
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/0_controls_add.png" alt="Add">
                <div class="slideshow-description">
                    <b>Add</b>
                    <p>Add selected mesh objects in the scene to the table.</p>
                </div>
            </div>
            <div class="content row active">
                <img src="../../_static/images/pages/start/objects/1_controls_remove.png" alt="Remove">
                <div class="slideshow-description">
                    <b>Remove</b>
                    <p>Remove the active object from the table.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/2_controls_moveup.png" alt="Move Up">
                <div class="slideshow-description">
                    <b>Move Up</b>
                    <p>Move the object's bake priority up.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/3_controls_movedown.png" alt="Mode Down">
                <div class="slideshow-description">
                    <b>Mode Down</b>
                    <p>Move the object's bake priority down.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/4_controls_nm.png" alt="Name Matching">
                <div class="slideshow-description">
                    <b>Name Matching</b><a href="./objects.html#name-matching"> (read more)</a>
                    <p>Toggle Name Matching.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/5_controls_preset.png" alt="Full Object Preset">
                <div class="slideshow-description">
                    <b>Full Object Preset</b><a href="../advanced/savetime.html#advanced-presets"> (read more)</a>
                    <p>Save or load the Full Object Preset.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/6_controls_trash.png" alt="Trash">
                <div class="slideshow-description">
                    <b>Trash</b>
                    <p>Remove all objects from the table.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/7_controls_selectactive.png" alt="Active Object">
                <div class="slideshow-description">
                    <b>Active/current Object</b>
                    <p>To configure an object, select it in the table. Containers can be collapsed/expanded.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/8_controls_bakevis.png" alt="Bake visibility">
                <div class="slideshow-description">
                    <b>Bake visibility</b>
                    <p>Toggle include/exclude the object from baking.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/9_controls_objecttypes.png" alt="Object type">
                <div class="slideshow-description">
                    <b>Objects' types</b>
                    <p>Lowpoly, Highpoly, Cage, Decal, Container, or just a simple object have unique icons.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/10_controls_expandtable.png" alt="Expand the table">
                <div class="slideshow-description">
                    <p>Make the table wider or less.</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-0', -1)" onselectstart="return false">&#10094;</a>
            <div class="controls">
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 0)"></span>
                <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 1)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 2)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 3)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 4)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 5)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 6)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 7)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 8)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 9)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 10)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-0', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>

Object settings
===============

Select the object in the Table of Objects to configure its settings.

High to Lowpoly
---------------

Mind this section if you plan to bake from high to lowpoly meshes.

.. raw:: html

    <div class="slideshow" id="slideshow-1">
        <div class="content-wrapper">
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/0_hl_unique.png" alt="Unique per map">
                <div class="slideshow-description">
                    <b>Unique per map</b>
                    <p>Set unique High to Lowpoly settings for each map.</p>
                </div>
            </div>
            <div class="content row active">
                <img src="../../_static/images/pages/start/objects/1_hl_table.png" alt="Table of Highpolies">
                <div class="slideshow-description">
                    <b>Table of Highpolies</b>
                    <p>Table of all added highpolies for the current object.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/2_hl_add.png" alt="Add">
                <div class="slideshow-description">
                    <b>Add Highpoly</b>
                    <p>Add new highpoly for the current object.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/3_hl_remove.png" alt="Remove">
                <div class="slideshow-description">
                    <b>Remove Highpoly</b>
                    <p>Remove the current highpoly from the table.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/4_hl_active_list.png" alt="Active Highpoly">
                <div class="slideshow-description">
                    <b>Active/current Highpoly</b>
                    <p>Click and choose highpoly for the current object. Highpolies should also be in the Table of Objects.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/5_hl_decal.png" alt="Decal">
                <div class="slideshow-description">
                    <b>Is Decal</b>
                    <p>Mark the current highpoly as a decal for the lowpoly. If you want to bake decals onto lowpoly, add them as highpolies and check this option for each decal. BakeMaster can <a href="./objects.html#decal-object">bake decals separately</a> too.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/6_hl_sepdecals.png" alt="Separate decals">
                <div class="slideshow-description">
                    <b>Separate decals</b>
                    <p>Bake specified decals to a separate texture set. If turned off, decals map passes will be baked to the object's textures.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/7_hl_extrusion.png" alt="Extrusion">
                <div class="slideshow-description">
                    <b>Extrusion/Cage Extrusion</b>
                    <p>Inflate the lowpoly by the specified distance to create cage.</p>
                    <a href="../advanced/improve.html#understanding-cages">(more about cages)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/8_hl_usecage.png" alt="Use Cage">
                <div class="slideshow-description">
                    <b>Use Cage</b>
                    <p>Cast rays to object from a cage object.</p>
                    <a href="../advanced/improve.html#understanding-cages">(more about cages)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/9_hl_cageobj.png" alt="Cage Object">
                <div class="slideshow-description">
                    <b>Cage Object</b>
                    <p>Object to use as cage instead of calculating with cage extrusion. Cage Object should also be in the Table of Objects.</p>
                    <a href="../advanced/improve.html#understanding-cages">(more about cages)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/10_hl_preset.png" alt="High to Lowpoly Preset">
                <div class="slideshow-description">
                    <b>High to Lowpoly Preset</b>
                    <p>Load/save High to Lowpoly panel Settings to a preset.</p>
                    <a href="../advanced/savetime.html#presets">(more about presets)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/11_hl_collapsepanel.png" alt="Collapse/Expand the panel">
                <div class="slideshow-description">
                    <b>Collapse/Expand the panel</b>
                    <p>Click to collapse/expand High to Lowpoly Settings panel.</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-1', -1)" onselectstart="return false">&#10094;</a>
            <div class="controls">
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 0)"></span>
                <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 1)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 2)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 3)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 4)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 5)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 6)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 7)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 8)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 9)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 10)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 11)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-1', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>

UVs and Layers
--------------

Configure crucial UV and other settings for the object like bake to Image Textures or Vertex Colors.

.. raw:: html

    <div class="slideshow" id="slideshow-2">
        <div class="content-wrapper">
            <div class="content row active">
                <img src="../../_static/images/pages/start/objects/0_uv_unique.png" alt="Unique per map">
                <div class="slideshow-description">
                    <b>Unique per map</b>
                    <p>Set unique UVs and Layers settings for each map.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/1_uv_data.png" alt="Bake Data">
                <div class="slideshow-description">
                    <b>Bake Data</b>
                    <p>Set bake data to use for baking. BakeMaster can bake in a regular way or from the object's vertex colors.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/2_uv_target.png" alt="Bake Target">
                <div class="slideshow-description">
                    <b>Bake Target</b>
                    <p>Set baked maps output target. <em>Image Textures</em> or <em>Vertex Colors</em>.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/3_uv_uvlayer.png" alt="UV Layer for bake">
                <div class="slideshow-description">
                    <b>UV Layer for bake</b>
                    <p>Choose UV Map to use for baking.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/4_uv_uvtype.png" alt="UV Type">
                <div class="slideshow-description">
                    <b>UV Layer Type</b>
                    <p>Set the type of chosen UV Layer for bake. <em>Single</em> - single tile, <em>Tiled</em> - UDIM tiles, <em>Automatic</em> - automatically determine if the chosen UV Layer for bake is single-tiled or uses UDIMs.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/5_uv_snap.png" alt="Snap UV to pixels">
                <div class="slideshow-description">
                    <b>Snap UV to pixels</b>
                    <p>Make the chosen UV Layer pixel perfect by aligning UV coordinates to pixels' corners/edges.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/6_uv_useautouv.png" alt="Use auto UV unwrap">
                <div class="slideshow-description">
                    <b>Use auto UV unwrap</b>
                    <p>Auto UV unwrap the current object using the smart project. Enabled automatically if the object has no UV Layers and the bake target is Image Textures.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/7_uv_anglelimit.png" alt="Angle limit">
                <div class="slideshow-description">
                    <b>Angle limit</b>
                    <p>The angle at which to place a seam on the mesh for unwrapping (When auto UV unwrap is enabled).</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/8_uv_islandmargin.png" alt="Island margin">
                <div class="slideshow-description">
                    <b>Island margin</b>
                    <p>Set distance between adjacent UV islands (When auto UV unwrap is enabled).</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/9_scaletobounds.png" alt="Scale to bounds">
                <div class="slideshow-description">
                    <b>Scale to bounds</b>
                    <p>Scale UV coordinates to bounds to fill the whole UV tile area (When auto UV unwrap is enabled).</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/10_uv_preset.png" alt="Preset">
                <div class="slideshow-description">
                    <b>UVs and Layers Preset</b>
                    <p>Load/save UVs and Layers panel Settings to a preset.</p>
                    <a href="../advanced/savetime.html#presets">(more about presets)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/11_uv_expandpanel.png" alt="Collapse/expand the panel">
                <div class="slideshow-description">
                    <b>Collapse/Expand the panel</b>
                    <p>Click to collapse/expand UVs and Layers Settings panel.</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-2', -1)" onselectstart="return false">&#10094;</a>
            <div class="controls">
                <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 0)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 1)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 2)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 3)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 4)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 5)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 6)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 7)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 8)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 9)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 10)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-2', 11)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-2', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>

Shading Correction
------------------

Let BakeMaster save you time with important mesh normals and shading correction that can decrease the number of projection glitches when baking from highpoly.

.. raw:: html

    <div class="slideshow" id="slideshow-3">
        <div class="content-wrapper">
            <div class="content row active">
                <img src="../../_static/images/pages/start/objects/0_csh_trilow.png" alt="Triangulate lowpoly">
                <div class="slideshow-description">
                    <b>Triangulate lowpoly</b>
                    <p>Enable lowpoly triangulation. Takes time but improves lowpoly mesh shading with redundant UV stretches.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/1_csh_lowout.png" alt="Recalculate lowpoly normals outside">
                <div class="slideshow-description">
                    <b>Recalculate lowpoly normals outside</b>
                    <p>Recalculate lowpoly mesh vertex and face normals outside.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/2_csh_smoothlow.png" alt="Smooth lowpoly">
                <div class="slideshow-description">
                    <b>Enable smooth-shaded lowpoly</b>
                    <p>Use smooth-shaded lowpoly for baking. Can be kept unchecked if you've set up the shading on your own.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/3_csh_lowsmoothtype.png" alt="Lowpoly smoothing type">
                <div class="slideshow-description">
                    <b>Lowpoly smoothing type</b>
                    <p><em>Standard</em> - apply default shade smooth to the whole object, <em>Auto Smooth</em> - apply Auto Shade Smooth based on the specified angle, <em>Vertex Groups</em> - apply smooth shading to specified mesh vertex groups, vertex group's boundary will be marked sharp.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/4_csh_lowsmoothangle.png" alt="Lowpoly auto smooth angle">
                <div class="slideshow-description">
                    <b>Lowpoly auto smooth angle</b>
                    <p>Max angle between face normals that will be considered as smooth.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/5_csh_smoothhigh.png" alt="Highpoly smoothing settings">
                <div class="slideshow-description">
                    <b>Highpoly smoothing settings</b>
                    <p>Highpoly has got identical smoothing settings.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/6_csh_preset.png" alt="Preset">
                <div class="slideshow-description">
                    <b>Shading Correction Preset</b>
                    <p>Load/save the Shading Correction panel Settings to a preset.</p>
                    <a href="../advanced/savetime.html#presets">(more about presets)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/7_csh_expandpanel.png" alt="Collapse/expand the panel">
                <div class="slideshow-description">
                    <b>Collapse/Expand the panel</b>
                    <p>Click to collapse/expand the Shading Correction Settings panel.</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-3', -1)" onselectstart="return false">&#10094;</a>
            <div class="controls">
                <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 0)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 1)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 2)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 3)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 4)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 5)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 6)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 7)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-3', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>

Decal Object
------------

When baking decals separately, configure Decal Object baking.

.. raw:: html

    <div class="slideshow" id="slideshow-4">
        <div class="content-wrapper">
            <div class="content row active">
                <img src="../../_static/images/pages/start/objects/0_decal_isdecal.png" alt="Decal Object">
                <div class="slideshow-description">
                    <b>Enable Decal Object</b>
                    <p>Set the current object to be the Decal Object.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/1_decal_usecustomcam.png" alt="Use custom camera">
                <div class="slideshow-description">
                    <b>Use custom camera</b>
                    <p>Use a custom camera object for capturing and baking decal maps.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/2_decal_upaxis.png" alt="Upper coordinate">
                <div class="slideshow-description">
                    <b>Upper coordinate</b>
                    <p>Choose a coordinate specifying where the decal object's top is.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/3_decal_boundoffset.png" alt="Boundary offset">
                <div class="slideshow-description">
                    <b>Boundary offset</b>
                    <p>The distance to use between the decal object's bounds and captured image area bounds.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/4_decal_preset.png" alt="Preset">
                <div class="slideshow-description">
                    <b>Decal Object Preset</b>
                    <p>Load/save the Decal Object panel Settings to a preset.</p>
                    <a href="../advanced/savetime.html#presets">(more about presets)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/5_decal_expandpanel.png" alt="Collapse/expand the panel">
                <div class="slideshow-description">
                    <b>Collapse/Expand the panel</b>
                    <p>Click to collapse/expand the Decal Object Settings panel.</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-4', -1)" onselectstart="return false">&#10094;</a>
            <div class="controls">
                <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-4', 0)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-4', 1)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-4', 2)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-4', 3)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-4', 4)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-4', 5)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-4', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>

.. todo:: Examples of baked decal objects (normal, opacity - 2 images side by side).

Bake Output
-----------

Specify how you want to output the baked result.

.. raw:: html

    <div class="slideshow" id="slideshow-5">
        <div class="content-wrapper">
            <div class="content row active">
                <img src="../../_static/images/pages/start/objects/0_bakeout_batchname.png" alt="Batch name">
                <div class="slideshow-description">
                    <b>Batch name</b>
                    <p>Output files naming convention. Write keywords starting with <code class="docutils literal notranslate"><span class="pre">$</span></code>, any additional text can be added. View available keywords by hovering over this setting.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/1_bakeout_usecaps.png" alt="Use caps">
                <div class="slideshow-description">
                    <b>Use caps</b>
                    <p>Use capital letters for the batch name.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/2_bakeout_previewbatch.png" alt="Preview the batch name">
                <div class="slideshow-description">
                    <b>Preview the batch name</b>
                    <p>Preview how the configured batch naming convention will look in the output image filename.</p>
                    <a href="../advanced/nolimits.html#batch-name-preview">(more about the batch name preview)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/3_bakeout_internal.png" alt="Save internally">
                <div class="slideshow-description">
                    <b>Save internally</b>
                    <p>Pack baked maps into the current Blender file.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/4_bakeout_outpath.png" alt="Output filepath">
                <div class="slideshow-description">
                    <b>Output filepath</b>
                    <p>Directory path on your disk to save baked maps to. <code class="docutils literal notranslate"><span class="pre">//</span></code> is relative to the blend file.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/5_bakeout_createsubfolder.png" alt="Create subfolder">
                <div class="slideshow-description">
                    <b>Create subfolder</b>
                    <p>Create a subfolder in the Output Path directory and save baked maps there.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/6_bakeout_subfoldername.png" alt="Subfolder name">
                <div class="slideshow-description">
                    <b>Subfolder name</b>
                    <p>How to name the subfolder (if <em>Create Subfolder</em> is enabled).</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/7_bakeout_bakedevice.png" alt="Bake device">
                <div class="slideshow-description">
                    <b>Bake device</b>
                    <p>Device to use for baking. <em>CPU</em> - use CPU for baking, <em>GPU</em> - use GPU compute device for baking, configured in the system tab in the user preferences.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/8_bakeout_createmat.png" alt="Create material">
                <div class="slideshow-description">
                    <b>Create material</b>
                    <p>Assign a new material to the object after the bake with all baked maps included.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/9_bakeout_assignmods.png" alt="Assign modifiers">
                <div class="slideshow-description">
                    <b>Assign modifiers</b>
                    <p>If Object maps like Displacement or Vector Displacement have the Result to Modifiers option chosen, modifiers will be assigned, if this is checked. If unchecked, baked maps will be just saved to image textures.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/10_hidewheninactive.png" alt="Hide when inactive">
                <div class="slideshow-description">
                    <b>Hide when inactive</b>
                    <p>if checked, the object won't affect any other objects while baking.</p>
                    <a href="../advanced/nolimits.html#visibility-groups">(more about visibility groups)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/11_bakeout_preset.png" alt="Preset">
                <div class="slideshow-description">
                    <b>Bake Output Preset</b>
                    <p>Load/save Bake Output panel Settings to a preset.</p>
                    <a href="../advanced/savetime.html#presets">(more about presets)</a>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/objects/12_bakeout_expandpanel.png" alt="Collapse/expand the panel">
                <div class="slideshow-description">
                    <b>Collapse/Expand the panel</b>
                    <p>Click to collapse/expand Bake Output Settings panel.</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-5', -1)" onselectstart="return false">&#10094;</a>
            <div class="controls">
                <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 0)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 1)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 2)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 3)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 4)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 5)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 6)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 7)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 8)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 9)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 10)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 11)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-5', 12)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-5', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>
