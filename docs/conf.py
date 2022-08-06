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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Local Varibles ----------------------------------------------------------

bakemaster_version = '1.0'

# -- Project information -----------------------------------------------------

project = 'BakeMaster %s Documentation' % bakemaster_version
copyright = ': This page is licensed under a CC-BY-SA 4.0 Int. License'
author = 'kemplerart'
version = bakemaster_version

# The full version, including alpha/beta/rc tags
release = bakemaster_version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "default"
try:
    import sphinx_rtd_theme
    html_theme = "sphinx_rtd_theme"
    del sphinx_rtd_theme
except ModuleNotFoundError:
    pass

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# A list of paths that contain custom themes, either as subdirectories
# or as zip files. Relative paths are taken as relative to
# the configuration directory.
html_theme_path = ['_static/css/theme.css']

if html_theme == "sphinx_rtd_theme":
    html_theme_options = {
        # included in the title
        "display_version": False,
        "collapse_navigation": True,
        "navigation_depth": -1,
        "logo_only": True,
        "display_version": True,
        "style_nav_header_background": "black",
        "style_external_links": True
    }

    extensions.append('sphinx_rtd_theme')

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
html_logo = "_static/bakemaster-addon-logo-master-doc-64.png"

# If given, this must be the name of an image file
# (path relative to the configuration directory) that is the favicon of
# the docs, or URL that points an image file for the favicon.
html_favicon = "_static/bakemaster-addon-logo-64.png"

# If this is not None, a ‘Last updated on:’ timestamp is inserted at
# every page bottom, using the given strftime() format.
# The empty string is equivalent to '%b %d, %Y'
# (or a locale-dependent equivalent).
html_last_updated_fmt = '07/30/2022'

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


# -- Options for HTML help output --------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'BakeMaster Documentation'