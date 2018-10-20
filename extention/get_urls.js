console.log(chrome);


chrome.alarms.create("post_urls", {periodInMinutes: 1});


function getLastTS() {
    var xhr = new XMLHttpRequest();
    var url = "ec2-34-220-99-208.us-west-2.compute.amazonaws.com:8000"
    xhr.open("POST", url, true);
    var data = JSON.stringify({"user": "nzinov"});
    xhr.send(data);
    xhr.onreadystatechange = function() { 
      if (req.readyState == 4)
        if (xhr.readyState == 4) {
              if (xhr.status == 200) {
                var jsonData = xhr.responseText; 
                alert("POST ANSWER: " + jsonData);
            }
        }
    };

    var microsecondsPerWeek = 1000 * 60 * 60 * 24 * 7;
    return (new Date).getTime() - microsecondsPerWeek;
}


function postUrls(startTimestamp) {
    chrome.history.search({
        'text': '',  // Return every history item
        'startTime': startTimestamp
    },
        function(historyItems) {
            var counter = 0;
            for (var i = 0; i < historyItems.length; ++i) {
                var url = historyItems[i].url;
                counter += 1;
            }
            alert("Items in history: " + counter);
        }
    );
}

chrome.alarms.onAlarm.addListener(function (alarm) {
    if (alarm.name == "post_urls") {
        lastTS = getLastTS();
        postUrls(lastTS);
    }
});
