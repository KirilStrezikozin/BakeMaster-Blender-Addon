===========
Style guide
===========

We highly encourage you to obey established style guides for writing documentation. This page includes:

- :ref:`writing_style` (writing rules)
- :ref:`markup_style` (markup syntax)

.. _writing_style:

Writing Style Guide
===================

Rules to follow when writing documentation pages

Goals
-----

Overall goals for writing documentation:

User Relation
    The documentation is created for users educated in CG, especially the Blender application and its workflow. The user should be familiar with texture baking, and what it stands for. But at the same time explicable for beginners and proficients, as far as baking can be complex in particular areas.
Concise
    Baking involves many aspects that can become hard and unnecessary to be documented. BakeMaster Documentation should include particular information and description regarding its functionality and features.
Complete
    Documented features should be provided with an understandable explanation covering the whole feature, its purpose range of usage and grouped under the appropriate topic.
Polished
    The described topic should follow the established documentation style.

Content Writing
---------------

.. admonition:: **Recommended:**
    :class: tip

    - Use American English
    - Check spelling and grammar
    - Make it simple, but fulfilled appropriately
    - Keep the sentence length between 4 and 12 words
    - If you don't know what the feature you are documenting refers to, ask someone else before writing.
    - Paragraphs like Note that, Attention here, a warning should be placed in specific markdown admonition directories
    - Follow the existing documentation structure to know where to place a short description, and a full one.
    - Place enumerations or similar content in a list or table.
  
.. admonition:: **Avoid:**
    :class: DANGER

    - Long unseparated paragraphs (hard to read)
    - Writing in the first person
    - Vague language and weasel words
    - Long explanation if there is a simpler way to do it
    - Repeating information - better put a reference link

.. _markup_style:

Markup Style Guide
==================

The documentation is written in reStructuredText format files (.rst). This page is a quick tutorial about how to get around the reStructuredText markup syntax used in the BakeMaster docs.

Headings
--------

.. code-block:: rst

    ==========
    Page Title
    ==========

    Section
    =======

    Subsection
    ----------

    Subsubsection
    *************

    Another Section
    ===============

    Subsection
    ----------

.. note:: 
    Only one **Page Title** can exist on the page.

Paragraphs
----------

.. code-block:: rst

    This is a simple paragraph. It describes some information
    about an important feature. This is a simple paragraph.
    It describes some information about an important feature.
    This is a simple paragraph. It describes some information
    about an important feature. This is a simple paragraph.
    It describes some information about an important feature. 

    Another simple paragraph that is a little shorter. It
    describes some further information about an important
    feature.

.. note:: 
    Use the syntax below to write a paragraph with one-line blocks:

    .. code-block:: rst

        | This is a simple paragraph.
        | The lines will break exactly how there are here.
        | This is a simple paragraph.

Inline Markup
-------------

.. code-block:: rst

    *italic text*
    **bold text**
    ``literal``

Lists
-----

.. code-block:: rst

    - this is a bulleted list
    - bullet list second item

    1. this is a numbered list
    2. this is a numbered list
    3. this is a numbered list

    * this is also a bulleted list
    * this is also a bulleted list
        * that has some subelements
        * that has some subelements
           * that has some subelements
    * this is also a bulleted list


.. admonition:: **Renders into:**
    :class: note

    - this is a bulleted list
    - bullet list second item
    
    1. this is a numbered list
    2. this is a numbered list
    3. this is a numbered list
    
    * this is also a bulleted list
    * this is also a bulleted list
        * that has some subelements
        * that has some subelements
           * that has some subelements
    * this is also a bulleted list

Tables
------

