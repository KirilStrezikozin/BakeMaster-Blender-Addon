.. |howtochannelpack| image:: ../../_static/images/pages/advanced/nolimits/howtochannelpack_592x762.gif
    :alt: How to set up a Channel Pack

.. |howtotexset| image:: ../../_static/images/pages/advanced/nolimits/howtotexset_800x908.gif
    :alt: How to set up a Texture Set

.. |howtobakejob| image:: ../../_static/images/pages/advanced/nolimits/howtobakejob_500x700.gif
    :alt: How to set up a Texture Set

.. |batchnamepreview| image:: ../../_static/images/pages/advanced/nolimits/batchnamepreview_450x330.gif
    :alt: Batch Name Preview

.. |matchres| image:: ../../_static/images/pages/advanced/nolimits/matchres_584x466.gif
    :alt: Match Resolution

.. |containers| image:: ../../_static/images/pages/advanced/nolimits/containers_504x684.gif
    :alt: Containers

.. |openaddonprefs| image:: ../../_static/images/pages/advanced/nolimits/openaddonprefs_320x277.gif
    :alt: How to open Addon Preferences

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
    It may not be a good idea to denoise maps like Normal because might blur out some important details.

    It's recommended to avoid using it with other maps like Albedo when colors have sharp details and you want to preserve them. You can always add two similar maps and stick with the one that looks the best.

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

.. seealso:: 
    `Comparison between denoised/not denoised bakes <../advanced/improve.html#what-s-the-best-sample-count>`__ and how much time they took to bake.

Supersample anti-aliasing
=========================

With SSAA, BakeMaster bakes at a higher resolution and then downscales back to the chosen map resolution. Such technique smoothes out very contrasted edges and makes images jaggy-free. Enable SSAA in the map's `Format Settings <../start/maps.html#format-settings>`__.

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_ssaa_1x1.png" alt="1x1 SSAA">
            <div class="content-description">
                <p>1K (1024x1024)</p>
                <p>No SSAA</p>
                <p>Took 1s to bake</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/1_ssaa_2x2.png" alt="2x2 SSAA">
            <div class="content-description">
                <p>1K (1024x1024)</p>
                <p>2x2 SSAA</p>
                <p>Took 3s to bake</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/2_ssaa_8x8.png" alt="8x8 SSAA">
            <div class="content-description">
                <p>1K (1024x1024)</p>
                <p>8x8 SSAA</p>
                <p>Took 4m to bake</p>
            </div>
        </div>
    </div>

.. note::
   SSAA increases the bake time as if you were to manually increase the resolution.

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

|howtobakejob|

.. caution:: 
    | Only objects not in Containers already can form a new Bake Job Container.
    | Read more about `Containers <./nolimits.html#containers>`__ in BakeMaster.

Visibility Groups
=================

Objects in a single Visibility Group might cause an effect on each other when baking (where meshes intersect). That can result in intersection errors or cage glitches.

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/1_vg_intersection.png" alt="Intersection">
            <div class="content-description">
                <p>Normal Map, flat area,</p>
                <p>intersection caused by mesh overlapping</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/nolimits/0_vg_nointersection.png" alt="No intersection">
            <div class="content-description">
                <p>Normal Map, flat area,</p>
                <p>no issues</p>
            </div>
        </div>
    </div>

1. You can fix this by enabling the ``Hide when Inactive`` option in the object's Bake Output panel.

2. Or by putting objects that shouldn't affect others into separate Visibility Groups.

.. raw:: html

    <div class="slideshow" id="slideshow-3">
        <div class="content-wrapper">
            <div class="content row active">
                <img src="../../_static/images/pages/advanced/nolimits/0_vg_hidewheninactive.png" alt="Hide when inactive">
                <div class="slideshow-description">
                    <b>Hide when inactive</b>
                    <p>If checked, Object's Mesh will not affect any other Objects while baking.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/1_vg_index.png" alt="VG Index">
                <div class="slideshow-description">
                    <b>VG Index</b>
                    <p>Object's Mesh will affect other objects' meshes if their Visibility Group Indexes are equal to the same value. The effect is noticeable in areas where meshes intersect.</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-3', -1)" onselectstart="return false">&#10094;</a>
            <div class="controls">
                <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 0)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-3', 1)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-3', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>

Batch Name Preview
==================

