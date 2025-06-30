import impmagic
from os.path import join

@impmagic.loader(
	{'module':'logs', 'submodule': ['logs', 'print_nxs']},
	{'module':'os.path', 'submodule': ['join']}
)
def parse_arguments(proc_arguments, parameters):
	"""
	Parse les paramètres en arguments nommés et positionnels.
	
	proc_arguments : [('arg1',), ('arg2', default), ...]
	parameters : liste d'objets de types variés (str, int, float, bytes, etc)
	
	Retourne dict avec les arguments prêts pour appel fonction.
	"""

	c_args = {}
	c_params = []

	for p in parameters:
		# On peut reconnaître un argument nommé uniquement si p est str et contient '='
		if isinstance(p, str) and "=" in p:
			k, v = p.split("=", 1)
			c_args[k.strip()] = v.strip()  # Note: v reste une str ici, conversion possible à faire plus tard si besoin
		else:
			c_params.append(p)

	args_function = {}

	for a in proc_arguments:
		name = a[0]
		has_default = len(a) > 1
		default = a[1] if has_default else None

		if name in c_args:
			# Ici c_args[name] est une str, on pourrait tenter une conversion automatique (optionnel)
			args_function[name] = c_args[name]
		elif c_params:
			args_function[name] = c_params.pop(0)
		elif has_default:
			# même si default est None, on considère qu'on doit prendre la valeur par défaut
			args_function[name] = default
		else:
			# Demande à l'utilisateur la valeur manquante
			user_input = input(f"{name}: ")
			args_function[name] = user_input

	return args_function



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
			mod_file = impmagic.get_from_file(join(flow_base, proc['path']))
			func = getattr(mod_file, proc['func_name'])

			logs(f"Démarrage de la fonction {proc['func_name']}", "info")

			if len(proc['arguments']):
				try:
					args_function = parse_arguments(proc['arguments'], parameter[1:])
					result = func(**args_function)
					show_debug(result)
				except ValueError as e:
					logs(f"task {task_name}: {e}", "warning")
			else:
				result = func()
				show_debug(result)
		else:
			logs(f"task {task_name}: path non identifié", "warning")


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
			mod_file = impmagic.get_from_file(join(flow_base, proc['path']))
			func = getattr(mod_file, proc['func_name'])

			logs(f"Démarrage de la fonction {proc['func_name']}", "info")

			if len(proc['arguments']):
				try:
					args_function = parse_arguments(proc['arguments'], arguments)
				except ValueError as e:
					# Arguments obligatoires manquants, demander à l'utilisateur
					missing_args = str(e).split(":")[-1].strip().split(",")
					for arg in missing_args:
						val = input(f"{arg.strip()}: ")
						arguments.append(val)
					args_function = parse_arguments(proc['arguments'], arguments)

				result = func(**args_function)
				show_debug(result)
			else:
				result = func()
				show_debug(result)
		else:
			logs(f"flow {task_name}: path non identifié", "warning")

		# Préparer les arguments pour la fonction suivante
		if result:
			if isinstance(result, tuple):
				arguments = list(result)
			else:
				arguments = [result]
		else:
			arguments = []
