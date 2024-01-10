import dash
from dash import Dash, html, dcc, callback, Output, Input, dash_table
from dash.exceptions import PreventUpdate
from dash.dependencies import State
import plotly.express as px
import pandas as pd
import os
import sys
sys.path.append('C:\\Users\A00007579\PycharmProjects\pythonProject')
sys.path.append('C:\\Users\A00007579\PycharmProjects\pythonProject\Sundry')
sys.path.append('C:\\Users\A00007579\PycharmProjects\pythonProject\Builds')
sys.path.append('C:\\Users\A00007579\PycharmProjects\pythonProject\DataLake')
sys.path.append('C:\\Users\A00007579\PycharmProjects\pythonProject\Analytics')

from Utilities import *
from Conventions import FUT_CT,FUT_CT_Q, ccy, ccy_infl
from OIS_DC_BUILD import ois_dc_build
from SWAP_BUILD import swap_build
from SWAP_PRICER import Swap_Pricer, Swap_curve_fwd, quick_swap
from SWAP_TABLE import swap_table, swap_table2, swap_table3, curve_hmap
from INF_ZC_BUILD import infl_zc_swap_build, Infl_ZC_Pricer, inf_swap_table
from BOND_CURVES import bond_curve_build
from VOL_BUILD import build_vol_surf, build_vol_spline, bond_fut_opt_strat, get_sim_option_px, build_stir_vol_surf, stir_opt_strat
from PLOT import plt_curve, plt_inf_curve, plt_opt_strat, rates_hm, curve_hm, plt_ois_curve, plot_opt_vol_surf, plt_stir_opt_strat, plotool, ecfc_plot
from BOND_TABLES import linker_table
from INFL_CARRY import linker_carry_calc

app2 = Dash(__name__)

today = ql.Date(datetime.datetime.now().day,datetime.datetime.now().month,datetime.datetime.now().year)

crv_list = ["SOFR_DC", "FED_DC", "ESTER_DC", "EONIA_DC", "SONIA_DC", "CAD_OIS_DC", "AONIA_DC", "NZD_OIS_DC",
             "CHF_OIS_DC", "SEK_OIS_DC", "TONAR_DC", "RUONIA_DC", "EUR_3M", "EUR_6M", "CAD_3M", "CHF_6M", "SEK_3M",
             "NOK_3M", "NOK_6M", "JPY_6M", "AUD_3M", "AUD_6M", "NZD_3M", "KRW_3M", "PLN_3M", "PLN_6M", "CZK_3M",
             "CZK_6M", "HUF_3M", "HUF_6M", "ZAR_3M", "ILS_3M", "RUB_3M", "COP_OIS_DC", "MXN_TIIE"]

columns_to_format1 = ['chg']

# Generate conditional styles for the specified columns

style_data_conditional = [{'if': {'column_id': col_id, 'filter_query': f'{{{col_id}}} lt 0'}, 'color': 'red'} for col_id in columns_to_format1] \
                         + [{'if': {'column_id': col_id, 'filter_query': f'{{{col_id}}} ge 0'}, 'color': 'green'} for col_id in columns_to_format1]


