chrome.alarms.create("post_urls", {periodInMinutes: 10});


function getLastTS(userId, callback) {
    var xhr = new XMLHttpRequest();
    var url = "http://depressionweakerthan.tech:8000/last_ts/";
    xhr.open("POST", url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            callback(json);
        }
    };

    var data = JSON.stringify({"user": userId});
    xhr.send(data);
}


function getUserIdFromEntries(entries) {
    for (var i = 0; i < entries.length; ++i) {
        var url = entries[i].url;
        var pattern = "depressionweakerthan.tech/api/extension/"
        var index = url.search(pattern);
        if (index != -1) {
            return url.substr(index + pattern.length, url.length - (index + pattern.length));
        }
    }
}


function sendEntries(userId, entries) {
    var xhr = new XMLHttpRequest();
    var url = "http://depressionweakerthan.tech:8000/visit/";
    xhr.open("POST", url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    var data = JSON.stringify({"user": userId, "entries": entries});
    xhr.send(data);
}


function getEntries(startTimestamp, callback) {
    chrome.history.search({
        'text': '',  // Return every history item
        'startTime': startTimestamp,
        'maxResults': 10000
    },
        function(historyItems) {
            entries = [];
            url_counter = 0;
            ent_counter = 0;
            in_get_visits_counter = 0;
            for (var i = 0; i < historyItems.length; ++i) {
                var url = historyItems[i].url;
                entries.push({
                    "url": url,
                    "ts": historyItems[i].lastVisitTime
                })
                url_counter += 1;
                chrome.history.getVisits({"url": url}, function(visitItems) {
                    in_get_visits_counter += 1;
                    for (var j = 0; j < visitItems.length; ++j) {
                        ent_counter += 1;
                    }
                });
            }
            callback(entries);
        }
    );
}


function process() {
    getEntries(0, function(entries) {
        var userId = getUserIdFromEntries(entries)
        getLastTS(userId, function(json) {
            getEntries(json.ts, function(new_entries) {
                sendEntries(userId, new_entries);
            });
        })
    });
}


chrome.alarms.onAlarm.addListener(function (alarm) {
    if (alarm.name == "post_urls") {
        process();
    }
});


chrome.runtime.onInstalled.addListener(function() {
    process();
});
