"""
Utilities for model input preparation web services
"""
from datetime import datetime
from epsg_list import EPSG_List


def validate_model_input_form(request):

    validation = {
        'is_valid': True,
        'result': {}
    }

    # check the bounding box value
    north_lat = request.POST['north_lat']
    south_lat = request.POST['south_lat']
    west_lon = request.POST['west_lon']
    east_lon = request.POST['east_lon']

    try:
        north_lat = float(north_lat)
        south_lat = float(south_lat)
        west_lon = float(west_lon)
        east_lon = float(east_lon)
        box_type_valid = True

    except Exception:
        validation['is_valid'] = False
        validation['result']['box_title'] = 'Please enter number values for bounding box.'
        box_type_valid = False

    if box_type_valid:
        error_info = []

        if north_lat <= 24.9493 or north_lat >= 49.5904:
            error_info.append('The North Latitude should be in the US continent.')

        if south_lat <= 24.9493 or south_lat >= 49.5904:
            error_info.append('The South Latitude should be in the US continent.')

        if south_lat >= north_lat:
            error_info.append('The South Latitude should be smaller than the North Latitude.')

        if west_lon <= -125.0011 or west_lon >= -66.9326:
            error_info.append('The West Longitude should be in the US continent.')

        if east_lon <= -125.0011 or east_lon >= -66.9326:
            error_info.append('The East Longitude should be in the US continent.')

        if west_lon >= east_lon:
            error_info.append('The West Longitude should be smaller than the East Longitude.')

        if error_info:
            validation['is_valid'] = False
            validation['result']['box_title'] = ' '.join(error_info)


    # check the outlet point value
    outlet_x = request.POST['outlet_x']
    outlet_y = request.POST['outlet_y']

    try:
        outlet_x = float(outlet_x)
        outlet_y = float(outlet_y)
        point_type_valid = True

    except Exception:
        validation['is_valid'] = False
        validation['result']['point_title'] = 'Please enter number values for outlet point.'
        point_type_valid = False

    if point_type_valid:
        error_info = []
        if not (outlet_x >= west_lon and outlet_x <= east_lon) :
            error_info.append('The outlet point longitude should be in the bounding box.')

        if not (outlet_y >= south_lat and outlet_y <= north_lat):
            error_info.append('The outlet point latitude should be in the bounding box.')

        if error_info:
            validation['is_valid'] = False
            validation['result']['point_title'] = ' '.join(error_info)


    # check epsg
    epsg_code = request.POST['epsg_code']
    if epsg_code not in [item[1] for item in EPSG_List]:
        validation['result']['epsg_title'] = 'Please provide the valide epsg code from the dropdown list.'


    # check the date
    start_time_str = request.POST['start_time']
    end_time_str = request.POST['end_time']

    try:
        start_time_obj = datetime.strptime(start_time_str, '%Y/%M/%d')
        end_time_obj = datetime.strptime(end_time_str, '%Y/%M/%d')
        time_type_valid = True
    except:
        validation['is_valid'] = False
        validation['result']['time_title'] = 'Please provide time information.'
        time_type_valid = False

    if time_type_valid:
        if start_time_obj > end_time_obj:
            validation['is_valid'] = False
            validation['result']['time_title'] = 'The end time should be equal as or later than the start time.'
    # TODO check the supported time period for simulation based on the data source

    # check x, y
    x_size = request.POST['x_size']
    y_size = request.POST['y_size']

    try:
        x_size = float(x_size)
        y_size = float(y_size)
        proj_cell_valid = True
    except:
        validation['is_valid'] = False
        validation['result']['proj_cell_title'] = 'The cell size for reprojection should be number value.'
        proj_cell_valid = False


    # check dx,dy
    dx_size = request.POST['dx_size']
    dy_size = request.POST['dy_size']

    if dx_size or dy_size:
        try:
            dx_size = float(dx_size)
            dy_size = float(dy_size)
        except:
            validation['is_valid'] = False
            validation['result']['model_cell_title'] = 'The cell size for model simulation should be number values or as empty.'


    # check HS res name and keywords
    res_title = request.POST['res_title']
    res_keywords = request.POST['res_keywords']


    # create job parameter if input is valid
    if validation['is_valid']:
        validation['result'] = {
            'north_lat': north_lat,
            'south_lat': south_lat,
            'west_lon': west_lon,
            'east_lon': east_lon,
            'outlet_x': outlet_x,
            'outlet_y': outlet_y,
            'epsg_code': epsg_code,
            'start_time': start_time_str,
            'end_time': end_time_str,
            'x_size': x_size,
            'y_size': y_size,
            'dx_size': dx_size,
            'dy_size': dy_size,
            'res_title': res_title,
            'res_keywords': res_keywords
        }

    return validation


def submit_model_input_job(job_parameters):

    model_input_job = {
        'status': 'Success',
        'result': job_parameters
    }

    return model_input_job