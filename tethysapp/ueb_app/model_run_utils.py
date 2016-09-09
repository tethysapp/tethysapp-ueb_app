"""
utility functions for model run service
"""

import shutil
import os
import zipfile
import tempfile

from hydrogate import HydroDS
from model_parameters_list import site_initial_variable_codes, input_vairable_codes


def submit_model_run_job(res_id, OAuthHS, hydrods_name, hydrods_password):
    # TODO: call model run service

    try:
        # authentication
        hs = OAuthHS['hs']
        client = HydroDS(username=hydrods_name, password=hydrods_password)
        
        # clean up the HydroDS space
        for item in client.list_my_files():
            try:
                client.delete_my_file(item.split('/')[-1])

            except Exception as e:
                continue

        # download resource bag
        temp_dir = tempfile.mkdtemp()
        hs.getResource(res_id, temp_dir, unzip=False)
        bag_path = os.path.join(temp_dir, res_id + '.zip')
        zf = zipfile.ZipFile(bag_path)
        zf.extractall(temp_dir)
        zf.close()
        os.remove(bag_path)

        # validate files and run model service
        model_input_folder = os.path.join(temp_dir, res_id, 'data', 'contents')

        if os.path.isdir(model_input_folder):  # the resource contents model input files

            # validate the model input files
            validation = validate_model_input_files(model_input_folder)

            # upload the model input and parameter files to HydroDS
            if validation['is_valid']:
                zip_file_path = os.path.join(model_input_folder, 'input_package.zip')
                zf = zipfile.ZipFile(zip_file_path, 'w')
                for file_path in validation['result']:
                    zf.write(file_path)
                zf.close()
                upload_zip_file_url = client.upload_file(file_to_upload=zip_file_path)
                client.delete_my_file(upload_zip_file_url.split('/')[-1])  # TODO clean this line for testing

                model_run_job = {
                    'status': 'Success',
                    'result': upload_zip_file_url
                }

            else:
                model_run_job = {
                    'status': 'Error',
                    'result': validation['result']
                }

        else:  # the resource doesn't have files
            model_run_job = {
                'status': 'Error',
                'result': 'The model instance resource includes no model input data and parameter files.'
            }

        # remove the tempdir
        shutil.rmtree(temp_dir)

    except Exception as e:

        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)

        model_run_job = {
            'status': 'Error',
            'result': 'Failed to submit the model execution.' + e.message
        }

    return model_run_job


def validate_model_input_files(model_input_folder):
    try:
        # move all files from zip and folders in the same model_input_folder level
        model_files_path_list = move_files_to_folder(model_input_folder)

        if model_files_path_list:

            # check model parameter files:
            validation = validate_param_files(model_input_folder)

            # check the data input files:
            if validation['is_valid']:
                validation = validate_data_files(model_input_folder, validation['result'])
        else:
            validation = {
                'is_valid': False,
                'result': 'Failed to unpack the model instance resource for file validation.'
            }

    except Exception as e:

        validation = {
            'is_valid': False,
            'result': 'Failed to validate the model input files before submitting the model execution job. ' + e.message
        }

    return validation


def move_files_to_folder(model_input_folder):
    """
    move all the files in sub-folder or zip file to the given folder level and remove the zip and sub-folders
    Return the new file path list in the folder
    """
    try:
        model_files_path_list = [os.path.join(model_input_folder, name) for name in os.listdir(model_input_folder)]

        while model_files_path_list:
            added_files_list = []

            for model_file_path in model_files_path_list:

                if os.path.isfile(model_file_path) and os.path.splitext(model_file_path)[1] == '.zip':
                    zf = zipfile.ZipFile(model_file_path, 'r')
                    zf.extractall(model_input_folder)
                    extract_file_names = zf.namelist()
                    added_files_list += [os.path.join(model_input_folder, name) for name in extract_file_names]
                    zf.close()
                    os.remove(model_file_path)

                elif os.path.isdir(model_file_path):
                    for dirpath, _, filenames in os.walk(model_file_path):
                        for name in filenames:
                            sub_file_path = os.path.abspath(os.path.join(dirpath, name))
                            new_file_path = os.path.join(model_input_folder, name)
                            shutil.move(sub_file_path, new_file_path)
                            added_files_list.append(new_file_path)
                    shutil.rmtree(model_file_path)

            model_files_path_list = added_files_list

        model_files_path_list = [os.path.join(model_input_folder, name) for name in os.listdir(model_input_folder)]

    except Exception as e:
        model_files_path_list = []

    return model_files_path_list


