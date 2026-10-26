import importlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))


class DeviceContractTests(unittest.TestCase):
    def setUp(self):
        self.module = importlib.import_module('framework_core.device_contract')

    def test_two_protocol_shapes_have_one_success_contract_and_replay(self):
        calls = []
        def tuple_protocol(capability, command, value):
            calls.append((capability, command, value))
            return 'ok', 75
        def mapping_protocol(capability, command, value):
            calls.append((capability, command, value))
            return {'ok': True, 'value': 75}
        first = self.module.DeviceAdapter(tuple_protocol)
        second = self.module.DeviceAdapter(mapping_protocol)
        one = first.execute('brightness', 'set', 75, idempotency_key='scene-1')
        two = second.execute('brightness', 'set', 75, idempotency_key='scene-2')
        self.assertEqual(one['status'], 'OK')
        self.assertEqual(two['status'], 'OK')
        self.assertEqual(one['value'], two['value'])
        self.assertNotIn('device_id', one)
        replay = first.execute('brightness', 'set', 75, idempotency_key='scene-1')
        self.assertTrue(replay['replayed'])
        self.assertEqual(calls.count(('brightness', 'set', 75)), 2)

    def test_idempotency_key_cannot_be_reused_for_another_request(self):
        adapter = self.module.DeviceAdapter(lambda capability, command, value: {'ok': True, 'value': value})
        adapter.execute('brightness', 'set', 10, idempotency_key='same')
        with self.assertRaisesRegex(ValueError, 'IDEMPOTENCY_CONFLICT'):
            adapter.execute('brightness', 'set', 90, idempotency_key='same')

    def test_errors_and_malformed_results_remain_distinguishable(self):
        cases = [
            ({'error': 'OFFLINE'}, 'OFFLINE'),
            ({'error': 'TIMEOUT'}, 'TIMEOUT'),
            ({'error': 'UNAUTHORIZED'}, 'UNAUTHORIZED'),
            ({'error': 'INDETERMINATE'}, 'INDETERMINATE'),
            ({'unexpected': True}, 'INVALID_RESPONSE')
        ]
        for raw, expected in cases:
            with self.subTest(expected=expected):
                adapter = self.module.DeviceAdapter(lambda capability, command, value: raw)
                result = adapter.execute('power', 'get')
                self.assertEqual(result['status'], expected)
                self.assertNotEqual(result['status'], 'OK')

    def test_exceptions_and_invalid_input_do_not_become_success(self):
        adapter = self.module.DeviceAdapter(lambda capability, command, value: (_ for _ in ()).throw(TimeoutError()))
        self.assertEqual(adapter.execute('power', 'get')['status'], 'TIMEOUT')
        denied = self.module.DeviceAdapter(lambda capability, command, value: (_ for _ in ()).throw(PermissionError()))
        self.assertEqual(denied.execute('power', 'get')['status'], 'UNAUTHORIZED')
        with self.assertRaisesRegex(ValueError, 'INVALID_COMMAND'):
            denied.execute('', 'get')


if __name__ == '__main__':
    unittest.main()
