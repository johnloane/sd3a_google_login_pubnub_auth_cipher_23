import RPi.GPIO as GPIO
import time, threading

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'Your subscribe key'
pnconfig.publish_key = 'Your publish key'
pnconfig.user_id = "johns-pi"
pnconfig.cipher_key="secret"
pnconfig.auth_key="johns-sd3a-pi"
pubnub = PubNub(pnconfig)

my_channel = 'johns-sd3a-pi-channel'
sensors_list=["buzzer"]
data={}

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];
class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost
        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pubnub.publish().channel(my_channel).message('Hello world!').pn_async(my_publish_callback)
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.
    def message(self, pubnub, message):
        # Handle new message stored in message.message
        print(message.message)

    def message(self, pubnub, message):
        # Handle new message stored in message.message
        try:
            print(message.message, ": ", type(message.message))
            msg = message.message
            key = list(msg.keys())
            if key[0] == "event":
                self.handleEvent(msg)
        except Exception as e:
            print("Received: ", message.message)
            print(e)
            pass

    def handleEvent(self, msg):
        global data
        eventData = msg["event"]
        key = list(eventData.keys())
        print(key)
        print(key[0])
        if key[0] in sensors_list:
            if eventData[key[0]] == "ON":
                print("Setting the alarm")
                data["alarm"] = True
            elif eventData[key[0]] == "OFF":
                print("Turning alarm off")
                data["alarm"] = False

def publish(channel, msg):
    pubnub.publish().channel(channel).message(msg).pn_async(my_publish_callback)



PIR_pin = 23
Buzzer_pin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(Buzzer_pin, GPIO.OUT)

def beep(repeat):
    for i in range(0, repeat):
        for pulse in range(60):
            GPIO.output(Buzzer_pin, True)
            time.sleep(0.001)
            GPIO.output(Buzzer_pin, False)
            time.sleep(0.001)
        time.sleep(0.02)


def motion_detection():
    data["alarm"] = False
    trigger = False
    while(True):
        if GPIO.input(PIR_pin):
            print("Motion detected")
            beep(4)
            trigger = True
            publish(my_channel, {"motion" : "Yes"})
        elif trigger:
            publish(my_channel, {"motion" : "No"})
            trigger = False
        if data["alarm"]:
            beep(2)
        time.sleep(1)

if __name__ == '__main__':
    sensors_thread = threading.Thread(target=motion_detection)
    sensors_thread.start()
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(my_channel).execute()
