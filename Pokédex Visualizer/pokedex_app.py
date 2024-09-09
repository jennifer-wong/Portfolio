from dash import Dash, _dash_renderer, html, dcc, callback, Output, Input
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


pokedex = pd.read_json('pokedex.jl', lines=True).sort_values('number').reset_index(drop=True)
pokedex['display_height'] = pokedex['height'].apply(lambda x: f'{int(x / 12)}\' {x % 12}"')
pokedex['height'] = pokedex['height'] / 12
pokedex['display_name'] = pokedex.apply(lambda x: x['name'] + f" (#{x['number']})", axis=1)
pokedex['image_path'] = pokedex['images'].apply(lambda x: x[0]['path'].replace('full', 'assets'))
pokedex['primary_type'] = pokedex.apply(lambda x: x['type'][0], axis=1)
pokedex['secondary_type'] = pokedex.apply(lambda x: x['type'][1] if len(x['type']) > 1 else None, axis=1)

# assign generation
generation_df = pd.DataFrame(
	[
	    {'name': 'Generation I', 'start_number': 1, 'end_number': 151, 'marker_symbol': 'star'},
	    {'name': 'Generation II', 'start_number': 152, 'end_number': 251, 'marker_symbol': 'square'},
	    {'name': 'Generation III', 'start_number': 252, 'end_number': 386, 'marker_symbol': 'diamond'},
	    {'name': 'Generation IV', 'start_number': 387, 'end_number': 493, 'marker_symbol': 'triangle-up'},
	    {'name': 'Generation V', 'start_number': 494, 'end_number': 649, 'marker_symbol': 'cross'},
	    {'name': 'Generation VI', 'start_number': 650, 'end_number': 721, 'marker_symbol': 'hexagon'},
	    {'name': 'Generation VII', 'start_number': 722, 'end_number': 809, 'marker_symbol': 'triangle-down'},
	    {'name': 'Generation VIII', 'start_number': 810, 'end_number': 905, 'marker_symbol': 'x'}
	]
)

for ix, number in enumerate(pokedex['number']):
    for index, row in generation_df.iterrows():
        if row['start_number'] <= number <= row['end_number']:
            pokedex.loc[ix, 'generation'] = row['name']
            pokedex.loc[ix, 'marker_symbol'] = row['marker_symbol']
            break
assert pokedex['generation'].isna().sum() == 0, 'generation field has null value'

# assign marker_symbol by primary_type
type_df = pd.DataFrame(
	[
	    {'name': 'Bug', 'marker_color': px.colors.qualitative.Safe[3]},
	    {'name': 'Dark', 'marker_color': px.colors.qualitative.Safe[4]},
	    {'name': 'Dragon', 'marker_color': px.colors.qualitative.Dark24[23]},
	    {'name': 'Electric', 'marker_color': px.colors.qualitative.T10[5]},
	    {'name': 'Fairy', 'marker_color': px.colors.qualitative.Plotly[8]},
	    {'name': 'Fighting', 'marker_color': px.colors.qualitative.Dark24[3]},
	    {'name': 'Fire', 'marker_color': px.colors.qualitative.D3[1]},
	    {'name': 'Flying', 'marker_color': px.colors.qualitative.Pastel[5]},
	    {'name': 'Ghost', 'marker_color': px.colors.qualitative.G10[4]},
	    {'name': 'Grass', 'marker_color': px.colors.qualitative.Light24[19]},
	    {'name': 'Ground', 'marker_color': px.colors.qualitative.Dark24[21]},
	    {'name': 'Ice', 'marker_color': px.colors.qualitative.Plotly[5]},
	    {'name': 'Normal', 'marker_color': '#000000'},
	    {'name': 'Poison', 'marker_color': px.colors.qualitative.Pastel[9]},
	    {'name': 'Psychic', 'marker_color': px.colors.qualitative.Alphabet[22]},
	    {'name': 'Rock', 'marker_color': px.colors.qualitative.Light24[14]},
	    {'name': 'Steel', 'marker_color': px.colors.qualitative.Safe[10]},
	    {'name': 'Water', 'marker_color': px.colors.qualitative.G10[0]}
	]
)
pokedex = pokedex.merge(type_df.rename(columns={'name': 'primary_type'}), how='left', on='primary_type')
assert pokedex['marker_color'].isna().sum() == 0, 'marker_color field has null value'

