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

# Return code level
# 0 - OK       - The plugin was able to check the service and it appeared to be functioning properly
# 1 - WARNING  - The plugin was able to check the service, but it appeared to be above some "warning"
#                threshold or did not appear to be working properly
# 2 - CRITICAL - The plugin detected that either the service was not running or it was above some "critical" threshold
# 3 - UNKNOWN  - Invalid command line arguments were supplied to the plugin or low-level failures
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# Try to load hpilo and fail gracefully
try:
    import hpilo
except ImportError as e: # pragma: no cover
    print("[UNKNOWN] Could not load python-hpilo, ensure all dependencies are installed:", e)
    sys.exit(UNKNOWN)


def commandline(args):
    """
    Configure and parse command line arguments
    """

    parser = argparse.ArgumentParser(description="Check for hardware health of an HP ILO system")

    parser.add_argument('--ilo', '-i', help='ILO IP or Hostname', required=True)
    parser.add_argument('--user', '-u', help='Username for ILO Access', required=True)
    parser.add_argument('--password', '-p', help='Password for ILO Access', required=True)
    parser.add_argument('--port', help='TCP port for ILO Access', type=int, default=443)
    parser.add_argument('--timeout', '-t', help='Connection timeout in seconds', type=int, default=10)
    parser.add_argument('--exclude', '-x', action='append', required=False,
                        help='Sub-checks to exclude. Can be used multiple times', default=[])

    return parser.parse_args(args)


def print_perfdata(health):
    """
    Generate perfdata from Health Output
    """

    print("|", end='')
    for fan in health["fans"]:
        print_performance_line(fan + "_usage", health['fans'][fan]['speed'][0], '%')

    for temp in health["temperature"]:
        if health['temperature'][temp]['currentreading'] != "N/A":
            print_performance_line(temp + "_temp", health['temperature'][temp]['currentreading'][0])

    print_performance_line("present_power_reading", health['power_supply_summary']['present_power_reading'].split(" ")[0])

    # Newline at the end
    print("")

def print_performance_line(label, value, uom=''):
    """
    Generate perfdata line
    """
    label = label.strip().replace(' ', '_')
    label = re.sub(r'[^A-Za-z0-9]+', '_', label)
    print(f"{label}={value}{uom},", end='')


def main(args):
    print(args)
    try:
        ilo = hpilo.Ilo(args.ilo, args.user, args.password, port=args.port, timeout=args.timeout)
    except Exception:
        exception_exc = sys.exc_info()
        print("[CRITICAL] Could not connect to ILO:", exception_exc[0], exception_exc[1])
        return CRITICAL

    power_status = ilo.get_host_power_status()

    if power_status == "OFF":
        print("[OK] System powered off")
        return OK

    health = ilo.get_embedded_health()
    device = ilo.get_product_name()

    check_status = OK
    text_status = "OK"
    check_output = []

    for check in health["health_at_a_glance"]:
        if check in args.exclude:
            continue

        status = health["health_at_a_glance"][check]["status"]
        # Check if status is Critical
        status_is_critical = status not in ["OK", "Redundant", "Not Installed"]

        if status_is_critical:
            # Sub-Check not OK setting global status
            check_status = CRITICAL
            text_status = "CRITICAL"
            check_output.append(f" \\ [{text_status}] {check} is {status}")
        else:
            check_output.append(f" \\ [OK] {check} is {status}")

    # Overall Status Output
    print(f"[{text_status}] Overall Status for ({device})")

    # Sub-Check Output
    for status in check_output:
        print(status)

    # Perfdata
    print_perfdata(health)

    return check_status


if __name__ == "__main__": # pragma: no cover
    try:
        ARGS = commandline(sys.argv[1:])
        sys.exit(main(ARGS))
    except Exception:
        exception = sys.exc_info()
        print("[UNKNOWN] Unexpected Python error:", exception[0], exception[1])
        sys.exit(UNKNOWN)
