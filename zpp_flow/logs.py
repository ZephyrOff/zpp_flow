import impmagic

@impmagic.loader(
    {'module': 'zpp_color', 'submodule': ['fg', 'attr']},
    {'module': 'datetime', 'submodule': ['datetime']},
)
def logs(message, lvl='info', nodate=True):
	#if __main__.nxs.conf.load(val='logs.display', section='',default=True):
	if lvl=='logs':
		color = 'light_gray'
	elif lvl=='info':
		color = 'cyan'
	elif lvl=='warning':
		color = 'yellow'
	elif lvl=='error':
		color = 'red'
	elif lvl=='critical':
		color = 'light_red'
	elif lvl=='valid':
		color = 'green'
	
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