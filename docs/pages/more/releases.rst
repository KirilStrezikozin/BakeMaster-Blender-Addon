========
Releases
========

All BakeMaster Releases and Changelogs are listed on this page. Each new release comes with new features, improvements, or fixes. For clarity, each section has a ``tag`` to identify the changes.

2.5.0 Release
=============

.. admonition:: Tag
    :class: important

    `2.5.0 - June 21st, 2023 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

**Fixes:**

#. Corrected alpha mode for Channel Packs and images (CU-85zt9dgvu).
#. **Existing nodes in Compositor are correctly restored after Denoise or Channel Pack (CU-85zt9rf2t).**
#. Safely bake if Output Filepath is invalid (CU-85zt9p981).
#. Correctly set baked images' color spaces (CU-85zt9rfjx, CU-85ztapkvm).
#. **SSAA didn't work and had no effect (CU-85zt9ecuy).**
#. **Ovewrite to remove previously baked images if the same names encountered (CU-85ztamht0).**
#. Saved images to the disk had wrong indexes (CU-85ztab9u7).
#. Correctly set Output Render/Scene settings (CU-85ztapkyb).
#. Apply Lastly Edited Setting didn't work for Decal Map (CU-85ztawmwb).
#. **One extra bake was by mistake internally invoked when baking Texture Sets, which resulted in corrupted, unsaved image data (CU-85ztaz4vz).**
#. Correctly set Channel Packed images' color spaces (CU-85zt7bn79).
#. **Match Resolution swapped height and width values (CU-85ztbhnjr).**
#. **Existing Triangulation modifiers were ignored (CU-85zt7bmyc).**
#. Help buttons didn't open documentation.

**New Features:**

#. View From - use active camera to capture direction of specular reflections (CU-85zt7bn1q).
#. JPEG Output Quality slider to the Format settings (CU-85zt9cp75).
#. **Color Management Panel (CU-85zt7bm29).**
#. Show Image Color Depth options and set it correctly (CU-85zt9345a)
#. TGA file format + TGA raw - uncompressed option (CU-85zt98v6t)
#. DPX file format + save in Log option (CU-85ztaqqx5).
#. CINEON file format (CU-85ztaqqx5).
#. Output Compression for TIFF file format (CU-85ztaqrdc).
#. **Default file format and bit depth from color management is applied to new maps (CU-85ztaqtmx).**
#. **Cavity map default values to match 50% grey in neutral areas (CU-85ztau27p).**
#. **Channel Pack, Denoise, and Decal bake is now available when baking internally (CU-85ztauwtt, CU-85ztapkqf).**
#. **Add Time elapsed and bake time of each map to Progress Report messages (CU-85ztauwzf).**
#. **Bake with scene color management applied - Apply Scene (CU-85zt9rew9).**
#. **Apply compositor nodes to bakes - Compositor (CU-85zt9revj).**
#. **ACES color space for bakes (CU-85ztapkvm).**
#. **Bake Cancel (``BACKSPACE + ESC``) now removes already baked files (CU-85ztb8bz5).**
#. Apply configured color management settings (Color Spaces, File Formats, Bit Depths) to existing maps with Quick Apply (CU-85ztb8q9h).
#. **Match Resolution now also shows images from the .blend file itself that are not linked to materials (CU-85ztbhnjr).**
#. **Toggle image bit depth and see available properly in Format settings (CU-85zt933wz).**
#. Average Islands Scale checkbox for Texture Set UV Repack (CU-85zt7bqf7).
#. All panels now have scroll bars (CU-85zt8wmqm).
#. Low Resolution Mesh checkbox for bakes from Multires (CU-85zt8xnpv).
#. Choose base subdivision level for bakes from Multires (CU-85zt7bqt9).

**Edits:**

#. Removed Alpha and Trans BG options for JPEG, BMP file format because they do not support it anyway (CU-85zt9d78z).
#. Show available map data first for Displacement, Normal maps (CU-85ztatzht).
#. Channel Pack, Denoise, and Decal bake now proceedes without a need for Render Result image (CU-85ztauwjz).
#. Map baking progress now shows not total maps count to left, but the count of maps that are actually valid for bake (CU-85ztb5pn6).

`Features <https://bakemaster-blender-addon.readthedocs.io/en/2.5.0/pages/about.html#key-features>`__.

2.0.2 Release
=============

.. admonition:: Tag
    :class: important

    `2.0.2 - April 28th, 2023 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

**Fixes:**

#. Albedo, Metallic, Roughness, and Opacity Maps weren't baked properly from Highpoly (`issue-29 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/issues/29>`__)
#. ID Maps weren't baked if Object had NoneType Materials (`dev-a1a4836 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/a1a4836aa42eae83b6173df147ae63545dff5416>`__)
#. If bake took more than a minute, "Bake completed in ..." didn't show correct time the bake took (`dev-de81454 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/de81454994b1dd73b59fb1167cf0f76bf0011451>`__)
#. Normal map colorspace could not be set (`issue-27 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/issues/27>`__)
#. Normal Map bake with Oject/Materials data outputted raw vectors colors instead of normals (`dev-717cc45 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/717cc4574e985fca7f0617bffd0b195c509f6068>`__)
#. UVMap for bake was set to be the UVMap to bake from (`dev-e4aff4e <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/e4aff4ef30027124ed7270e22f854f10d41de651>`__)
#. Bake could not proceed when objects were hidden at the start (`dev-07ead0b <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/07ead0b3f7716624e098402c2c7990ed08995610>`__)
#. Normal Map bake from multires caused errors (`dev-2c27a29 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/2c27a29c08b20a0d8f95577264e5fcde52997842>`__)

**New Features:**

#. Pack tiled images since Blender 3.5 supports it (`dev-9a954c8 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/9a954c8aadd3b086b609676dad4492e588b3abbe>`__)

`Features <https://bakemaster-blender-addon.readthedocs.io/en/2.0.2/pages/about.html#key-features>`__.

2.0.1 Release
=============

.. admonition:: Tag
    :class: important

    `2.0.1 - March 8th, 2023 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

**Fixes:**

#. Image format (.png) is occasionally written twice (.png.png) (`issue-22 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/issues/22>`__)
#. Roughness map wasn't added to Baked Material (`dev-9d1a30a <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/9d1a30ab757115b1c7c976c20b2c36e0566cb971>`__)
#. Color stepping when baking Displacement from Multires (`dev-9d1a30a <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/9d1a30ab757115b1c7c976c20b2c36e0566cb971>`__)
#. Displacement map from material not baking out (`dev-9d1a30a <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/9d1a30ab757115b1c7c976c20b2c36e0566cb971>`__)

`Features <https://bakemaster-blender-addon.readthedocs.io/en/2.0.1/pages/about.html#key-features>`__.

2.0.0 Release
=============

.. admonition:: Tag
    :class: important

    `2.0.0 - December 29th, 2022 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

Powerful update, refactor of the whole addon.

`Features <https://bakemaster-blender-addon.readthedocs.io/en/2.0.0/pages/about.html#key-features>`__.

1.1.0 Release
=============

.. admonition:: Tag
    :class: important

    `1.1.0 - October 6th, 2022 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

Presets functionality added.

`Features <https://bakemaster-blender-addon.readthedocs.io/en/1.1.0/start/about/introduction.html#key-features>`__.

1.0.0 Release
=============

.. admonition:: Tag
    :class: important

    `1.0.0 - September 12th, 2022 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

The first release of BakeMaster Blender Addon.

`Features <https://bakemaster-blender-addon.readthedocs.io/en/1.0.0/start/about/introduction.html#key-features>`__.
