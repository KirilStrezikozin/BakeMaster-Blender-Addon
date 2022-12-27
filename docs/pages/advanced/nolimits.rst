.. |howtochannelpack| image:: ../../_static/images/pages/advanced/nolimits/howtochannelpack_592x762.gif
    :alt: How to set up a Channel Pack

.. |howtotexset| image:: ../../_static/images/pages/advanced/nolimits/howtotexset_800x908.gif
    :alt: How to set up a Texture Set

=========
No Limits
=========

Denoising Maps
==============

Baking with a low sample count might result in image noise. Enable denoising (noise reduction) in the map's `Format Settings <../start/maps.html#format-settings>`__.

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_denoise_aond.png" alt="AO, not denoised">
            <div class="content-description">
                <p>AO fragment,</p>
                <p>not denoised</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/1_denoise_aod.png" alt="AO, denoised">
            <div class="content-description">
                <p>AO fragment,</p>
                <p>denoised</p>
            </div>
        </div>
    </div>

.. caution:: 
     Note that *on some occasions* denoising maps like Albedo or Normal mightn't be a good idea as it might blur out some sharp details.

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_denoise_albedond.png" alt="Albedo, not denoised">
            <div class="content-description">
                <p>Albedo fragment,</p>
                <p>not denoised</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/1_denoise_albedod.png" alt="Albedo, denoised">
            <div class="content-description">
                <p>Albedo fragment,</p>
                <p>denoised</p>
            </div>
        </div>
    </div>

Supersample anti-aliasing
=========================

With SSAA, BakeMaster bakes at a higher resolution and then downscales back to the chosen map resolution. Such a technique results in smoother and jaggy-free images (not always noticeable). Enable SSAA in the map's `Format Settings <../start/maps.html#format-settings>`__.

Channel Packing
===============

Channel Packing is commonly used in the Game Dev industry when there's a need to pack baked maps into image color channels to save memory usage. For example, you can have a single image file baked, where the Red channel holds Metalness, the Green carries Roughness, and the Blue one - AO.

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_chnlp_metal.png" alt="Metalness">
            <div class="content-description">
                <p>Metalness</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/1_chnlp_rough.png" alt="Roughness">
            <div class="content-description">
                <p>Roughness</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/2_chnlp_ao.png" alt="AO">
            <div class="content-description">
                <p>AO</p>
            </div>
        </div>
    </div>

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_chnlp_metalroughao.png" alt="Channel Packed">
            <div class="content-description">
                <p>Channel Packed</p>
                <p>Metalness, Roughness, AO</p>
                <p>R+G+B</p>
            </div>
        </div>
    </div>

With BakeMaster, you can easily configure Channel Packs and have any maps packed.

|howtochannelpack|

.. admonition:: Channel Pack type
    :class: important

    Imagine having Channel Pack types, with which you can pack not only in the ``R+G+B`` way but also ``RGB+A`` or ``R+G+B+A``. BakeMaster allows you to do even that.

    .. raw:: html

        <div class="slideshow" id="slideshow-0">
            <div class="content-wrapper">
                <div class="content row active">
                    <img src="../../_static/images/pages/advanced/nolimits/0_chnlptypes_4.png" alt="R+G+B+A">
                    <div class="slideshow-description">
                        <b>R+G+B+A</b>
                    </div>
                </div>
                <div class="content row">
                    <img src="../../_static/images/pages/advanced/nolimits/1_chnlptypes_2.png" alt="RGB+A">
                    <div class="slideshow-description">
                        <b>RGB+A</b>
                    </div>
                </div>
                <div class="content row">
                    <img src="../../_static/images/pages/advanced/nolimits/2_chnlptypes_3.png" alt="R+G+B">
                    <div class="slideshow-description">
                        <b>R+G+B</b>
                    </div>
                </div>
            </div>
            <div class="footer">
                <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-0', -1)" onselectstart="return false">&#10094;</a>
                <div class="controls">
                    <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 0)"></span>
                    <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 1)"></span>
                    <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 2)"></span>
                </div>
                <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-0', 1)" onselectstart="return false">&#10095;</a>
            </div>
        </div>

Texture Sets
============

A Texture Set is a set of images baked for one object. By default, BakeMaster will save baked maps for each object into separate Texture Sets. Meaning there will be sets of image files for each object. In some cases, you might want, for example, an Albedo map for ten objects baked onto a single image file. BakeMaster allows doing so and even with automatic UV Repack if needed.

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_texset_n.png" alt="No Texture Set">
            <div class="content-description">
                <p>Object1, not in a Texture Set</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/1_texset_n.png" alt="No Texture Set">
            <div class="content-description">
                <p>Object2, not in a Texture Set</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/2_texset_n.png" alt="No Texture Set">
            <div class="content-description">
                <p>Object3, not in a Texture Set</p>
            </div>
        </div>
    </div>

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_texset_y.png" alt="Texture Set">
            <div class="content-description">
                <p>All objects in one Texture Set</p>
            </div>
        </div>
    </div>

Follow the instruction below, If you want some objects to share the same Texture Set.

|howtotexset|

PBR-Metallic and PBR-Specular
=============================

Blender supports only PBR-Metallic workflow, but BakeMaster can bake both PBRS and PBRM types. It'll correctly recalculate the Metallic workflow used in your materials, giving a clear and clean PBRS output, and then restore all materials back after baking. You can add both PBR-Specular and PBR-Metallic maps to the Table of Maps.

PBR-Metallic:

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_pbrm.png" alt="AlbedoM">
            <div class="content-description">
                <p>AlbedoM</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/1_pbrm.png" alt="Metalness">
            <div class="content-description">
                <p>Metalness</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/2_pbrm.png" alt="Roughness">
            <div class="content-description">
                <p>Roughness</p>
            </div>
        </div>
    </div>

PBR-Specular:

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_pbrs.png" alt="AlbedoS">
            <div class="content-description">
                <p>AlbedoS</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/1_pbrs.png" alt="Specular">
            <div class="content-description">
                <p>Specular</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/2_pbrs.png" alt="Glossiness">
            <div class="content-description">
                <p>Glossiness</p>
            </div>
        </div>
    </div>

| The examples of PBRS and PBRM bakes shown above were baked with BakeMaster.
| `(more about PBR-Metallic and PBR-Specular workflows) <./improve.html#pbr-metallic-and-pbr-specular>`__

.. admonition:: How BakeMaster names maps of both workflows
    :class: important

    | PBR-Metallic: ``AlbedoM``, ``Metalness``, ``Roughness``;
    | PBR-Specular: ``AlbedoS``, ``Specular``, ``Glossiness``.

    You can always specify your custom map naming in the ``Prefix`` field of the `Map Settings area <../start/maps.html#map-settings>`__.

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