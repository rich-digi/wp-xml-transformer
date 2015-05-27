# --------------------------------------------------------------------------------
# Rewrite Wordpress XML (using LXML)
# --------------------------------------------------------------------------------

import sys, os, re, operator, codecs, shutil, sqlite3
sys.path.append('/usr/local/lib/python2.7/site-packages/')

from lxml import etree as ET

from StringIO import StringIO

#xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'
xmldata = '../bizclub-content/xml/bizclub.xml'
xmldata = '../bizclub-content/xml/communications.xml'
xmldata = '../bizclub-content/xml/customerservice.xml'
xmldata = '../bizclub-content/xml/finance.xml'
xmldata = '../bizclub-content/xml/personaldevelopment.xml'
# xmldata = '../bizclub-content/xml/pd.xml'
# xmldata = '../bizclub-content/xml/salesandmarketing.xml'


# Hardwire site_path (no trailing slash)
site_path = '/home/sites/_default/www'

# Register Wordpress XML namespaces
namespaces = {
	'wp'		: 'http://wordpress.org/export/1.2/',
	'excerpt'	: 'http://wordpress.org/export/1.2/excerpt/',
	'content'	: 'http://purl.org/rss/1.0/modules/content/',
	'wfw'		: 'http://wellformedweb.org/CommentAPI/',
	'dc'		: 'http://purl.org/dc/elements/1.1/',
}

"""
# REGISTER NAMESPACE WHEN WRITING ONLY
for prefix, uri in namespaces.iteritems():
    ET.register_namespace(prefix, uri)
"""

def make_dir(dir):
	dir = os.getcwd() + dir
	if not os.path.exists(dir): os.makedirs(dir)


def write_utf8_file(fp, ustr):
	f = codecs.open(os.getcwd()+fp, 'w', 'utf-8')
	f.write(ustr)
	f.close()
    
    
make_dir('/output-nonsplit/xml')
make_dir('/output-nonsplit/resources')


print """
----------------------------------------------------

rewrite-only.py

REWRITE WORDPRESS XML INTO ENTITIES,
AND STORE ASSOCIATED RESOURCES

----------------------------------------------------
"""

_illegal_unichrs = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F), 
                        (0x7F, 0x84), (0x86, 0x9F), 
                        (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF)] 
if sys.maxunicode >= 0x10000:  # not narrow build 
	_illegal_unichrs.extend([(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), 
							 (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF), 
							 (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF), 
							 (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), 
							 (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF), 
							 (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF), 
							 (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), 
							 (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)]) 

_illegal_ranges = ["%s-%s" % (unichr(low), unichr(high)) for (low, high) in _illegal_unichrs] 
_illegal_xml_chars_RE = re.compile(u'[%s]' % u''.join(_illegal_ranges)) 

# Filter out any invalid characters so that the document contains only the XML-legal subset of utf-8
o = codecs.open('temp.xml', 'w', 'utf-8')
f = codecs.open(xmldata, 'r', 'utf-8')
for line in f:
	line = _illegal_xml_chars_RE.sub('***', line)
	o.write(line);
o.close();


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

#generator = tree.xpath('//channel/generator')[0].text
#print '{:17s} {:83s}'.format('GENERATOR', generator)

# Setting main domain
main_domain = link

print
print 'Rewriting attacment links in XML...'
print '-----------------------------------'

# Get all the top level tags in the XML, as we'll parse on these
top_level_tags = [o.tag for o in tree.xpath('//channel/*', namespaces=namespaces)]
top_level_tags = list(set(top_level_tags))

# Open the output stream
fp = '/output-nonsplit/xml/wp.xml'
f = codecs.open(os.getcwd()+fp, 'w', 'utf-8');

# Start the XML
f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')

# Get the root element, without its children
root = tree.getroot()
root.remove(root.find('channel'))
xmlstr = ET.tostring(root, pretty_print=True, encoding='unicode', method='xml')
xmlstr = xmlstr.replace('</'+root.tag+'>', '').strip() + '\n'
f.write(xmlstr)
f.write('<channel>\n')

# Parse the XML using ElementTree's streaming SAX-like parser
context = ET.iterparse('temp.xml', tag=top_level_tags, events=('start', 'end'), strip_cdata=False, remove_blank_text=True)
depth = 0
for event, elem in context:

	# ------------------------------------------------------------------------------------------------
	# ------------------------------------------------------------------------------------------------
	# Loop efficiency optimisations (as we're only interested in the root's immediate child nodes)
	#
	if event == 'start':
		depth += 1
		if depth > 1: continue
			
	if event == 'end' and depth > 1:
		depth -= 1
		continue 
	#
	# END Loop efficiency optimisations (as we're only interested in the root's immediate child nodes)
	# ------------------------------------------------------------------------------------------------
	# ------------------------------------------------------------------------------------------------
			
	# if event == 'start':
	# 	print str(depth) + ('----' * depth) + 'ST_' + elem.tag

	#
	# ONLY PROCESS XML NOdE ON 'end' EVENT, TO ENSURE THAT IT IS ALL THERE
	# Otherwise children can occasionally go missing
	#
	
	if event == 'end':
		# print str(depth) + ('----' * depth) + 'EN_' + elem.tag

		if depth == 1:
		
			print 'Handling ' + elem.tag

			# Posts are <item>s in the WXR file
			if elem.tag == 'item':
				print '        ',
				name = elem.find('wp:post_name', namespaces=namespaces)
				if name is not None:
					print name.text
				else:
					title = elem.find('title', namespaces=namespaces)
					if title is not None:
						print title.text
					else:
						print 'NONE'
						
				# Do we have an attachment?		
				type = elem.find('wp:post_type', namespaces=namespaces)
				if type is not None and type.text == 'attachment':

					# Make a directory to store the attachment
					dir = '/output-nonsplit/resources'

					# Copy attachment
					attachment = elem.find('wp:attachment_url', namespaces=namespaces);
					if attachment is not None:
					
						ori_att_url = attachment.text
						print ori_att_url
						new_att_url = re.sub(r'http://[\w+/.-]+/', '', ori_att_url)

						ori_att_path = ori_att_url.replace(main_domain, site_path)
						new_att_path = dir + '/' + new_att_url
						try:
							shutil.copy(ori_att_path, os.getcwd() + new_att_path)
						except:
							print 'ERROR: Could not copy ' + ori_att_path
		
						# Rewrite guid and wp:attachment_url (and link?)
						attachment.text = new_att_url
						elem.find('guid').text = new_att_url
			
					else:
						print 'ERROR: Could not determine attachment URI'

			xmlstr = ET.tostring(elem, pretty_print=True, encoding='unicode', method='xml')
			xmlstr = re.sub(r'\s?xmlns:\w+="[^"]*"', '', xmlstr) # Strip namespaces		
			f.write(xmlstr)

		depth -= 1
		
		if depth == 0:
			print 'RUNNING GARBAGE COLLECTION'
			print
			elem.clear()

f.write('</channel>\n')
f.write('</'+root.tag+'>')
f.close()

print
print 'DONE'
print
