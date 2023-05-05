#!/usr/bin/env python3

import unittest
import unittest.mock as mock
import sys

sys.path.append('..')


from check_hp_ilo import commandline
from check_hp_ilo import print_performance_line
from check_hp_ilo import print_perfdata
from check_hp_ilo import main


fixture_product_name1 = 'ProLiant BL460c Gen8'

fixture_embedded_health1 = {
    'fans': {'Virtual Fan': {'label': 'Virtual Fan',
                             'speed': (22, 'Percentage'),
                             'status': 'OK',
                             'zone': 'Virtual'}},
    'power_supply_summary': {'power_management_controller_firmware_version': '3.3',
                          'present_power_reading': '65 Watts'},
    'health_at_a_glance': {'bios_hardware': {'status': 'OK'},
                           'fans': {'status': 'OK'},
                           'memory': {'status': 'OK'},
                           'network': {'status': 'OK'},
                           'processor': {'status': 'OK'},
                           'storage': {'status': 'OK'},
                           'temperature': {'status': 'OK'}},
    'temperature': {'01-Inlet Ambient': {'caution': (42, 'Celsius'),
                                      'critical': (46, 'Celsius'),
                                         'currentreading': (19, 'Celsius'),
                                         'label': '01-Inlet Ambient',
                                         'location': 'Ambient',
                                         'status': 'OK'},
                    '02-CPU 1': {'caution': (70, 'Celsius'),
                                 'critical': 'N/A',
                                 'currentreading': (40, 'Celsius'),
                                 'label': '02-CPU 1',
                                 'location': 'CPU',
                                 'status': 'OK'},
                    '03-CPU 2': {'caution': (70, 'Celsius'),
                                 'critical': 'N/A',
                                 'currentreading': 'N/A',
                                 'label': '03-CPU 2',
                                 'location': 'CPU',
                                 'status': 'OK'},
                    }
}

fixture_embedded_health2 = {
    'fans': {'Virtual Fan': {'label': 'Virtual Fan',
                             'speed': (22, 'Percentage'),
                             'status': 'OK',
                             'zone': 'Virtual'}},
    'power_supply_summary': {'power_management_controller_firmware_version': '3.3',
                          'present_power_reading': '65 Watts'},
    'health_at_a_glance': {'bios_hardware': {'status': 'ERROR'},
                           'fans': {'status': 'EXPLODED'},
                           'memory': {'status': 'OK'},
                           'network': {'status': 'COMPROMISED'},
                           'processor': {'status': 'OK'},
                           'storage': {'status': 'OK'},
                           'temperature': {'status': 'OK'}},
    'temperature': {'01-Inlet Ambient': {'caution': (42, 'Celsius'),
                                      'critical': (46, 'Celsius'),
                                         'currentreading': (19, 'Celsius'),
                                         'label': '01-Inlet Ambient',
                                         'location': 'Ambient',
                                         'status': 'OK'},
                    '02-CPU 1': {'caution': (70, 'Celsius'),
                                 'critical': 'N/A',
                                 'currentreading': (40, 'Celsius'),
                                 'label': '02-CPU 1',
                                 'location': 'CPU',
                                 'status': 'OK'}
                    }
}

class UtilTest(unittest.TestCase):

    @mock.patch('builtins.print')
    def test_performance_line(self, mock_print):
        print_performance_line("unit/()test123", 1, 'C')
        mock_print.assert_called_with("'unit_test123'=1C")

        print_performance_line("", 1, 'C')
        mock_print.assert_called_with("''=1C")

        print_performance_line(" Unit Test ", 1, 'C')
        mock_print.assert_called_with("'_Unit_Test_'=1C")

    @mock.patch('builtins.print')
    def test_print_perfdata(self, mock_print):
        print_perfdata(fixture_embedded_health1)
        expected = [mock.call('|', end=''),
                    mock.call("'Virtual_Fan_usage'=22%"),
                    mock.call("'01_Inlet_Ambient_temp'=19"),
                    mock.call("'02_CPU_1_temp'=40"),
                    mock.call("'present_power_reading'=65")]

        mock_print.assert_has_calls(expected)


    def test_commandline(self):
        args = ['--ilo', 'localhost', '--user', 'secretuser', '--password', 'secretpass']
        actual = commandline(args)
        self.assertEqual(actual.ilo, 'localhost')
        self.assertEqual(actual.user, 'secretuser')
        self.assertEqual(actual.password, 'secretpass')
        self.assertEqual(actual.timeout, 10)


