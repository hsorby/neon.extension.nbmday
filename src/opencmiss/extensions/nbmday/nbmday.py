import os
import threading
import time

from PySide2.QtCore import QTimer
from PySide2.QtMultimedia import QSound
from opencmiss.neon.extensions.nbmday import NBMDay

from opencmiss.extensions.nbmday import __version__ as extension_version
from opencmiss.extensions.nbmday.dockwidget import DockWidget
from opencmiss.extensions.nbmday.model import Model
from opencmiss.extensions.nbmday.scene import Scene, get_jaw_rotation

import cProfile as profile

class MainNBMDay(NBMDay):
    """Main class for the National Bio-mechanics Day extension."""

    def __init__(self, main_view):
        self._model = Model(main_view.get_zinc_context())
        self._scene = Scene(self._model)
        self._widget = DockWidget(main_view)
        # self._view = View(self._model)
        self._make_connections()
        self._current_sound = "standard_laugh.wav"
        self._timer = QTimer()
        self._timer.setInterval(20)
        self._timer.timeout.connect(self._update_jaw)
        self._elapsed_time = 0.0
        self._start_time = time.time()
        self._sound = None
        self._sound_thread = None
        self._code_object = None

    def _make_connections(self):
        self._widget.simulate.connect(self._simulate)

    def _simulate(self):

        self._widget.enable_simulation(False)
        code_string = """from math import cos, sin, sqrt, exp
"""
        code_string += self._widget.get_code()
        code_string += """
angle = animate_jaw(elapsed_time)
"""
        self._code_object = compile(code_string, '<string>', 'exec')
        elapsed_time = 0.0
        angle = 0.0
        try:
            exec(self._code_object)
        except Exception as e:
            print(e)
        # projection_matrix = get_jaw_rotation(angle)
        self._scene.update_angle(angle)
        sound_file = os.path.join(os.path.dirname(__file__), 'sounds', self._current_sound)
        # self._sound_thread = FunctionArgumentThread(play_sound, sound_file)
        #
        # self._sound_thread.start()
        self._sound_thread = QSound(sound_file)
        self._sound_thread.play()
        # print(self._sound_thread)
        # QSound.play(sound_file)
        self._start_time = time.time()
        self._timer.start()

    def _update_jaw(self):
        if not self._sound_thread.isFinished():
            angle = 0.0
            elapsed_time = time.time() - self._start_time
            exec (self._code_object)
            # projection_matrix = get_jaw_rotation(angle)
            self._scene.update_angle(angle)
        else:
            self._widget.enable_simulation(True)
            self._timer.stop()

    # def _slow_code(self):
    #     angle = 0.0
    #     elapsed_time = time.time() - self._start_time
    #     exec (self._code_object)
    #     projection_matrix = get_jaw_rotation(angle)
    #     self._scene.update_projection_values(projection_matrix)

    def save(self):
        saved_data = {"version": extension_version, "current_sound": self._current_sound}

        return saved_data

    def _load_setting(self, json_data, key):
        if key in json_data:
            setattr(self, "_%s" % key, json_data[key])

    def open(self, saved_data):
        if "version" in saved_data:
            if saved_data["version"] in extension_version:
                self._load_setting(saved_data, "current_sound")


def play_sound(sound_file):
    print("play sound: %s" % sound_file)
    QSound.play(sound_file)
    # sound.play()
    # QSound.play(sound_file)


class FunctionArgumentThread(threading.Thread):

    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)

# node_location_right = [[55.27, 15.22, -36.96], [52.72, 41.04, -44.22]]
# node_location_left = [[55.27, 15.22, -36.96], [52.72, 40.81, -43.53]]
# 53.995
# 28.13
# -40.59
#
# 53.995
# 28.015
# -40.245
#
# 212,252,291,312