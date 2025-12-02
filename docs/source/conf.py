# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os, sys
sys.path.insert(0, os.path.abspath('../../src/'))

import constrainthg

project = 'ConstraintHg'
copyright = '2024, John Morris'
license = 'Apache 2.0'
author = 'John Morris'
release = '0.3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax',
    # 'sphinxcontrib.youtube',
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# THEME
html_theme = 'furo'
html_static_path = ['_static']
html_favicon = './media/icon.ico'
html_logo = './media/logo.svg'
html_theme_options = {
    "sidebar_hide_name": True,
    "source_repository": "https://github.com/jmorris335/ConstraintHg",
    "source_branch": "main",
    "source_directory": "docs/source",
}
templates_path = ['_templates']

redirects = {
     "constrainthg": "api/index"
}

def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip

def setup(app):
    app.connect("autodoc-skip-member", skip)
