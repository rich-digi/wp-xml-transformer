# ------------------------------------------------------------------------------------------------
# Split Wordpress XML (using LXML) and commit to content branch
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
	U.logprint('cts-export.py : running at ' + U.logtime)
	U.logprint('------------------------------------------------------')
	U.logprint()	
	U.logprint('Let\'s split & commit...')	
	U.logprint()	
	U.logprint(pprint.pformat(config))
	U.logprint()	

	if os.getenv('HOME') == None:
		# Export HOME environment variable, so Git knows where to look for config files
		# when it's not running from bash
		U.logprint('Setting HOME environment variable to /home/www')	
		U.logprint()	
		os.environ['HOME'] = '/home/www'
	
	U.shexec('printenv')
	U.shexec('git config -l')

	if len(sys.argv) > 1:
		commit_message = sys.argv[1]
	else:
		U.logprint('STATUS: FAILURE: Please supply a commit message')
		U.logprint('DONE')
		U.logprint()	
		return
		
	wpxml = config['CTS_ExportTarget'] if len(sys.argv) < 3 else sys.argv[2]

	# make_export_dirs()
	# parse_xml_and_split(wpxml)
	
	U.logprint('Copying into local repo @ ' + config['GIT_ContentLocal'])
	# U.shexec('cp -pr output/* ' + config['CTS_ContentLocal'])
	U.shexec(['cp -pr', wpxml, config['GIT_ContentLocal']])

	# Commit to Git, and push to the central repo
	os.chdir(config['GIT_ContentLocal'])
	U.shexec('git add -A')
	res = U.shexec('git status')
	if 'nothing to commit' not in res:
		U.shexec('git commit -m "' + commit_message + '"')
		U.shexec('git push')
		
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
	U.create_logfile(config['CTS_ExportLogDir'] + 'cts-export-')
	
	# Run
	run();
	
	# Close logfile
	U.close_logfile()
