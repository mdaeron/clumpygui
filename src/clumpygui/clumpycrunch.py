import streamlit as st
import pandas as pd
import datetime as dt
import D47crunch
import io
import zipfile

__version__ = '3.0.0-beta'

def callback_random_data():

	kwargs = dict(
		samples = [
			dict(Sample = 'ETH-1', N = 3),
			dict(Sample = 'ETH-2', N = 3),
			dict(Sample = 'ETH-3', N = 3),
			dict(Sample = 'FOO', N = 3,
				d13C_VPDB = -5., d18O_VPDB = -10.,
				D47 = 0.3, D48 = 0.15),
			dict(Sample = 'BAR', N = 3,
				d13C_VPDB = -15., d18O_VPDB = -2.,
				D47 = 0.6, D48 = 0.2),
			],
		rD47 = 0.008,
		rD48 = 0.025,
		)

	_data_ = D47crunch.D47data(
		D47crunch.virtual_data(session = 'Session_01', **kwargs)
		+ D47crunch.virtual_data(session = 'Session_02', **kwargs)
		+ D47crunch.virtual_data(session = 'Session_03', **kwargs)
		)	

	return pd.DataFrame({
		'UID':     pd.Series([r['UID'] for r in _data_], dtype = 'str'),
		'Session': pd.Series([r['Session'] for r in _data_], dtype = 'str'),
		'Sample':  pd.Series([r['Sample'] for r in _data_], dtype = 'str'),
		'd45':     pd.Series([r['d45'] for r in _data_], dtype = 'float'),
		'd46':     pd.Series([r['d46'] for r in _data_], dtype = 'float'),
		'd47':     pd.Series([r['d47'] for r in _data_], dtype = 'float'),
		'd48':     pd.Series([r['d48'] for r in _data_], dtype = 'float'),
		'd49':     pd.Series([r['d47'] for r in _data_], dtype = 'float'),
		})

st.set_page_config(
	page_title = 'ClumpyCrunch',
	layout = 'wide',
	)

st.write('''
	<style>
		h1 {
			background-color: #fdcf4e;
			}
		h2, h3 {
			background-color: #F0F0F0;
		}
		h1, h2, h3 {
			padding-left: 2% !important;
			margin-bottom: 1ex !important;
		}
	</style>
''', unsafe_allow_html = True)

st.markdown('# ClumpyCrunch')

st.markdown('### Input data')

if 'rawdata_df' not in st.session_state:
	st.session_state.rawdata_df = pd.DataFrame({
		'UID':     pd.Series([None], dtype = 'str'),
		'Session': pd.Series([None], dtype = 'str'),
		'Sample':  pd.Series([None], dtype = 'str'),
		'd45':     pd.Series([None], dtype = 'float'),
		'd46':     pd.Series([None], dtype = 'float'),
		'd47':     pd.Series([None], dtype = 'float'),
		'd48':     pd.Series([None], dtype = 'float'),
		'd49':     pd.Series([None], dtype = 'float'),
	})

if st.button("Generate Random Data"):
	st.session_state.rawdata_df = callback_random_data()

st.session_state.rawdata_df = st.data_editor(
	st.session_state.rawdata_df,
	num_rows = 'dynamic',
	use_container_width = True,
	hide_index = True,
	column_config = {
		k: st.column_config.NumberColumn(format = '%.4f')
		for k in ['d45', 'd46', 'd47', 'd48', 'd49']
		},
	)

rawdata = st.session_state.rawdata_df.to_dict('records')

st.write("### Data reduction parameters")

isoparams = [
	(
		'R13_VPDB',
		0.01118,
		'13C/12C ratio of VPDB',
		),
	(
		'R18_VSMOW',
		0.0020052,
		'18O/16O ratio of VSMOW',
		),
	(
		'R17_VSMOW',
		0.00038475,
		'17O/16O ratio of VSMOW',
		),
	(
		'lambda_17',
		0.528,
		'Triple oxygen isotope exponent',
		),
	(
		'alpha_18_acid',
		1.008129,
		'18O/16O fractionation factor of acid reaction',
		),
	]

isoparams_df = pd.DataFrame({
	'Parameter':  pd.Series([_[0] for _ in isoparams],    dtype = 'str'),
	'Definition': pd.Series([_[2] for _ in isoparams],    dtype = 'str'),
	'Value':      pd.Series([_[1] for _ in isoparams],    dtype = 'str'),
	})

