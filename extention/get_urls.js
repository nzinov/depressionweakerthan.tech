chrome.alarms.create("post_urls", {periodInMinutes: 1});


function getLastTS() {
    var xhr = new XMLHttpRequest();
    var url = "http://ec2-34-220-99-208.us-west-2.compute.amazonaws.com:8000/last_ts/"
    xhr.open("POST", url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            alert("LAST TS: " + json.ts);
            return json.ts
        }
    };

    var data = JSON.stringify({"user": "nzinov"});
    xhr.send(data);
}


function sendEntries(entries) {
    var xhr = new XMLHttpRequest();
    var url = "http://ec2-34-220-99-208.us-west-2.compute.amazonaws.com:8000/last_ts/"
    xhr.open("POST", url, true);

    xhr.setRequestHeader("Content-Type", "application/json");

    var data = JSON.stringify({"user": "nzinov", "entries": entries});
    xhr.send(data);
}


function postURLs(startTimestamp) {
    chrome.history.search({
        'text': '',  // Return every history item
        'startTime': startTimestamp
    },
        function(historyItems) {
            alert("will collect entries")
            entries = [];
            url_counter = 0;
            ent_counter = 0;
            for (var i = 0; i < historyItems.length; ++i) {
                var url = historyItems[i].url;
                entries.push({
                    "url": url,
                    "ts": historyItems[i].lastVisitTime
                })
                url_counter += 1;
                chrome.history.getVisits({"url": url}, function(visitItems) {
                    for (var j = 0; j < visitItems.length; ++j) {
                        ent_counter += 1;
                    }
                });
            }
            sendEntries(entries);
            alert("entries len:" + entries.length)
            alert("urls counter:" + url_counter)
            alert("entr counter:" + ent_counter)
        }
    );
}


chrome.alarms.onAlarm.addListener(function (alarm) {
    if (alarm.name == "post_urls") {
        lastTS = getLastTS();
        postURLs(lastTS);
    }
});
