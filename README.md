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
usage: check_hp_ilo.py [-h] --ilo ILO --user USER --password PASSWORD [--timeout TIMEOUT] [--exclude EXCLUDE]

check ilo

required arguments:
  --ilo ILO, -i ILO     ILO IP or Hostname
  --user USER, -u USER  Username for ILO Access
  --password PASSWORD, -p PASSWORD
                        Password for ILO Access
  --timeout TIMEOUT, -t TIMEOUT
                        Timeout to connect

Options:
  -h, --help            show this help message and exit
  --exclude EXCLUDE, -x EXCLUDE
                        exclude this check
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
