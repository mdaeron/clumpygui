import streamlit as st
import pandas as pd
import D47crunch

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

if len(st.session_state.rawdata_df) > 1:

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
	
	st.write("### Standardization of clumped isotopes :red[(not yet implemented)]")
	
	D4x_stdz_methods = st.data_editor(
		pd.DataFrame({
			'Quantity':     pd.Series(['Δ47', 'Δ48'],    dtype = 'str'),
			'Method':     pd.Series(['Pooled regression', 'Pooled regression'],    dtype = 'str'),
			}),
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
				options=['Pooled regression', 'Independent sessions'],
				)
			},
		)

	process_button = st.button(':red[Process data]')
	st.write(':red[(Δ48 not yet implemented)]')

	if process_button:
		st.markdown('### Foo bar baz')