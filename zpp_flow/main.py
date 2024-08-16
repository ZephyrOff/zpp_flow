import impmagic


class Flow:
	@impmagic.loader(
		{'module':'os'},
		{'module':'zpp_config', 'submodule': ['Config']},
		{'module':'os.path', 'submodule': ['abspath', 'expanduser', 'exists', 'join', 'dirname']}
	)
	def __init__(self):
		if os.name=="nt":
			self.flow_folder = expanduser("~\\AppData\\Local\\zpp_flow\\.config")
		else:
			self.flow_folder = expanduser("~/.config/zpp_flow/.config")

		self.ini_file = join(self.flow_folder,"flow.ini")

		if not exists(self.ini_file):
			if not exists(self.flow_folder):
				os.makedirs(self.flow_folder)
			print("Création du fichier de config")
			self.conf = Config(self.ini_file, auto_create = True)
			if os.name=="nt":
				self.conf.add(val="flow_base", key=join("~\\AppData\\Local\\zpp_flow\\.config", "base"), section="general")
			else:
				self.conf.add(val="flow_base", key=join("~/.config/zpp_flow/.config", "base"), section="general")

		else:
			self.conf = Config(self.ini_file)

		#Création du répertoire base s'il n'existe pas
		self.flow_base = expanduser(self.conf.load('flow_base', section='general'))
		if not exists(self.flow_base):
			makedirs(self.flow_base)


	@impmagic.loader(
		{'module':'os'}
	)
	def open_base(self):
		os.startfile(self.flow_base)


	@impmagic.loader(
		{'module':'logs', 'submodule': ['logs', 'print_nxs']},
		{'module':'runner', 'submodule': ['run_task', 'run_flow']},
		{'module':'analyse', 'submodule': ['tree_plugin']},
		{'module':'datetime', 'submodule': ['datetime']},
		{'module':'time'},
		{'module':'re'}
	)
	def start(self, task_name, parameter, only_task=False, only_flow=False, starter=None, repeat=None, debug=False):
		data = tree_plugin(self.flow_base)
		
		task_data = None

		if parameter[0] in data['flow'] and (only_flow or (not only_task and not only_flow)):
			task_data = data['flow'][parameter[0]]
		
		if parameter[0] in data['task'] and (only_task or (not only_task and not only_flow)):
			task_data = data['task'][parameter[0]]


		if task_data and len(task_data):
			if starter:
				matcher_starter = re.match(r"^(?P<starter_hour>\d{2}):(?P<starter_minute>\d{2})(:(?P<starter_second>\d{2}))?$", starter)
				if matcher_starter:
					wait = True
					logs(f"Démarrage à {starter}")
					while wait:
						now = datetime.now()

						if now.hour==int(matcher_starter.group('starter_hour')) and now.minute==int(matcher_starter.group('starter_minute')) and (not matcher_starter.group('starter_second') or now.second==int(matcher_starter.group('starter_second'))):
							wait=False
						else:
							time.sleep(1)

				else:
					logs("Format started invalide", "critical")
					return

			if 'is_task' in task_data[0] and task_data[0]['is_task']:
				rtype = "task"
				run_func = run_task
			else:
				rtype = "flow"
				run_func = run_flow

			if repeat:
				matcher = re.match(r"^(?P<repeat_value>\d{1,})(?P<repeat_type>(s|m|h|d)?)$", repeat)
				if matcher:
					timer = int(matcher.group('repeat_value'))

					if matcher.group('repeat_type'):
						if matcher.group('repeat_type')=="m":
							timer *= 60
						elif matcher.group('repeat_type')=="h":
							timer *= 3600
						elif matcher.group('repeat_type')=="d":
							timer *= 86400

					try:
						while True:
							if rtype=="task":
								print_nxs(f"Démarrage de la task {task_name}", color="magenta")
							else:
								print_nxs(f"Démarrage du flow {task_name}", color="magenta")
							run_func(task_name, task_data, parameter, self.flow_base,debug=debug)
							print_nxs(f"Attente de la prochaine itération", color="magenta")
							time.sleep(timer)
					except KeyboardInterrupt:
						logs("Arrêt demandé")
				else:
					logs("Format de repeat invalide", "critical")
			else:
				if rtype=="task":
					print_nxs(f"Démarrage de la task {task_name}", color="magenta")
				else:
					print_nxs(f"Démarrage du flow {task_name}", color="magenta")
				run_func(task_name, task_data, parameter, self.flow_base, debug=debug)

		else:
			logs(f"task {task_name} non trouvé", "warning")


	#Afficher la liste des task et flow
	@impmagic.loader(
		{'module':'analyse', 'submodule': ['tree_plugin']}
	)
	def list(self):
		data = tree_plugin(self.flow_base)

		return data['task'].keys(), data['flow'].keys()


	#Afficher le détail des task et flow
	@impmagic.loader(
		{'module':'analyse', 'submodule': ['tree_plugin']}
	)
	def details(self):
		return tree_plugin(self.flow_base)


	@impmagic.loader(
		{'module':'base', 'submodule': ['pull_code']}
	)
	def pull_base(self, filename, output=None):
		pull_code(filename, self.flow_base, output)


	@impmagic.loader(
		{'module':'base', 'submodule': ['push_code']}
	)
	def push_base(self, filename, dest=None):
		push_code(filename, self.flow_base, dest)


	@impmagic.loader(
		{'module':'base', 'submodule': ['pop_code']}
	)
	def pop_base(self, filename):
		pop_code(filename, self.flow_base)



"""
doc
exécution d'un flow dans une sandbox (reprendre code nexus)
"""
