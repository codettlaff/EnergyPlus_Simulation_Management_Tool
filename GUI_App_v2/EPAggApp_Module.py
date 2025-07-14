"""
Created on Tue Jan 30 15:32:25 2024

@author: Athul Jose P
"""

# Importing Required Modules
import shutil
import sys
import os
import re
import datetime
import pickle
import copy
from datetime import date, timedelta
from dash import Dash, dcc, html, Input, Output, State, dash_table
import pandas as pd
import numpy as np
import opyplus as op
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Importing User-Defined Modules
import MyDashApp_Module as AppFuncs

database_dir = os.path.join(os.path.dirname(__file__), '..', 'Database')
sys.path.append(database_dir)
import Database_Creator as db_creator
import Data_Uploader as db_uploader

def upload_custom_building(db_settings): return db_uploader.upload_custom_building(db_settings)
def get_building_id(conn, building_information): return db_uploader.get_building_id(conn, building_information)
def get_building_id_old(conn, building_type, building_name): return db_uploader.get_building_id_old(conn, building_type, building_name)


database_generation_dir = os.path.join(os.path.dirname(__file__), '..', 'Data_Generation')
sys.path.append(database_generation_dir)
import EP_DataAggregation_v2_20250619 as EP_Agg

import PSQLApp_Module as psql

