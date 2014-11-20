# ------------------------------------------------------------------------------------------------
# Utility functions

import os, re, codecs, datetime, subprocess

class dml_utils:

	def __init__(self):
		self.lfp = None
		
	
	def make_dir(self, dir):
		dir = os.getcwd() + dir
		if not os.path.exists(dir): os.makedirs(dir)


	def write_utf8_file(self, fp, ustr):
		f = codecs.open(os.getcwd()+fp, 'w', 'utf-8');
		f.write(ustr)
		f.close()


	def create_logfile(self, prefix):
		today 	= datetime.datetime.today()
		self.logtime = today.strftime('%Y-%m-%d-%H-%M-%S')
		logfile = prefix + self.logtime + '.log'
		self.lfp = codecs.open(logfile, 'w', 'utf-8')
	

	def logprint(self, ustr=''):
		# Unicode-safe logger
		print ustr
		self.lfp.write(ustr+'\n')


	def close_logfile(self):
		self.lfp.close()


	def shexec(self, cmd):
		if type(cmd) is list: cmd = ' '.join(cmd)
		self.logprint(cmd)
		try:
			res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
		except:
			res = 'ERROR: Shell command error, running ' + cmd
		self.logprint(res)
		return res


	def parse_shellvars(self, file_name):
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


