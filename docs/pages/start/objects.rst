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
                    <b>Active Object</b>
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

.. todo:: Slideshow of gifs showing settings.

UVs and Layers
--------------

Configure crucial UV and other settings for the object.

.. todo:: Slideshow of gifs showing settings.

Shading Correction
------------------

Let BakeMaster save you time with important mesh normals and shading correction.

.. todo:: Slideshow of gifs showing settings.

Decal Object
------------

Configure Decal Object baking.

.. todo:: Slideshow of gifs showing settings.

Bake Output
-----------

Specify how you want to output the baked result.

.. todo:: Slideshow of gifs showing settings.
