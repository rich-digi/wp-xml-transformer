# --------------------------------------------------------------------------------
# Split Wordpress XML (using Element Tree)
# --------------------------------------------------------------------------------

import xml.etree.ElementTree as ET
# xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'
xmldata = 'input/test.xml'

for event, elem in ET.iterparse(xmldata, ['start', 'end', 'start-ns', 'end-ns']):
	if event == 'start':
		
		if elem.tag == 'country':
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
		
		if elem.tag == 'country':
			print
			print 'END COUNTRY'
			print '-------------------------------------------------------------------------------'
			print
			
			xmlstr = ET.tostring(elem, encoding='utf8', method='xml')
			print xmlstr
		