def validate_param_files(model_input_folder):
    try:

        if 'control.dat' in os.listdir(model_input_folder):

            # get the control file path and contents
            file_path = os.path.join(model_input_folder, 'control.dat')
            with open(file_path) as para_file:
                file_contents = [line.replace('\r\n', '').replace('\n', '') for line in para_file.readlines()]  # remember the repalce symble is '\r\n'. otherwise, it fails to recoganize the parameter file names

            param_files_dict = {
                'control_file': {'file_path': file_path,
                                 'file_contents': file_contents
                                 }
            }

            # get the other model parameter files path and contents
            file_types = ['param_file', 'site_file', 'input_file', 'output_file']
            missing_file_names = []

            for index in range(0, len(file_types)):
                content_index = index + 1
                file_name = param_files_dict['control_file']['file_contents'][content_index]
                file_path = os.path.join(model_input_folder, file_name)

                if file_name in os.listdir(model_input_folder):
                    param_files_dict[file_types[index]] = {'file_path': file_path}

                    with open(file_path) as para_file:
                        file_contents = [line.replace('\r\n', '').replace('\n', '') for line in para_file.readlines()]

                    param_files_dict[file_types[index]]['file_contents'] = file_contents
                else:
                    missing_file_names.append(file_name)

            if missing_file_names:
                validation = {
                    'is_valid': False,
                    'result': 'Please provide the missing model parameter files: {}.'.format(','.join(missing_file_names))
                }
            else:
                validation = {
                    'is_valid': True,
                    'result': param_files_dict
                }
        else:
            validation = {
                'is_valid': False,
                'result': 'Please provide the missing model parameter file: control.dat.'
            }

    except Exception as e:
        validation = {
            'is_valid': False,
            'result': 'Failed to validate the model parameter files. ' + e.message
        }

    return validation


def validate_data_files(model_input_folder, model_param_files_dict):
    missing_file_names = []

    try:
        # check the control.dat watershed.nc
        watershed_name = model_param_files_dict['control_file']['file_contents'][6]
        if watershed_name not in os.listdir(model_input_folder):
            missing_file_names.append(watershed_name)

        # check the missing files in siteinitial.dat
        site_file_names = []

        for var_name in site_initial_variable_codes:
            for index, content in enumerate(model_param_files_dict['site_file']['file_contents']):
                if var_name in content and model_param_files_dict['site_file']['file_contents'][index+1][0] == '1':
                    site_file_names.append(model_param_files_dict['site_file']['file_contents'][index+2].split(' ')[0])
                    break

        if site_file_names:
            for name in site_file_names:
                if name not in os.listdir(model_input_folder):
                    missing_file_names.append(name)

        # check the missing files in inputcontrol.dat
        input_file_names = []
        for var_name in input_vairable_codes:
            for index, content in enumerate(model_param_files_dict['input_file']['file_contents']):
                if var_name in content:
                    if model_param_files_dict['input_file']['file_contents'][index+1][0] == '1':
                        input_file_names.append(model_param_files_dict['input_file']['file_contents'][index+2].split(' ')[0]+'0.nc')
                    elif model_param_files_dict['input_file']['file_contents'][index+1][0] == '0':
                        input_file_names.append(model_param_files_dict['input_file']['file_contents'][index + 2].split(' ')[0])
                    break

        if input_file_names:
            for name in input_file_names:
                if name not in os.listdir(model_input_folder):
                    missing_file_names.append(name)

        if missing_file_names:
            validation = {
                'is_valid': False,
                'result': 'Please provide the missing model input data files: {}'.format(',\n'.join(missing_file_names))
            }
        else:
            validation = {
                'is_valid': True,
                'result': [os.path.join(model_input_folder, name) for name in os.listdir(model_input_folder)]
            }

    except Exception as e:

        validation = {
            'is_valid': False,
            'result':  'Failed to validate the model input data files.' + e.message
        }

    return validation