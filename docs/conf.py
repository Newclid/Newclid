# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from importlib.metadata import metadata
from typing import Any

sys.path.insert(0, os.path.abspath("../"))

package_metadata = metadata("newclid")


project = "Newclid"
copyright = "2024-2025, Mathïs Fédérico, Vladmir Sicca, Tianxiang Xia, Yury Kudryashov, Harmonic.fun"
author = "AutoMathis <automathis@protonmail.com>, Vladmir Sicca <vsiccag@gmail.com>, Tianxiang Xia <xia.tianxiang00@gmail.com>, Yury Kudryashov <yury.kudryashov@harmonic.fun>"
release = "3.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosectionlabel",
]

master_doc = "index"
autoapi_dirs = ["../benchmarks"]
autodoc_mock_imports = []
autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
}
intersphinx_mapping = {}

add_module_names = False
autoclass_content = "both"
napoleon_use_param = True
# pygments_style = 'monokai'

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "canonical_url": "",
    "logo_only": False,
    "prev_next_buttons_location": "both",
    "style_external_links": "#ff9900",
    "style_nav_header_background": "#ff9900",
    # Toc options
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}


def setup(app: Any):
    app.add_css_file("styles/custom.css")