# insert rows for creating generation and primary type legends
type_legend = generation_df\
    .rename(columns={'name': 'generation'})\
    .merge(type_df.rename(columns={'name': 'primary_type'}), how='cross')\
    .drop(columns=['start_number', 'end_number'])
type_legend['height'] = -1000
type_legend['weight'] = -1000

generation_legend = type_legend.reset_index(drop=True)
generation_legend['display_name'] = 'generation_legend'
generation_legend['marker_color'] = px.colors.qualitative.Dark2[7]

type_legend['marker_symbol'] = 'circle'
type_legend['display_name'] = 'type_legend'

pokedex = pd.concat([pokedex, type_legend, generation_legend]).reset_index(drop=True)

generation_list = sorted(pokedex['generation'].unique())
type_list = sorted(pokedex['primary_type'].unique())
pokemon_list = pokedex[~pokedex['display_name'].isin(['generation_legend', 'type_legend'])]\
	.sort_values('number')['display_name']\
	.to_list()

# create dash app
_dash_renderer._set_react_version('18.2.0')

app = Dash(external_stylesheets=dmc.styles.ALL)
server = app.server
app.title = 'Pokédex Visualizer'
app._favicon = ('assets/favicon.ico')
app.layout = dmc.MantineProvider(
	html.Div(
		html.Div(
			[
				html.Div( # header section
					[
						html.H1( # title
							'Pokédex Visualizer',
							style={
								'margin': '0 0 0 0'
							}
						),
						html.Div( # filter section
							[
								dmc.Popover( # generation and type filter
									[
										dmc.PopoverTarget([dmc.Button('Generation and Type Filter', w=250, radius='md')]),
										dmc.PopoverDropdown(
											[
												dmc.MultiSelect(
													id='generation-filter',
													data=generation_list,
													label='Generations',
													value=['Generation I', 'Generation V', 'Generation VII'],
													hidePickedOptions=True,
													clearable=True,
													comboboxProps={'withinPortal': False}
												),
												dmc.MultiSelect(
													id='type-filter',
													data=type_list,
													value=['Dark', 'Ground', 'Grass', 'Psychic'],
													label='Types (select up to 6)',
													maxValues=6,
													hidePickedOptions=True,
													clearable=True,
													comboboxProps={'withinPortal': False}
												)
											],
											style={
												'display': 'flex',
												'flex-direction': 'column',
												'gap': '10px'
											}
										)
									],
									withArrow=True,
									width=400,
									position='left',
									shadow='md',
									zIndex=2000
								),
								dmc.Popover( # pokemon search
									[
										dmc.PopoverTarget(dmc.Button('Pokémon Search', w=250, radius='md')),
										dmc.PopoverDropdown(
											dmc.MultiSelect(
												id='search-filter',
												data=pokemon_list,
												description='Search for Pokémon by name or number (max #890). Select up to 10',
												maxValues=10,
												limit=50,
												hidePickedOptions=True,
												clearable=True,
												searchable=True,
												nothingFoundMessage='no Pokémons found...',
												comboboxProps={'withinPortal': False}
											)
										)
									],
									withArrow=True,
									width=250,
									position='bottom',
									shadow='md',
									zIndex=2000
								)
							],
							style={
								'display': 'flex',
								'flex-direction': 'column',
								'gap': '5px'
							}
						)
					],
					style={
						'display': 'flex',
						'flex-direction': 'row',
						'justify-content': 'space-between',
						'align-items': 'flex-start'
					}
				),
				html.Div( # display section
					[
						dcc.Graph(
							id='graph',
							figure={},
							style={'border-right-style': 'solid', 'border-width': '1px'},
							config={
								'modeBarButtonsToRemove': ['toImage', 'select2d', 'lasso2d'],
								'displaylogo': False
							}
						),
						html.Div(
							[
								html.H4(id='name-widget', children=''),
								html.Img(id='image-widget', height='350px', width='350px'),
								dcc.Graph(id='stats-widget', figure={}, config={'staticPlot': True})
							],
							style={
								'display': 'flex',
								'flex-direction': 'column',
								'align-items': 'center'
							}
						)
					],
					style={
						'display': 'flex',
						'flex-direction': 'row'
					}
				)
			],
			style = {
				'width': '1200px',
				'height': '730px',
				'margin': '1em 1em 1em 1em'
			}
		),
		style = {
			'display': 'flex',
			'flex-direction': 'column',
			'align-items': 'center',
			'justify-content': 'center',
			'font-family': 'Arial'
		}
	)		
)


