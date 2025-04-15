//const stop_id = "{{ stop_id }}" 
const stop_url = `/website/stop_entries/${stop_id}/`;
console.log(stop_url);
const call_stopUpdates = setInterval(addRow, 30000);
function addRow() {
    var table = document.getElementById("timeTable");
    table.innerHTML = "";

    var headerRow = table.insertRow();

    var routeHeader = document.createElement("th");
    routeHeader.innerHTML = "Route";
    headerRow.appendChild(routeHeader);

    var scheduleHeader = document.createElement("th");
    scheduleHeader.innerHTML = "Status";
    headerRow.appendChild(scheduleHeader);

    var timeTabledHeader = document.createElement("th");
    timeTabledHeader.innerHTML = "Timetabled Arrival Time";
    headerRow.appendChild(timeTabledHeader);

    var mlHeader = document.createElement("th");
    mlHeader.innerHTML = "Predicted Arrival Time";
    headerRow.appendChild(mlHeader);

    var actualHeader = document.createElement("th");
    actualHeader.innerHTML = "Actual Arrival";
    headerRow.appendChild(actualHeader);


    fetch(stop_url)
        .then(response => response.json())
        .then(data => {
            const now = new Date();
            const hoursSinceMidnight = now.getHours();
            const minutesSinceMindnight = now.getMinutes();
            const secondsSinceMidnight = now.getSeconds();
            const totalSecondsSinceMidnight = hoursSinceMidnight * 3600 + minutesSinceMindnight * 60 + secondsSinceMidnight;
            
            const timeEntries = data['active_relevant_stoptimes_json']
            const stopUpdateEntries = data['stop_updates_json']
            const tripUpdateEntries = data['trip_updates_json']
            const delayEntries = data['delays_json']
            /*var timeEntriesJson = document.getElementById('data').textContent;
            var stopUpdatesJson = document.getElementById('stop_updates').textContent;
            var timeEntries = JSON.parse(timeEntriesJson);
            var stopUpdateEntries = JSON.parse(stopUpdatesJson);*/
            //console.log(timeEntries)
            //console.log(stopUpdateEntries)
            timeEntries.forEach(time_entry => {
                var delay_value = 0.0
                var ml_time = time_entry.arrival_time
                const delay = delayEntries.find(delay => delay.trip_id === time_entry.trip_id);
                if (delay) {
                    delay_value = delay.delay
                    ml_time += delay_value
                }
                var overallRelationship = 'ASSUMED SCHEDULED';
                const trip = tripUpdateEntries.find(trip => trip.trip_id === time_entry.trip_id);
                if (trip) {
                    //console.log("Trip found, changing relationship")
                    overallRelationship = trip.schedule_relationship;
                }
                var actualTime = "In the future!";
                if (totalSecondsSinceMidnight > time_entry.arrival_time) {
                    actualTime = 'Late'
                }
                else {
                    actualTime = 'On Time'
                }
                //console.log("NEW TIME ENTRY!");
                const update = stopUpdateEntries.find(update => update.trip_id === time_entry.trip_id);
                if (update) {
                    //console.log("Found an update!");
                    //console.log(update.arrival_delay);
                    //overallRelationship = update.schedule_relationship;
                    if (update.schedule_relationship == 'SCHEDULED') {
                        overallRelationship = "ARRIVED";
                        actualTime = time_entry.arrival_time + update.arrival_delay;
                        const delay_hours = Math.floor(actualTime / 3600);
                        const delay_minutes = Math.floor((actualTime % 3600) / 60);
                        const delay_remainingSeconds = actualTime % 60;

                        const delay_formattedHours = String(delay_hours).padStart(2, '0');
                        const delay_formattedMinutes = String(delay_minutes).padStart(2, '0');
                        const delay_formattedSeconds = String(delay_remainingSeconds).padStart(2, '0');
                        actualTime = `${delay_formattedHours}:${delay_formattedMinutes}:${delay_formattedSeconds}`;
                    }
                    else {
                        overallRelationship = update.schedule_relationship;
                        actualTime = "Skipped"
                    }
                } /*else {
                    console.log("No arrival time match, it hasn't arrived yet!");
                }*/
                //console.log(time_entry)
                var newRow = table.insertRow();
                var routeCell = newRow.insertCell();
                var relationshipCell = newRow.insertCell();
                var timeTabledCell = newRow.insertCell();
                var mlCell = newRow.insertCell();
                var actualCell = newRow.insertCell();

                if (time_entry.trip__route_id == 93327) {
                    routeCell.innerHTML = 205;
                }
                else if (time_entry.trip__route_id == 93330) {
                    routeCell.innerHTML = 208;
                }

                relationshipCell.innerHTML = overallRelationship

                const hours = Math.floor(time_entry.arrival_time / 3600);
                const minutes = Math.floor((time_entry.arrival_time % 3600) / 60);
                const remainingSeconds = time_entry.arrival_time % 60;

                const formattedHours = String(hours).padStart(2, '0');
                const formattedMinutes = String(minutes).padStart(2, '0');
                const formattedSeconds = String(remainingSeconds).padStart(2, '0');
                const timeToDisplay = `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;

                const mlhours = Math.floor(ml_time / 3600);
                const mlminutes = Math.floor((ml_time % 3600) / 60);
                const mlremainingSeconds = ml_time % 60;

                const mlformattedHours = String(mlhours).padStart(2, '0');
                const mlformattedMinutes = String(mlminutes).padStart(2, '0');
                const mlformattedSeconds = String(mlremainingSeconds).padStart(2, '0');
                const mltimeToDisplay = `${mlformattedHours}:${mlformattedMinutes}:${mlformattedSeconds}`;

                timeTabledCell.innerHTML = timeToDisplay;
                mlCell.innerHTML = mltimeToDisplay;
                actualCell.innerHTML = actualTime;
            });
            // Should add in something to sort the table by scheduled arrival time here.
        })
}
addRow();