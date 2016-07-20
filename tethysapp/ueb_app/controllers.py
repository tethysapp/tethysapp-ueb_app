from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import TextInput, SelectInput,DatePicker, GoogleMapView
import EPSG_List


@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'ueb_app/home.html', context)


def test(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'ueb_app/test.html', context)


@login_required()
def model_input(request):

    # bounding box
    north_lat = TextInput(display_text='North Latitude',
                          name='north_lat',
                          )

    south_lat = TextInput(display_text='South Latitude',
                          name='south_lat',
                          )

    west_lon = TextInput(display_text='West Longitude',
                         name='west_lon',
                          )

    east_lon = TextInput(display_text='East Longitude',
                         name='east_lon',
                         )

    # outlet point
    outlet_x = TextInput(display_text='Longitude',
                       name='outlet_x',
                       )

    outlet_y = TextInput(display_text='Latitude',
                       name='outlet_y',
                       )

    # epsg code
    epsg_code = SelectInput(display_text='',
                            name='epsg_code',
                            multiple=False,
                            options=EPSG_List.EPSG_List,
                            attributes={'style': 'width:200px'}
                           )

    # time period
    start_time = DatePicker(name='start_time',
                         display_text='Start Date',
                         autoclose=True,
                         format='MM d, yyyy',
                         today_button=True,
                         multidate='1'
                        )

    end_time = DatePicker(name='start_time',
                            display_text='End Date',
                            autoclose=True,
                            format='MM d, yyyy',
                            today_button=True,
                            multidate='1'
                            )

    # model resolution
    x_size = TextInput(display_text='X size(m)',
                       name='x_size',
                       )

    y_size = TextInput(display_text='Y size(m)',
                       name='y_size',
                       )

    dx_size = TextInput(display_text='dX size(m)',
                       name='dx_size',
                       )

    dy_size = TextInput(display_text='dY size(m)',
                        name='dy_size',
                        )

    # resource info
    res_title = TextInput(display_text='HydroShare resource title',
                       name='res_title',
                       placeholder='e.g My New UEB model inputs',
                       attributes={'style': 'width:350px'}
                       )
    res_keywords = TextInput(display_text='HydroShare resource keywords',
                       name='res_keywords',
                       placeholder='e.g. keyword1, keyword2',
                       attributes={'style': 'width:350px'}
                       )
    # context
    context = {'north_lat': north_lat,
               'south_lat': south_lat,
               'west_lon': west_lon,
               'east_lon': east_lon,
               'outlet_x': outlet_x,
               'outlet_y': outlet_y,
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