# main chart
@callback(
	Output(component_id='graph', component_property='figure'),
	Input(component_id='generation-filter', component_property='value'),
	Input(component_id='type-filter', component_property='value'),
	Input(component_id='search-filter', component_property='value')
)
def update_graph(generations, types, names):
	if names is None:
		names = []

	df = pokedex[
		(
			(pokedex['generation'].isin(generations)) &
			(pokedex['primary_type'].isin(types)) &
			(~pokedex['display_name'].isin(['generation_legend', 'type_legend']))
		) | (pokedex['display_name'].isin(names))
	].reset_index()
		
	fig = go.Figure()

	for primary_type in sorted(df['primary_type'].unique()):
	    fig.add_trace(
	    	go.Scatter(
		        x=df.loc[df['primary_type'] == primary_type, 'height'],
		        y=df.loc[df['primary_type'] == primary_type, 'weight'],
		        name=primary_type,
		        mode='markers',
		        marker=dict(
		        	opacity=.45,
		        	symbol=df.loc[df['primary_type'] == primary_type, 'marker_symbol'],
		            color=df.loc[df['primary_type'] == primary_type, 'marker_color']
		        ),
		        text=df.loc[df['primary_type'] == primary_type, 'display_name'],
		        customdata=df[df['primary_type'] == primary_type]\
		        	[['generation', 'image_path', 'hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed', 'display_height']],
		        hovertemplate=(
		        	'<b>%{text}</b><br>' +
		        	'<i>%{customdata[0]}</i><br>' +
		        	'Height: %{customdata[8]}<br>' +
		        	'Weight: %{y:} lbs<br>'
		        ),
		        showlegend=False
		    )
		)

	# create generation legend
	for index, row in pokedex[
		(
			(pokedex['generation'].isin(generations)) &
			(pokedex['primary_type'].isin(types)) &
			(pokedex['display_name'] == 'generation_legend')
		) |
		(
			(pokedex['display_name'] == 'generation_legend') &
			(pokedex['generation'].isin(pokedex[pokedex['display_name'].isin(names)]['generation'].to_list()))
		)
	].drop_duplicates(subset=['generation']).iterrows():
	    fig.add_trace(
	    	go.Scatter(
		    	x=[row['height']],
		    	y=[row['weight']],
		    	name=row['generation'],
		    	mode='markers',
		        marker=dict(
		        	symbol=[row['marker_symbol']],
		        	color=[row['marker_color']]
		        ),
		        legendgroup='Generation',
		        legendgrouptitle_text='Generation (shape)'
		    )
		)

	# create type legend
	for index, row in pokedex[
		(
			(pokedex['generation'].isin(generations)) &
			(pokedex['primary_type'].isin(types)) &
			(pokedex['display_name'] == 'type_legend')
		) |
		(
			(pokedex['display_name'] == 'type_legend') &
			(pokedex['primary_type'].isin(pokedex[pokedex['display_name'].isin(names)]['primary_type'].to_list()))
		)
	].drop_duplicates(subset=['primary_type']).iterrows():
	    fig.add_trace(
	    	go.Scatter(
		    	x=[row['height']],
		    	y=[row['weight']],
		    	name=row['primary_type'],
		    	mode='markers',
		        marker=dict(
		        	opacity=.45,
		        	symbol=[row['marker_symbol']],
		        	color=[row['marker_color']]
		        ),
	            legendgroup='Type',
	            legendgrouptitle_text='Type (color)'
		    )
		)
	
	x_range = [-df['height'].max() / 40, df['height'].max() * 1.05]
	y_range = [-df['weight'].max() / 40, df['weight'].max() * 1.05]
	
	fig.update_xaxes(
		title='Height (feet)',
		range=x_range,
		autorangeoptions_minallowed=x_range[0],
		autorangeoptions_maxallowed=x_range[1]
	)
	fig.update_yaxes(
		title='Weight (lbs)',
		range=y_range,
		autorangeoptions_minallowed=y_range[0],
		autorangeoptions_maxallowed=y_range[1]
	)
	fig.update_layout(
		legend={'itemclick': False, 'itemdoubleclick': False},
		margin=dict(t=30, b=10, l=20, r=10),
		width=850,
		height=650
	)

	return fig


