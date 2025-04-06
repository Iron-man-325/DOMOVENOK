import os
import sys
import django

sys.path.insert(0, os.path.abspath("../.."))
os.environ['DJANGO_SETTINGS_MODULE'] = 'house_checker.settings'
django.setup()


project = 'sv'
copyright = '2024, KriptYashka'
author = 'KriptYashka'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['source']

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
# html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
