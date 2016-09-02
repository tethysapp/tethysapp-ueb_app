var allRectangles = [];
var allMarkers = [];
var map; // global variable
var drawingManager;

$(document).ready(function() {

    // Hide the metadata section and model run btn when user changes the selection
    $('#resource_list').change(function(){
        $('#submit-model-run-btn').hide();
        $('#load-metadata-response').hide();
        $('#load-metadata-fail').hide();
    })

    // ajax call function to submit the form for metadat loading or
    var user_form= $('#user-form');

    user_form.submit(function(){
        var btn_val = $(this).find("input[type=submit]:focus" ).val();

        if (btn_val == 'Load Resource Metadata') {
            $('#wait').modal();

            $(this).attr('action','model_run_load_metadata/');

            $.ajax({
                type: user_form.attr('method'),
                url: user_form.attr('action'),
                data: user_form.serialize(),

                success: function(result) {
                    console.log(result);
                    json_response = JSON.parse(result);
                    console.log(json_response);
                    alert('happy');

                    if (json_response.status == 'Success'){
                        // show metadata elements info
                        $('#res-id').text(json_response.result.res_id);
                        $('#north-lat').text(json_response.result.north_lat);
                        $('#south-lat').text(json_response.result.south_lat);
                        $('#east-lon').text(json_response.result.east_lon);
                        $('#west-lon').text(json_response.result.west_lon);
                        $('#outlet-x').text(json_response.result.outlet_x);
                        $('#outlet-y').text(json_response.result.outlet_y);
                        $('#start-time').text(json_response.result.start_time);
                        $('#end-time').text(json_response.result.end_time);
                        $('#cell-x-size').text(json_response.result.cell_x_size);
                        $('#cell-y-size').text(json_response.result.cell_y_size);
                        $('#epsg-code').text(json_response.result.epsg_code);


                        document.getElementById('load-metadata-response').style.display = 'block';
                        document.getElementById('submit-model-run-btn').style.display = 'block';

                        // draw marker on map
                        if (json_response.result.outlet_x != 'unknown' && json_response.result.outlet_y != 'unknown'){
                            var myLatLng = {lat: parseFloat(json_response.result.outlet_y),
                                            lng: parseFloat(json_response.result.outlet_x)};
                            drawMarkerOnTextChange(myLatLng);
                        }

                        // draw rectangle on map
                        if (json_response.result.north_lat != 'unknown' && json_response.result.south_lat != 'unknown' &&
                        json_response.result.east_lon != 'unknown' && json_response.result.west_lon != 'unknown'){
                            var bounds = {
                                    north: parseFloat(json_response.result.north_lat),
                                    south: parseFloat(json_response.result.south_lat ),
                                    east: parseFloat(json_response.result.east_lon),
                                    west: parseFloat(json_response.result.west_lon)
                                };
                            drawRectangleOnTextChange(bounds);
                        }

                    }
                    else {
                        $('#load-metadata-error').text(json_response.result);
                        $('#load-metadata-fail').show();
                    }

                },

                error: function() {
                    alert('sad');
                },

                complete: function(){
                    alert('complete');
                    $('#wait').modal('hide');
                }
            });
            return false;

        }
        else {
        // run service
        }

    });

});

function initMap() {
var mapDiv = document.getElementById('map');
map = new google.maps.Map(mapDiv, {
    center: {lat: 37.09024, lng: -95.712891},
    zoom: 4,
});

map.setMapTypeId('terrain');

} // end of initmap function


function drawMarkerOnTextChange(myLatLng){

    // Delete previous drawings
    for (var i = 0; i < allMarkers.length; i++) {
            allMarkers[i].setMap(null);
     };

    // Bounds validation
    var badInput = false;

    if (myLatLng.lat > 90 || myLatLng.lat < -90) {
        $("#outlet_y").val('');
        badInput = true;
    }

    if (myLatLng.lng > 180 || myLatLng.lng < -180) {
        $("#outlet_x").val('');
        badInput = true;
    }

    if (badInput || isNaN(myLatLng.lat) || isNaN(myLatLng.lng)) {
        return;
    }

    // Define the marker
    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map
    });
    map.setCenter(marker.getPosition());

    allMarkers.push(marker);

} // end of drawMarkerOnTextChange


function drawRectangleOnTextChange(bounds){
    // Delete previous drawings
    for (var i = 0; i < allRectangles.length; i++) {
            allRectangles[i].setMap(null);
     };

    // Bounds validation
    var badInput = false;

    // North
    if (bounds.north > 90 || bounds.north < -90) {
        badInput = true;
    }

    // East
    if (bounds.east > 180 || bounds.east < -180) {
        badInput = true;
    }

    // South
    if (bounds.south < -90 || bounds.south > 90) {
        badInput = true;
    }

    // West
    if (bounds.west < -180 || bounds.west > 180) {
        badInput = true;
    }

    if (badInput || isNaN(bounds.north) || isNaN(bounds.south) || isNaN(bounds.east) || isNaN(bounds.west)) {
        return;
    }

    // Define the rectangle and set its editable property to true.
    var rectangle = new google.maps.Rectangle({
        bounds: bounds,
        editable: false,
        draggable: false,
    });
    rectangle.setMap(map);

    var southWest = new google.maps.LatLng(bounds.south,bounds.west);
    var northEast = new google.maps.LatLng(bounds.north,bounds.east);
    var bounds = new google.maps.LatLngBounds(southWest,northEast);
    map.fitBounds(bounds);

    allRectangles.push(rectangle);
}


