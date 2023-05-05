#!/usr/bin/env python3
"""
Check for hardware health of an HP ILO system, using the XML API.

Create a read-only account to run the check against your ILO systems.

Based on https://seveas.github.io/python-hpilo

See https://seveas.github.io/python-hpilo/health.html
"""

# Copyright (C) 2021 NETWAYS GmbH <info@netways.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import sys
import re

# State codes for Icinga
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# Try to load hpilo and fail gracefully
try:
    import hpilo
except ImportError as e:
    print("[UNKNOWN] Could not load python-hpilo, please ensure its installed:", e)
    sys.exit(UNKNOWN)


def get_args():
    parser = argparse.ArgumentParser(description="check ilo")
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')

    required.add_argument('--ilo', '-i', help='ILO IP or Hostname', required=True)
    required.add_argument('--user', '-u', help='Username for ILO Access', required=True)
    required.add_argument('--password', '-p', help='Password for ILO Access', required=True)
    required.add_argument('--port', help='TCP port for ILO Access', type=int, default=443)
    required.add_argument('--timeout', '-t', help='Timeout to connect', type=int, default=10)

    optional.add_argument('--exclude', '-x', help='exclude this check')

    parser._action_groups.append(optional)
    parser._optionals.title = "Options"

    return parser.parse_args()


def print_perfdata(health):
    print("|")
    for fan in health["fans"]:
        print_performance_line(fan + "_usage", health['fans'][fan]['speed'][0], '%')

    for temp in health["temperature"]:
        if health['temperature'][temp]['currentreading'] != "N/A":
            print_performance_line(temp + "_temp", health['temperature'][temp]['currentreading'][0])

    print_performance_line("present_power_reading", health['power_supply_summary']['present_power_reading'].split(" ")[0])


def sane_perfdata_label(label):
    return re.sub(r'[^A-Za-z0-9]+', '_', label)


def print_performance_line(label, value, uom=''):
    label = sane_perfdata_label(label)
    print(f"\'{label}\'={value}{uom}")


def main():
    args = get_args()

    try:
        ilo = hpilo.Ilo(args.ilo, args.user, args.password, port=args.port, timeout=args.timeout)
        power_status = ilo.get_host_power_status()
        health = ilo.get_embedded_health()
        device = ilo.get_product_name()
    except Exception:
        exception_exc = sys.exc_info()
        print("[CRITICAL] Could not connect to ILO:", exception_exc[0], exception_exc[1])
        sys.exit(CRITICAL)

    if power_status == "OFF":
        print("[OK] System powered off")
        sys.exit(OK)

    check_status = OK
    text_status = "OK"
    check_output = []

    for check in health["health_at_a_glance"]:
        status = health["health_at_a_glance"][check]["status"]
        if status not in ["OK", "Redundant", "Not Installed"] or (args.exclude and check not in args.exclude):
            check_status = CRITICAL
            text_status = "CRITICAL"
        check_output.append(f"[{status}] {check}")

    # Shortoutput
    print(f"[{text_status}] Overallstatus ({device})")

    # Longoutput
    for i in check_output:
        print(i)

    # Perfdata
    print_perfdata(health)

    sys.exit(check_status)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        exception = sys.exc_info()
        print("[UNKNOWN] Unexpected Python error:", exception[0], exception[1])
        sys.exit(UNKNOWN)
