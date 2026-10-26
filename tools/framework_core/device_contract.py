"""Small provider-neutral device capability contract; no device I/O by itself."""


class DeviceAdapter:
    """Normalize provider results and replay successful keyed operations."""

    ERRORS = {'OFFLINE', 'TIMEOUT', 'INVALID_RESPONSE', 'UNAUTHORIZED', 'INDETERMINATE'}

    def __init__(self, provider):
        if not callable(provider):
            raise ValueError('INVALID_PROVIDER')
        self.provider = provider
        self._requests = {}
        self._results = {}

    def execute(self, capability, command, value=None, idempotency_key=None):
        if (not isinstance(capability, str) or not capability.strip()
                or not isinstance(command, str) or not command.strip()):
            raise ValueError('INVALID_COMMAND')
        request = (capability, command, value)
        if idempotency_key is not None:
            if idempotency_key in self._requests:
                if self._requests[idempotency_key] != request:
                    raise ValueError('IDEMPOTENCY_CONFLICT')
                replay = dict(self._results[idempotency_key])
                replay['replayed'] = True
                return replay
        try:
            raw = self.provider(capability, command, value)
        except TimeoutError:
            return {'status': 'TIMEOUT'}
        except PermissionError:
            return {'status': 'UNAUTHORIZED'}
        except (ConnectionError, OSError):
            return {'status': 'OFFLINE'}
        result = self._normalize(raw)
        if idempotency_key is not None and result['status'] == 'OK':
            self._requests[idempotency_key] = request
            self._results[idempotency_key] = result
        return dict(result)

    def _normalize(self, raw):
        if isinstance(raw, tuple) and len(raw) == 2 and raw[0] == 'ok':
            return {'status': 'OK', 'value': raw[1]}
        if isinstance(raw, dict):
            if raw.get('ok') is True and set(raw) <= {'ok', 'value'}:
                return {'status': 'OK', 'value': raw.get('value')}
            if set(raw) == {'error'} and raw['error'] in self.ERRORS:
                return {'status': raw['error']}
        return {'status': 'INVALID_RESPONSE'}
