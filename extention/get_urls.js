chrome.alarms.create("post_urls", {periodInMinutes: 1});


function getLastTS(callback) {
    var xhr = new XMLHttpRequest();
    var url = "http://depressionweakerthan.tech/api/last_ts/";
    xhr.open("POST", url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
			callback(json.ts);
        }
    };

    var data = JSON.stringify({"user": "nzinov"});
    xhr.send(data);
}


function sendEntries(entries) {
    var xhr = new XMLHttpRequest();
    var url = "http://depressionweakerthan.tech/api/visit/";
    xhr.open("POST", url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    var data = JSON.stringify({"user": "nzinov", "entries": entries});
    xhr.send(data);
}


function postURLs(startTimestamp) {
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
                console.log("url:" + url)
                chrome.history.getVisits({"url": url}, function(visitItems) {
                    in_get_visits_counter += 1;
                    for (var j = 0; j < visitItems.length; ++j) {
                        ent_counter += 1;
                    }
                });
            }
            sendEntries(entries);
        }
    );
}


function process() {
	getLastTS(postURLs);
} 


chrome.alarms.onAlarm.addListener(function (alarm) {
    if (alarm.name == "post_urls") {
		process();
    }
});
