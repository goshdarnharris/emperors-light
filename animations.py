import time
'''
import board
import neopixel
'''
import random
import math

import time
'''
import neopixel
'''

gamma8 = [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]

#this isn't used by the animations, it's a utility for use in the main code
class NonBlockingDelay:
    def __init__(self, delay_s):
        self.delay_s = delay_s
        self.start_time = None

    def start(self):
        self.start_time = time.monotonic()

    def is_done(self):
        if self.start_time is None:
            return False
        current_time = time.monotonic()
        if current_time - self.start_time >= self.delay_s:
            return True
        return False

#this class is to make it easier to change the color of a whole animation/LED List/etc.
class ColorRef:
    def __init__(self, color=(255, 241, 224)):
        self.color = color

    def get_color(self):
        return self.color

    def set_color(self, color=(255, 241, 224)):
        self.color = color

def accept_any(led, inner_index, outer_index):
    return True

class LEDGroup:

    def __init__(self, *args, **kwargs):
        self.lists = [*args]
        self.filter = accept_any if 'filter' not in kwargs else kwargs['filter']

    def iterate_leds(self):
        outer_index = 0 # the index across lists
        for led_list in self.lists:
            inner_index = 0 # the index within a single list
            for led in led_list.leds:
                if self.filter(led, inner_index, outer_index):
                    yield led, inner_index, outer_index
                inner_index += 1
                outer_index += 1

class BaseAnimation:
    def __init__(self, led_group:LEDGroup, duration=0, frame_length=0.01, base_color=ColorRef((25, 25, 25)), after_animation_color=ColorRef((25, 25, 25))):
        self.duration = duration
        self.frame_length = frame_length
        self.led_group = led_group
        self.neoPixel_objects = []
        self.base_color = base_color
        self.start_time = None
        self.frame_start = None
        self.is_active = False
        self.fade_start_time = None
        self.after_animation_color = after_animation_color

    def start(self):
        self.start_time = time.monotonic()
        self.frame_start = self.start_time
        self.fade_start_time = self.start_time
        self.is_active = True

    def stop(self):
        self.is_active = False
        for neopixel_obj, pixel_num in self.led_list:
            neopixel_obj[pixel_num] = self.after_animation_color.get_color()
        for string in self.neoPixel_objects:
            string.show()

    def interpolate_color(self, t, color1, color2):
        return tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3))

    def scale_color(self, color, scale):
        return tuple(min(255, max(0, int(c * scale))) for c in color)

    def animate(self):
        raise NotImplementedError("Subclasses should implement this method")

