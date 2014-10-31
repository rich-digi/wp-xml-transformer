# --------------------------------------------------------------------------------
# Split Wordpress XML (using SAX)
# --------------------------------------------------------------------------------

import xml.sax

class WPContentHandler(xml.sax.ContentHandler):
	def __init__(self):
		xml.sax.ContentHandler.__init__(self)
 
	def startElement(self, name, attrs):
		self.is_item = 0
		self.html    = ''
		if name == 'content:encoded':
			self.is_item = 1
			
 
	def endElement(self, name):
		if name == 'content:encoded':
			print
			print(self.html)
			print
			print
			print '----------------------------------------------------------------------------------------------------'
			print
			print
 
	def characters(self, content):
		if self.is_item == 1: 
			self.html += content
			
def main(sourceFileName):
	source = open(sourceFileName)
	xml.sax.parse(source, WPContentHandler())
 
if __name__ == '__main__':
	main('input/dmclubcustomerblog.wordpress.2014-10-29.xml')