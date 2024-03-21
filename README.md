This plugin will be no longer maintained. We recommend to use the [check_redfish](https://github.com/bb-Ricardo/check_redfish)

# check_hp_ilo

Check for hardware health of an HP ILO system, using the XML API.

Create a read-only account to run the check against your ILO systems.

## Requirements

Currently, the plugin requires at least Python 3.6.

Make sure to install `hpilo` from [python-hpilo] or [seveas on GitHub].

[python-hpilo]: https://pypi.org/project/python-hpilo/
[seveas on GitHub]: https://github.com/seveas/python-hpilo

## Usage

```
check_hp_ilo.py [-h] --ilo ILO --user USER --password PASSWORD \
                    [--port PORT] [--timeout TIMEOUT] [--exclude EXCLUDE]

Check for hardware health of an HP ILO system

optional arguments:
  -h, --help            show this help message and exit
  --ilo ILO, -i ILO     ILO IP or Hostname
  --user USER, -u USER  Username for ILO Access
  --password PASSWORD, -p PASSWORD
                        Password for ILO Access
  --port PORT           TCP port for ILO Access
  --timeout TIMEOUT, -t TIMEOUT
                        Connection timeout in seconds
  --exclude EXCLUDE, -x EXCLUDE
                        Sub-checks to exclude. Can be used multiple times
```

### Examples

```
check_hp_ilo.py --ilo my.ilo.exaple \
   --user user1 --password secret

[OK] Overall Status for (ProLiant BL460c Gen8)
 \ [OK] bios_hardware is OK
 \ [OK] fans is OK
 \ [OK] memory is OK
 \ [OK] network is OK
 \ [OK] processor is OK
 \ [OK] storage is OK
 \ [OK] temperature is OK
```

```
check_hp_ilo.py --ilo my.ilo.exaple \
   --user user1 --password secret \
   --exclude temperature --exclude memory

[CRITICAL] Overall Status for (ProLiant BL460c Gen8)
 \ [CRITICAL] bios_hardware is ERROR
 \ [CRITICAL] fans is EXPLODED
 \ [CRITICAL] network is COMPROMISED
 \ [OK] processor is OK
 \ [OK] storage is OK
```

## License

Copyright (C) 2021 [NETWAYS GmbH](mailto:info@netways.de)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
