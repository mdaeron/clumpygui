import typer

app = typer.Typer(
	add_completion = True,
	context_settings={'help_option_names': ['-h', '--help']},
	rich_markup_mode = 'rich',
	)

@app.callback(invoke_without_command = True)
def callback(ctx: typer.Context):
	"""
	\b
	 .d88b.  88                                    .d88b.  88     88 888888
	d8P  Y8b 88                                   d8P  Y8b 88     88   88  
	88    88 88                                   88    88 88     88   88  
	88       88 88  88 8888b.db.  888b.  88  88   88       88     88   88  
	88       88 88  88 88 "88 "8b 88 "8b 88  88   88  8888 88     88   88  
	88    88 88 88  88 88  88  88 88  88 88  88   88    88 88     88   88  
	Y8b  d8P 88 Y8b 88 88  88  88 88 d8P Y8b 88   Y8b  d8P Y8b. .d8P   88  
	 "Y88P"  88  Y8888 88  88  88 888P"    "Y88    "Y888P8  "Y888P"  888888
	                              88         88
	                              88    Yb  d8P
	                              88     "Y8P"
	
	A collection of clumpy web apps
	"""
	if ctx.invoked_subcommand is None:
		typer.echo(ctx.get_help())
		raise typer.Exit()

@app.command(name = "D47calib")
def D47calib():
	"""
	Use D47calib library to convert between carbonate Δ47 and temperature using various calibrations
	"""
	print('Hi from D47calib')

@app.command(name = "D95thermo")
def D95thermo():
	print('Hi from D95thermo')

def main() -> None:
	app()
	