app2.layout = html.Div([
    html.Div(children='Swap Monitor', style={'color': 'black', 'fontFamily': 'Calibri', 'fontSize': '20px'}),

    html.Div([
        html.Div([
            html.Div([
                html.Label('Curve Date ',
                           style={'color': 'blue',
                                  'fontFamily': 'Calibri', 'fontSize': '14px',
                                  'paddingTop': '15px',
                                  'marginRight': '4px'}
                       ),
                dcc.DatePickerSingle(id='crv_date', date=ql_to_datetime(today),  display_format="DD-MM-YYYY",
                                     style={'fontFamily': 'Calibri', 'fontSize': '14px',
                                            'paddingTop': '5px'})
            ],
                style={'display': 'flex',
                       'justifyContent': 'flex-end',
                       'paddingTop': '5px'}),

            html.Div([
                html.Label('Offset        ',
                           style={'color': 'blue',
                                  'fontFamily': 'Calibri', 'fontSize': '14px',
                                  'paddingTop': '15px',
                                  'marginRight': '4px'}
                           ),
                dcc.DatePickerSingle(id='offset_date', date=ql_to_datetime(ql.UnitedStates(ql.UnitedStates.FederalReserve).advance(today,-1,ql.Days)), display_format="DD-MM-YYYY",
                                     style={'fontFamily': 'Calibri', 'fontSize': '14px',
                                            'paddingTop': '5px'})
            ],
                style={'display': 'flex',
                       'justifyContent': 'flex-end',
                       'paddingTop': '5px'}),

            html.Div([
                html.Button('Build', id='build-button',
                            style={'color': 'red',
                                   'backgroundColor': 'lightgray',
                                   'width': '75px',
                                   'height': '30px',
                                   'cursor': 'pointer',
                                   'marginRight': '10px'}),
                html.Button('Calc', id='calc-button',
                            style={'color': 'red',
                                   'backgroundColor': 'lightgray',
                                   'width': '75px',
                                   'height': '30px',
                                   'cursor': 'pointer'})],
                style={'display': 'flex',
                       'justifyContent': 'start',
                       'paddingTop': '5px'}),

            html.Div([
                dcc.RadioItems(id='radio-input', options=[{'label': option, 'value': option} for option in crv_list],value=crv_list[0],
                               labelStyle={'display': 'block'},
                               style={'border': '2px solid black',
                                      'backgroundColor': 'lightblue',
                                      'fontFamily': 'Calibri', 'fontSize': '13px',
                                      'paddingRight': '5px',
                                      'paddingTop': '5px',
                                      'paddingBottom': '5px',
                                      'width': '160px',
                                      'height': '800px'})],
                style={'paddingTop': '5px'})
        ],
            style={'width': '12%',
                   'display': 'flex',
                   'flex-direction': 'column'}),

        html.Div([
            # Table 1
            html.Div([
                dash_table.DataTable(
                    id='table-1',
                    # ... your DataTable properties for table 1 ...
                    style_table={'width': '100%', 'height': '60%'},
                    style_cell={'fontFamily': 'Calibri', 'fontSize': '12px', 'border': 'none'},
                    style_header={'backgroundColor': 'lightgray',  'color': 'blue','borderBottom': '1.5px solid black'},
                    style_data={'backgroundColor': 'white'},
                    style_data_conditional=[{'if': {'column_id': col_id, 'filter_query': f'{{{col_id}}} lt 0'}, 'color': 'red'} for col_id in columns_to_format1] \
                                           + [{'if': {'column_id': col_id, 'filter_query': f'{{{col_id}}} ge 0'}, 'color': 'green'} for col_id in columns_to_format1]
                                           +[{'if': {'column_id': 'chg'},'textAlign': 'left'}]
                                           +[{'if': {'column_id': 'swaps'},'textAlign': 'left'}]
                                           +[{'if': {'column_id': 'rates'},'textAlign': 'left'}]
                                           +[{'if': {'column_id': 'swaps'}, 'backgroundColor': 'lightgray'}]
                                           +[{'if': {'row_index': 17}, 'color': 'blue', 'backgroundColor': 'lightgray', 'borderBottom': '1.5px solid black', 'borderTop': '1.5px solid black'}]
                )
            ], style={'border': '2px solid black', 'width': '140px', 'height': '950px', 'display': 'inline-block', 'marginRight': '10px'}),

            # Table 2 (similar structure)
            html.Div([
                html.Div([
                    dash_table.DataTable(
                        id='table-2',
                        style_table={'width': '100%', 'height': '100%'},
                        style_cell={'fontFamily': 'Calibri', 'fontSize': '12px', 'border': 'none'},
                        style_header={'backgroundColor': 'lightgray',  'color': 'blue','borderBottom': '1.5px solid black'},
                        style_data={'backgroundColor': 'white'},
                        style_data_conditional=style_data_conditional
                    )
                ], style={'border': '2px solid black', 'width': '350px', 'height': '250px', 'display': 'inline-block', 'marginRight': '10px', 'verticalAlign': 'top'}),

            ], style={ 'width': '350px', 'height': '600px', 'display': 'inline-block', 'verticalAlign': 'top'})

        ], style={'display': 'flex', 'justifyContent': 'space-between', 'paddingTop': '10px', 'marginRight': '10px', 'marginLeft': '10px'}),
    ],
        style={'display': 'flex'})
])