.. code-block:: rst

    +------------------------------+-------------------------------------------+
    | Column heading               | Column heading                            |
    +------------------------------+-------------------------------------------+
    | this is a simple table       | description                               |
    +------------------------------+-------------------------+-----------------+
    | it can have nested structure | like this - two columns | in one frame    |
    +------------------------------+-------------------------+-----------------+
    | bulleted list below          | | one-line blocks                         |
    +------------------------------+ | can be written                          |
    | - item 1                     | | with some *italic* text                 |
    | - item 2                     |                                           |
    | - item 3                     |                                           |
    |                              |                                           |
    +------------------------------+-------------------------------------------+

.. admonition:: **Renders into:**
    :class: note

    +------------------------------+-------------------------------------------+
    | Column heading               | Column heading                            |
    +------------------------------+-------------------------------------------+
    | this is a simple table       | description                               |
    +------------------------------+-------------------------+-----------------+
    | it can have nested structure | like this - two columns | in one frame    |
    +------------------------------+-------------------------+-----------------+
    | bulleted list below          | | one-line blocks                         |
    +------------------------------+ | can be written                          |
    | - item 1                     | | with some *italic* text                 |
    | - item 2                     |                                           |
    | - item 3                     |                                           |
    |                              |                                           |
    +------------------------------+-------------------------------------------+

Code Blocks
-----------

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_bake : bpy.props.BoolProperty
    ...

Class code block like the one above can be written using a ``code-block``:

.. code-block:: rst

    .. code-block:: python
        :caption: properties.py
        :emphasize-lines: 2

        ...
        use_bake : bpy.props.BoolProperty
        ...

Properties and classes
----------------------

.. py:property:: map.use_bake
    :noindex:

.. py:class:: map
    :noindex:

The class and the property above can be written using the syntax below:

.. code-block:: rst

    .. py:property:: map.use_bake
        :noindex:

    .. py:class:: map
        :noindex: 

Images
------

**Image with a caption under it:**

.. code-block:: rst

    .. figure:: /images/documentation/index_page/teaser_social_1200x600.png

        Image caption.

**Image reference:**

.. code-block:: rst

    .. |image_ref_name| image:: /images/documentation/index_page/teaser_social_1200x600.png
        :alt: alternative text
        :width: 600 px
        :height: 300 px
        :class: float-right

    |image_ref_name|

    This paragraph is a simple paragraph about some paragraphical paragrof.

.. hint:: 
    ``:class: float-right`` will make the image right-floated.

File Paths
----------

.. code-block:: rst

    :file:`docs/_static/css/theme.css`

Admonition Directories
----------------------

.. code-block:: rst

    .. note::
        this is a short note.

    .. attention::
        attention here, please.

    .. warning:: 
        please keep in mind that...

    .. DANGER::
        Oh no! **frightened**.

    .. tip::
        Here is some tip.
    
    .. hint::
        There is a hidden treasure.
    
    .. admonition:: Custom Admonition title
        :class: seealso

        Custom admonition with a ``:class:`` as its class type and text.

**Render into:**

.. note::
    this is a short note.

.. attention::
    attention here, please.

.. warning:: 
    please keep in mind that...

.. DANGER::
    Oh no! **frightened**.

.. tip::
    Here is some tip.

.. hint::
    There is a hidden treasure.

.. admonition:: Custom Admonition title
    :class: seealso

    Custom admonition with a ``:class:`` as its class type and text.

Links, References and Cross-references
--------------------------------------

**External link:**

.. code-block:: rst

    `Link Title <https://link-to-the-webiste>`__

**Reference within the page:**

.. code-block:: rst

    .. _my_reference:

    Document section
    ----------------

    Some important text goes there. Some important text goes there.
    Some important text goes there.

    ...

    To reference that section, use :ref:`my_reference`.

**For a reference to another document:**

.. code-block:: rst

    :doc:`Title /path/to/file`


Further Reading
---------------

To learn more about reStructuredText, you can visit the following websites:

`Sphinx RST Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`__
    A brief introduction to reStructuredText (reST) concepts and syntax
`Tutorial on GitHub <https://github.com/DevDungeon/reStructuredText-Documentation-Reference/blob/master/README.rst>`__
    reStructuredText (RST) Tutorial