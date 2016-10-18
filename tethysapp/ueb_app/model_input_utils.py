"""
Utilities for model input preparation web services
"""
from datetime import datetime
from epsg_list import EPSG_List
from hydrods_model_input import hydrods_model_input_service
from user_settings import *


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
        north_lat = round(float(north_lat), 4)
        south_lat = round(float(south_lat), 4)
        west_lon = round(float(west_lon), 4)
        east_lon = round(float(east_lon), 4)
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
        if not (outlet_x >= west_lon and outlet_x <= east_lon):
            error_info.append('The outlet point longitude should be in the bounding box.')

        if not (outlet_y >= south_lat and outlet_y <= north_lat):
            error_info.append('The outlet point latitude should be in the bounding box.')

        if error_info:
            validation['is_valid'] = False
            validation['result']['point_title'] = ' '.join(error_info)


   # check stream threshold
    stream_threshold = request.POST['stream_threshold']
    try:
        stream_threshold = int(stream_threshold)
        thresh_type_valid = True
    except:
        validation['is_valid'] = False
        validation['result']['threshold_title'] = 'The stream threshold should be an integer or as default value 1000.'


    # check epsg
    epsg_code = request.POST['epsg_code']
    if epsg_code not in [item[1] for item in EPSG_List]:
        validation['is_valid'] = False
        validation['result']['epsg_title'] = 'Please provide the valide epsg code from the dropdown list.'
    else:
        epsg_code = int(epsg_code)

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
        # TODO check the supported time period for simulation based on the data source (2009-2015, 2005-2015)
        start_limit_obj = datetime.strptime('2010/01/01', '%Y/%M/%d')
        end_limit_obj = datetime.strptime('2011/12/31', '%Y/%M/%d')

        if start_time_obj > end_time_obj:
            validation['is_valid'] = False
            validation['result']['time_title'] = 'The end time should be equal as or later than the start time.'
        if not(start_time_obj >= start_limit_obj and end_time_obj <= end_limit_obj):
            validation['is_valid'] = False
            validation['result']['time_tile'] = 'The start and end time should be a date between {} and {}.'.\
                format(start_limit_obj.strftime('%Y/%M/%d'), end_limit_obj.strftime('%Y/%M/%d'))


    # check x, y
    x_size = request.POST['x_size']
    y_size = request.POST['y_size']

    try:
        x_size = int(x_size)
        y_size = int(y_size)
        if x_size < 1 or y_size < 1:
            validation['is_valid'] = False
            validation['result']['model_cell_title'] = 'The cell size for reprojection should not be smaller than 1 meter.'
    except:
        validation['is_valid'] = False
        validation['result']['proj_cell_title'] = 'The cell size for reprojection should be number input.'


    # check dx,dy
    dx_size = request.POST['dx_size']
    dy_size = request.POST['dy_size']

    try:
        dx_size = int(dx_size)
        dy_size = int(dy_size)
        if dx_size < 1 or dy_size < 1:
            validation['is_valid'] = False
            validation['result']['model_cell_title'] = 'The cell size for model simulation should not be smaller than 1 meter.'
    except:
        validation['is_valid'] = False
        validation['result']['model_cell_title'] = 'The cell size for model simulation should be number input.'


    # check HS res name and keywords
    res_title = request.POST['res_title']
    res_keywords = request.POST['res_keywords']

    if len(res_title) < 5:
        validation['is_valid'] = False
        validation['result']['res_title'] = 'The resource title should include at least 5 characters.'


    # create job parameter if input is valid
    if validation['is_valid']:
        # TODO: pass the hydroshare token, client-id, client-secret not the user name and password
       validation['result'] = {
            'hs_name': hs_name,
            'hs_password': hs_password,
            'hydrods_name': hydrods_name,
            'hydrods_password': hydrods_password,
            'north_lat': north_lat,
            'south_lat': south_lat,
            'west_lon': west_lon,
            'east_lon': east_lon,
            'outlet_x': outlet_x,
            'outlet_y': outlet_y,
            'watershed_name': 'UEB_model_',
            'stream_threshold': stream_threshold,
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
    # TODO: pass the hydroshare token, client-id, client-secret not the user name and password
    # generate parameter dict
    model_input_parameters = {
        'hs_name': job_parameters['hs_name'],
        'hs_password': job_parameters['hs_password'],
        'hydrods_name': job_parameters['hydrods_name'],
        'hydrods_password': job_parameters['hydrods_password'],
        'topY': job_parameters['north_lat'],
        'bottomY': job_parameters['south_lat'],
        'leftX': job_parameters['west_lon'],
        'rightX': job_parameters['east_lon'],
        'lat_outlet': job_parameters['outlet_y'],
        'lon_outlet': job_parameters['outlet_x'],
        'streamThreshold': job_parameters['stream_threshold'],
        'watershedName': job_parameters['watershed_name'],
        'epsgCode': job_parameters['epsg_code'],
        'startDateTime': job_parameters['start_time'],
        'endDateTime': job_parameters['end_time'],
        'dx': job_parameters['x_size'],
        'dy': job_parameters['y_size'],
        'dxRes': job_parameters['dx_size'],
        'dyRes': job_parameters['dy_size'],
        'res_title': job_parameters['res_title'],
        'res_keywords': job_parameters['res_keywords'],
    }

    # call the hs model input preparation service
    service_response = hydrods_model_input_service(** model_input_parameters)

    # service_response = {
    #     'status': 'Success',
    #     'result': model_input_parameters
    # }

    return service_response