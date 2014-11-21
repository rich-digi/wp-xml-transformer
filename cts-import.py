# ------------------------------------------------------------------------------------------------
# Pull content from branch and rebuild Wordpress XML (using LXML)
# ------------------------------------------------------------------------------------------------

import sys, os, re, pprint, codecs, datetime, subprocess
# sys.path.append('/usr/local/lib/python2.7/site-packages/')

# from lxml import etree as ET
# from phpserialize import serialize, unserialize

from dml_utils import dml_utils

class trml:
	BLACK 	= '\033[30m'
	RED 	= '\033[31m'
	GREEN 	= '\033[32m'
	BOLD	= '\033[1m'
	NORMAL	= '\033[0;0m'

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


# --------------------------------------------------------------------------------
# RUN

def run():
	U.logprint()	
	U.logprint('------------------------------------------------------')
	U.logprint('cts-import.py : running at ' + U.logtime)
	U.logprint('------------------------------------------------------')
	U.logprint()	
	U.logprint('Let\'s join & import...')	
	U.logprint()	
	U.logprint(pprint.pformat(config))
	U.logprint()	

	if len(sys.argv) > 1: revision = sys.argv[1]
		
	# Pull latest version from central Git repo
	scdir = os.getcwd()
	os.chdir(config['GIT_ContentLocal'])
	U.shexec('git pull')

	# parse_html_xml_and_join()

	os.chdir(scdir)
	U.logprint('Copying into import area @ ' + config['CTS_ImportTarget'])
	U.shexec(' '.join(['cp -pr', config['GIT_ContentLocal']+'/*', config['CTS_ImportTarget']]))
		
	# res = trigger_import()
	
	U.logprint()	
	U.logprint('STATUS: SUCCESS')
	U.logprint('DONE')
	U.logprint()
	

# --------------------------------------------------------------------------------


if __name__ == '__main__':

	# Change the CWD to this file's directory, so relative paths work
	os.chdir(os.path.dirname(os.path.realpath(__file__)))

	# Initialise utilities
	U = dml_utils()
	
	# Parse config file
	config = U.parse_shellvars('bizclub-instance.cfg')

	# Create logfile as global
	U.create_logfile(config['CTS_ImportLogDir'] + 'cts-import-')
	
	# Run
	run();
	
	# Close logfile
	U.close_logfile()
