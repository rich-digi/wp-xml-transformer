# --------------------------------------------------------------------------------
# Split Wordpress XML (using Element Tree)
# --------------------------------------------------------------------------------

import sys
sys.path.append('/usr/local/lib/python2.7/site-packages/')

from lxml import etree as ET

# xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'
xmldata = 'input/test3.xml'

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
for event, elem in ET.iterparse(xmldata, ['start', 'end', 'start-ns', 'end-ns'], strip_cdata=False, remove_blank_text=True):

	if event == 'start':
		# Remove XML namespace prefix	
		tag = ET.QName(elem.tag).localname
		
		if tag == 'country':
			print
			print '-------------------------------------------------------------------------------'
			print 'START COUNTRY'
			print
		
		# The element's name and text
		if elem.text != None:
			print elem.tag, elem.text
		else:
			# The element's attributes
			print elem.tag,
			for name, value in elem.items():
				print name, value,
			print
			
	if event == 'end':
		# Remove XML namespace prefix	
		tag = ET.QName(elem.tag).localname
		
		if tag == 'country':
			print
			print 'END COUNTRY'
			print '-------------------------------------------------------------------------------'
			print
			
			xmlstr = ET.tostring(elem, pretty_print=True, encoding='utf8', method='xml')
			print xmlstr
		
			f = open('output/post_'+str(i)+'.xml', 'w');
			f.write(xmlstr)
			f.close()
			i += 1
