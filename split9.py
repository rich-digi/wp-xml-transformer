# --------------------------------------------------------------------------------
# Split Wordpress XML (using LXML)
# --------------------------------------------------------------------------------

import sys, os, re, codecs, shutil, sqlite3
sys.path.append('/usr/local/lib/python2.7/site-packages/')

from lxml import etree as ET

#xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'
xmldata = 'input/wp.xml'

# Hardwire site_path (no trailing slash)
site_path = '/Users/richardknight/Documents/WORKAREA/DML/NOT-NEEDED/_GIT/wp-xml-transformer'

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


make_dir('/output/posts')
make_dir('/output/authors')
make_dir('/output/categories')
make_dir('/output/terms')


print """
----------------------------------------------------

split9.py

SPLIT WORDPRESS XML INTO ENTITIES,
AND STORE ASSOCIATED RESOURCES

----------------------------------------------------
"""
print
print 'Gathering blog info...'
print

# Get general blog info
tree = ET.parse(xmldata)

title = tree.xpath('//channel/title')[0].text
print '{:17s} {:83s}'.format('SITE NAME', title)

link = tree.xpath('//channel/link')[0].text
print '{:17s} {:83s}'.format('DOMAIN', link)

description = tree.xpath('//channel/description')[0].text
print '{:17s} {:83s}'.format('DESCRIPTION', description)

pubDate = tree.xpath('//channel/pubDate')[0].text
print '{:17s} {:83s}'.format('PUBLICATION DATE', pubDate)

language = tree.xpath('//channel/language')[0].text
print '{:17s} {:83s}'.format('LANGUAGE', language)

wxr_version = tree.xpath('//channel/wp:wxr_version', namespaces=namespaces)[0].text
print '{:17s} {:83s}'.format('WXR VERSION', wxr_version)

base_site_url = tree.xpath('//channel/wp:base_site_url', namespaces=namespaces)[0].text
print '{:17s} {:83s}'.format('BASE SITE URL', base_site_url)

base_blog_url = tree.xpath('//channel/wp:base_blog_url', namespaces=namespaces)[0].text
print '{:17s} {:83s}'.format('BASE BLOG URL', base_blog_url)

generator = tree.xpath('//channel/generator')[0].text
print '{:17s} {:83s}'.format('GENERATOR', generator)

# Setting main domain
main_domain = link


conn = sqlite3.connect('post_ids.db')
with conn:
    cur = conn.cursor()    
    cur.execute('DROP TABLE IF EXISTS AuthorIDs')
    cur.execute('DROP TABLE IF EXISTS CategoryIDs')
    cur.execute('DROP TABLE IF EXISTS TermIDs')
    cur.execute('DROP TABLE IF EXISTS PostIDs')
    cur.execute('CREATE TABLE AuthorIDs(id INT, login TEXT)')
    cur.execute('CREATE TABLE CategoryIDs(id INT, parent INT, nicename TEXT)')
    cur.execute('CREATE TABLE TermIDs(id INT, something TEXT)')
    cur.execute('CREATE TABLE PostIDs(id INT, parent INT, type TEXT, name TEXT)')


# Get authors, categories and terms

print
print 'Parsing and splitting authors...'
print '--------------------------------'
authors = tree.xpath('//channel/wp:author', namespaces=namespaces)
for author in authors:
	author_id 		= author.find('wp:author_id', 		namespaces=namespaces).text 
	author_login 	= author.find('wp:author_login', 	namespaces=namespaces).text 
	print 'Inserting DB record and writing XML for ' + author_login
	cur.execute('INSERT INTO AuthorIDs VALUES(?, ?)', (int(author_id), author_login))
	xmlstr = ET.tostring(author, pretty_print=True, encoding='unicode', method='xml')
	write_utf8_file('/output/authors/'+author_login+'.xml', xmlstr)
conn.commit()


print
print 'Parsing categories to compile TermID data...'
print '--------------------------------------------'
cats = tree.xpath('//channel/wp:category', namespaces=namespaces)
for cat in cats:
	term_id	 = cat.find('wp:term_id', 			namespaces=namespaces).text 
	cat_par	 = cat.find('wp:category_parent', 	namespaces=namespaces).text # What does this look like, when a category has a parent?
	nicename = cat.find('wp:category_nicename', namespaces=namespaces).text 
	print 'Inserting DB record for ' + nicename
	cur.execute('INSERT INTO CategoryIDs VALUES(?, ?, ?)', (int(term_id), int(cat_par or 0), nicename))

