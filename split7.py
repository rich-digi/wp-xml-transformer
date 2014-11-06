# --------------------------------------------------------------------------------
# Split Wordpress XML (using LXML)
# --------------------------------------------------------------------------------

import sys, os, re, codecs
sys.path.append('/usr/local/lib/python2.7/site-packages/')

from lxml import etree as ET

#xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'
xmldata = 'input/wp.xml'

# Register Wordpress XML namespaces
namespaces = {
	'wp'		: 'http://wordpress.org/export/1.2/',
	'excerpt'	: 'http://wordpress.org/export/1.2/excerpt/',
	'content'	: 'http://purl.org/rss/1.0/modules/content/',
	'wfw'		: 'http://wellformedweb.org/CommentAPI/',
	'dc'		: 'http://purl.org/dc/elements/1.1/',
}

"""
REGISTER NAMESPACE WHEN WRITING ONLY
for prefix, uri in namespaces.iteritems():
    ET.register_namespace(prefix, uri)
"""


def make_dir(dir):
	dir = os.getcwd() + dir
	if not os.path.exists(dir): os.makedirs(dir)


def write_utf8_file(fp, ustr):
	f = codecs.open(os.getcwd()+fp, 'w', 'utf-8');
	f.write(ustr)
	f.close()


make_dir('/output/WP-META/authors')
make_dir('/output/WP-META/categories')
make_dir('/output/WP-META/terms')


# Parse the XML using ElementTree's streaming SAX-like parser, looking for 'items'
for event, elem in ET.iterparse(xmldata, tag='item', strip_cdata=False, remove_blank_text=True):

	title 	= elem.find('title').text
	type  	= elem.find('wp:post_type', 	namespaces=namespaces).text
	name  	= elem.find('wp:post_name', 	namespaces=namespaces).text

	print '{:15s} {:100s} {:100s}'.format(type, title, name)
	
	content = elem.find('content:encoded', 	namespaces=namespaces)
	excerpt = elem.find('excerpt:encoded', 	namespaces=namespaces)
	elem.remove(content)
	elem.remove(excerpt)
	
	if title is not None:
	
		dir_suffix = name
		if dir_suffix is None:
			dir_suffix = re.sub(r'[^\w]', '_', title.lower())
		dir = '/output/'+type+'__'+dir_suffix
		make_dir(dir)

		xmlstr = ET.tostring(elem, pretty_print=True, encoding='unicode', method='xml')
		write_utf8_file(dir+'/meta.xml', xmlstr)
		write_utf8_file(dir+'/content.html', content.text)
		write_utf8_file(dir+'/excerpt.html', excerpt.text)




tree = ET.parse(xmldata)

# Get general blog info

title = tree.xpath('//channel/title')[0].text
print title

link = tree.xpath('//channel/link')[0].text
print link

description = tree.xpath('//channel/description')[0].text
print description

pubDate = tree.xpath('//channel/pubDate')[0].text
print pubDate

language = tree.xpath('//channel/language')[0].text
print language

wxr_version = tree.xpath('//channel/wp:wxr_version', namespaces=namespaces)[0].text
print wxr_version

base_site_url = tree.xpath('//channel/wp:base_site_url', namespaces=namespaces)[0].text
print base_site_url

base_blog_url = tree.xpath('//channel/wp:base_blog_url', namespaces=namespaces)[0].text
print base_blog_url

generator = tree.xpath('//channel/generator')[0].text
print generator


# Get authors, categories and terms


authors = tree.xpath('//channel/wp:author', namespaces=namespaces)
for author in authors:
	author_login = author.find('wp:author_login', namespaces=namespaces).text 
	print author_login
	xmlstr = ET.tostring(author, pretty_print=True, encoding='unicode', method='xml')
	write_utf8_file('/output/WP-META/authors/'+author_login+'.xml', xmlstr)

cats = tree.xpath('//channel/wp:category', namespaces=namespaces)
for cat in cats:
	nicename = cat.find('wp:category_nicename', namespaces=namespaces).text 
	print nicename
	xmlstr = ET.tostring(cat, pretty_print=True, encoding='unicode', method='xml')
	write_utf8_file('/output/WP-META/categories/'+nicename+'.xml', xmlstr)

terms = tree.xpath('//channel/wp:term', namespaces=namespaces)
for term in terms:
	term_taxonomy = term.find('wp:term_taxonomy', namespaces=namespaces).text 
	print term_taxonomy
	xmlstr = ET.tostring(term, pretty_print=True, encoding='unicode', method='xml')
	write_utf8_file('/output/WP-META/terms/'+term_taxonomy+'.xml', xmlstr)
