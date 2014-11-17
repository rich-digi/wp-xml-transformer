# ------------------------------------------------------------------------------------------------
# Split Wordpress XML (using LXML)
# ------------------------------------------------------------------------------------------------

import sys, os, re, codecs, datetime, subprocess, shlex
# sys.path.append('/usr/local/lib/python2.7/site-packages/')

from lxml import etree as ET
from phpserialize import serialize, unserialize

class trml:
	BLACK 	= '\033[30m'
	RED 	= '\033[31m'
	GREEN 	= '\033[32m'
	BOLD	= '\033[1m'
	NORMAL	= '\033[0;0m'

class config:
	REPO 	= '../bizclub-content'

xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'
#xmldata = 'input/ginger.xml'

# Wordpress XML namespaces
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


# ------------------------------------------------------------------------------------------------
# Utility functions

def make_dir(dir):
	dir = os.getcwd() + dir
	if not os.path.exists(dir): os.makedirs(dir)


def write_utf8_file(fp, ustr):
	f = codecs.open(os.getcwd()+fp, 'w', 'utf-8');
	f.write(ustr)
	f.close()


def logprint(ustr=''):
	# Unicode-safe logger
	print ustr
	lfp.write(ustr+'\n')


def shexec(cmd):
	try:
		res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
	except:
		res = 'ERROR: Shell command error, running ' + cmd
	logprint(res)
	return res


# ------------------------------------------------------------------------------------------------
# Export routine

def make_export_dirs():
	make_dir('/output/_WP-META/authors')
	make_dir('/output/_WP-META/categories')
	make_dir('/output/_WP-META/terms')


def parse_xml_and_split(xmldata):
	
	tree = ET.parse(xmldata)

	# ---------------------
	# Get general blog info

	title = tree.xpath('//channel/title')[0].text
	logprint(title)

	link = tree.xpath('//channel/link')[0].text
	logprint(link)

	description = tree.xpath('//channel/description')[0].text
	logprint(description)

	pubDate = tree.xpath('//channel/pubDate')[0].text
	logprint(pubDate)

	language = tree.xpath('//channel/language')[0].text
	logprint(language)

	wxr_version = tree.xpath('//channel/wp:wxr_version', namespaces=namespaces)[0].text
	logprint(wxr_version)

	base_site_url = tree.xpath('//channel/wp:base_site_url', namespaces=namespaces)[0].text
	logprint(base_site_url)

	base_blog_url = tree.xpath('//channel/wp:base_blog_url', namespaces=namespaces)[0].text
	logprint(base_blog_url)

	generator = tree.xpath('//channel/generator')[0].text
	logprint(generator)


	# ---------------------------------
	# Get authors, categories and terms

	authors = tree.xpath('//channel/wp:author', namespaces=namespaces)
	for author in authors:
		author_login = author.find('wp:author_login', namespaces=namespaces).text 
		logprint(author_login)
		xmlstr = ET.tostring(author, pretty_print=True, encoding='unicode', method='xml')
		write_utf8_file('/output/_WP-META/authors/'+author_login+'.xml', xmlstr)

	cats = tree.xpath('//channel/wp:category', namespaces=namespaces)
	for cat in cats:
		nicename = cat.find('wp:category_nicename', namespaces=namespaces).text 
		logprint(nicename)
		xmlstr = ET.tostring(cat, pretty_print=True, encoding='unicode', method='xml')
		write_utf8_file('/output/_WP-META/categories/'+nicename+'.xml', xmlstr)

	terms = tree.xpath('//channel/wp:term', namespaces=namespaces)
	for term in terms:
		term_taxonomy = term.find('wp:term_taxonomy', namespaces=namespaces).text 
		logprint(term_taxonomy)
		xmlstr = ET.tostring(term, pretty_print=True, encoding='unicode', method='xml')
		write_utf8_file('/output/_WP-META/terms/'+term_taxonomy+'.xml', xmlstr)
	
	
	# ------------------------------------------------------------------------------------------------
	# Parse the XML using LXML's ElementTree-compatible streaming SAX-like parser, looking for 'items'

	for event, elem in ET.iterparse(xmldata, tag='item', strip_cdata=False, remove_blank_text=True):

		title 	= elem.find('title').text
		type  	= elem.find('wp:post_type', 	namespaces=namespaces).text
		name  	= elem.find('wp:post_name', 	namespaces=namespaces).text

		logprint(u'{:15s} {:100s} {:100s}'.format(type, title, name))
	
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


	# Now find and save the locally-linked images (except service graphics)




	# ---------------
	# Comments - TODO




# --------------------------------------------------------------------------------
# RUN

def run():
	if len(sys.argv) > 1:
		commit_message = sys.argv[1]
	else:
		logprint('ERROR: Please supply a commit message')
		return
		
	make_export_dirs()
	parse_xml_and_split(xmldata)
	
	logprint('Copying into local repo')
	shexec('cp -pr output/* ' + config.REPO)

	# Commit to Git, and push to the central repo
	os.chdir(config.REPO)
	shexec('pwd')
	shexec('git add -A')
	shexec('git commit -m "' + commit_message + '"')
	shexec('git push')
		
	
if __name__ == '__main__':
	today = datetime.datetime.today()
	logtime = today.strftime('%Y-%m-%d-%H-%M-%S')
	logfile = 'log/ctr-export-' + logtime + '.log'
	lfp = codecs.open(logfile, 'w', 'utf-8')
	logprint()	
	logprint('------------------------------------------------------')
	logprint('SPLIT & COMMIT: running at ' + logtime)
	logprint('------------------------------------------------------')
	logprint()	
	run();
	logprint()
	lfp.close()