print
print 'Splitting categories...'
print '-----------------------'
for cat in cats:
	nicename = cat.find('wp:category_nicename', namespaces=namespaces).text 
	print 'Writing XML for ' + nicename
	xmlstr = ET.tostring(cat, pretty_print=True, encoding='unicode', method='xml')
	write_utf8_file('/output/categories/'+nicename+'.xml', xmlstr)
conn.commit()


print
print 'Parsing and splitting terms...'
print '------------------------------'
terms = tree.xpath('//channel/wp:term', namespaces=namespaces)
for term in terms:
	term_id		  = term.find('wp:term_id', 		namespaces=namespaces).text 
	term_taxonomy = term.find('wp:term_taxonomy', 	namespaces=namespaces).text 
	print 'Inserting DB record and writing XML for ' + term_taxonomy
	cur.execute('INSERT INTO TermIDs VALUES(?, ?)', (int(term_id), term_taxonomy))
	xmlstr = ET.tostring(term, pretty_print=True, encoding='unicode', method='xml')
	write_utf8_file('/output/terms/'+term_taxonomy+'.xml', xmlstr)


print
print 'Parsing posts to compile PostID data...'
print '---------------------------------------'
# Parse the XML using ElementTree's streaming SAX-like parser, looking for 'items'
for event, elem in ET.iterparse(xmldata, tag='item', strip_cdata=False, remove_blank_text=True):
	
	post_id 	= elem.find('wp:post_id', 		namespaces=namespaces).text
	post_par 	= elem.find('wp:post_parent', 	namespaces=namespaces).text
	type  		= elem.find('wp:post_type', 	namespaces=namespaces).text
	name  		= elem.find('wp:post_name', 	namespaces=namespaces).text
	print 'Inserting DB record for ' + type + ':' + str(name or '')
	cur.execute('INSERT INTO PostIDs VALUES(?, ?, ?, ?)', (int(post_id), int(post_par), type, name))

conn.commit()


print
print 'Splitting posts...'
print '------------------'
# Parse the XML using ElementTree's streaming SAX-like parser, looking for 'items'
for event, elem in ET.iterparse(xmldata, tag='item', strip_cdata=False, remove_blank_text=True):

	title 	= elem.find('title').text
	post_id = elem.find('wp:post_id', 		namespaces=namespaces).text
	type  	= elem.find('wp:post_type', 	namespaces=namespaces).text
	name  	= elem.find('wp:post_name', 	namespaces=namespaces).text

	print '{:5s} {:15s} {:100s} {:100s}'.format(post_id, type, title, name)
	
	content = elem.find('content:encoded', 	namespaces=namespaces)
	excerpt = elem.find('excerpt:encoded', 	namespaces=namespaces)
	elem.remove(content)
	elem.remove(excerpt)
	
	if title is not None:
	
		dir_suffix = name
		if dir_suffix is None:
			dir_suffix = re.sub(r'[^\w]', '_', title.lower())
		dir = '/output/posts/'+type+'__'+dir_suffix
		make_dir(dir)

		if type == 'attachment':
			# Rewrite guid and wp:attachment_url (and link?)
			attachment = elem.find('wp:attachment_url', namespaces=namespaces);
			ori_att_url = attachment.text
			new_att_url = re.sub(r'http://[\w+/.-]+/', '', ori_att_url)
			attachment.text = new_att_url
			elem.find('guid').text = new_att_url
			
			# Copy attachment
			ori_att_path = ori_att_url.replace(main_domain, site_path)
			new_att_path = dir + '/' + new_att_url
			try:
				shutil.copy(ori_att_path, os.getcwd() + new_att_path)
			except:
				print 'ERROR: Could not copy ' + ori_att_path
				
		xmlstr = ET.tostring(elem, pretty_print=True, encoding='unicode', method='xml')
		write_utf8_file(dir+'/meta.xml', xmlstr)
		if content.text:
			write_utf8_file(dir+'/content.html', content.text)
		if excerpt.text:
			write_utf8_file(dir+'/excerpt.html', excerpt.text)

print
print 'DONE'
print

