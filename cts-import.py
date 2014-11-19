# ------------------------------------------------------------------------------------------------
# Split Wordpress XML (using LXML)
# ------------------------------------------------------------------------------------------------

import sys, os, re, pprint, codecs, datetime, subprocess
# sys.path.append('/usr/local/lib/python2.7/site-packages/')

# from lxml import etree as ET
# from phpserialize import serialize, unserialize

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


# ------------------------------------------------------------------------------------------------
# Utility functions

def make_dir(dir):
	dir = os.getcwd() + dir
	if not os.path.exists(dir): os.makedirs(dir)


def write_utf8_file(fp, ustr):
	f = codecs.open(os.getcwd()+fp, 'w', 'utf-8');
	f.write(ustr)
	f.close()


def logprint(ustr=''):
	# Unicode-safe logger
	print ustr
	lfp.write(ustr+'\n')


def shexec(cmd):
	try:
		res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
	except:
		res = 'ERROR: Shell command error, running ' + cmd
	logprint(res)
	return res


def parse_shellvars(file_name):
	TIC = "'"
	QUOTE = '"'
	return_dict = dict()
	with open(file_name) as reader:
		for line in reader.readlines():
			line = re.sub(r"export\s+", "", line.strip())
			if "=" in line:
				key, value = line.split("=", 1)
				# Values that are wrapped in tics:	remove the tics but otherwise leave as is
				if value.startswith(TIC):
					# Remove first tic and everything after the last tic
					last_tic_position = value.rindex(TIC)
					value = value[1:last_tic_position]
					return_dict[key] = value
					continue
				# Values that are wrapped in quotes:  remove the quotes and optional trailing comment
				elif value.startswith(QUOTE): # Values that are wrapped quotes
					value = re.sub(r'^"(.+?)".+', '\g<1>', value)
				# Values that are followed by whitespace or comments:  remove the whitespace and/or comments
				else:
					value = re.sub(r'(#|\s+).*', '', value)
				for variable in re.findall(r"\$\{?\w+\}?", value):
					# Find embedded shell variables
					dict_key = variable.strip("${}")
					# Replace them with their values
					value = value.replace(variable, return_dict.get(dict_key, ""))
				# Add this key to the dictionary
				return_dict[key] = value
	return return_dict


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
	os.chdir(config['GIT_ContentLocal'])
	shexec('pwd')
	shexec('git pull')

	# parse_html_xml_and_join()

	logprint('Copying into import area @')
	shexec(' '.join(['cp -pr', config['GIT_ContentLocal'], config['GIT_ImportTarget']]))
		
	# res = trigger_import()
	
	logprint()	
	logprint('STATUS: SUCCESS')
	logprint('DONE')
	logprint()
	

# --------------------------------------------------------------------------------


if __name__ == '__main__':

	# Parse config file
	config = parse_shellvars('bizclub-instance.cfg')

	# Create logfile as global
	today 	= datetime.datetime.today()
	logtime = today.strftime('%Y-%m-%d-%H-%M-%S')
	logfile = config['CTS_ImportLogDir'] + 'cts-import-' + logtime + '.log'
	lfp 	= codecs.open(logfile, 'w', 'utf-8')
	
	# Run
	run();
	
	# Close logfile
	lfp.close()
