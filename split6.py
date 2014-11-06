# --------------------------------------------------------------------------------
# Split Wordpress XML (using Element Tree)
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


def write_utf8_file(fp, ustr):
	f = codecs.open(fp, 'w', 'utf-8');
	f.write(ustr)
	f.close()


# Parse the XML using ElementTree's streaming SAX-like parser
for event, elem in ET.iterparse(xmldata, strip_cdata=False, remove_blank_text=True):

	# Process on 'end' event (not 'start', as using start the element MAY not have fully loaded)
	if event == 'end':
		
		# Remove XML namespace prefix	
		tag = ET.QName(elem.tag).localname
		
		if tag == 'item':
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
				dir = os.getcwd()+'/output/'+type+'__'+dir_suffix
				if not os.path.exists(dir): os.makedirs(dir)

				xmlstr = ET.tostring(elem, pretty_print=True, encoding='unicode', method='xml')
				write_utf8_file(dir+'/meta.xml', xmlstr)
				write_utf8_file(dir+'/content.html', content.text)
				write_utf8_file(dir+'/excerpt.html', excerpt.text)
