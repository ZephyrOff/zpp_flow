def task(*args, **kwargs):
	inject = {'is_task': True}

	# Vérifie si des arguments ont été passés
	if len(args) == 1 and callable(args[0]):
		# Utilisation simple sans paramètres
		func = args[0]
		
		func._taskflow_decorators = func._taskflow_decorators if hasattr(func, '_taskflow_decorators') else []
		func._taskflow_decorators.append(inject)
		return func
	else:
		# Utilisation avec paramètres
		def decorator(func):
			func._taskflow_decorators = func._taskflow_decorators if hasattr(func, '_taskflow_decorators') else []

			for key, value in kwargs.items():
				inject[key] = value
			func._taskflow_decorators.append(inject)

			return func
		return decorator


def flow(*args, **kwargs):
	inject = {'is_flow': True}

	# Vérifie si des arguments ont été passés
	if len(args) == 1 and callable(args[0]):
		# Utilisation simple sans paramètres
		func = args[0]

		func._taskflow_decorators = func._taskflow_decorators if hasattr(func, '_taskflow_decorators') else []
		func._taskflow_decorators.append(inject)
		return func
	else:
		# Utilisation avec paramètres
		def decorator(func):
			func._taskflow_decorators = func._taskflow_decorators if hasattr(func, '_taskflow_decorators') else []
			for key, value in kwargs.items():
				inject[key] = value
			func._taskflow_decorators.append(inject)

			return func
		return decorator
