# ------------------------------------------------------------------------------------------------
# Pull content from branch and rebuild Wordpress XML (using LXML)
# ------------------------------------------------------------------------------------------------

import sys, os, re, pprint, codecs, datetime, subprocess
# sys.path.append('/usr/local/lib/python2.7/site-packages/')

# from lxml import etree as ET
# from phpserialize import serialize, unserialize

import dml_utils as U

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
	logprint()	
	logprint('------------------------------------------------------')
	logprint('cts-import.py : running at ' + logtime)
	logprint('------------------------------------------------------')
	logprint()	
	logprint('Let\'s join & import...')	
	logprint()	
	logprint(pprint.pformat(config))
	logprint()	

	if len(sys.argv) > 1: revision = sys.argv[1]
		
	# Pull latest version from central Git repo
	scdir = os.getcwd()
	os.chdir(config['GIT_ContentLocal'])
	shexec('git pull')

	# parse_html_xml_and_join()

	os.chdir(scdir)
	logprint('Copying into import area @ ' + config['CTS_ImportTarget'])
	shexec(' '.join(['cp -pr', config['GIT_ContentLocal']+'/*', config['CTS_ImportTarget']]))
		
	# res = trigger_import()
	
	logprint()	
	logprint('STATUS: SUCCESS')
	logprint('DONE')
	logprint()
	

# --------------------------------------------------------------------------------


if __name__ == '__main__':

	# Parse config file
	config = U.parse_shellvars('bizclub-instance.cfg')

	# Create logfile as global
	today 	= datetime.datetime.today()
	logtime = today.strftime('%Y-%m-%d-%H-%M-%S')
	logfile = config['CTS_ImportLogDir'] + 'cts-import-' + logtime + '.log'
	lfp 	= codecs.open(logfile, 'w', 'utf-8')
	dml_utils.lfp = lfp
	
	# Run
	run();
	
	# Close logfile
	lfp.close()
