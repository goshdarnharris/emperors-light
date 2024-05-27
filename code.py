``import time
import board
import neopixel
import random
from animations2 import *
import os, ssl, socketpool, wifi, ipaddress
# from umqtt.robust import uMQTT
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import gc
import adafruit_logging as logging
# logger = logging.getLogger('test')

#auto_write needs to be false for this to perform fast animations
animations = list()

onBoardPixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixelString = neopixel.NeoPixel(board.A4, 115, auto_write=False) #TODO consider how best to sync show if needed
teleporterPixelString = neopixel.NeoPixel(board.A5, 115, auto_write=False) #TODO consider how best to sync show if needed
infintyPixelString = neopixel.NeoPixel(board.A3, 64, auto_write=False,pixel_order=neopixel.RGBW) #TODO consider how best to sync show if needed

infiniteChase = list()#LEDList()

for i in range(2):
    infiniteChase.append(LEDList())
    for j in range(0,8):
        infiniteChase[-1].add_led(infintyPixelString, i*32+j)
    infiniteChase.append(LEDList())
    for j in range(0,8):
        infiniteChase[-1].add_led(infintyPixelString, (7+8+(i*32))-(j))
    infiniteChase.append(LEDList())
    for j in range(0,8):
        infiniteChase[-1].add_led(infintyPixelString, (15+(i*32))+(j))
    infiniteChase.append(LEDList())
    for j in range(0,8):
        infiniteChase[-1].add_led(infintyPixelString, 23+8+i*32-j)

infinity_color_1 = ColorRef((64, 60, 57))
# infiniteChaseAnimation = Chase(frame_length=0.1,total_chase_length=10,chase_leds_on=2,base_color=infinity_color_1)
infiniteChaseAnimation = ChaseWithPartial2(frame_length=0.1,total_chase_length=10,move_rate_led_per_sec=8,chase_leds_on=2,base_color=infinity_color_1)
for i in range(8):
    infiniteChaseAnimation.add_led_list(infiniteChase[i].get_leds())
animations.append(infiniteChaseAnimation)
infiniteChaseAnimation.start()


front_LEDs = LEDList()
for i in range(0,115):
    front_LEDs.add_led(pixelString, i)
front_LEDs_base_color = (10,0,0)
front_LEDs_off_color = (0,0,0)
# front_LEDs.fill(front_LEDs_base_color)
# front_LEDs.fill((1,0,0))
i = 0
# print(len(b))
# while True:
#     print(i)
#     front_LEDs.fill((b[i],0,0))
#     i = (i+1)%256
#     time.sleep(0.01)

# colors we'll use as color objects to make it easier to change
teleporter_color_1 = ColorRef((0,40,80))
teleporter_color_outer = ColorRef((80,0,0))
teleporter_color_inner = ColorRef((80,20,0))
teleporter_color_flicker = ColorRef((0,40,80))
teleporter_color_off = ColorRef((0,0,0))
teleporter_color_Blue = ColorRef((0,40,80))
teleporter_color_Red = ColorRef((80,0,0))
teleporter_color_2 = ColorRef((0,0,0))
teleporter_color_3 = ColorRef((80,20,0))

# teleporter pad lists

all_teleporter_pad_leds = LEDList()
for i in range(0,115):
    all_teleporter_pad_leds.add_led(teleporterPixelString, i)
    # teleporterPixelString[i] = teleporter_color_1.get_color()
teleporterPixelString.show()

even_teleporter_pad_leds = LEDList()
for i in range(0,115,2):
    even_teleporter_pad_leds.add_led(teleporterPixelString, i)

odd_teleporter_pad_leds = LEDList()
for i in range(1,115,2):
    odd_teleporter_pad_leds.add_led(teleporterPixelString, i)

outer_ring_teleporter_pad_leds = LEDList()
for i in range(0,115,23):
    for j in range(16):
        outer_ring_teleporter_pad_leds.add_led(teleporterPixelString, i+j)
        # teleporterPixelString[i+j] = teleporter_color_1.get_color()

inner_ring_teleporter_pad_leds = LEDList()
for i in range(0,115,23):
    for j in range(17,23):
        inner_ring_teleporter_pad_leds.add_led(teleporterPixelString, i+j)
        # teleporterPixelString[i+j] = teleporter_color_1.get_color()