| BakeMaster allows you to customize the naming pattern of the output filenames in the ``Batch Name`` field in the object's Bake Output panel. That gives a lot of control over output image naming. But sometimes, it's hard to get an idea of what the filename will be.
| Luckily, there's the ``Preview Batch Name`` operator that can do just that!

|batchnamepreview|

Match Resolution
================

If you have image textures in the object's materials and want to bake maps with similar resolutions, check out the ``Match Resolution`` operator.

|matchres|

Containers
==========

A Container holds a group of objects that can share the same settings. It can consist of Lowpolies, Highpolies, and Cages Subcontainers that carry objects of their corresponding type.

Containers become available when `Name Matching <../start/objects.html#name-matching>`__ is enabled.

.. admonition:: Additional features
    :class: important

    You can expand/collapse formed containers and rename them to your liking.

    |containers|

    | A Container can share the same settings for all its objects.
    | For this, toggle the ``Global`` option for the Container.

        .. raw:: html

            <div class="slideshow" id="slideshow-1">
                <div class="content-wrapper">
                    <div class="content row active">
                        <img src="../../_static/images/pages/advanced/nolimits/0_container_notglobal.png" alt="Not Global">
                        <div class="slideshow-description">
                            <b>Not Global</b>
                            <p>Container is just a holder for objects.</p>
                        </div>
                    </div>
                    <div class="content row">
                        <img src="../../_static/images/pages/advanced/nolimits/1_container_global.png" alt="Global">
                        <div class="slideshow-description">
                            <b>Global</b>
                            <p>All Container's objects inherit its settings.</p>
                        </div>
                    </div>
                </div>
                <div class="footer">
                    <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-1', -1)" onselectstart="return false">&#10094;</a>
                    <div class="controls">
                        <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 0)"></span>
                        <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-1', 1)"></span>
                    </div>
                    <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-1', 1)" onselectstart="return false">&#10095;</a>
                </div>
            </div>

Addon Preferences
=================

Some influential settings sit in the addon preferences.

|openaddonprefs|
   
.. raw:: html

    <div class="slideshow" id="slideshow-2">
        <div class="content-wrapper">
            <div class="content row active">
                <img src="../../_static/images/pages/advanced/nolimits/0_addonprefs_low.png" alt="Lowpoly Tag">
                <div class="slideshow-description">
                    <b>Lowpoly Tag</b>
                    <p>What keyword to search for in the object's name to determine if it's a Lowpoly Object.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/1_addonprefs_high.png" alt="Highpoly Tag">
                <div class="slideshow-description">
                    <b>Highpoly Tag</b>
                    <p>What keyword to search for in the object's name to determine if it's a Highpoly Object.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/2_addonprefs_cage.png" alt="Cage Tag">
                <div class="slideshow-description">
                    <b>Cage Tag</b>
                    <p>What keyword to search for in the object's name to determine if it's a Cage Object.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/3_addonprefs_decal.png" alt="Decal Tag">
                <div class="slideshow-description">
                    <b>Decal Tag</b>
                    <p>What keyword to search for in the object's name to determine if it's a Decal Object.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/4_addonprefs_uvtag.png" alt="UVMap Tag">
                <div class="slideshow-description">
                    <b>UVMap Tag</b>
                    <p>What UVMap name should include for BakeMaster to see it as UVMap for bake. UVMaps with that value in their names will have a higher priority in the Active UVMap setting.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/5_addonprefs_hidenotbaked.png" alt="Hide not baked">
                <div class="slideshow-description">
                    <b>Hide not baked</b>
                    <p>Hide all Objects in the scene that are not proceeded in the bake, so that they do not affect it.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/6_addonprefs_mapsmatchtype.png" alt="Maps Match Type">
                <div class="slideshow-description">
                    <b>Maps Match Type</b>
                    <p>When baking with Texture Sets, this will specify how to determine what maps should be baked onto the same image files. <em>Maps Prefixes</em> - default, match by maps' prefixes, <em>Maps Types</em> - match by maps' types, <em>Both</em> - match maps by both their prefixes and types.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/7_addonprefs_location.png" alt="Addon Location">
                <div class="slideshow-description">
                    <b>Addon Location</b>
                    <p>Where the addon is located.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/advanced/nolimits/8_addonprefs_version.png" alt="Addon Version">
                <div class="slideshow-description">
                    <b>Addon Version</b>
                    <p>BakeMaster version you're using.</p>
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
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-2', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>
