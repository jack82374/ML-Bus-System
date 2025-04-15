var markers = [];
var dynamic_markers = [];
var map = new maplibregl.Map({
    container: 'map', // container id
    //style: 'https://demotiles.maplibre.org/style.json', // style URL
    //style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    //style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
    style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
    //style: 'https://raw.githubusercontent.com/go2garret/maps/main/src/assets/json/openStreetMap.json',
    center: [-8.4710, 51.8991], // starting position [lng, lat]
    zoom: 14 // starting zoom
});
function fetchStops() {
    fetch('/website/stops/')
        .then(response => response.json())
        .then(data => {
            const stop_img = new Image(20, 20);
            // Set the desired size
            stop_img.src = "/static/images/bus_stop_black.svg";
            stop_img.alt = "Bus Stop Icon";
            markers = data.map(stop => {
                const markerElement = document.createElement('div');
                markerElement.appendChild(stop_img.cloneNode(true));
                markerElement.className = 'stop_marker';
                markerElement.dataset.stopName = stop.stop_name;

                const marker = new maplibregl.Marker({
                    element: markerElement
                })
                    .setLngLat([stop.stop_lon, stop.stop_lat])
                    .setPopup(new maplibregl.Popup().setHTML(`<a href="stop_example/${stop.stop_id}">${stop.stop_name}</a>`))
                    .addTo(map);
                return { marker, markerElement };
            });
            //updateVisibleMarkers();
        });
}

const call_locations = setInterval(fetchLocations, 30000);

function fetchLocations() {
    dynamic_markers.forEach(markerEntry => {
        markerEntry.marker.remove();
    });
    //var dynamic_markers = [];
    fetch('/website/locations/')
        .then(response => response.json())
        .then(data => {
            const five_bus_img = new Image(20, 20);
            five_bus_img.src = "/static/images/bus_red.svg";
            five_bus_img.alt = "205 Red Moving Bus Icon";

            const five_bus_img_light = new Image(20, 20);
            five_bus_img_light.src = "/static/images/bus_light_red.svg";
            five_bus_img_light.alt = "205 Light Red Moving Bus Icon";

            const eight_bus_img = new Image(20, 20);
            eight_bus_img.src = "/static/images/bus_blue.svg";
            eight_bus_img.alt = "208 Blue Moving Bus Icon";

            const eight_bus_img_light = new Image(20, 20);
            eight_bus_img_light.src = "/static/images/bus_light_blue.svg";
            eight_bus_img_light.alt = "208 Light Blue Moving Bus Icon";

            dynamic_markers = data.map(position => {
                const markerElement = document.createElement('div');
                if (position.direction_id == 0) {
                    var orientation = "west"
                }
                else {
                    var orientation = "east"
                }
                const vehicle_string = position.vehicle_id.toString();
                if (position.route_id == '93327') {
                    const location_string = vehicle_string.concat(" on route ", "205 going ", orientation);
                    if (position.direction_id == 1) {
                        markerElement.appendChild(five_bus_img_light.cloneNode(true));
                    }
                    else {
                        markerElement.appendChild(five_bus_img.cloneNode(true));
                    }
                    markerElement.className = 'bus_marker';
                    markerElement.dataset.trip = position.trip_id;

                    const marker = new maplibregl.Marker({
                        element: markerElement
                    })
                        .setLngLat([position.longitude, position.latitude])
                        .setPopup(new maplibregl.Popup().setText(location_string))
                        .addTo(map);
                    return { marker, markerElement };
                }
                else if (position.route_id == '93330') {
                    const location_string = vehicle_string.concat(" on route ", "208 going ", orientation);
                    if (position.direction_id == 1) {
                        markerElement.appendChild(eight_bus_img_light.cloneNode(true));
                    }
                    else {
                        markerElement.appendChild(eight_bus_img.cloneNode(true));
                    }
                    markerElement.className = 'bus_marker';
                    markerElement.dataset.trip = position.trip_id;

                    const marker = new maplibregl.Marker({
                        element: markerElement
                    })
                        .setLngLat([position.longitude, position.latitude])
                        .setPopup(new maplibregl.Popup().setText(location_string))
                        .addTo(map);
                    return { marker, markerElement };
                }
            });
            //updateVisibleMarkers();
        });
    //markers = markers.concat(dynamic_markers)
}

/*function updateVisibleMarkers() {
  const currentZoom = map.getZoom();
  const bounds = map.getBounds();
  markers.forEach(({ marker, markerElement }) => {
      if (currentZoom < 10 && markerElement.className == 'bus_marker') {
        markerElement.classList.add('hidden'); // Hide the markers
      }
      else if (currentZoom < 7 && markerElement.className == 'stop_marker') {
        markerElement.classList.add('hidden'); // Hide the markers
      }
      //else {
      //  markerElement.classList.remove('hidden'); // Show the marker
      //}
      const lngLat = marker.getLngLat();
      if (bounds.contains(lngLat) && currentZoom > 7 && markerElement.className == 'stop_marker') {
          markerElement.classList.remove('hidden');
      }
      else if (bounds.contains(lngLat) && currentZoom > 10 && markerElement.className == 'bus_marker') {
        markerElement.classList.remove('hidden');
      }
      //else {
      //    markerElement.classList.add('hidden');
      //}
  });
}*/

function fetchShapes() {
    fetch('/website/shapes/')
        .then(response => response.json())
        .then(shapesData => {
            for (const key in shapesData) {
                const geojson = {
                    type: 'FeatureCollection',
                    features: [
                        {
                            type: 'Feature',
                            geometry: {
                                type: 'LineString',
                                coordinates: shapesData[key]['coordinates'].map(point => [point.lon, point.lat])
                            },
                            properties: {
                                shape_id: shapesData[key].shape_id,
                                route_id: shapesData[key].route_id
                            }
                        }
                    ]
                };
                const id_string = "bus-routes-layer-key ".concat(key.toString())
                const source_string = "bus-routes ".concat(key.toString())
                // I'm not sure why the above have to be here to be honest

                var colour;
                switch (shapesData[key].route_id) {
                    case '93327':
                        colour = '#FF5D5D';
                        break;
                    case '93330':
                        colour = '#5DC7FF';
                        break;
                    default:
                        colour = 'grey';
                }

                //map.on('load', () => {
                //if (!map.getSource('bus-routes')) {
                map.addSource(source_string, {
                    type: 'geojson',
                    data: geojson
                });

                map.addLayer({
                    id: id_string,
                    type: 'line',
                    source: source_string,
                    layout: {
                        'line-join': 'round',
                        'line-cap': 'round'
                    },
                    paint: {
                        'line-color': colour,
                        'line-width': 3
                    }
                });
                //}
            }
            //});
        });
}

fetchStops();
fetchLocations();
fetchShapes();



//map.on('move', updateVisibleMarkers);
//map.on('zoom', updateVisibleMarkers);