isoparams_df = st.data_editor(
	isoparams_df,
	num_rows = 5,
	use_container_width = False,
	hide_index = True,
	disabled = ('Parameter', 'Definition'),
	)

isoparams = {r['Parameter']: float(r['Value']) for r in isoparams_df.to_dict('records')}

st.write("""
### Reference Materials
The following samples are used as anchors to standardize δ<sup>13</sup>C<sub>VPDB</sub>, δ<sup>18</sup>O<sub>VPDB</sub>, Δ<sub>47</sub>, and Δ<sub>48</sub> values:
""", unsafe_allow_html = True)	

anchors = {}

for s in D47crunch.D4xdata().Nominal_d13C_VPDB:
	if s not in anchors:
		anchors[s] = {}
	anchors[s]['d13C_VPDB'] = f'{D47crunch.D4xdata().Nominal_d13C_VPDB[s]:.2f}'

for s in D47crunch.D4xdata().Nominal_d18O_VPDB:
	if s not in anchors:
		anchors[s] = {}
	anchors[s]['d18O_VPDB'] = f'{D47crunch.D4xdata().Nominal_d18O_VPDB[s]:.2f}'

for s in D47crunch.D47data().Nominal_D47:
	if s not in anchors:
		anchors[s] = {}
	anchors[s]['D47'] = f'{D47crunch.D47data().Nominal_D47[s]:.4f}'

for s in D47crunch.D48data().Nominal_D48:
	if s not in anchors:
		anchors[s] = {}
	anchors[s]['D48'] = f'{D47crunch.D48data().Nominal_D48[s]:.3f}'

with st.expander('Instructions'):
	st.write(
		"""
Each row corresponds to a given sample which may be used as a standardization anchor for
any combination of δ<sup>13</sup>C<sub>VPDB</sub>, δ<sup>18</sup>O<sub>VPDB</sub>,
Δ<sub>47</sub>, and/or Δ<sub>48</sub>, simply by specifying the nominal value for each
sample in the relevant column.
""",
		unsafe_allow_html = True,
		)

anchors_df = pd.DataFrame({
	'Sample':    pd.Series([s for s in anchors], dtype = 'str'),
	'd13C_VPDB': pd.Series([anchors[s]['d13C_VPDB'] if 'd13C_VPDB' in anchors[s] else None for s in anchors], dtype = 'str'),
	'd18O_VPDB': pd.Series([anchors[s]['d18O_VPDB'] if 'd18O_VPDB' in anchors[s] else None for s in anchors], dtype = 'str'),
	'D47':       pd.Series([anchors[s]['D47'] if 'D47' in anchors[s] else None for s in anchors], dtype = 'str'),
	'D48':       pd.Series([anchors[s]['D48'] if 'D48' in anchors[s] else None for s in anchors], dtype = 'str'),
	})

anchors_df = st.data_editor(
	anchors_df,
	num_rows = 'dynamic',
	use_container_width = False,
	hide_index = True,
	)

anchors = anchors_df.to_dict('records')
anchors = [{k: r[k] for k in r if not pd.isnull(r[k])} for r in anchors]

st.write("### Standardization of bulk composition :red[(not yet implemented)]")

d1xX_stdz_df = pd.DataFrame({
		'Quantity':     pd.Series(['δ13C', 'δ18O'],    dtype = 'str'),
		'Method':     pd.Series(['Affine transformation', 'Affine transformation'],    dtype = 'str'),
		})

d1xX_stdz_methods = st.data_editor(
	d1xX_stdz_df,
	num_rows = 2,
	use_container_width = False,
	hide_index = True,
	disabled = ('Quantity',),
	column_config = {
		'Method': st.column_config.SelectboxColumn(
			'Method',
			help = 'Which standardization method to use',
			width = 'medium',
			required = True,
			options=['Affine transformation', 'Constant offset'],
			)
		},
	)

process_button = st.button(':red[Process data]')

