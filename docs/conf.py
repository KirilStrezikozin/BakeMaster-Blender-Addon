# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Local Varibles ----------------------------------------------------------

bakemaster_version = '2.0.0'

# -- Project information -----------------------------------------------------

project = 'BakeMaster %s Documentation' % bakemaster_version
copyright = ': 2022, Kiril Strezikozin'
author = 'kemplerart'
version = bakemaster_version
branch = "dev-2.0.0"

# The full version, including alpha/beta/rc tags
release = bakemaster_version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Sphinx's own extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_issues",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    # External stuff
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_inline_tabs",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'README.md']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_title = "BakeMaster"
language = "en"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = [
    'custom/css/typography.css',
]

# A list of paths that contain custom themes, either as subdirectories
# or as zip files. Relative paths are taken as relative to
# the configuration directory.
html_theme_path = []

html_theme_options = {
    "sidebar_hide_name": True,
    "top_of_page_button": "edit",
    "footer_icons": [
        {
            "name": "BlenderMarket",
            "url": "https://blendermarket.com/products/bakemaster",
            "html": """
                <svg height="25" width="25">
                    <g transform="translate(0.000000,25.000000) scale(0.100000,-0.100000)"
                    fill="#646776" stroke="none">
                        <path d="M135 150 c10 -11 20 -20 22 -20 1 0 3 9 3 20 0 14 -7 20 -22 20 -20
                        0 -21 -1 -3 -20z"/>
                        <path d="M27 145 c-25 -24 -21 -30 19 -30 28 0 41 -6 57 -28 18 -23 19 -31 9
                        -47 -10 -16 -10 -20 1 -20 21 0 37 22 37 51 0 60 -86 111 -123 74z"/>
                        <path d="M15 80 c-10 -17 23 -60 46 -60 25 0 34 22 19 49 -11 22 -54 29 -65
                        11z"/>
                    </g>
                    <g transform="translate(0.000000,25.000000) scale(0.100000,-0.100000)"
                    fill="#a0a3b1" stroke="none">
                        <path d="M4 236 c-13 -34 0 -51 41 -53 33 -2 36 -1 18 7 -25 10 -29 30 -11 48
                        9 9 6 12 -15 12 -15 0 -30 -6 -33 -14z"/>
                        <path d="M170 68 c0 -34 20 -68 40 -68 10 0 40 29 40 38 0 4 -4 13 -9 20 -7
                        11 -9 11 -14 -2 -10 -25 -27 -19 -42 17 l-14 32 -1 -37z"/>
                    </g>
                    <g transform="translate(0.000000,25.000000) scale(0.100000,-0.100000)"
                    fill="#f4f4f4" stroke="none">
                        <path d="M43 224 c-7 -19 4 -31 40 -39 33 -9 35 4 4 33 -28 26 -36 27 -44 6z"/>
                        <path d="M170 115 c0 -17 31 -75 40 -75 22 0 22 32 0 56 -22 22 -40 31 -40 19z"/>
                    </g>
                <svg/>

            """,
            "class": "community-icon",
        },
        {
            "name": "Discord",
            "url": "https://discord.gg/2ePzzzMBf4",
            "html": """
                <svg height="25" width="35">
                    <g transform="translate(0.000000,25.000000) scale(0.100000,-0.100000)"
                    fill="#646776" stroke="none">
                        <path d="M63 238 c-29 -14 -63 -96 -63 -153 0 -42 3 -47 34 -62 20 -9 42 -13
                        53 -9 17 7 17 8 -2 22 -19 14 -18 15 10 7 37 -10 102 -10 135 -1 14 5 19 5 13
                        2 -15 -6 -17 -30 -5 -38 5 -3 28 4 52 16 l42 21 -5 49 c-9 70 -41 136 -72 148
                        -16 6 -47 7 -81 2 -30 -5 -54 -5 -54 0 0 11 -30 9 -57 -4z m71 -111 c8 -12 7
                        -21 -5 -32 -21 -21 -49 -9 -49 20 0 36 34 44 54 12z m110 1 c14 -22 -12 -52
                        -37 -42 -17 6 -23 44 -10 58 11 11 35 3 47 -16z"/>
                    </g>
                    <g transform="translate(0.000000,25.000000) scale(0.100000,-0.100000)"
                    fill="#f4f4f4" stroke="none">
                        <path d="M93 143 c-19 -7 -16 -50 4 -57 24 -10 51 20 37 41 -12 19 -23 24 -41
                        16z"/>
                        <path d="M197 144 c-13 -14 -7 -52 10 -58 25 -10 51 20 37 42 -12 19 -36 27
                        -47 16z"/>
                    </g>
                <svg/>
            """,
            "class": "community-icon",
        },
        {
            "name": "YouTube",
            "url": "https://www.youtube.com/watch?v=Cedk9L2OqAo",
            "html": """
                <svg height="25" width="35">
                    <g transform="translate(0.000000,25.000000) scale(0.100000,-0.100000)"
                    fill="#646776" stroke="none">
                        <path d="M24 236 c-16 -12 -20 -29 -22 -98 -3 -72 -1 -87 16 -108 20 -24 23
                        -25 162 -25 173 0 170 -2 170 126 0 118 -2 119 -175 119 -98 0 -136 -4 -151
                        -14z m184 -94 l23 -15 -38 -23 c-21 -13 -41 -24 -45 -24 -5 0 -8 23 -8 50 0
                        56 1 56 68 12z"/>
                    </g>
                    <g transform="translate(0.000000,25.000000) scale(0.100000,-0.100000)"
                    fill="#f4f4f4" stroke="none">
                        <path d="M140 130 c0 -27 3 -50 8 -50 4 0 24 11 45 24 l38 23 -23 15 c-67 44
                        -68 44 -68 -12z"/>
                    </g>
                <svg>
            """,
            "class": "community-icon",
        },
    ],
    "source_repository": "https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/",
    "source_branch": branch,
    "source_directory": "docs/",
    "light_css_variables": {
        "color-brand-primary": "#df4c34",
        "color-brand-content": "#df4c34",
        "color-foreground-primary": "black",
        "color-background-secondary": "#ffffff",
        "color-foreground-border" : "#ffffff",
        "color-background-border" : "#ffffff",
        "admonition-font-size": "100%",
        "admonition-title-font-size": "100%",
    },
    "dark_css_variables": {
        "color-brand-primary": "#df4c34",
        "color-brand-content": "#df4c34",
        "color-foreground-primary": "#f8f8f8",
        "color-background-secondary": "#131416",
        "color-foreground-border" : "#131416",
        "color-background-border" : "#131416",
        "admonition-font-size": "100%",
        "admonition-title-font-size": "100%",
    },
}

