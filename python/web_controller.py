#
# This file is part of the mowbot distribution (https://github.com/jefure/mowbot).
# Copyright (c) 2022 Jens Reese.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import base64
import serial
import driver
from flask import Flask, render_template, url_for
from werkzeug.utils import redirect

app = Flask(__name__)

serial_com = serial.Serial('/dev/ttyACM0', 115200, timeout=.1)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/cmd/<string:cmd>', methods=('POST',))
def control(btn_value):
    move(btn_value)


def move(cmd):
    print(cmd)
    driver.drive({}, serial_com)
