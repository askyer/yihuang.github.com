#!/usr/bin/python
class Klass(object):
    def __init__(self, d):
        self.__dict__.update(d)

def dict2obj(d):
    return Klass(d)

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_parts, default_description
import pygments_support

# Call the docutils publisher to render the input as html::
import os
import sys
from mako.lookup import TemplateLookup
import config
loader = TemplateLookup(directories=['./templates'], output_encoding='utf-8')
listtpl = loader.get_template('detail_tpl.mako')
#indextpl = loader.get_template('index_tpl.mako')

path = './src/'
fullpath = sys.argv[1]
basename = os.path.splitext(os.path.basename(fullpath))[0]
source_url = 'src/%s.txt'%basename
parts = dict2obj(publish_parts(source=sys.stdin.read(), writer_name='html', settings_overrides={'source_url':source_url}))
content = listtpl.render(c=parts, cfg=config)

destname = os.path.join('./html/',basename+'.html')
open(destname, 'w').write(content)
print destname
