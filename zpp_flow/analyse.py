import impmagic

#Vérifie si une fonction attends des arguments
@impmagic.loader(
	{'module':'inspect'}
)
def get_function_arguments(func):
	# Obtenir les arguments de la fonction
	signature = inspect.signature(func)
	parameters = signature.parameters
	
	# Créer des listes pour différents types d'arguments
	arguments = []
	args = False
	kwargs = False
	kwonlyargs = []
	
	# Classer les arguments en fonction de leur type
	for name, param in parameters.items():
		if param.kind == inspect.Parameter.VAR_POSITIONAL:
			args = True
		elif param.kind == inspect.Parameter.VAR_KEYWORD:
			kwargs = True
		elif param.default == inspect.Parameter.empty:
			arguments.append((name, ))
		else:
			arguments.append((name, param.default))
	
	return {
		'arguments': arguments,
		'args': args,
		'kwargs': kwargs,
	}


#Récupération des informations d'une fonction
def get_function_info(mod_file, data, type):
	content = []
	for func_name in data:
		insert_base = {'func_name': func_name}
		custom = {}
		func_inf = getattr(mod_file, func_name, None)

		if callable(func_inf):
			# Récupérer tous les attributs de la fonction
			attributes = dir(func_inf)
			
			# Filtrer les attributs qui commencent par '_flow'
			flow_attributes = [attr for attr in attributes if attr.startswith('_taskflow_')]
			for attribute in flow_attributes:
				custom[attribute[10:]] = getattr(func_inf, attribute, None)

			#Parse des decorators pour récupérer les fonctions nécessaires
			if "decorators" in custom:
				for i, dec in enumerate(custom['decorators'].copy()):
					insert = insert_base.copy()
					#Définition du nom
					if 'name' not in insert:
						insert['name'] = func_name
					
					args_type = get_function_arguments(func_inf)
					insert.update(args_type)
					insert.update(dec)

					if f'is_{type}' in insert and insert[f'is_{type}']:
						content.append(insert)

	return content


@impmagic.loader(
	{'module':'os'}
)
def parse_module(mod_file, flow_base=None):
	func_total = {'task': {}, 'flow': {}}

	mod_name = mod_file.__name__

	mod_filename = mod_file.__file__
	if flow_base:
		mod_filename = mod_filename.replace(flow_base+os.sep, "")

	task_funcs, flow_funcs = find_decorated_functions(mod_file)
	task_data = get_function_info(mod_file, task_funcs, type="task")
	flow_data = get_function_info(mod_file, flow_funcs, type="flow")

	for element in (task_data + flow_data):
		if 'is_task' in element and element['is_task']:
			type_task = 'task'
		else:
			type_task = 'flow'

		element['path'] = mod_filename

		element_name = element['name']
		del element['name']
		if element_name not in func_total[type_task]:
			func_total[type_task][element_name] = []
			func_total[type_task][element_name].append(element)
		else:
			if 'order' in func_total[type_task][element_name][0] and 'order' in element:
				func_total[type_task][element_name].append(element)
				func_total[type_task][element_name] = sorted(func_total[type_task][element_name], key=lambda x: x['order'])
			else:
				raise ValueError(f"Value 'order' not define for multi-task {element['name']}")

	return func_total


@impmagic.loader(
	{'module':'base', 'submodule': ['tree_base']},
	{'module':'analyse', 'submodule': ['parse_module']}
)
def tree_plugin(flow_base):
	mod_data = {}

	base_file = tree_base(flow_base)

	for file in base_file:
		mod_file = impmagic.get_from_file(file)
		if mod_file:
			mod_data_file = parse_module(mod_file, flow_base=flow_base)

			mod_data.update(mod_data_file)

	#Ajout des fonctions *
	if '*'in mod_data['task']:
		mod_data['task'] = broadcast_function(mod_data['task'], mod_data['task']['*'])
		
	if '*'in mod_data['flow']:
		mod_data['flow'] = broadcast_function(mod_data['flow'], mod_data['flow']['*'])

	return mod_data


@impmagic.loader(
	{'module':'inspect'}
)
def find_decorated_functions(module):
	task_functions = []
	flow_functions = []

	for name, func in inspect.getmembers(module, inspect.isfunction):
		for deco in getattr(func, '_taskflow_decorators', []):
			if 'is_task' in deco and deco['is_task']:
				task_functions.append(name)
			if 'is_flow' in deco and deco['is_flow']:
				flow_functions.append(name)

			if getattr(func, '_taskflow_is_task', False):
				task_functions.append(name)
			if getattr(func, '_taskflow_is_flow', False):
				flow_functions.append(name)

	return task_functions, flow_functions


#Ajouter les fonctions * aux autres fonctions
def broadcast_function(mod_data, function):
	del mod_data['*']

	for task_name, task in mod_data.items():
		mod_data[task_name] = task + function
		mod_data[task_name] = sorted(mod_data[task_name], key=lambda x: x['order'])

	return mod_data