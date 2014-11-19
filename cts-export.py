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
	logprint()	
	logprint('------------------------------------------------------')
	logprint('cts-export.py : running at ' + logtime)
	logprint('------------------------------------------------------')
	logprint()	
	logprint('Let\'s split & commit...')	
	logprint()	
	logprint(pprint.pformat(config))
	logprint()	

	if len(sys.argv) > 1:
		commit_message = sys.argv[1]
	else:
		logprint('STATUS: FAILURE: Please supply a commit message')
		logprint('DONE')
		logprint()	
		return
		
	wpxml = config['CTS_ExportTarget'] if len(sys.argv) < 3 else sys.argv[2]

	# make_export_dirs()
	# parse_xml_and_split(wpxml)
	
	logprint('Copying into local repo @')
	# shexec('cp -pr output/* ' + config['CTS_ContentLocal'])
	shexec(['cp -pr', wpxml, config['GIT_ContentLocal']])

	# Commit to Git, and push to the central repo
	os.chdir(config['GIT_ContentLocal'])
	shexec('git add -A')
	res = shexec('git status')
	if 'nothing to commit' not in res:
		shexec('git commit -m "' + commit_message + '"')
		shexec('git push')
		
	logprint()	
	logprint('STATUS: SUCCESS')
	logprint('DONE')
	logprint()


# --------------------------------------------------------------------------------


if __name__ == '__main__':

	# Initialise utilities
	U = dml_utils()
	
	# Parse config file
	config = U.parse_shellvars('bizclub-instance.cfg')

	# Create logfile as global
	lfp = create_logfile(config['CTS_ExportLogDir'] + 'cts-export-')
	print lfp
	dml_utils.lfp = lfp
	
	# Run
	run();
	
	# Close logfile
	lfp.close()
