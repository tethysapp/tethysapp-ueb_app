"""
utility functions for model run service
"""

import shutil
import os
import zipfile
import tempfile

from hs_restclient import HydroShare, HydroShareAuthBasic
from hydrogate import HydroDS


def submit_model_run_job(res_id, hs_name, hs_password, hydrods_name, hydrods_password):
    try:
        # authentication
        auth = HydroShareAuthBasic(hs_name, hs_password)
        hs = HydroShare(auth=auth)
        client = HydroDS(username=hydrods_name, password=hydrods_password)

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

                # TODO: call model run service

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

        # check model parameter files:
        model_files_path_list = [os.path.join(model_input_folder, name) for name in os.listdir(model_input_folder)]

        if 'control.dat' in os.listdir(model_input_folder):
            # # get the other parameter file path and contents
            # model_param_list = {
            #     'control_file': {'file_path': os.path.join(model_input_folder, 'control.dat')}
            #
            # }
            # with open(os.path.join(model_input_folder, 'control.dat')) as para_file:
            #     para_file_contents = [line.replace('\n', '') for line in para_file.readlines()]
            #
            #     para_file_types = ['control_file', 'param_file', 'site_file', 'input_file', 'output_file']
            #     model_param_list['param_file'] = os.path.join(model_input_folder, 'control.dat')
            #     file_contents_dict[file_name] = [line.replace('\n', '') for line in para_file.readlines()]
            #
            #
            #
            validation = {
                'is_valid': True,
                'result': model_files_path_list
            }

        else:
            validation = {
                'is_valid': False,
                'result': 'Please provide the model simulation control file: control.dat.'
            }


    except Exception as e:

        validation = {
            'is_valid': False,
            'result': 'Failed to validate the model input files. ' + e.message
        }

    return validation