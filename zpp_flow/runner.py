import impmagic

@impmagic.loader(
	{'module':'logs', 'submodule': ['logs', 'print_nxs']},
	{'module':'os.path', 'submodule': ['join']}
)
def run_task(task_name, data, parameter, flow_base, debug=False):
	def show_debug(result):
		if debug:
			print_nxs(f"Result: ", color="yellow", nojump=True)
			print_nxs(result, color="dark_gray")

	for proc in data:
		if 'path' in proc:
			mod_file = impmagic.get_from_file(join(flow_base ,proc['path']))
			func = getattr(mod_file, proc['func_name'])

			logs(f"Démarrage de la fonction {proc['func_name']}", "info")
			if len(proc['arguments']):
				mandatory_size = sum(1 for t in proc['arguments'] if len(t) == 1)

				#Vérifie si le nom d'un argument a été défini explicitement
				dyn_args = True if sum(True for t in parameter if "=" in t)>0 else False

				if len(parameter)-1 >= mandatory_size:
					#Si des arguments sont définis avec key=value, parse et appelle de la fonction
					if dyn_args:
						c_args = {}
						c_params = []

						for p in parameter[1:]:
							if "=" in p:
								p = p.split("=", 1)
								c_args[p[0]] = p[1]
							else:
								c_params.append(p)

						args_function = {}

						for a in proc['arguments']:
							if a[0] in c_args:
								args_function[a[0]] = c_args[a[0]]
							else:
								if len(c_params):
									args_function[a[0]] = c_params.pop(0)
								else:
									if len(a)>1:
										args_function[a[0]] = a[1]

						result = func(**args_function)
						show_debug(result)
					else:
						result = func(*parameter[1:len(proc['arguments'])+1])
						show_debug(result)
				else:
					logs(f"task {task_name}: argument(s) manquant(s)", "warning")
			else:
				result = func()
				show_debug(result)
		else:
			logs(f"task {task_name}: path non indentifié", "warning")


@impmagic.loader(
	{'module':'logs', 'submodule': ['logs', 'print_nxs']},
	{'module':'os.path', 'submodule': ['join']}
)
def run_flow(task_name, data, parameter, flow_base, debug=False):
	def show_debug(result):
		if debug:
			print_nxs(f"Result: ", color="yellow", nojump=True)
			print_nxs(result, color="dark_gray")

	arguments = parameter[1:]

	for proc in data:
		result = None

		if 'path' in proc:
			mod_file = impmagic.get_from_file(join(flow_base ,proc['path']))
			func = getattr(mod_file, proc['func_name'])

			logs(f"Démarrage de la fonction {proc['func_name']}", "info")
			#print(func)
			if len(proc['arguments']):
				mandatory_size = sum(1 for t in proc['arguments'] if len(t) == 1)

				#Vérifie si le nom d'un argument a été défini explicitement
				dyn_args = True if sum(True for t in arguments if (isinstance(t, str) and "=" in t))>0 else False

				if len(arguments) >= mandatory_size:
					#Si des arguments sont définis avec key=value, parse et appelle de la fonction
					if dyn_args:
						c_args = {}
						c_params = []

						for p in arguments:
							if "=" in p:
								p = p.split("=", 1)
								c_args[p[0]] = p[1]
							else:
								c_params.append(p)

						args_function = {}

						for a in proc['arguments']:
							if a[0] in c_args:
								args_function[a[0]] = c_args[a[0]]
							else:
								if len(c_params):
									args_function[a[0]] = c_params.pop(0)
								else:
									if len(a)>1:
										args_function[a[0]] = a[1]

						result = func(**args_function)
						show_debug(result)
					else:
						result = func(*arguments[:len(proc['arguments'])+1])
						show_debug(result)
				else:
					logs(f"flow {task_name}: argument(s) manquant(s)", "warning")
			else:
				result = func()
				show_debug(result)
		else:
			logs(f"flow {task_name}: path non indentifié", "warning")

		#Récupération des arguments pour la fonction suivante
		if result:
			if isinstance(result, tuple):
				arguments = list(result)
			else:
				arguments = [result]
		else:
			arguments = []