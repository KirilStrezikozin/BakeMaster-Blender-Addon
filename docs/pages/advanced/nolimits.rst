=========
No Limits
=========

Denoising Maps
==============

Baking with a low sample count might result in image noise. Enable denoising (noise reduction) in the map's `Format Settings <../start/maps.html#format-settings>`__.

.. todo:: Images showing a difference between denoised and not denoised images.

Supersample anti-aliasing
=========================

With SSAA, BakeMaster bakes at a higher resolution and then downscales back to the chosen map resolution. Such a technique results in smoother and jaggy-free images. Enable SSAA in the map's `Format Settings <../start/maps.html#format-settings>`__.

.. todo:: Images showing a difference between no SSAA and different SSAA values.

Channel Packing
===============

Channel Packing is commonly used in the Game Dev industry when there's a need to pack baked maps into image color channels to save memory usage. For example, you can have a single image file baked, where the Red channel holds Metalness, the Green carries Roughness, and the Blue one - AO.

With BakeMaster, you can easily configure Channel Packs and have any maps packed.

.. todo:: Slideshow showing how to create and configure a Channel Pack.

.. admonition:: Channel Pack type
    :class: important

    Imagine having Channel Pack types, with which you can pack not only in the ``R+G+B`` way but also ``RGB+A`` or ``R+G+B+A``. BakeMaster allows you to do even that.

    .. todo:: Image requested showing the list of available channel pack types.

Texture Sets
============

A Texture Set is a set of images baked for one object. By default, BakeMaster will save baked maps for each object into separate Texture Sets. Meaning there will be sets of image files for each object. In some cases, you might want, for example, an Albedo map for ten objects baked onto a single image file. BakeMaster allows doing so and even with automatic UV Repack if needed.

Follow the slideshow below, If you want some objects to share the same Texture Set.

.. todo:: Slideshow showing how to create and configure a Texture Set.

Create a Bake Job Group
=======================

You can create a new Container and choose objects to put in it. That will act as a Bake Job. With Bake Jobs, you can choose maps and set identical settings for all objects in them at once. Follow the slideshow below to build one up:

.. todo:: Slideshow showing how to create a Bake Job.

.. caution:: 
    | Only objects not in Containers already can form a new Bake Job Container.
    | Read more about `Containers <./nolimits.html#containers>`__ in BakeMaster.

Visibility Groups
=================

Objects in a single Visibility Group might cause an effect on each other when baking. That can result in intersection errors or cage glitches.

.. todo:: Image requested showing the intersection errors or cage glitches.

1. You can fix this by enabling the ``Hide when Inactive`` option in the object's Bake Output panel.

    .. todo:: Image requested showing the hide when inactive property and its description.

2. Or by putting objects that shouldn't affect others into separate Visibility Groups.

    .. todo:: Image requested showing the VG Index property and its description.

Batch Name Preview
==================

| BakeMaster allows you to customize the naming pattern of the output filenames in the ``Batch Name`` field in the object's Bake Output panel. That gives a lot of control over output image naming. But sometimes, it's hard to get an idea of what the filename will be.
| Luckily, there's the ``Preview Batch Name`` operator that can do just that!

.. todo:: Gif requested showing how the preview batch name operator works.

Match Resolution
================

If you have image textures in the object's materials and want to bake maps with similar resolutions, check out the ``Match Resolution`` operator.

.. todo:: Gif requested showing how to use the match resolution operator.

Containers
==========

A Container holds a group of objects that can share the same settings. It can consist of Lowpolies, Highpolies, and Cages Subcontainers that carry objects of their corresponding type.

Containers become available when `Name Matching <../start/objects.html#name-matching>`__ is enabled.

.. admonition:: Additional features
    :class: important

    You can expand/collapse formed containers and rename them to your liking.

    .. todo:: Gif showing how to rename and collapse containers.

    | A Container can share the same settings for all its objects.
    | For this, toggle the ``Global`` option for the Container.

    .. todo:: Gif showing the container's global option.

Addon Preferences
=================

Some influential settings sit in the addon preferences.

.. todo:: Gif requested showing hot to access the addon preferences.

.. todo:: Slideshow of images showing the addon preferences' settings.