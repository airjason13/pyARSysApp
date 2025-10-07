#!/bin/sh

killall hostapd
sleep 3
hostapd /etc/uap0_hostapd.conf