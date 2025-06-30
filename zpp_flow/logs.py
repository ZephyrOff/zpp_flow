import impmagic

@impmagic.loader(
	{'module': 'zpp_color', 'submodule': ['fg', 'attr']},
	{'module': 'datetime', 'submodule': ['datetime']},
)
def logs(message, lvl='info', nodate=True):
	#if __main__.nxs.conf.load(val='logs.display', section='',default=True):
	level_colors = {
		'logs': 'light_gray',
		'info': 'cyan',
		'warning': 'yellow',
		'error': 'red',
		'critical': 'light_red',
		'valid': 'green',
		'success': 'green',
	}

	color = level_colors.get(lvl, 'cyan')  # couleur par défaut
	
	#if nodate==False or (nodate==None and __main__.nxs.conf.load(val='logs.date', section='',default=True)):
	if not nodate:
		date = datetime.now().strftime("%Y/%m/%d - %H:%M:%S.%f")
		print(f"{fg('dark_gray')}[{date}] - {attr(0)}{fg(color)}{message}{attr(0)}")
	else:
		print(f"{fg(color)}{message}{attr(0)}")


@impmagic.loader(
	{'module': 'zpp_color', 'submodule': ['fg', 'attr']}
)
def print_nxs(message, color=None, nojump=False):
	if color==None:
		color = 'cyan'
	
	if nojump:
		print(f"{fg(color)}{message}{attr(0)}", end="")
	else:
		print(f"{fg(color)}{message}{attr(0)}")