class Chase(BaseAnimation):
    def __init__(self, led_group:LEDGroup, duration = 0, frame_length = 0.5, total_chase_length = 3, chase_leds_on = 1, base_color=ColorRef((255, 255, 255)), after_animation_color=ColorRef((255, 255, 255)), off_color=ColorRef((0, 0, 0))): #TODO align the chase versions
        super().__init__(led_group, duration, frame_length, base_color, after_animation_color) #we need to use lists of LEDs, not a list of LEDs
        self.total_chase_length = total_chase_length
        self.chase_leds_on = chase_leds_on
        self.off_color = off_color
        self.current_positions = [0] * len(self.led_group.lists)
        self.neoPixel_objects = list()
        self.base_color = base_color
        self.after_animation_color = after_animation_color

    def animate(self):
        if not self.is_active:
            return

        current_time = time.monotonic()
        if self.duration != 0 and current_time - self.start_time > self.duration:
            self.stop()
            return

        if current_time - self.frame_start >= self.frame_length:
            self.frame_start = current_time

            for list_idx, led_list in enumerate(self.led_lists):

                current_position = self.current_positions[list_idx]
                num_leds = len(led_list)
                new_states = [0] * num_leds

                # Turn off all LEDs first
                for i in range(num_leds):
                    neopixel_obj, pixel_num = led_list[i]
                    neopixel_obj[pixel_num] = self.off_color.get_color()

                # Calculate the number of chase segments
                num_chase_segments = max(1, (num_leds // self.total_chase_length)+(self.total_chase_length < num_leds))

                # Turn on the chase LEDs for each segment
                for segment in range(num_chase_segments):
                    segment_offset = segment * self.total_chase_length
                    for i in range(self.chase_leds_on):
                        position = (((current_position + i )% self.total_chase_length) + segment_offset)
                        if position < num_leds:  # Only turn on LEDs if within the actual LED list length
                            neopixel_obj, pixel_num = led_list[position]
                            neopixel_obj[pixel_num] = self.base_color.get_color()

                # Update current position
                self.current_positions[list_idx] = (current_position + 1) % self.total_chase_length
            
            for string in self.neoPixel_objects:
                string.show()

class Fade(BaseAnimation):
    def __init__(self, led_group:LEDGroup, duration, frame_length, fade_duration, start_color=ColorRef((255, 255, 255)), after_animation_color=ColorRef((255, 255, 255)), end_color=ColorRef((0, 0, 0))):
        super().__init__(led_group, duration, frame_length, start_color, after_animation_color)
        self.fade_duration = fade_duration
        self.end_color = end_color

    def animate(self):
        if not self.is_active:
            return

        current_time = time.monotonic()
        if self.duration != 0 and current_time - self.start_time > self.duration:
            self.stop()
            return

        if current_time - self.frame_start >= self.frame_length:
            self.frame_start = current_time

            # Calculate the fade progress
            fade_progress = (current_time - self.fade_start_time) / self.fade_duration
            fade_progress = max(0, min(1, fade_progress))  # Clamp between 0 and 1
            current_color = self.interpolate_color(fade_progress, self.base_color.get_color(), self.end_color.get_color())

            # Update the color of each LED
            for neopixel_obj, pixel_num in self.led_list:
                neopixel_obj[pixel_num] = current_color

            # Reset the fade if it reaches the end
            if fade_progress >= 1:
                self.fade_start_time = current_time
                temp = self.base_color.get_color()
                self.base_color.set_color(self.end_color.get_color())
                self.end_color.set_color(temp) # Swap colors

            for string in self.neoPixel_objects:
                string.show()


class Flicker(BaseAnimation):
    def __init__(self, led_group:LEDGroup, duration=0, frame_length=0.025, flicker_off_range=0.5, max_flicker_brightness=0.8, base_color=ColorRef((255, 255, 255)), after_animation_color=ColorRef((255, 255, 255)), flicker_to_color=ColorRef((0, 0, 0))):
        super().__init__(led_group, duration, frame_length, base_color, after_animation_color)
        print(self.base_color)
        self.flicker_off_range = flicker_off_range
        self.max_flicker_brightness = max_flicker_brightness
        self.flicker_to_color = flicker_to_color

    def animate(self):
        # Do I want to actually track duration here?
        if not self.is_active:
            return

        curTime = time.monotonic()
        if curTime > (self.start_time + self.duration) and self.duration != 0:
            self.stop()

        elif curTime > (self.frame_start + self.frame_length):
            self.frame_start = curTime
            rand = random.random()
            # the idea here is that the rand is 0-1, anything below off range is the LED off, anything above max brightness is reduced
            # so by default 50% of the time the LED is off and of the rest it is between 0-30% with the top 20% being counted as 30%
            # idk, it looks good though, very flickery
            rand = (max(min(rand, self.max_flicker_brightness), self.flicker_off_range) - self.flicker_off_range)
            scaled_color = self.interpolate_color(rand,self.flicker_to_color.get_color(),self.base_color.get_color())
#             scaled_color = tuple(min(255, max(0, int(c * rand))) for c in self.base_color)
            for neopixel_obj, pixel_num in self.led_list:
                neopixel_obj[pixel_num] = scaled_color
            for string in self.neoPixel_objects:
                string.show()

class IndividualFlicker(BaseAnimation):
    def __init__(self,
            led_group:LEDGroup,
            duration=2,
            frame_length=0.025,
            flicker_off_range=0.5,
            max_flicker_brightness=0.8,
            base_color=ColorRef((255, 255, 255)), 
            after_animation_color=ColorRef((255, 255, 255)), 
            flicker_to_color=ColorRef((0, 0, 0)),
            min_time_before_add_led = 2,
            max_time_before_add_led = 10
            ):
        super().__init__(led_group, duration, frame_length, base_color, after_animation_color)
        print(self.base_color)
        self.flicker_off_range = flicker_off_range
        self.max_flicker_brightness = max_flicker_brightness
        self.flicker_to_color = flicker_to_color
        self.min_time_before_add_led = min_time_before_add_led
        self.max_time_before_add_led = max_time_before_add_led
        self.add_delay = NonBlockingDelay(random.randrange(self.min_time_before_add_led, self.max_time_before_add_led))
        self.add_delay.start()
        self.remove_delays = list()

    def animate(self):
        # Do I want to actually track duration here?
        if not self.is_active:
            return

        if self.add_delay.is_done() and len(self.led_list)>0:
            #add a single random led and a corresponding delay
            self.remove_delays.append( (NonBlockingDelay(self.duration), random.randrange(0,len(self.led_list))) )
            self.remove_delays[-1][0].start()
            self.add_delay.duration = random.randrange(self.min_time_before_add_led, self.max_time_before_add_led)
            self.add_delay.start()

        curTime = time.monotonic()
        delays_to_remove = []
        for delay_num in range(len(self.remove_delays)):
            delay, led_num_ani = self.remove_delays[delay_num]
            if delay.is_done():
                neo_obj, led_num = self.led_list[led_num_ani]
                neo_obj[led_num] = self.after_animation_color
                neo_obj.show()
                self.remove_delays[delay_num][0].start_time = None
        self.remove_delays = [x for x in self.remove_delays if not x[0].start_time==None]

        if curTime > (self.frame_start + self.frame_length) and len(self.remove_delays)>0:
            self.frame_start = curTime
            rand = random.random()
            # the idea here is that the rand is 0-1, anything below off range is the LED off, anything above max brightness is reduced
            # so by default 50% of the time the LED is off and of the rest it is between 0-30% with the top 20% being counted as 30%
            # idk, it looks good though, very flickery
            rand = (max(min(rand, self.max_flicker_brightness), self.flicker_off_range) - self.flicker_off_range)
            scaled_color = self.interpolate_color(rand,self.flicker_to_color.get_color(),self.base_color.get_color())
#             scaled_color = tuple(min(255, max(0, int(c * rand))) for c in self.base_color)
            for d, i in self.remove_delays:
                neopixel_obj, pixel_num = self.led_list[i]
                neopixel_obj[pixel_num] = scaled_color

            for string in self.neoPixel_objects:
                string.show()

class ChaseWithPartial2(BaseAnimation):
    def __init__(self, led_group:LEDGroup, duration = 0, frame_length = 0.025, move_rate_led_per_sec = 0.5, total_chase_length = 3, chase_leds_on = 1, base_color=ColorRef((255, 255, 255)), after_animation_color=ColorRef((255, 255, 255)), off_color=ColorRef((0, 0, 0))):
        super().__init__(led_group, duration, frame_length, base_color, after_animation_color) #we need to use lists of LEDs, not a list of LEDs
        self.total_chase_length = total_chase_length
        self.chase_leds_on = chase_leds_on
        self.off_color = off_color
        self.current_positions = [0.0] * len(self.led_group.lists)
        self.neoPixel_objects = list()
        self.move_rate = move_rate_led_per_sec
        self.segment_start = 0.0
        self.intensities = [0.0]*total_chase_length
        self.centerPosition = 0.0

    def start(self):
        super().start()
        self.segment_start = time.monotonic()

    def animate(self):
        if not self.is_active:
            return

        current_time = time.monotonic()
        if self.duration != 0 and current_time - self.start_time > self.duration:
            self.stop()
            return

        if current_time - self.frame_start >= self.frame_length:
            # print(self.move_rate*float(current_time - self.frame_start))
            self.centerPosition = (self.centerPosition + self.move_rate*(float(current_time - self.frame_start)))%self.total_chase_length
            for i in range(self.total_chase_length):
                int_center = int(self.centerPosition*100)
                int_i = 100*i
                int_total = 100*int(self.total_chase_length)
                int_distance = max(0,min((int_i-int_center)%int_total,(int_center-int_i)%int_total)-(self.chase_leds_on * 50))
                # if int_distance < (self.chase_leds_on * 50):
                #     int_distance = 0
                int_distance = int((int_distance/2))
                # print(int_distance)
                
                int_distance = 75-min(int_distance,75)

                
                self.intensities[i] = float(int_distance)/75.0  
                # self.intensities[i] = min((i-self.centerPosition)%self.total_chase_length,(self.centerPosition-i)%self.total_chase_length)
                # self.intensities[i] = max((self.intensities[i])-0.5,0.0)
                # self.intensities[i] = min(self.intensities[i],1.0)
                # self.intensities[i] = 1.0-self.intensities[i]
                # print(self.centerPosition)
                # self.intensities[i] = max(1.0-min(max((abs(i-self.centerPosition)%self.total_chase_length)-0.75,0),1),0)
            # print(self.intensities)

            self.frame_start = current_time

#             if current_time - self.segment_start >= self.move_rate:
#                 self.segment_start += self.move_rate #TODO make this better at missing time

            for list_idx, led_list in enumerate(self.led_lists):

                num_leds = len(led_list)
                new_states = self.intensities

                # Turn off all LEDs first
                for i in range(num_leds):
                    neopixel_obj, pixel_num = led_list[i]
                    neopixel_obj[pixel_num] = self.off_color.get_color()

                # Calculate the number of chase segments
                num_chase_segments = max(1, (num_leds // self.total_chase_length) + (self.total_chase_length < num_leds))

                # Turn on the chase LEDs for each segment
                for segment in range(num_chase_segments):
                    segment_offset = segment * self.total_chase_length
                    for i in range(self.total_chase_length):
                        position = (((i) % self.total_chase_length) + segment_offset)
                        if position < num_leds:  # Only turn on LEDs if within the actual LED list length
                            neopixel_obj, pixel_num = led_list[position]
                            corrected_color = self.interpolate_color(self.intensities[i],self.off_color.get_color(),self.base_color.get_color())
                            corrected_color = tuple(gamma8[c] for c in corrected_color)
                            neopixel_obj[pixel_num] = corrected_color#self.interpolate_color(self.intensities[i],self.off_color,self.base_color)
                            # if i == 2:
                            #     print(corrected_color)# make this be a pixel and watch the corrected vals
            for string in self.neoPixel_objects:
                string.show()

class Breathe(BaseAnimation):
    def __init__(self, led_group:LEDGroup, duration = 0, frame_length = 0.025, breath_rate = 2, base_color=ColorRef((255, 255, 255)), after_animation_color=ColorRef((255, 255, 255)), low_intensity=0.2):
        super().__init__(led_group, duration, frame_length, base_color, after_animation_color) #we need to use lists of LEDs, not a list of LEDs
        self.low_intensity = low_intensity
        self.breath_rate = breath_rate
        self.segment_start = 0.0
        

    def start(self):
        super().start()
        self.segment_start = time.monotonic()

    def animate(self):
        if not self.is_active:
            return

        current_time = time.monotonic()
        if self.duration != 0 and current_time - self.start_time > self.duration:
            self.stop()
            return

        if current_time - self.frame_start >= self.frame_length:
            # print(self.move_rate*float(current_time - self.frame_start))
            while current_time - self.segment_start >= self.breath_rate:
                self.segment_start += self.breath_rate 
            delta = current_time%self.breath_rate # - self.segment_start
            intensity = (1.0-self.low_intensity)*(1.0-abs(2*(delta)/self.breath_rate - 1.0)) + self.low_intensity
            scaled_color = self.scale_color(self.base_color.get_color(), intensity)
            # scaled_color = tuple(min(255, max(0, int(c * scale))) for c in color)
            # print(scaled_color)

            for neopixel_obj, pixel_num in self.led_list:
                neopixel_obj[pixel_num] = scaled_color
            for string in self.neoPixel_objects:
                string.show()


class Solid(BaseAnimation):
    def __init__(self, led_group:LEDGroup, duration=0, frame_length=1, base_color=ColorRef((255, 255, 255)), after_animation_color=ColorRef((255, 255, 255))):
        super().__init__(led_group, duration, frame_length, base_color, after_animation_color)

    def animate(self):
        # Do I want to actually track duration here?
        if not self.is_active:
            return

        curTime = time.monotonic()
        if curTime > (self.start_time + self.duration) and self.duration != 0:
            self.stop()

        elif curTime > (self.frame_start + self.frame_length):
            self.frame_start = curTime
            for neopixel_obj, pixel_num in self.led_list:
                neopixel_obj[pixel_num] = self.base_color.get_color()
            for string in self.neoPixel_objects:
                string.show()

class LEDList:
    def __init__(self, color):
        self.leds = []
        self.strands = []
        self.base_color = color
        self.current_color = ColorRef(color.get_color())

    def add_led(self, neopixel_obj, led_number):
        """Add a single LED."""
        self.leds.append((neopixel_obj, led_number))
        if neopixel_obj not in self.strands:
            self.strands.append(neopixel_obj)

    def add_leds(self, led_list):
        """Add multiple LEDs as a list of tuples (neopixel_obj, led_number)."""
        for neopixel_obj, led_number in led_list:
            self.leds.append((neopixel_obj, led_number))
            if neopixel_obj not in self.strands:
                self.strands.append(neopixel_obj)

    def remove_led(self, neopixel_obj, led_number):
        """Remove a single LED."""
        if (neopixel_obj, led_number) in self.leds:
            self.leds.remove((neopixel_obj, led_number))
            if not any(obj == neopixel_obj for obj, _ in self.leds):
                self.strands.remove(neopixel_obj)

    def remove_leds(self, led_list):
        """Remove multiple LEDs as a list of tuples (neopixel_obj, led_number)."""
        for neopixel_obj, led_number in led_list:
            if (neopixel_obj, led_number) in self.leds:
                self.leds.remove((neopixel_obj, led_number))
        self.strands = list({obj for obj, _ in self.leds})

    def fill(self, color):
        """Fill all LEDs with a specified color and call show() for each strand."""
        for neopixel_obj, led_number in self.leds:
            neopixel_obj[led_number] = color
        for strand in self.strands:
            strand.show()

    def get_leds(self):
        """Return a list of all LEDs as tuples (neopixel_obj, led_number)."""
        return self.leds
