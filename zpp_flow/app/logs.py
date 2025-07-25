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


def format_duration(seconds):
    total_ms = int(seconds * 1000)

    MS = 1
    S = 1000 * MS
    M = 60 * S
    H = 60 * M
    D = 24 * H
    MO = 30 * D      # mois = 30 jours (approx.)
    Y = 12 * MO      # année = 360 jours (approx.)

    y, rem = divmod(total_ms, Y)
    mo, rem = divmod(rem, MO)
    d, rem = divmod(rem, D)
    h, rem = divmod(rem, H)
    m, rem = divmod(rem, M)
    s, rem = divmod(rem, S)
    ms = rem

    parts = []
    if y > 0:
        parts.append(f"{y}y")
    if mo > 0 or parts:
        parts.append(f"{mo}mo")
    if d > 0 or parts:
        parts.append(f"{d}d")
    if h > 0 or parts:
        parts.append(f"{h}h")
    if m > 0 or parts:
        parts.append(f"{m}m")
    if s > 0 or parts:
        parts.append(f"{s}s")
    parts.append(f"{ms}ms")

    return ".".join(parts)