# The “title” for HTML documentation generated with Sphinx’s own templates.
# This is appended to the <title> tag of individual pages, and
# used in the navigation bar as the “topmost” element.
html_title = "BakeMaster Documentation"

# The base URL which points to the root of the HTML documentation.
# It is used to indicate the location of document using
# The Canonical Link Relation.
#html_baseurl = "https://docs.bakemaster.com/documentation/en/latest/"

# If given, this must be the name of an image file
# (path relative to the configuration directory) that is the logo of the docs,
# or URL that points an image file for the logo.
html_logo = "_static/images/icons/bakemaster_logo_150x150.png"

# If given, this must be the name of an image file
# (path relative to the configuration directory) that is the favicon of
# the docs, or URL that points an image file for the favicon.
html_favicon = "_static/images/icons/bakemaster_logo_64x64.png"

# If this is not None, a ‘Last updated on:’ timestamp is inserted at
# every page bottom, using the given strftime() format.
# The empty string is equivalent to '%b %d, %Y'
# (or a locale-dependent equivalent).
html_last_updated_fmt = '12/21/2022'

# If true, the reST sources are included in the HTML build as _sources/name.
html_copy_source = True

# If true (and html_copy_source is true as well), links to the reST sources
# will be added to the sidebar.
html_show_sourcelink = False

# If true, “(C) Copyright …” is shown in the HTML footer.
html_show_copyright = True

# If true, “Created using Sphinx” is shown in the HTML footer.
html_show_sphinx = False

# If true, the text around the keyword is shown as summary of each search result.
html_show_search_summary = True

# If this is True, todo and todolist produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML help output --------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'BakeMaster Documentation'

def setup(app):
    pass
    # app.builder.css_files.insert(0, '_static/custom/css/typography.css')
    # for filepath in css_files:
    #     app.add_css_file(filepath)