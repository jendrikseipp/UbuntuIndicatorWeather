#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of indicator-weather.
# Indicator Weather is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# Indicator Weather is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.  <http://www.gnu.org/licenses/>
#
# Author(s):
# (C) 2015 Kasra Madadipouya <kasra@madadipouya.com>

import argparse
import json
import sys
import urllib

import appindicator
import gtk


PING_FREQUENCY_IN_MINUTES = 10

ICON_NAMES = {
    "01d": "weather-clear",
    "01n": "weather-clear-night",
    "02d": "weather-few-clouds",
    "02n": "weather-few-clouds-night",
    "03d": "ubuntuone-client-idle",
    "04d": "weather-overcast",
    "09d": "weather-showers",
    "10d": "weather-showers-scattered",
    "11d": "weather-storm",
    "13d": "weather-snow",
    "50d": "weather-fog",
}


def get_local_icon_name(code):
    if code in ICON_NAMES:
        return ICON_NAMES[code]
    else:
        day_code = code[:2] + 'd'
        return ICON_NAMES[day_code]


def get_location():
    url = 'http://ipinfo.io/json/'
    u = urllib.urlopen(url)
    data = u.read()
    info = json.loads(data)
    loc = info['loc']
    lat, lon = loc.strip().split(",")
    return (lat, lon)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--location",
        help="comma-separated latitude and longitude")
    return parser.parse_args()


class GetWeather:
    def __init__(self, location=None):
        self.location = location

        self.ind = appindicator.Indicator(
            "weather-indicator",
            "weather-clear",
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.menu_setup()
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        self.menu = gtk.Menu()

        self.update_item = gtk.MenuItem("Update")
        self.update_item.connect("activate", self.get_weather)
        self.update_item.show()
        self.menu.append(self.update_item)

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        gtk.idle_add(self.get_weather)
        gtk.timeout_add(PING_FREQUENCY_IN_MINUTES * 60000, self.get_weather)
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

    def get_weather(self, widget=None):
        lat, lon = self.location or get_location()
        url = (
            'http://weatherwebservicecall.herokuapp.com/'
            'current?lat={}&lon={}'.format(lat, lon))
        u = urllib.urlopen(url)
        data = u.read()
        j = json.loads(data)
        temp = j['temperature']
        temp = int(float(temp))
        location = j['geoLocation']
        code = j['iconName']
        icon_name = get_local_icon_name(code)
        city = location.strip().rsplit(",")[-1]
        label = u'{temp}° {city}'.format(**locals())
        self.ind.set_label(label)
        self.ind.set_icon(icon_name)
        return True


if __name__ == "__main__":
    args = parse_args()
    location = None
    if args.location:
        location = args.location.strip().split(",")
    indicator = GetWeather(location=location)
    indicator.main()
