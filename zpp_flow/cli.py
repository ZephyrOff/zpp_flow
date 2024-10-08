import impmagic

@impmagic.loader(
	{'module':'logs', 'submodule': ['print_nxs']}
)
def help():
	print_nxs("    ________             \n   / ____/ /___ _      __\n  / /_  / / __ \\ | /| / /\n / __/ / / /_/ / |/ |/ / \n/_/   /_/\\____/|__/|__/  \n                         \n")

	helper= {
		"config": "Affiche/Modifie la configuration",
		"run": "Lance une task/flow",
		"list": "Liste les task/flow disponibles",
		"info": "Affiche les détails d'une task/flow",
		"details": "Affiche les détails de l'ensemble des task/flow",
		"base": "Ouvrir le répertoire base",
		"tree": "Afficher l'arborescence du répertoire base",
		"pull": "Récupération d'un fichier du base",
		"push": "Ajouter un fichier dans la base",
		"pop": "Supprimer un fichier du base"
	}

	for el, le in helper.items():
		print_nxs(f"{el}: ", color='yellow', nojump=True)
		print_nxs(le, color='dark_gray')
	print("")


#Affichage de la configuration des tasks/flows
def print_config(data):
	for task_name, element in data.items():
		print_nxs(f"Plugin: {task_name}", color='green')

		for function in element:
			function = function.copy()
			print_nxs(f"  {function['func_name']}: ", color="magenta")
			del function['func_name']

			for key, value in function.items():
				if key=="arguments":
					if len(value):
						print_nxs(f"    arguments: ")
						for e in value:
							print_nxs(f"      {e}", color='yellow')

				elif (key=="args" and value==True) or (key=="kwargs" and value==True) or (key!="args" and key!="kwargs"):
					print_nxs(f"    {key}: ", nojump=True)
					print_nxs(value, color='yellow')