tab_layout =[
    
            dbc.Row([

                # First Column
                dbc.Col([
                    dcc.Store(id='agg_input_variables_pickle_filepath'),
                    dcc.Store(id='agg_input_eio_pickle_filepath'),
                    # Input selection
                    dcc.RadioItems(
                    id = 'agg_input_selection',
                    labelStyle = {'display': 'block'},
                    options = [
                        {'label' : " Continue Session", 'value' : 1},
                        {'label' : " Upload Files", 'value' : 2}
                        ]  ,
                    value = 1,
                    className = 'ps-4 p-3',
                    style = {
                        'width': '100%',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        }
                    ),

                    html.Br(),

                    # Box 2 C1
                    html.Div([
                        dcc.Store(id='upload_variable_pickle_filepath', data=None),
                        dcc.Store(id='upload_eio_pickle_filepath', data=None),
                        # Upload Pickled Variable file
                        dcc.Upload(['Upload Pickled Variable file'],
                            className = 'center',
                            id = 'agg_upload_variables_pickle',
                            style = {
                                'width': '90%',
                                'height': '40px',
                                'lineHeight': '40px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin-left': '5%',
                                'margin-top': '5%'
                                }),

                        # Upload EIO file
                        dcc.Upload(['Upload EIO file'],
                            className = 'center',
                            id = 'agg_upload_eio_pickle',
                            style = {
                                'width': '90%',
                                'height': '40px',
                                'lineHeight': '40px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '5%',
                                }),

                        ],id = 'agg_inputs_upload_files',
                        hidden = True,
                        style = {
                            'borderWidth': '1px',
                            'borderStyle': 'solid',
                            'borderRadius': '5px',
                            #'display':'none'
                            }),

                    html.Br(),

                    # Aggregation Variables
                    html.Div([
                        dcc.RadioItems(
                            id = 'agg_variable_all_or_select',
                            labelStyle = {'display': 'block'},
                            options = [
                                {'label' : " All Variables", 'value' : 1},
                                {'label' : " Select Variables", 'value' : 2}
                                ]  ,
                            value = 2,
                            className = 'ps-4 p-3',
                        ),

                        html.Label("Available Variables",
                            className = 'text-left ms-4'),
                        dcc.Dropdown([], '',
                            multi = True,
                            id='agg_variable_selection',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',
                                'margin-bottom': '2.5%'
                                }),

                    ],id = 'agg_variables_menu',
                    hidden = True,
                    style = {
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        },),

                    html.Br(),

                ], xs = 12, sm = 12, md = 6, lg = 6, xl = 6,),


                # Second Column
                dbc.Col([

                    # Box 1 C2
                    html.Div([
                        dcc.Store(id='aggregation_settings', data={
                            'aggregation_zone_list': [[]],
                            'aggregation_type': None,
                            'aggregation_variable_list': []
                        }),
                        # Zone selection
                        html.Label("Available Zones",
                            className = 'text-left ms-4 mt-1'),
                        dcc.Dropdown([], '',
                            id='agg_zone_list',
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%',   
                                }),

                        dcc.RadioItems(
                            id = 'aggregate_to_selection',
                            labelStyle = {'display': 'block'},
                            options = [
                                {'label' : " Aggregate to one", 'value' : 1},
                                {'label' : " Custom Aggregation", 'value' : 2}
                                ]  ,
                            value = 1,
                            className = 'ps-4 p-3',
                        ),

                        html.Label("Input Custom Aggregation Zone List",
                            className = 'text-left ms-4 mt-1'),
                        dcc.Textarea(
                            id='custom_aggregation_zone_list',
                            placeholder="zone_1,zone_2,zone_3;zone_4,zone_5,zone_6",
                            value='',
                            style={'width': '90%',
                                   'margin-left':'5%',
                                   'height': 30},
                        ),

                        # Type of Aggregation
                        html.Label("Type of Aggregation",
                            className = 'text-left ms-4 mt-1'),
                        dcc.Dropdown([
                            {'label' : " Average", 'value' : 1},
                            {'label' : " Weighted Floor Area Average", 'value' : 2},
                            {'label' : " Weighted Volume Average", 'value' : 3},
                            ],
                            id='aggregation_type',
                            value=1,
                            style = {
                                'width': '95%',
                                'margin-left': '2.5%', 
                                'margin-bottom': '2.5%'  
                                }),

                    ],id = 'aggregation_details_menu',
                    hidden = True,
                    style = {
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        },),

                    html.Br(),

                    # Box 2 C2
                    html.Div([
                        dcc.Store(id='aggregation_pickle_filepath', data=None),
                        html.Button('Aggregate',
                            id = 'aggregate_data_button',
                            className = "btn btn-secondary btn-lg col-12",
                            hidden = True,
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        html.Button('Upload to Database',
                            id = 'agg_upload_to_db_button',
                            hidden = True,
                            className = "btn btn-secondary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin':'5%'
                                },),

                        html.Button('Download',
                            id = 'agg_download_button',
                            hidden = True,
                            className = "btn btn-primary btn-lg col-12",
                            style = {
                                'width':'90%',
                                'margin-left':'5%',
                                'margin-bottom':'5%'
                                },),
                        dcc.Download(id = 'agg_download_files'),


                    ],id = 'aggregation_final_box',
                    hidden = True,
                    style = {
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        },),

                    # Simulation Information Box
                    html.Div(
                        children=[
                            dcc.Input(
                            id='agg_simulation_name',
                            type='text',
                            value='',
                            placeholder='Enter Simulation Name',
                            className="center-placeholder center-input",
                            style={
                                'width':'100%',
                                'height':'50px',
                                'margin':'0%',
                                'text-align': 'center',
                                'font-size': '24px'
                                },),

                        dcc.RadioItems(
                            id = 'agg_upload_to_db_custom_or_no',
                            labelStyle = {'display': 'block'},
                            options = [
                                {'label' : " Custom Building", 'value' : 1},
                                {'label' : " Find Building in Database", 'value' : 2}
                                ]  ,
                            value = 1,
                            className = 'ps-4 p-3',
                        ),

                        # Time-step selection
                        dbc.Stack([
                            html.Label("Building ID",
                                       className='text'),
                            daq.NumericInput(
                                id='building_id',
                                value=1,
                                style={'margin-left': '28%'}
                            ),
                        ], direction="horizontal",
                            style={'margin': '5%'}
                        ),

                        ],
                        hidden=True,
                        style={
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderRadius': '5px',
                        'margin': '30px 0',
                        },
                        id='simulation_info_box'  # optional: add an ID if you'll reference it in callbacks
                    ),

                    html.Br(),

                ], xs = 12, sm = 12, md = 6, lg = 6, xl = 6,),

                html.Button('End Session',
                    id = 'Button_es_aggregation',
                    className = "btn btn-primary btn-lg col-12",
                    style = {
                        'width':'98%',
                        'margin-left':'1%'
                        },),

                ])
            
]

