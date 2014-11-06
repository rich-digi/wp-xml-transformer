# --------------------------------------------------------------------------------
# Split Wordpress XML (using Element Tree)
# --------------------------------------------------------------------------------

import sys, os, re
sys.path.append('/usr/local/lib/python2.7/site-packages/')

from lxml import etree as ET
import codecs

xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'

# Register namespaces
namespaces = {
	'excerpt'	: 'http://wordpress.org/export/1.2/excerpt/',
	'content'	: 'http://purl.org/rss/1.0/modules/content/',
	'wfw'		: 'http://wellformedweb.org/CommentAPI/',
	'dc'		: 'http://purl.org/dc/elements/1.1/',
	'wp'		: 'http://wordpress.org/export/1.2/'
}

for prefix, uri in namespaces.iteritems():
    ET.register_namespace(prefix, uri)

# Now parse the XML
i = 0;
for event, elem in ET.iterparse(xmldata, ['start', 'end', 'start-ns', 'end-ns'], encoding='utf-8', strip_cdata=False, remove_blank_text=True):

	if event == 'start':
		# Remove XML namespace prefix	
		tag = ET.QName(elem.tag).localname
		
		if tag == 'item':
			print '-------------------------------------------------------------------------------'
			title = elem.find('title').text
			print title
			type = elem.find('wp:post_type', namespaces=namespaces)
			print type
			if type == None:
				type = elem.xpath('wp:post_type', namespaces=namespaces)
				print type
			
			content = elem.find('content:encoded', namespaces=namespaces)
			elem.remove(content)
		
			print type, title
			print
			
			xmlstr = ET.tostring(elem, pretty_print=True, encoding='unicode', method='xml')
			
			dir = ''.join([os.getcwd()+'/output/post__', re.sub(r'[^\w]', '_', title.lower())])
			print dir
			
			if not os.path.exists(dir): os.makedirs(dir)

			f = codecs.open(dir+'/meta.xml', 'w', 'utf-8');
			f.write(xmlstr)
			f.close()
			
			f = codecs.open(dir+'/contnet.html', 'w', 'utf-8');
			f.write(content.text)
			f.close()

			i += 1