class Cli:
	@impmagic.loader(
		{'module':'main', 'submodule': ['Flow']}
	)
	def __init__(self):
		self.flow = Flow()

		self.switch()


	@impmagic.loader(
		{'module':'sys'},
		{'module':'base', 'submodule': ['show_tree']}
	)
	def switch(self):
		if len(sys.argv)>1:
			match sys.argv[1]:
				case "config":
					self.config()
				case "run":
					self.start()
				case "list":
					self.list()
				case "info":
					self.info()
				case "details":
					self.details()
				case "base":
					self.flow.open_base()
				case "tree":
					show_tree(self.flow.flow_base)
				case "pull":
					self.pull_base()
				case "push":
					self.push_base()
				case "pop":
					self.pop_base()
				case _:
					help()
		else:
			help()


	@impmagic.loader(
		{'module':'logs', 'submodule': ['logs']},
		{'module':'zpp_args'}
	)
	def start(self):
		parse = zpp_args.parser(sys.argv[1:])
		parse.command = "flow run"
		parse.set_description("Démarrage d'une task ou d'un flow")
		parse.set_argument("t", "task", description="Filtrer sur les task", default=False)
		parse.set_argument("f", "flow", description="Filtrer sur les flow", default=False)
		parse.set_argument("d", "debug", description="Lancement en mode debug", default=False)
		parse.set_argument("r", "repeat", description="Intervalle de répétition", default=None, store="value")
		parse.set_argument("s", "starter", description="Définir l'heure de démarrage", default=None, store="value")
		parse.set_parameter("task_name", description="Nom de la task")
		parse.set_parameter("argument", description="Différents arguments")
		parse.disable_check()
		parameter, argument = parse.load()

		if parameter!=None:
			if len(parameter):
				self.flow.start(task_name=parameter[0], parameter=parameter, only_task=argument.task, only_flow=argument.flow, starter=argument.starter, repeat=argument.repeat, debug=argument.debug)

			else:
				logs("Nom de la task/flow non précisé", "error")


	#Afficher le détail des task et flow
	@impmagic.loader(
		{'module':'logs', 'submodule': ['print_nxs']},
		{'module':'analyse', 'submodule': ['tree_plugin']},
	)
	def details(self):
		data = self.flow.details()

		print_nxs("== TASK ==", color='dark_gray')
		print_config(data['task'])

		print_nxs("\n== FLOW==", color='dark_gray')
		print_config(data['flow'])


	#Afficher la liste des task et flow
	@impmagic.loader(
		{'module':'logs', 'submodule': ['print_nxs']}
	)
	def list(self):
		task, flow = self.flow.list()

		print_nxs("== TASK ==", color='dark_gray')
		for t in task:
			print_nxs(t)

		print_nxs("\n== FLOW==", color='dark_gray')
		for f in flow:
			print_nxs(f)


	#Afficher les détails d'une task ou d'un flow
	@impmagic.loader(
		{'module':'zpp_args'},
		{'module':'sys'},
		{'module':'logs', 'submodule': ['logs', 'print_nxs']},
		{'module':'analyse', 'submodule': ['tree_plugin']}
	)
	def info(self):
		parse = zpp_args.parser(sys.argv[1:])
		parse.command = "flow info"
		parse.set_description("Afficher les détails d'une task spécifique")
		parse.set_argument("t", "task", description="Filtrer sur les task", default=False)
		parse.set_argument("f", "flow", description="Filtrer sur les flow", default=False)
		parse.set_parameter("task_name", description="Nom de la task")
		parameter, argument = parse.load()

		if parameter!=None:
			data = self.flow.details()
			#data = tree_plugin(self.flow_base)

			task_data = None

			if parameter[0] in data['flow'] and (argument.flow or (not argument.task and not argument.flow)):
				task_data = data['flow'][parameter[0]]
			
			if parameter[0] in data['task'] and (argument.task or (not argument.task and not argument.flow)):
				task_data = data['task'][parameter[0]]

			if task_data:
				for function in task_data:
					print_nxs(f"{function['func_name']}: ", color="magenta")
					del function['func_name']

					for key, value in function.items():
						if key=="arguments":
							if len(value):
								print_nxs(f"  arguments: ")
								for e in value:
									print_nxs(f"    {e}", color='yellow')

						elif (key=="args" and value==True) or (key=="kwargs" and value==True) or (key!="args" and key!="kwargs"):
							print_nxs(f"  {key}: ", nojump=True)
							print_nxs(value, color='yellow')
			else:
				logs("Task introuvable", "error")


	@impmagic.loader(
		{'module':'zpp_args'},
		{'module':'logs', 'submodule': ['logs', 'print_nxs']}
	)
	def config(self):
		parse = zpp_args.parser(sys.argv[1:])
		parse.command = "flow config"
		parse.set_description("Affichage/Modification de la configuration de nexus")
		parse.disable_check()
		parameter, argument = parse.load()

		if parameter!=None:
			data = self.flow.conf.load()
			if len(parameter):
				parameter[0] = parameter[0].lower()
				if parameter[0] in data:
					if isinstance(data[parameter[0]], bool):
						if data[parameter[0]]==True:
							self.flow.conf.change(parameter[0], False)
							logs(f"Passage de {parameter[0]} à False")  
						else:
							self.flow.conf.change(parameter[0], True)	
							logs(f"Passage de {parameter[0]} à True")  
					if isinstance(data[parameter[0]], str):
						if len(parameter)==2:
							logs(f"Modification du paramètre {parameter[0]}")  
							self.flow.conf.change(parameter[0], parameter[1])
					if isinstance(data[parameter[0]], int):
						if len(parameter)==2 and parameter[1].isdigit():
							logs(f"Modification du paramètre {parameter[0]}")  
							self.flow.conf.change(parameter[0], parameter[1])
			else:
				for cat, cat_info in data.items():
					print_nxs(f"\n#{cat}", color='dark_gray')
					for key, value in cat_info.items():
						print_nxs(f"{key}: ", nojump=True)
						print_nxs(value, color='yellow')


	@impmagic.loader(
		{'module':'zpp_args'},
		{'module':'sys'}
	)
	def pull_base(self):
		parse = zpp_args.parser(sys.argv[1:], error_lock=True)
		parse.command = "flow pull"
		parse.set_description("Récupération d'un fichier du base")
		parse.set_argument("o", "output", description="Spécifier le chemin de sortie", default=False, store="value")
		parse.set_parameter("path", description="Fichier à récupérer")
		parameter, argument = parse.load()

		if parameter!=None:
			self.flow.pull_base(parameter[0], argument.output)


	@impmagic.loader(
		{'module':'zpp_args'},
		{'module':'sys'}
	)
	def push_base(self):
		parse = zpp_args.parser(sys.argv[1:], error_lock=True)
		parse.command = "flow push"
		parse.set_description("Ajouter un fichier dans la base")
		parse.set_argument("f", "folder", description="Spécifier l'emplacement", default=False, store="value")
		parse.set_parameter("path", description="Fichier à envoyer")
		parameter, argument = parse.load()

		if parameter!=None:
			self.flow.push_base(parameter[0], argument.folder)


	@impmagic.loader(
		{'module':'zpp_args'},
		{'module':'sys'}
	)
	def pop_base(self):
		parse = zpp_args.parser(sys.argv[1:], error_lock=True)
		parse.command = "flow pop"
		parse.set_description("Supprimer un fichier du base")
		parse.set_parameter("path", description="Fichier à supprimer")
		parameter, argument = parse.load()

		if parameter!=None:
			self.flow.pop_base(parameter[0])


def main():
	Cli()