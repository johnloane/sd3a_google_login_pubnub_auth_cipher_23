let aliveSecond = 0;
let heartbeatRate = 5000;

let myChannel = "johns-sd3a-pi-channel"

sendEvent('get_auth_key');

//Rewrite using the fetch api
function keepAlive()
{
	fetch('/keep_alive')
	.then(response=> {
		if(response.ok){
			let date = new Date();
			aliveSecond = date.getTime();
			return response.json();
		}
		throw new Error('Server offline');
	})
	.then(responseJson => console.log(responseJson))
	.catch(error => console.log(error));
	setTimeout('keepAlive()', heartbeatRate);
}

function time(){
	let d = new Date();
	let currentSec = d.getTime();
	if(currentSec - aliveSecond > heartbeatRate + 1000){
		document.getElementById("Connection_id").innerHTML = "DEAD";
	}
	else{
		document.getElementById("Connection_id").innerHTML = "ALIVE";
	}
	setTimeout('time()', 1000);
}

function grantAccess(ab)
{
    let userId = ab.id.split("-")[2];
    let readState = document.getElementById("read-user-"+userId).checked;
    let writeState = document.getElementById("write-user-"+userId).checked;
    console.log("grant-"+userId+"-"+readState+"-"+writeState);
    sendEvent("grant-"+userId+"-"+readState+"-"+writeState);
}

function sendEvent(value)
{
    fetch(value,
    {
        method:"POST",
    })
    .then(response => response.json())
    .then(responseJson => {
        if(responseJson.hasOwnProperty('auth_key'))
        {
            pubnub.setAuthKey(responseJson.auth_key);
            console.log(responseJson.auth_key);
            pubnub.setCipherKey(responseJson.cipher_key);
            console.log(responseJson.cipher_key);
            console.log("Auth key and cipher ket set " + responseJson);
            subscribe();
        }
    });
}

pubnub = new PubNub({
    publishKey: "Your Publish Key",
    subscribeKey: "Your Subscribe key",
    uuid: "client"
    })


pubnub.addListener({
    status: function(statusEvent){
        if(status.category == "PNConnectedCategory")
        {
            console.log("Successfully connected to PubNub");
            publishMessage(myChannel, "Hello everyone. Online");
        }
    },
    message : function(msg)
    {
        console.log(msg.message);
        document.getElementById("Motion_id").innerHTML = msg.message.motion;
    },
    presence: function(presenceEvent)
    {
    }
})

function publishMessage(channelToPublish, messageToPublish)
{
    console.log(message);

    var publishPayload = {
        channel : channelToPublish,
        message : messageToPublish
    }

    pubnub.publish(publishPayload, function(status, response)
    {
        console.log(status, response);
    })
}

pubnub.subscribe({channels: [myChannel]})

function subscribe()
{
    pubnub.subscribe({channels: [myChannel],},
    function(status, response)
    {
        if(status.error)
        {
            console.log("Subscribe failed ", status)
        }
        else
        {
            console.log("Subscribe success", status)
        }
    }
    );
}

function publishUpdate(data, channel)
{
    pubnub.publish({
        channel : channel,
        message : data
    },
    function(status, response)
    {
        if(status.error)
        {
            console.log(status)
        }
        else
        {
            console.log("Message published with timetoken", response.timetoken);
        }
    }
    );
}


function logout()
{
    console.log("Logging out and unsubscribing");
    pubnub.unsubscribe({
        channels : [myChannel]
    })
    location.replace("/logout");
}

function handleClick(cb)
{
	if(cb.checked)
	{
		value = "ON";
	}
	else
	{
		value = "OFF";
	}
	let ckbStatus = new Object();
	ckbStatus[cb.id] = value;
	let event = new Object();
	event.event = ckbStatus;
	publishUpdate(event, myChannel);
}

