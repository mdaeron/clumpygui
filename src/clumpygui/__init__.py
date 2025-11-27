import typer

app = typer.Typer(
	add_completion = True,
	context_settings={'help_option_names': ['-h', '--help']},
	rich_markup_mode = 'rich',
	)

@app.callback(invoke_without_command = True)
def callback(ctx: typer.Context):
	"""
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
	