if process_button:

	rawdata47 = D47crunch.D47data(rawdata)

	rawdata47.R13_VPDB = isoparams['R13_VPDB']
	rawdata47.R18_VSMOW = isoparams['R18_VSMOW']
	rawdata47.R17_VSMOW = isoparams['R17_VSMOW']
	rawdata47.LAMBDA_17 = isoparams['lambda_17']
	rawdata47.R18_VPDB = rawdata47.R18_VSMOW * 1.03092
	rawdata47.R17_VPDB = rawdata47.R17_VSMOW * 1.03092 ** rawdata47.LAMBDA_17

	rawdata47.Nominal_d13C_VPDB = {a['Sample']: float(a['d13C_VPDB']) for a in anchors if 'd13C_VPDB' in a}
	rawdata47.Nominal_d18O_VPDB = {a['Sample']: float(a['d18O_VPDB']) for a in anchors if 'd18O_VPDB' in a}
	rawdata47.Nominal_D47 = {a['Sample']: float(a['D47']) for a in anchors if 'D47' in a}
	rawdata47.refresh()
	rawdata47.wg()
	rawdata47.crunch()
	rawdata47.standardize()
	
	st.session_state['data_has_been_brocessed'] = True
	st.session_state['rawdata47'] = rawdata47

if 'data_has_been_brocessed' in st.session_state:

	rawdata47 = st.session_state['rawdata47']

	st.write('### Results')

	st.write('#### Table of samples')
	table_of_samples = D47crunch.table_of_samples(rawdata47, output = 'raw')
	table_of_samples = [[b for a,b in zip(table_of_samples[0], l) if a != 'p_Levene'] for l in table_of_samples]
	st.data_editor(
		pd.DataFrame(
			table_of_samples[1:],
			columns = table_of_samples[0],
			),
		hide_index = True,
		disabled = table_of_samples[0],
		)

	st.write('#### Table of sessions')
	table_of_sessions = D47crunch.table_of_sessions(rawdata47, output = 'raw')
	st.data_editor(
		pd.DataFrame(
			table_of_sessions[1:],
			columns = table_of_sessions[0],
			),
		hide_index = True,
		disabled = table_of_sessions[0],
		)

	st.write('#### Table of analyses')
	table_of_analyses = D47crunch.table_of_analyses(rawdata47, output = 'raw')
	st.data_editor(
		pd.DataFrame(
			table_of_analyses[1:],
			columns = table_of_analyses[0],
			),
		hide_index = True,
		disabled = table_of_analyses[0],
		)

# 	st.write('#### Correlations between sample Δ47 errors')
# 	table_of_samples = D47crunch.table_of_samples(rawdata47, output = 'raw')
# 	table_of_samples = [[b for a,b in zip(table_of_samples[0], l) if a != 'p_Levene'] for l in table_of_samples]
# 	st.data_editor(
# 		pd.DataFrame(
# 			table_of_samples[1:],
# 			columns = table_of_samples[0],
# 			),
# 		hide_index = True,
# 		disabled = table_of_samples[0],
# 		)

	st.write('#### Sessions plots')
	plots = {}
	for session in rawdata47.sessions:
		sp = rawdata47.plot_single_session(session, xylimits = 'constant')
		st.pyplot(sp.fig, use_container_width = False, dpi = 100)
		plots[session] = sp.fig

	buf = io.BytesIO()

	readme = f'''
ClumpyCrunch version {__version__}, using D47crunch version {D47crunch.__version__}
Downloaded on {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Contents:

* analyses.csv  : table of analyses
* anchors.csv   : table of the anchors used to standardize δ13C, δ18O, Δ47, and Δ48 measurements
* isoparams.csv : table of the parameters used for data reduction
* rawdata.csv   : table of the raw input data, before any standardization
'''

	with zipfile.ZipFile(buf, 'x') as dl_zip:
		dl_zip.writestr('analyses.csv', '\n'.join([','.join(l) for l in table_of_analyses]))
		dl_zip.writestr('anchors.csv', anchors_df.to_csv(index = False))
		dl_zip.writestr('isoparams.csv', isoparams_df.to_csv(index = False))
		dl_zip.writestr('rawdata.csv', st.session_state.rawdata_df.to_csv(index = False))
		dl_zip.writestr('readme.txt', readme[1:])
		for session in rawdata47.sessions:
			plotbuf = io.BytesIO()
			plots[session].savefig(plotbuf, format='pdf')
			plotbuf.seek(0)
			dl_zip.writestr(f'D47_{session}.pdf', plotbuf.read())


	st.download_button(
		label = 'Download zip',
		data = buf.getvalue(),
		file_name = 'clumpycrunch-results.zip',
		mime = 'application/zip',
		)