center_teleporter_pad_leds = LEDList()
for i in range(16,115,23):
    center_teleporter_pad_leds.add_led(teleporterPixelString, i)
    # teleporterPixelString[i] = teleporter_color_1.get_color()

teleporter_pad_chase_lists = list()
#the first lists (per pad) have 3 LEDs in them
for i in range(5):
    teleporter_pad_chase_lists.append(LEDList())
    teleporter_pad_chase_lists[-1].add_led(teleporterPixelString,0+i*23)
    teleporter_pad_chase_lists[-1].add_led(teleporterPixelString,17+i*23)
    teleporter_pad_chase_lists[-1].add_led(teleporterPixelString,16+i*23)
``
#the second have 2
for i in range(5):
    for j in range(5):
        teleporter_pad_chase_lists.append(LEDList())
        teleporter_pad_chase_lists[-1].add_led(teleporterPixelString,1+j+i*23)
        teleporter_pad_chase_lists[-1].add_led(teleporterPixelString,18+j+i*23)

#the third set is just hte remaining outer leds
for i in range(5):
    for j in range(10):
        teleporter_pad_chase_lists.append(LEDList())
        teleporter_pad_chase_lists[-1].add_led(teleporterPixelString,6+j+i*23)

#setup chasing inwards (or outwards) #todo make toggling chase direction easy
telporter_pads_inward_animation = Chase(frame_length=0.1,total_chase_length=3,chase_leds_on=1,base_color=teleporter_color_1,off_color=teleporter_color_2,after_animation_color=teleporter_color_1)
for led_list in teleporter_pad_chase_lists:
    telporter_pads_inward_animation.add_led_list(led_list.get_leds())
animations.append(telporter_pads_inward_animation)
# telporter_pads_inward_animation.start()

telporter_pads_inward_animation_partial = ChaseWithPartial2(frame_length=0.1,move_rate_led_per_sec=5,total_chase_length=3,chase_leds_on=0.1,base_color=teleporter_color_1,off_color=teleporter_color_2,after_animation_color=teleporter_color_1)
for led_list in teleporter_pad_chase_lists:
    telporter_pads_inward_animation_partial.add_led_list(led_list.get_leds())
animations.append(telporter_pads_inward_animation_partial)
# telporter_pads_inward_animation_partial.start()


# for led_list in teleporter_pad_chase_lists:
#     for strip, led in led_list.get_leds():
#         strip[led] = teleporter_color_1.get_color()

# teleporterPixelString.show()

# while True:
#     telporter_pads_inward_animation.animate()
#     telporter_pads_inward_animation_partial.animate()


outer_chase = ChaseWithPartial2(duration=0, frame_length=0.001, move_rate_led_per_sec =6, total_chase_length=6, chase_leds_on=1, base_color=teleporter_color_outer, off_color=teleporter_color_off)
outer_chase.add_led_list(outer_ring_teleporter_pad_leds.get_leds())
outer_chase.start()
animations.append(outer_chase)

inner_chase = ChaseWithPartial2(duration=0, frame_length=0.001, move_rate_led_per_sec = 4, total_chase_length=6, chase_leds_on=1, base_color=teleporter_color_inner, off_color=teleporter_color_off)
inner_chase.add_led_list(inner_ring_teleporter_pad_leds.get_leds())
# inner_chase.start()
animations.append(inner_chase)

inner_breath = Breathe(base_color=teleporter_color_inner, frame_length = 0.005, breath_rate = 4, after_animation_color=teleporter_color_1, low_intensity=0.0)
inner_breath.add_led_list(center_teleporter_pad_leds.get_leds())
inner_breath.add_led_list(inner_ring_teleporter_pad_leds.get_leds())
inner_breath.start()
animations.append(inner_breath)

center_flicker = Flicker(frame_length=0.025,base_color=teleporter_color_flicker,flicker_to_color=teleporter_color_inner,after_animation_color=teleporter_color_Blue)
center_flicker.add_led_list(center_teleporter_pad_leds.get_leds())
center_flicker.add_led_list(inner_ring_teleporter_pad_leds.get_leds())
# center_flicker.start()
animations.append(center_flicker)

