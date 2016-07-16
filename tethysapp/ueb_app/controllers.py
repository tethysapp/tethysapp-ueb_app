from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import TextInput, SelectInput,DatePicker, GoogleMapView



@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'ueb_app/home.html', context)


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
                            options=['1','2','3'],
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

    # map
    google_map_view = GoogleMapView(height='600px',
                                    width='100%',
                                    drawing_types_enabled=['POLYGONS', 'POINTS'],
                                    initial_drawing_mode='POLYGONS',
                                    output_format='WKT')


    # GeoJSON Example
    google_map_view_options = {'height': '700px',
                               'width': '100%',
                               'maps_api_key': 'AIzaSyCHOUQD9R_tLb6NKA22cuTTvF0j6X8wkgI',
                               'drawing_types_enabled': ['POLYGONS', 'POINTS'],
                               'initial_drawing_mode': 'POLYGONS',
                            }
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
               'google_map_view_options': google_map_view_options,
               'google_map_view': google_map_view
               }

    return render(request, 'ueb_app/model_input.html', context)