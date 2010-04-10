#!/usr/bin/python
# coding: utf-8
import os, re, sys
import functools
from cStringIO import StringIO
import pygments_support
import imgmathhack
import config
from utils import *

def init_publisher():
    from docutils.core import Publisher
    from docutils.io import StringOutput
    p = Publisher(destination_class=StringOutput)
    p.set_components('standalone', 'restructuredtext', 'html')
    p.get_settings()
    return p

def load_articles():
    src_dir = 'src/'
    filename_reg = re.compile(r'^(\d+-\d+-\d+)_(.*)')
    for fullname in sys.stdin.readlines():
        fullname = fullname.strip()
        filename = os.path.basename(fullname)
        if filename.endswith('.txt'):
            m = filename_reg.match(filename)
            if m:
                date = m.group(1)
                print date, m.group(2)
                yield Klass(date=date, fullname=fullname, filename=filename, filename_noext=os.path.splitext(filename)[0])

def parse_doclist(p, article_list):
    for article in article_list:
        result = imgmathhack.process(open(article.fullname).read(), {'m': imgmathhack.texmath}, None,
                {'m': imgmathhack.texdisplay})

        p.set_source(source=StringIO(result), source_path=article.fullname)
        p.document = p.reader.read(p.source, p.parser, p.get_settings())
        p.apply_transforms()
        article.doc = p.document
        article.ndoc = p.reader.new_document()
        yield article

def trans_doclist(article_list):
    # 算法，从文档中萃取简介和目录
    # 简单段落，取第一段
    # 有标题的段落，取标题和第一段
    # 有标题有topic的，取标题和topic
    # 有标题有topic的有简介的，取标题和topic和简介
    for article in article_list:
        doc,ndoc = article.doc,article.ndoc
        rootlist = filter(lambda n:n.tagname!='decoration', doc.children)
        resultlist = []
        if rootlist[0].tagname == 'title':
            article.title = rootlist[0].astext()
            if len(rootlist)>2 and rootlist[1].tagname == 'paragraph' and rootlist[2].tagname == 'topic':
                resultlist = rootlist[1:3]
            else:
                resultlist = rootlist[1:2]
        else:
            article.title = u'吐槽'
            resultlist = rootlist[:]

        ndoc.children = resultlist
        yield article

def writedoc(p, article):
    buf = StringIO()
    p.set_destination()
    p.writer.write(article.ndoc, p.destination)
    p.writer.assemble_parts()
    article.content = p.writer.parts['fragment']
    #article.title = p.writer.parts['title'].strip()
    #article.content = p.destination.destination.decode('utf-8')
    return article

def render(articles):
    from mako.lookup import TemplateLookup
    loader = TemplateLookup(directories=['./templates'], output_encoding='utf-8', input_encoding='utf-8')
    indextpl = loader.get_template('index_tpl.mako')
    html = indextpl.render(articles=articles, cfg=config)
    open('html/index.html', 'w').write(html)

if __name__ == '__main__':
    p = init_publisher()    
    articles = map(functools.partial(writedoc, p), trans_doclist(parse_doclist(p, load_articles())))
    render(articles)