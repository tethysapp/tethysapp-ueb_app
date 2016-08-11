import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from tethys_sdk.gizmos import TextInput, SelectInput,DatePicker, GoogleMapView

from epsg_list import EPSG_List
from model_input_utils import *


# home page views
@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'ueb_app/home.html', context)


# model input views and ajax
@login_required()
def model_input(request):

    # bounding box
    north_lat = TextInput(display_text='North Latitude',
                          name='north_lat',
                          attributes={'required': True}
                          )

    south_lat = TextInput(display_text='South Latitude',
                          name='south_lat',
                          attributes={'required': True}
                          )

    west_lon = TextInput(display_text='West Longitude',
                         name='west_lon',
                         attributes={'required': True}
                          )

    east_lon = TextInput(display_text='East Longitude',
                         name='east_lon',
                         attributes={'required': True}
                         )

    # outlet point
    outlet_x = TextInput(display_text='Longitude',
                       name='outlet_x',
                       attributes={'required': True}
                       )

    outlet_y = TextInput(display_text='Latitude',
                       name='outlet_y',
                       attributes={'required': True}
                       )

    # wathershed name and threshold
    watershed_name = TextInput(display_text='Watershed Name',
                       name='watershed_name',
                       initial='my watershed',
                       attributes={'style': 'width:350px'}
                       )

    stream_threshold = TextInput(display_text='Stream Threshold',
                       name='stream_threshold',
                       initial='1000',
                       attributes={'style': 'width:350px'}
                       )

    # epsg code
    epsg_code = SelectInput(display_text='',
                            name='epsg_code',
                            multiple=False,
                            options=EPSG_List,
                            initial=['4326'],
                            attributes={'style': 'width:200px', 'required': True}
                            )

    # time period
    start_time = DatePicker(name='start_time',
                         display_text='Start Date',
                         autoclose=True,
                         format='yyyy/mm/dd',
                         today_button=True,
                         multidate='1',
                         attributes={'required': True}
                        )

    end_time = DatePicker(name='end_time',
                            display_text='End Date',
                            autoclose=True,
                            format='yyyy/mm/dd',
                            today_button=True,
                            multidate='1',
                            attributes={'required': True}
                            )

    # model resolution
    x_size = TextInput(display_text='X size(m)',
                       name='x_size',
                       attributes={'required': True}
                       )

    y_size = TextInput(display_text='Y size(m)',
                       name='y_size',
                       attributes={'required': True}
                       )

    dx_size = TextInput(display_text='dX size(m)',
                       name='dx_size',
                       attributes={'required': True}
                       )

    dy_size = TextInput(display_text='dY size(m)',
                        name='dy_size',
                        attributes={'required': True}
                        )

    # resource info
    res_title = TextInput(display_text='HydroShare resource title',
                       name='res_title',
                       placeholder='e.g My New UEB model inputs',
                       attributes={'style': 'width:350px','required':True}
                       )
    res_keywords = TextInput(display_text='HydroShare resource keywords',
                       name='res_keywords',
                       placeholder='e.g. keyword1, keyword2',
                       attributes={'style': 'width:350px','required':True}
                       )
    # context
    context = {'north_lat': north_lat,
               'south_lat': south_lat,
               'west_lon': west_lon,
               'east_lon': east_lon,
               'outlet_x': outlet_x,
               'outlet_y': outlet_y,
               'watershed_name': watershed_name,
               'stream_threshold': stream_threshold,
               'epsg_code': epsg_code,
               'start_time': start_time,
               'end_time': end_time,
               'x_size': x_size,
               'y_size': y_size,
               'dx_size': dx_size,
               'dy_size': dy_size,
               'res_title': res_title,
               'res_keywords': res_keywords,
               }

    return render(request, 'ueb_app/model_input.html', context)


@login_required()
def model_input_submit(request):
    ajax_response = {}

    if request.is_ajax and request.method == 'POST':

        validation = validate_model_input_form(request)

        if validation['is_valid']:
            model_input_job = submit_model_input_job(validation['result'])
            ajax_response = model_input_job
        else:
            ajax_response['status'] = 'Error'
            ajax_response['result'] = ' '.join(validation['result'].values())

    else:
        ajax_response['status'] = 'Error'
        ajax_response['result'] = 'Please verify that the request is ajax call with post method'

    return HttpResponse(json.dumps(ajax_response))


# test part #
def test(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'ueb_app/test.html', context)


def test_submit(request):

    return HttpResponse(json.dumps({'name':'name'}))