def get_variable_list(variables_pickle_filepath):

    variables_list = []
    with open(variables_pickle_filepath, 'rb') as f: data_dict = pickle.load(f)
    for key, value in data_dict.items():
        if key != 'DateTime_List': variables_list.append(key)

    return variables_list

def get_zone_list(eio_pickle_filepath):

    with open(eio_pickle_filepath, 'rb') as f: eio_dict = pickle.load(f)
    zone_list = list(eio_dict['Zone Information'][eio_dict['Zone Information']['  Part of Total Building Area']  == 'Yes']['Zone Name'])
    return zone_list

def aggregate_data(aggregation_settings, variables_pickle_filepath, eio_pickle_filepath):
    variable_list = aggregation_settings['aggregation_variable_list']
    aggregation_type = aggregation_settings['aggregation_type']
    aggregation_zone_list = aggregation_settings['aggregation_zone_list']
    aggregation_pickle_filepath = EP_Agg.aggregate_data(variables_pickle_filepath, eio_pickle_filepath, variable_list, aggregation_type, aggregation_zone_list)
    return aggregation_pickle_filepath

def get_time_res(data_dict):
    start_datetime = data_dict['DateTime_List'][0]
    end_datetime = data_dict['DateTime_List'][-1]
    time_resolution = int((data_dict['DateTime_List'][1] - start_datetime).total_seconds() / 60)
    return start_datetime, end_datetime, time_resolution

def upload_to_db(db_settings, sim_name, aggregation_pickle_filepath, building_information, simulation_settings, aggregation_settings, building_id, variables_pickle_filepath, eio_pickle_filepath):

    conn = psql.connect(db_settings)
    with open(aggregation_pickle_filepath, "rb") as f: data_dict = pickle.load(f)

    epw_climate_zone = 'NA'

    time_resolution = simulation_settings['timestep_minutes']
    start_datetime = simulation_settings['start_datetime'] + timedelta(minutes=time_resolution)
    end_datetime = simulation_settings['end_datetime'] + timedelta(days=1)
    db_uploader.populate_datetimes_table(conn, base_time_resolution=1, start_datetime=start_datetime,
                                             end_datetime=end_datetime)

    simulation_settings['start_datetime'] = start_datetime
    simulation_settings['end_datetime'] = end_datetime

    # Not continuing from session
    # First, do all-zones aggregation on variables.pickle and eio.pickle - got this working, all_zones_df looks good
    all_zone_aggregation_pickle_filepath = EP_Agg.aggregate_data(variables_pickle_filepath, eio_pickle_filepath, aggregation_settings['aggregation_variable_list'])
    with open(all_zone_aggregation_pickle_filepath, "rb") as f: all_zone_data_dict = pickle.load(f)
    all_zones_df = db_uploader.upload_time_series_data(conn, all_zone_data_dict, sim_name, simulation_settings, building_id, epw_climate_zone, time_resolution)

    # make aggregation zone dict out of aggregation zone list - also needs zone ids
    aggregation_zone_dict = {}
    base_name = 'AGGREGATION_ZONE_'
    count = 0
    for aggregation_zone in aggregation_settings['aggregation_zone_list']:
        count += 1
        zones = [item.strip() for item in aggregation_zone]
        aggregation_zone_name = base_name + str(count)
        aggregation_zone_dict[aggregation_zone_name] = all_zones_df[all_zones_df['zone_name'].isin(zones)] # Segments all_zones_df to only include rows where the zone name is in the current aggregation zone name.

    return db_uploader.upload_time_series_data(conn, data_dict, sim_name, simulation_settings, building_id, epw_climate_zone, time_resolution, aggregation_zone_dict)



