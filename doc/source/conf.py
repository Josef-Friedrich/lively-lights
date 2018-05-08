import sphinx_rtd_theme
import lively_lights

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = u'lively_lights'
copyright = u'2016, Josef Friedrich'
author = u'Josef Friedrich'
version = lively_lights.__version__
release = lively_lights.__version__
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'

html_static_path = []
htmlhelp_basename = 'lively_lightsdoc'

latex_elements = {
     'papersize': 'a4paper',
     'pointsize': '11pt',
}

latex_documents = [
    (master_doc, 'lively_lights.tex', u'lively_lights Documentation',
     u'Josef Friedrich', 'manual'),
]

man_pages = [
    (master_doc, 'lively_lights', u'lively_lights Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'lively_lights', u'lively_lights Documentation',
     author, 'lively_lights', 'Rename audio files from metadata tags.',
     'Miscellaneous'),
]

[extensions]
todo_include_todos = True
