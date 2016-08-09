var allRectangles = [];
var allMarkers = [];
var map; // global variable
var drawingManager;

$(document).ready(function() {
    // Draw marker on text change
    $("#outlet_x").bind('input', drawMarkerOnTextChange);
    $("#outlet_y").bind('input', drawMarkerOnTextChange);

    // Draw rectangle on text change
    $("#north_lat").bind('input', drawRectangleOnTextChange);
    $("#south_lat").bind('input', drawRectangleOnTextChange);
    $("#east_lon").bind('input', drawRectangleOnTextChange);
    $("#west_lon").bind('input', drawRectangleOnTextChange);


    // ajax call function to submit the form
    var user_form= $('#user-form');

    user_form.submit(function(){
        alert($('#user-form').length);
        $.ajax({
            type: user_form.attr('method'),
            url: user_form.attr('action'),
            data: user_form.serialize(),

            success: function(result) {
                console.log(result);
                json_response = JSON.parse(result);
                console.log(json_response);
                alert('happy');
                alert(json_response.status);
                alert(json_response.result.start_time);
                alert(json_response.result.end_time);
                alert(json_response.result.north_lat);
                alert(json_response.result.south_lat);
                alert(json_response.result.west_lon);
                alert(json_response.result.east_lon);
                alert(json_response.result.outlet_x);
                alert(json_response.result.outlet_y);
                alert(json_response.result.epsg_code);
                alert(json_response.result.x_size);
                alert(json_response.result.y_size);
                alert(json_response.result.dx_size);
                alert(json_response.result.dy_size);
                alert(json_response.result.res_title);
                alert(json_response.result.res_keywords);

            },
            error: function() {
                alert('sad');
            },
            complete: function(){
                alert('complete')
            }
        });
        return false;
    });

});

function initMap() {
var mapDiv = document.getElementById('map');
map = new google.maps.Map(mapDiv, {
    center: {lat: 37.09024, lng: -95.712891},
    zoom: 4
});

var drawingManager = new google.maps.drawing.DrawingManager({
    drawingControl: true,
    drawingControlOptions: {
      position: google.maps.ControlPosition.TOP_CENTER,
      drawingModes: [
        google.maps.drawing.OverlayType.MARKER,
        google.maps.drawing.OverlayType.RECTANGLE
      ]
     },
    rectangleOptions: {
        editable: true,
        draggable: true
    }
 });

 drawingManager.setMap(map);

 google.maps.event.addListener(drawingManager, 'rectanglecomplete', function (rectangle) {

    for (var i = 0; i < allRectangles.length; i++) {
            allRectangles[i].setMap(null);
     };
    allRectangles.push(rectangle);

    var coordinates = (rectangle.getBounds());
    processDrawing(coordinates, 'rectangle');
    rectangle.addListener('bounds_changed', function () {
        var coordinates = (rectangle.getBounds());
        processDrawing(coordinates, "rectangle");
    });

 });

 google.maps.event.addListener(drawingManager, 'markercomplete', function (marker) {

    for (var i = 0; i < allMarkers.length; i++) {
            allMarkers[i].setMap(null);
     };

    var coordinates = (marker.getPosition());
    processDrawing(coordinates, 'marker');
    allMarkers.push(marker);
 });

} // end of initmap function



function processDrawing (coordinates, shape) {
    if (shape == "rectangle"){
        // get coordinate value
        var bounds = {
            north: parseFloat(coordinates.getNorthEast().lat()),
            south: parseFloat(coordinates.getSouthWest().lat()),
            east: parseFloat(coordinates.getNorthEast().lng()),
            west: parseFloat(coordinates.getSouthWest().lng())
        };

        // update form fields
        $("#north_lat").val(bounds.north);
        $("#south_lat").val(bounds.south);
        $("#east_lon").val(bounds.east);
        $("#west_lon").val(bounds.west);
    }
    else {
        $("#outlet_x").val(coordinates.lng());
        $("#outlet_y").val(coordinates.lat());
    }
} // end of processingDrawing function


function drawMarkerOnTextChange(){
    var myLatLng = {lat: parseFloat($("#outlet_y").val()), lng: parseFloat($("#outlet_x").val())};

    // Delete previous drawings
    for (var i = 0; i < allMarkers.length; i++) {
            allMarkers[i].setMap(null);
     };

    // Bounds validation
    var badInput = false;

    if (myLatLng.lat > 90 || myLatLng.lat < -90) {
        alert('Latitude should between -90 and 90 degree');
        $("#outlet_y").val('');
        badInput = true;
    }

    if (myLatLng.lng > 180 || myLatLng.lng < -180) {
        alert('Longitude should between -180 and 180 degree');
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


function drawRectangleOnTextChange(){
    var bounds = {
        north: parseFloat($("#north_lat").val()),
        south: parseFloat($("#south_lat").val()),
        east: parseFloat($("#east_lon").val()),
        west: parseFloat($("#west_lon").val())
    };

    // Delete previous drawings
    for (var i = 0; i < allRectangles.length; i++) {
            allRectangles[i].setMap(null);
     };

    // Bounds validation
    var badInput = false;
    // North
    if (bounds.north > 90 || bounds.north < -90) {
        alert('Latitude should between -90 and 90 degree');
        badInput = true;
        $("#north_lat").val('');
    }

    // East
    if (bounds.east > 180 || bounds.east < -180) {
        alert('Longitude should between -180 and 180 degree');
        badInput = true;
        $("#east_lon").val('');
    }

    // South
    if (bounds.south < -90 || bounds.south > 90) {
        alert('Latitude should between -90 and 90 degree');
        badInput = true;
        $("#south_lat").val('');
    }

    // West
    if (bounds.west < -180 || bounds.west > 180) {
        alert('Longitude should between -180 and 180 degree');
        badInput = true;
        $("#west_lon").val('');

    }

    if (badInput || isNaN(bounds.north) || isNaN(bounds.south) || isNaN(bounds.east) || isNaN(bounds.west)) {
        return;
    }

    // Define the rectangle and set its editable property to true.
    var rectangle = new google.maps.Rectangle({
        bounds: bounds,
        editable: true,
        draggable: true
    });
    rectangle.setMap(map);

    rectangle.addListener('bounds_changed', function () {
        var coordinates = (rectangle.getBounds());
        processDrawing(coordinates, "rectangle");
    });

    var southWest = new google.maps.LatLng(bounds.south,bounds.west);
    var northEast = new google.maps.LatLng(bounds.north,bounds.east);
    var bounds = new google.maps.LatLngBounds(southWest,northEast);
    map.fitBounds(bounds);

    allRectangles.push(rectangle);
}


