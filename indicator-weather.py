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

import json
import sys
import urllib

import appindicator
import gtk


PING_FREQUENCY_IN_MINUTES = 10


class GetWeather:
    def __init__(self):
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
        lat, lon = self.get_location()
        url = (
            'http://weatherwebservicecall.herokuapp.com/'
            'current?lat={}&lon={}'.format(lat, lon))
        u = urllib.urlopen(url)
        data = u.read()
        j = json.loads(data)
        temp = j['temperature']
        temp = int(float(temp))
        location = j['geoLocation']
        icon_name = j['iconName']
        icon_name = self.get_icon_name_local(icon_name)
        city = location.strip().rsplit(",")[-1]
        label = u'{temp}° {city}'.format(**locals())
        self.ind.set_label(label)
        self.ind.set_icon(icon_name)
        return True

    def get_icon_name_local(self, icon_name):
        if icon_name == "01d":
            return "weather-clear"
        elif icon_name == "01n":
            return "weather-clear-night"
        elif icon_name == "02d":
            return "weather-few-clouds"
        elif icon_name == "02n":
            return "weather-few-clouds-night"
        elif icon_name in ("03d", "03n"):
            return "ubuntuone-client-idle"
        elif icon_name in ("04d", "04n"):
            return "weather-overcast"
        elif icon_name in ("09d", "09n"):
            return "weather-showers"
        elif icon_name in ("10d", "10n"):
            return "weather-showers-scattered"
        elif icon_name in ("11d", "11n"):
            return "weather-storm"
        elif icon_name in ("13d", "13n"):
            return "weather-snow"
        elif icon_name in ("50d", "50n"):
            return "weather-fog"

    def get_location(self):
        url = 'http://ipinfo.io/json/'
        u = urllib.urlopen(url)
        data = u.read()
        info = json.loads(data)
        loc = info['loc']
        lat, lon = loc.strip().split(",")
        return (lat, lon)


if __name__ == "__main__":
    indicator = GetWeather()
    indicator.main()