pad_breath = Breathe(base_color=teleporter_color_1, frame_length = 0.005, breath_rate = 4, after_animation_color=teleporter_color_1, low_intensity=0.2)
pad_breath.add_led_list(all_teleporter_pad_leds.get_leds())
# time.sleep(1) TODO out of sync fix
# pad_breath.start()
animations.append(pad_breath)

# while True:
#     for anim in animations:
#         anim.animate()


# occasional_ladder_flicker = Flicker(duration=2, frame_length=0.025, base_color=ladder_LEDs_base_color, after_animation_color=ladder_LEDs_base_color, flicker_to_color = (0,0,0))
# occasional_ladder_flicker.add_led_list(ladder_LEDs.get_leds())
# # ladder_flicker.start()

# single_occasional_front_flicker = IndividualFlicker(duration=10, base_color=front_LEDs_base_color, after_animation_color=front_LEDs_base_color, flicker_to_color = (0,0,0), min_time_before_add_led = 0, max_time_before_add_led = 2)
# single_occasional_front_flicker.add_led_list(front_LEDs.get_leds())
# # single_occasional_front_flicker.start()

# # front_chase = Chase(duration=0, frame_length=1.25, total_chase_length=8, chase_leds_on=1, off_color=front_LEDs_off_color, base_color=front_LEDs_base_color)
# # front_chase.add_led_list(front_LEDs.get_leds())
# # front_chase.start()

# front_chase = ChaseWithPartial2(duration=0, frame_length=0.001, move_rate_led_per_sec = 10, total_chase_length=8, chase_leds_on=1, off_color=front_LEDs_off_color, base_color=front_LEDs_base_color)
# front_chase.add_led_list(front_LEDs.get_leds())
# front_chase.start()

# breath = Breathe(base_color=front_LEDs_base_color, frame_length = 0.025, breath_rate = 5, after_animation_color=front_LEDs_base_color, low_intensity=0.4)
# breath.add_led_list(front_LEDs.get_leds())
# # breath.start()

# animations.append(occasional_ladder_flicker)
# animations.append(single_occasional_front_flicker)
# animations.append(front_chase)
# animations.append(breath)


#################### Web Stuff

print(f"Connecting to Wifi")
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print("Connected!")

ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: ")
print((wifi.radio.ping(ipv4)))

pool = socketpool.SocketPool(wifi.radio)

aio_username = os.getenv("ADAFRUIT_AIO_USERNAME")
aio_key = os.getenv("ADAFRUIT_AIO_KEY")

strip_on_off_feed = aio_username + "/feeds/strip_on_off"
color_feed = aio_username + "/feeds/color_feed"
color_outer_feed = aio_username + "/feeds/teleporter_outer_color"
color_inner_feed = aio_username + "/feeds/teleporter_inner_color"
color_flicker_feed = aio_username + "/feeds/teleporter_flicker_color"

def connected(client, userdata, flags, rc):
    #connected to broker at adafruit IO
    print("Connected to Adafruit IO! Listening for changes")
    #subscribe to all changes in the feeds
    client.subscribe(strip_on_off_feed)
    client.subscribe(color_feed)
    client.subscribe(color_outer_feed)
    client.subscribe(color_inner_feed)
    client.subscribe(color_flicker_feed)

def disconnected(client, userdata, rc):
    #disconnected from broker at adafruit
    print("Disconnected from Adafruit IO")

def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))

def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

def message(client, topic, message):
    global strip_color
    print(f"topic: {topic}, message: {message}")
    if topic == strip_on_off_feed:
        if message == "ON":
            inner_breath.stop()
            center_flicker.start()
            outer_chase.move_rate = 20
        elif message == "OFF":
            inner_breath.start()
            center_flicker.stop()
            outer_chase.move_rate = 4
    elif topic == color_feed:
        if message[0] == "#": #color picker always sends colors as string hex starting with pund sign
            message = message[1:] #trim hashtag
            teleporter_color_off.set_color((int(message[0:2], 16),int(message[2:4], 16),int(message[4:6], 16)))
    elif topic == color_outer_feed:
        if message[0] == "#": #color picker always sends colors as string hex starting with pund sign
            message = message[1:] #trim hashtag
            teleporter_color_outer.set_color((int(message[0:2], 16),int(message[2:4], 16),int(message[4:6], 16)))
    elif topic == color_inner_feed:
        if message[0] == "#": #color picker always sends colors as string hex starting with pund sign
            message = message[1:] #trim hashtag
            teleporter_color_inner.set_color((int(message[0:2], 16),int(message[2:4], 16),int(message[4:6], 16)))
    elif topic == color_flicker_feed:
        if message[0] == "#": #color picker always sends colors as string hex starting with pund sign
            message = message[1:] #trim hashtag
            teleporter_color_flicker.set_color((int(message[0:2], 16),int(message[2:4], 16),int(message[4:6], 16)))
            # front_chase.base_color = front_LEDs_base_color