class MainTest(unittest.TestCase):

    @mock.patch('builtins.print')
    @mock.patch('check_hp_ilo.hpilo')
    def test_main_poweroff(self, mock_hp, mock_print):

        i = mock.MagicMock()
        i.get_host_power_status.return_value = 'OFF'
        i.get_embedded_health.return_value = ''
        i.get_product_name.return_value = ''
        mock_hp.Ilo.return_value = i

        args = commandline(['--ilo', 'localhost', '--user', 'secretuser', '--password', 'secretpass'])
        actual = main(args)

        expected = 0
        self.assertEqual(actual, expected)
        mock_print.assert_called_with("[OK] System powered off")


    @mock.patch('builtins.print')
    @mock.patch('check_hp_ilo.hpilo')
    def test_main_ok(self, mock_hp, mock_print):

        i = mock.MagicMock()
        i.get_host_power_status.return_value = 'ON'
        i.get_embedded_health.return_value = fixture_embedded_health1
        i.get_product_name.return_value = fixture_product_name1
        mock_hp.Ilo.return_value = i

        args = commandline(['--ilo', 'localhost', '--user', 'secretuser', '--password', 'secretpass'])
        actual = main(args)

        expected = 0
        self.assertEqual(actual, expected)

        expected = [
            mock.call('[OK] Overall Status for (ProLiant BL460c Gen8)'),
            mock.call(' \\ [OK] bios_hardware'),
            mock.call(' \\ [OK] fans'),
            mock.call(' \\ [OK] memory'),
            mock.call(' \\ [OK] network'),
            mock.call(' \\ [OK] processor'),
            mock.call(' \\ [OK] storage'),
            mock.call(' \\ [OK] temperature')]

        mock_print.assert_has_calls(expected)

    @mock.patch('builtins.print')
    @mock.patch('check_hp_ilo.hpilo')
    def test_main_critical(self, mock_hp, mock_print):

        i = mock.MagicMock()
        i.get_host_power_status.return_value = 'ON'
        i.get_embedded_health.return_value = fixture_embedded_health2
        i.get_product_name.return_value = fixture_product_name1
        mock_hp.Ilo.return_value = i

        args = commandline(['--ilo', 'localhost', '--user', 'secretuser', '--password', 'secretpass'])
        actual = main(args)

        expected = 2
        self.assertEqual(actual, expected)

        expected = [mock.call('[CRITICAL] Overall Status for (ProLiant BL460c Gen8)'),
                    mock.call(' \\ [ERROR] bios_hardware'),
                    mock.call(' \\ [EXPLODED] fans'),
                    mock.call(' \\ [OK] memory'),
                    mock.call(' \\ [COMPROMISED] network'),
                    mock.call(' \\ [OK] processor'),
                    mock.call(' \\ [OK] storage'),
                    mock.call(' \\ [OK] temperature')]

        mock_print.assert_has_calls(expected)

    @mock.patch('builtins.print')
    @mock.patch('check_hp_ilo.hpilo')
    def test_main_no_connection(self, mock_hp, mock_print):

        mock_hp.Ilo.side_effect = Exception('FAIL!')

        args = commandline(['--ilo', 'localhost', '--user', 'secretuser', '--password', 'secretpass'])
        actual = main(args)

        expected = 2
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