# pokemon display
@callback(
	[
		Output(component_id='name-widget', component_property='children'),
		Output(component_id='image-widget', component_property='src'),
		Output(component_id='stats-widget', component_property='figure')
	],
	Input(component_id='graph', component_property='hoverData')
)
def update_widgets(hoverData):
	if hoverData is None:
		name = pokedex['display_name'].iloc[0]
		image_src = pokedex['image_path'].iloc[0]
		stats_df = pd.DataFrame(
			[
				{'stat': 'HP', 'value': pokedex['hp'].iloc[0]},
				{'stat': 'Attack', 'value': pokedex['attack'].iloc[0]},
				{'stat': 'Defense', 'value': pokedex['defense'].iloc[0]},
				{'stat': 'Special Attack', 'value': pokedex['special_attack'].iloc[0]},
				{'stat': 'Special Defense', 'value': pokedex['special_defense'].iloc[0]},
				{'stat': 'Speed', 'value': pokedex['speed'].iloc[0]}
			]
		)
		
	else:
		name = hoverData['points'][0]['text']
		image_src = hoverData['points'][0]['customdata'][1]
		stats_df = pd.DataFrame(
			[
				{'stat': 'HP', 'value': hoverData['points'][0]['customdata'][2]},
				{'stat': 'Attack', 'value': hoverData['points'][0]['customdata'][3]},
				{'stat': 'Defense', 'value': hoverData['points'][0]['customdata'][4]},
				{'stat': 'Special Attack', 'value': hoverData['points'][0]['customdata'][5]},
				{'stat': 'Special Defense', 'value': hoverData['points'][0]['customdata'][6]},
				{'stat': 'Speed', 'value': hoverData['points'][0]['customdata'][7]}
			]
		)

	# stats chart
	fig = px.bar(
		stats_df,
		x='stat',
		y='value',
		text_auto=True,
		title='Stats',
		height=230,
		width=325
	)
	fig.update_xaxes(
		tickangle=45,
		tickmode = 'array',
		tickvals = list(range(0, stats_df.shape[0])),
		ticktext=['<br>'.join(x.split()) if len(x.split()) > 0 else x for x in stats_df['stat'].to_list()]
	)
	fig.update_yaxes(
		visible=False,
		showticklabels=False,
		range=[0, 15],
		showgrid=True,
		automargin='top+bottom'
	)
	fig.update_layout(
		margin=dict(l=0, r=0, t=30, b=20),
		xaxis_title=None,
		title_x=0
	)
	
	return [name, image_src, fig]


if __name__ == '__main__':
	app.run(debug=True)
