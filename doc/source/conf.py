import sphinx_rtd_theme
import lively_lights

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
extensions += ['sphinxarg.ext']

master_doc = 'index'

project = u'lively_lights'
copyright = u'2016, Josef Friedrich'
author = u'Josef Friedrich'
version = lively_lights.__version__
release = lively_lights.__version__
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'


[extensions]
todo_include_todos = True
