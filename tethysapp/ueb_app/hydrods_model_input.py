from hydrogate import HydroDS
from datetime import datetime


# TODO make the streamthreshold and watershedname as user inputs!!!
def hydrods_model_input_service(hs_name, hs_password, hydrods_name, hydrods_password, topY, bottomY, leftX, rightX, lat_outlet, lon_outlet,
                                epsgCode, startDateTime, endDateTime, dx, dy, dxRes, dyRes, res_title, res_keywords,
                                streamThreshold=1000, watershedName='my_watershed_', **kwargs):
    service_response = {
        'status': 'Success',
        'result': 'The model input has been shared in HydroShare'
    }

    # Authentication
    try:
        HDS = HydroDS(username=hydrods_name, password=hydrods_password)
        for item in HDS.list_my_files():
            HDS.delete_my_file(item.split('/')[-1])
    except:
        service_response['status'] = 'Error'
        service_response['result'] = 'Please provide the correct user name and password to use HydroDS web services.'
        return service_response

    # TODO: create new folder for new job


    # prepare watershed DEM data
    try:
        input_static_DEM  = 'nedWesternUS.tif'
        subsetDEM_request = HDS.subset_raster(input_raster=input_static_DEM, left=leftX, top=topY, right=rightX,
                                          bottom=bottomY,output_raster=watershedName + 'DEM84.tif')

        #Options for projection with epsg full list at: http://spatialreference.org/ref/epsg/
        myWatershedDEM = watershedName + 'Proj' + str(dx) + '.tif'
        WatershedDEM = HDS.project_resample_raster(input_raster_url_path=subsetDEM_request['output_raster'],
                                                          cell_size_dx=dx, cell_size_dy=dy, epsg_code=epsgCode,
                                                          output_raster=myWatershedDEM,resample='bilinear')

        outlet_shapefile_result = HDS.create_outlet_shapefile(point_x=lon_outlet, point_y=lat_outlet,
                                                          output_shape_file_name=watershedName+'Outlet.shp')
        project_shapefile_result = HDS.project_shapefile(outlet_shapefile_result['output_shape_file_name'], watershedName + 'OutletProj.shp',
                                                     epsg_code=epsgCode)

        Watershed_hires = HDS.delineate_watershed(WatershedDEM['output_raster'],
                        input_outlet_shapefile_url_path=project_shapefile_result['output_shape_file'],
                        threshold=streamThreshold, epsg_code=epsgCode,
                        output_raster=watershedName + str(dx) + 'WS.tif',
                        output_outlet_shapefile=watershedName + 'movOutlet.shp')

        #HDS.download_file(file_url_path=Watershed_hires['output_raster'], save_as=workingDir+watershedName+str(dx)+'.tif')

        ####Resample watershed grid to coarser grid
        Watershed =  HDS.resample_raster(input_raster_url_path= Watershed_hires['output_raster'],
                    cell_size_dx=dxRes, cell_size_dy=dyRes, resample='near', output_raster=watershedName + str(dxRes) + 'WS.tif')

        #HDS.download_file(file_url_path=Watershed['output_raster'], save_as=workingDir+watershedName+str(dxRes)+'.tif')

        ##  Convert to netCDF for UEB input
        Watershed_temp = HDS.raster_to_netcdf(Watershed['output_raster'], output_netcdf='watershed'+str(dxRes)+'.nc')

        # In the netCDF file rename the generic variable "Band1" to "watershed"
        Watershed_NC = HDS.netcdf_rename_variable(input_netcdf_url_path=Watershed_temp['output_netcdf'],
                                    output_netcdf='watershed.nc', input_variable_name='Band1', output_variable_name='watershed')
    except Exception as e:
        service_response['status'] = 'Error'
        service_response['result'] = 'Failed to prepare the watershed DEM data.'+ e.message
        # TODO clean up the space
        return service_response

    service_response['result'] = ','.join(HDS.list_my_files())

    # # prepare the terrain variables
    # try:
    #     # aspect
    #     aspect_hires = HDS.create_raster_aspect(input_raster_url_path=WatershedDEM['output_raster'],
    #                                 output_raster=watershedName + 'Aspect' + str(dx)+ '.tif')
    #     aspect = HDS.resample_raster(input_raster_url_path= aspect_hires['output_raster'], cell_size_dx=dxRes,
    #                                 cell_size_dy=dyRes, resample='near', output_raster=watershedName + 'Aspect' + str(dxRes) + '.tif')
    #     aspect_temp = HDS.raster_to_netcdf(input_raster_url_path=aspect['output_raster'],output_netcdf='aspect'+str(dxRes)+'.nc')
    #     aspect_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=aspect_temp['output_netcdf'],
    #                                 output_netcdf='aspect.nc', input_variable_name='Band1', output_variable_name='aspect')
    #     # slope
    #     slope_hires = HDS.create_raster_slope(input_raster_url_path=WatershedDEM['output_raster'],
    #                                 output_raster=watershedName + 'Slope' + str(dx) + '.tif')
    #     slope = HDS.resample_raster(input_raster_url_path= slope_hires['output_raster'], cell_size_dx=dxRes,
    #                                 cell_size_dy=dyRes, resample='near', output_raster=watershedName + 'Slope' + str(dxRes) + '.tif')
    #     slope_temp = HDS.raster_to_netcdf(input_raster_url_path=slope['output_raster'], output_netcdf='slope'+str(dxRes)+'.nc')
    #     slope_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=slope_temp['output_netcdf'],
    #                                 output_netcdf='slope.nc', input_variable_name='Band1', output_variable_name='slope')
    #
    #     #Land cover variables
    #     nlcd_raster_resource = 'nlcd2011CONUS.tif'
    #     subset_NLCD_result = HDS.project_clip_raster(input_raster=nlcd_raster_resource,
    #                                 ref_raster_url_path=Watershed['output_raster'],
    #                                 output_raster=watershedName + 'nlcdProj' + str(dxRes) + '.tif')
    #     #cc
    #     nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
    #                                 variable_name='cc', output_netcdf=watershedName+str(dxRes)+'cc.nc')
    #     cc_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
    #                                 output_netcdf='cc.nc', input_variable_name='Band1', output_variable_name='cc')
    #     #hcan
    #     nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
    #                                 variable_name='hcan', output_netcdf=watershedName+str(dxRes)+'hcan.nc')
    #     hcan_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
    #                                 output_netcdf='hcan.nc', input_variable_name='Band1',output_variable_name='hcan')
    #     #lai
    #     nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
    #                                 variable_name='lai', output_netcdf=watershedName+str(dxRes)+'lai.nc')
    #     lai_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
    #                                 output_netcdf='lai.nc', input_variable_name='Band1',output_variable_name='lai')
    #
    # except Exception as e:
    #     service_response['status'] = 'Error'
    #     service_response['result'] = 'Failed to prepare the terrain variables.' + e.message
    #     # TODO clean up the space
    #     return service_response
    #
    #
    # # prepare the climate variables
    # try:
    #     startYear = datetime.strptime(startDateTime,"%Y/%m/%d").year
    #     endYear = datetime.strptime(endDateTime,"%Y/%m/%d").year
    #     #### we are using data from Daymet; so data are daily
    #     startDate = datetime.strptime(startDateTime, "%Y/%m/%d").date().strftime('%m/%d/%Y')
    #     endDate = datetime.strptime(endDateTime, "%Y/%m/%d").date().strftime('%m/%d/%Y')
    #
    #     climate_Vars = ['vp', 'tmin', 'tmax', 'srad', 'prcp']
    #     ####iterate through climate variables
    #     for var in climate_Vars:
    #         for year in range(startYear, endYear + 1):
    #             climatestaticFile1 = var + "_" + str(year) + ".nc4"
    #             climateFile1 = watershedName + '_' + var + "_" + str(year) + ".nc"
    #             Year1sub_request = HDS.subset_netcdf(input_netcdf=climatestaticFile1,
    #                                                  ref_raster_url_path=Watershed['output_raster'],
    #                                                  output_netcdf=climateFile1)
    #             concatFile = "conc_" + climateFile1
    #             if year == startYear:
    #                 concatFile1_url = Year1sub_request['output_netcdf']
    #             else:
    #                 concatFile2_url = Year1sub_request['output_netcdf']
    #                 concateNC_request = HDS.concatenate_netcdf(input_netcdf1_url_path=concatFile1_url,
    #                                                            input_netcdf2_url_path=concatFile2_url,
    #                                                            output_netcdf=concatFile)
    #                 concatFile1_url = concateNC_request['output_netcdf']
    #
    #         timesubFile = "tSub_" + climateFile1
    #         subset_NC_by_time_result = HDS.subset_netcdf_by_time(input_netcdf_url_path=concatFile1_url,
    #                                                              time_dimension_name='time', start_date=startDate,
    #                                                              end_date=endDate, output_netcdf=timesubFile)
    #         subset_NC_by_time_file_url = subset_NC_by_time_result['output_netcdf']
    #         if var == 'prcp':
    #             proj_resample_file = var + "_0.nc"
    #         else:
    #             proj_resample_file = var + "0.nc"
    #         ncProj_resample_result = HDS.project_subset_resample_netcdf(
    #             input_netcdf_url_path=subset_NC_by_time_file_url,
    #             ref_netcdf_url_path=Watershed_NC['output_netcdf'],
    #             variable_name=var, output_netcdf=proj_resample_file)
    #         ncProj_resample_file_url = ncProj_resample_result['output_netcdf']
    #
    #         #### Do unit conversion for precipitation (mm/day --> m/hr)
    #         if var == 'prcp':
    #             proj_resample_file = var + "0.nc"
    #             ncProj_resample_result = HDS.convert_netcdf_units(input_netcdf_url_path=ncProj_resample_file_url,
    #                                                             output_netcdf=proj_resample_file,
    #                                                             variable_name=var, variable_new_units='m/hr',
    #                                                             multiplier_factor=0.00004167, offset=0.0)
    #             # ncProj_resample_file_url = ncProj_resample_result['output_netcdf']
    #
    # except Exception as e:
    #     service_response['status'] = 'Error'
    #     service_response['result'] = 'Failed to prepare the climate variables.' + e.message
    #     # TODO clean up the space
    #     return service_response
    #
    #
    # # share result to HydroShare
    # try:
    #     #upload ueb input package to hydroshare
    #     ueb_inputPackage_dict = ['control.dat','inputcontrol.dat','outputcontrol.dat','param.dat','siteinitial.dat','V.dat',
    #                          'watershed.nc', 'aspect.nc', 'slope.nc', 'cc.nc', 'hcan.nc', 'lai.nc',
    #                          'vp0.nc', 'srad0.nc', 'tmin0.nc', 'tmax0.nc', 'prcp0.nc']
    #     zip_files_result = HDS.zip_files(files_to_zip=ueb_inputPackage_dict, zip_file_name=watershedName+str(dxRes)+'.zip')
    #
    #     #save UEB input package as HydroShare resource
    #     hs_title = res_title
    #     hs_abstract = 'It was created using HydroShare UEB model application which utilized the HydroDS modeling services.'
    #     hs_keywords=res_keywords.split(',')
    #     HDS.set_hydroshare_account(hs_name, hs_password)
    #     HDS.create_hydroshare_resource(file_name=watershedName+str(dxRes)+'.zip', resource_type ='GenericResource', title= hs_title,
    #                                abstract= hs_abstract, keywords= hs_keywords)
    # except Exception as e:
    #     service_response['status'] = 'Error'
    #     service_response['result'] = 'Failed to prepare the climate variables.' + e.message
    #     # TODO clean up the space
    #     return service_response

    return service_response
