# --------------------------------------------------------------------------------
# Split Wordpress XML (using Element Tree)
# --------------------------------------------------------------------------------

import xml.etree.ElementTree as ET, xml.dom.minidom as minidom, xmlformatter

xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'

formatter = xmlformatter.Formatter(indent="1", indent_char="\t", encoding_output="ISO-8859-1", preserve=["literal"])

# Register namespaces
namespaces = {
	'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
	'content': 'http://purl.org/rss/1.0/modules/content/',
	'wf': 'http://wellformedweb.org/CommentAPI/',
	'dc': 'http://purl.org/dc/elements/1.1/',
	'wp': 'http://wordpress.org/export/1.2/'
}

for prefix, uri in namespaces.iteritems():
    ET.register_namespace(prefix, uri)

i = 0;
for event, elem in ET.iterparse(xmldata, ['start', 'end', 'start-ns', 'end-ns']):
	if event == 'start':
		
		if elem.tag == 'item':
			title 	= elem.find('title').text
			content = elem.find('content:encoded').text
			
			elem.remove(content)
			
			print
			print '-------------------------------------------------------------------------------'
			print 'ITEM', title
			xmlstr = ET.tostring(elem, encoding='utf8', method='xml')
			#elem.write('output/post_'+i+'.xml');
			xmlstr = formatter.format_string(xmlstr)
			f = open('output/post_'+str(i)+'.xml', 'w');
			f.write(xmlstr)
			f.close()
			i += 1