#     elif topic == color_feed:
#         if message[0] == "#": #color picker always sends colors as string hex starting with pund sign
#             message = message[1:] #trim hashtag
#             strip_color = int(message, 16)
#             pixels.fill(strip_color)

mqtt_client = MQTT.MQTT(
    broker = "io.adafruit.com",#os.getenv("BROKER"),
    port = 8883,#os.getenv("PORT"),
    username = aio_username,
    password = aio_key,
    socket_pool = pool,
    ssl_context = ssl.create_default_context(),
    is_ssl=True,
    keep_alive = 60, #5 hours, will ping at the 4.5 hour mark
)

mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_message = message

# mqtt_client.will_set("feeds/strip_on_off", "DISCONNECTED", 1);

print("connecting to Adafruit IO")
mqtt_client._socket_timeout = 0
mqtt_client.connect()
print(mqtt_client._socket_timeout)

# mqtt_client.set_logger_level(DEBUG)

# mqtt_client.enable_logger(log_pkg=logging,log_level=10)


# #################### End Web Stuff


delay = NonBlockingDelay(2.5)
delay.start() #for use below

mqtt_request_delay = NonBlockingDelay(1)
mqtt_request_delay.start() #for use below

mqtt_ping_delay = NonBlockingDelay(60)
mqtt_ping_delay.start() #for use below

delay.start() #for use below
try_again_next_loop = 0
onBoardPixel.fill((0,28,0))
while True:
    for anim in animations:
        anim.animate()

    if mqtt_request_delay.is_done():
        try:
            if try_again_next_loop:
                try:
                    print("trying a basic ping")
                    ipv4 = ipaddress.ip_address("8.8.4.4")
                    print("Ping google.com: ")
                    print((wifi.radio.ping(ipv4)))
                except Exception as excep:
                    print("Failed to Ping, Exception:")
                    print(excep)
                    print("reseting wifi")
                    wifi.radio.enabled = False
                    wifi.radio.enabled = True
                    wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
                    print("reconnected")
                    print("Ping google.com: ")
                    print((wifi.radio.ping(ipv4)))
                mqtt_client = MQTT.MQTT(
                broker = "io.adafruit.com",#os.getenv("BROKER"),
                port = 8883,#os.getenv("PORT"),
                username = aio_username,
                password = aio_key,
                socket_pool = socketpool.SocketPool(wifi.radio),
                ssl_context = ssl.create_default_context(),
                is_ssl=True,
                keep_alive = 60, #5 hours, will ping at the 4.5 hour mark
                )
                print("setup new mqtt_client object")
                mqtt_client.on_connect = connected
                mqtt_client.on_disconnect = disconnected
                mqtt_client.on_subscribe = subscribe
                mqtt_client.on_unsubscribe = unsubscribe
                mqtt_client.on_message = message

                # mqtt_client.will_set("feeds/strip_on_off", "DISCONNECTED", 1);

                print("connecting to Adafruit IO")
                mqtt_client._socket_timeout = 0
                mqtt_client.connect()
                print("connected")
                print(mqtt_client._socket_timeout)
                try_again_next_loop = 0
            mqtt_client.loop()
        except Exception as e:
            print("Exception in loop:")
            print(e)
            try_again_next_loop = 1
            
        mqtt_request_delay.start()




    # if mqtt_ping_delay.is_done():
    #     try:
    #         print("ping")
    #         mqtt_client.ping()
    #         print("mem free:")
    #         print(gc.mem_free())
    #     except Exception as e:
    #         print("Exception in ping:")
    #         print(e)
    #     mqtt_ping_delay.start()

# #     if (delay.is_done()):
# #         occasional_ladder_flicker.duration = 1.5
# #         occasional_ladder_flicker.start()
# #         delay.delay_s = random.randrange(100)/10 #random makes an int, delay for 0-10s
# #         delay.start() #restart delay