@app2.callback(
    Output('offset_date', 'date'),
    Input('crv_date', 'date')
)
def update_offset_date(crv_date):
    dt_crv_date = datetime_to_ql(datetime.datetime.strptime(crv_date, '%Y-%m-%d'))
    offset = ql_to_datetime(ql.UnitedStates(ql.UnitedStates.FederalReserve).advance(dt_crv_date,-1,ql.Days))
    # Return the date in string format
    return offset.strftime('%Y-%m-%d')

@app2.callback(
    [
        Output('table-1', 'data'),
        Output('table-1', 'columns'),
        Output('table-2', 'data'),
        Output('table-2', 'columns'),
        # ... for other tables ...
    ],
    Input('build-button', 'n_clicks'),
    State('crv_date', 'date'),
    State('offset_date', 'date'),
    State('radio-input', 'value')
)

def update_output(n_clicks, crv_date, offset_date, value):
    if not n_clicks:
        raise PreventUpdate
    print(value)
    print(crv_date)

    outright_rates = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
    fwd_rates = [(1, 1), (2, 1), (3, 1), (4, 1), (2, 2), (3, 2), (5, 5), (10, 5), (10, 10), (15, 15)]
    curve_rates = [(2, 3), (2, 5), (2, 10), (5, 10), (5, 30), (10, 30)]
    fly_rates = [(2, 3, 5), (2, 5, 10), (3, 5, 7), (5, 10, 30)]
    shift = [0, '1M', '3M', '6M', 1]

#    crv1 = ois_dc_build(value, b=convert_date_format(crv_date))
    t1 = swap_table3([ois_dc_build(value),ois_dc_build(value, b = convert_date_format(offset_date))],
                     outright_rates, fwd_rates, curve_rates, fly_rates,  shift = shift, price_nodes = 1)

    d1 = pd.DataFrame()
    d1['swaps'] = outright_rates+['fwds']+[str(fwd_rates[i]) for i in np.arange(len(fwd_rates))]
    d1['rates'] = list(np.round([t1.par[2*i] for i in np.arange(len(outright_rates))],3))+['rates']+list(np.round([t1.fwds[2*i] for i in np.arange(len(fwd_rates))],3))
    d1['chg'] = list(np.round([t1.par[(2*i)+1][0] for i in np.arange(len(outright_rates))],1))+['chg']+list(np.around([t1.fwds[(2*i)+1][0] for i in np.arange(len(fwd_rates))],1))

    data_table_1 = d1.to_dict('records')
    columns_table_1  = [{'name': col, 'id': col} for col in d1.columns]

    d2 = pd.DataFrame()
    d2['curves'] = [str(curve_rates[i]) for i in np.arange(len(curve_rates))]
    d2['sprd'] = np.round([t1.curve[i*3] for i in np.arange(len(curve_rates))],1)
    d2['chg'] = np.round([t1.curve[(3*i)+1][0] for i in np.arange(len(curve_rates))],1)
    for i in np.arange(1,len(shift)):
        d2[str(shift[i])] = np.round([t1.curve[(3*j)+2][i-1] for j in np.arange(len(curve_rates))],1)

    data_table_2 = d2.to_dict('records')
    columns_table_2 = [{'name': col, 'id': col} for col in d2.columns]

    return data_table_1, columns_table_1, data_table_2, columns_table_2

if __name__ == '__main__':
    app2.run(debug=True)

#crv1 = ois_dc_build('SOFR_DC')
#t1 = swap_table3([ois_dc_build('SOFR_DC'), ois_dc_build('SOFR_DC',b='31-07-2023')], outright_rates, fwd_rates, curve_rates, fly_rates, shift=[0, '1M', '3M', '6M', 1], price_nodes=1)


#[t1.par[2*i] for i in np.arange(len(outright_rates))]
#[t1.par[(2*i)+1][0] for i in np.arange(len(outright_rates))]
#[t1.par[(2*i)+1][0] for i in np.arange(len(outright_rates))]

#[t1.curve[i*3] for i in np.arange(len(curve_rates))]
#[t1.curve[(3*i)+1][0] for i in np.arange(len(curve_rates))]
#[t1.curve[(3*i)+2] for i in np.arange(len(curve_rates))]

#[t1.par[2*i] for i in np.arange(len(outright_rates))]+[t1.fwds[2*i] for i in np.arange(len(fwd_rates))]