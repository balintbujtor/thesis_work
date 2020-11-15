#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.


import glob
import os
import sys
import math

try:
    sys.path.append(glob.glob('/opt/carla-simulator/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random

try:
    import pygame
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

try:
    import queue
except ImportError:
    import Queue as queue

# todo: check if it is possible to get town number during simulation
IM_SIZE_X = '1024'
IM_SIZE_Y = '576'
FOV = '110'
IMAGES_PER_MAP = 1024


class CarlaSyncMode(object):
    """
    Context manager to synchronize output from different sensors. Synchronous
    mode is enabled as long as we are inside this context

        with CarlaSyncMode(world, sensors) as sync_mode:
            while True:
                data = sync_mode.tick(timeout=1.0)

    """

    def __init__(self, world, *sensors, **kwargs):
        self.world = world
        self.sensors = sensors
        self.frame = None
        self.delta_seconds = 1.0 / kwargs.get('fps', 20)
        self._queues = []
        self._settings = None

    def __enter__(self):
        self._settings = self.world.get_settings()
        self.frame = self.world.apply_settings(carla.WorldSettings(
            no_rendering_mode=False,
            synchronous_mode=True,
            fixed_delta_seconds=self.delta_seconds))

        def make_queue(register_event):
            q = queue.Queue()
            register_event(q.put)
            self._queues.append(q)

        make_queue(self.world.on_tick)
        for sensor in self.sensors:
            make_queue(sensor.listen)
        return self

    def tick(self, timeout):
        self.frame = self.world.tick()
        data = [self._retrieve_data(q, timeout) for q in self._queues]
        assert all(x.frame == self.frame for x in data)
        return data

    def __exit__(self, *args, **kwargs):
        self.world.apply_settings(self._settings)

    def _retrieve_data(self, sensor_queue, timeout):
        while True:
            data = sensor_queue.get(timeout=timeout)
            if data.frame == self.frame:
                return data


def draw_image(surface, image, blend=False):
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    image_surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
    if blend:
        image_surface.set_alpha(100)
    surface.blit(image_surface, (0, 0))


def get_font():
    fonts = [x for x in pygame.font.get_fonts()]
    default_font = 'ubuntumono'
    font = default_font if default_font in fonts else fonts[0]
    font = pygame.font.match_font(font)
    return pygame.font.Font(font, 14)


def should_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                return True
    return False


def main():
    """
    map config:
        cd PythonAPI/utils
        python config.py --map Town01
    weather settings:
        cd PythonAPI/examples
        python dynamic_weather.py
    actor spawning:
        python spawn_npc.py -n 200 -w 100 --safe
    """

    actor_list = []
    # pygame.init()

    # this is the display window for the animation
    # display = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)

    # clock = pygame.time.Clock()

    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)

    world = client.get_world()

    try:
        m = world.get_map()
        TOWN_NO = int(m.name[4] + m.name[5])
        start_pos = random.choice(m.get_spawn_points())

        blueprint_library = world.get_blueprint_library()

        # vehicle init
        vehicle = world.spawn_actor(blueprint_library.find('vehicle.audi.etron'), start_pos)

        # traffic manager manages the movement of the car, no collisions this way
        vehicle.set_simulate_physics(True)
        tm = client.get_trafficmanager()
        tm_port = tm.get_port()
        vehicle.set_autopilot(True, tm_port)

        # rgb camera initialization
        rgb_bp = blueprint_library.find('sensor.camera.rgb')
        rgb_bp.set_attribute('image_size_x', IM_SIZE_X)
        rgb_bp.set_attribute('image_size_y', IM_SIZE_Y)
        rgb_bp.set_attribute('fov', FOV)

        # semantic segmentation camera init
        # each pixel contains the tag encoded in the red channel
        semseg_bp = blueprint_library.find('sensor.camera.semantic_segmentation')
        semseg_bp.set_attribute('image_size_x', IM_SIZE_X)
        semseg_bp.set_attribute('image_size_y', IM_SIZE_Y)
        semseg_bp.set_attribute('fov', FOV)

        # depth camera init
        depth_bp = blueprint_library.find('sensor.camera.depth')
        depth_bp.set_attribute('image_size_x', IM_SIZE_X)
        depth_bp.set_attribute('image_size_y', IM_SIZE_Y)
        depth_bp.set_attribute('fov', FOV)

        # positive position is front or upwards negative is the opponent
        # attachment type is rigid by default

        # attaching the cameras to the ego vehicle
        camera_rgb = world.spawn_actor(
            rgb_bp, carla.Transform(carla.Location(x=2, z=2), carla.Rotation()), attach_to=vehicle)
        actor_list.append(camera_rgb)

        camera_semseg = world.spawn_actor(
            semseg_bp, carla.Transform(carla.Location(x=2, z=2), carla.Rotation()), attach_to=vehicle)
        actor_list.append(camera_semseg)

        camera_depth = world.spawn_actor(
            depth_bp, carla.Transform(carla.Location(x=2, z=2), carla.Rotation()), attach_to=vehicle)
        actor_list.append(camera_depth)

        # image, location and time counting
        ticks = 0
        prev_loc = vehicle.get_transform().location

        # todo: start with 1 and go until <= 1024
        im_num = 0

        # Create a synchronous mode context.
        with CarlaSyncMode(world, camera_rgb, camera_semseg, camera_depth, fps=30) as sync_mode:
            while im_num < IMAGES_PER_MAP:
                #if should_quit():
                 #   return
                # clock.tick()

                ticks += 1

                # Advance the simulation and wait for the data.
                snapshot, im_rgb, im_semseg, im_depth = sync_mode.tick(timeout=2.0)

                # check sun altitude and turn on / off lights depending on it
                weather = world.get_weather()
                sun_angle = weather.sun_altitude_angle
                if sun_angle < 0:
                    # Turn on lights
                    vehicle.set_light_state(carla.VehicleLightState(
                        carla.VehicleLightState.HighBeam | carla.VehicleLightState.LowBeam | carla.VehicleLightState.Position))
                else:
                    vehicle.set_light_state(carla.VehicleLightState.NONE)

                # location calc
                new_loc = vehicle.get_transform().location
                dx = new_loc.x - prev_loc.x
                dy = new_loc.y - prev_loc.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 15.0:
                    if 9 < im_num < 100:
                        im_num_str = "00" + str(im_num)
                    elif 1000 > im_num > 99:
                        im_num_str = "0" + str(im_num)
                    elif im_num > 999:
                        im_num_str = str(im_num)
                    else:
                        im_num_str = "000" + str(im_num)

                    if TOWN_NO == 10:
                        im_rgb.save_to_disk(path=f'/media/Balint/carla_images/rgb/{TOWN_NO}/town{TOWN_NO}_{im_num_str}.jpg')
                        im_semseg.save_to_disk(
                            path=f'/media/Balint/carla_images/semantic/{TOWN_NO}/town{TOWN_NO}_sem{im_num_str}.png')
                        im_semseg.save_to_disk(
                            path=f'/media/Balint/carla_images/converted/{TOWN_NO}/town{TOWN_NO}_conv{im_num_str}.png',
                            color_converter=carla.ColorConverter.CityScapesPalette)
                        im_depth.save_to_disk(
                            path=f'/media/Balint/carla_images/depth/{TOWN_NO}/town{TOWN_NO}_depth{im_num_str}.png',
                            color_converter=carla.ColorConverter.Depth)
                    else:
                        im_rgb.save_to_disk(path=f'/media/Balint/carla_images/rgb/0{TOWN_NO}/town0{TOWN_NO}_{im_num_str}.jpg')
                        im_semseg.save_to_disk(
                            path=f'/media/Balint/carla_images/semantic/0{TOWN_NO}/town0{TOWN_NO}_sem{im_num_str}.png')
                        im_semseg.save_to_disk(
                            path=f'/media/Balint/carla_images/converted/0{TOWN_NO}/town0{TOWN_NO}_conv{im_num_str}.png',
                            color_converter=carla.ColorConverter.CityScapesPalette)
                        im_depth.save_to_disk(
                            path=f'/media/Balint/carla_images/depth/0{TOWN_NO}/town0{TOWN_NO}_depth{im_num_str}.png',
                            color_converter=carla.ColorConverter.Depth)

                    im_num += 1
                    print("image no: ", str(im_num))
                    ticks = 0
                    prev_loc = new_loc

                # im_semseg.convert(carla.ColorConverter.CityScapesPalette)

                # Draw the display.
                # draw_image(display, im_rgb)
                # pygame.display.flip()
    finally:

        print('destroying actors.')
        for actor in actor_list:
            actor.destroy()

        #pygame.quit()
        print('done.')


if __name__ == '__main__':

    try:

        main()

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
