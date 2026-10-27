import contextlib
import io
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import mixer


class MixerTests(unittest.TestCase):
    def test_snapshot_merges_batches_and_removes_destroyed_objects(self):
        raw = '[{"id":1,"info":{"props":{"a":1,"b":2}}},{"id":2}]\n' \
              '[{"id":1,"info":{"props":{"a":3}}},{"id":2,"info":null}]'
        with patch.object(mixer, 'run', return_value=SimpleNamespace(returncode=0, stdout=raw)):
            self.assertEqual(mixer.snapshot(), [{'id': 1, 'info': {'props': {'a': 3, 'b': 2}}}])

    def test_failed_dump_is_not_treated_as_empty_graph(self):
        with patch.object(mixer, 'run', return_value=SimpleNamespace(returncode=1, stderr='offline')):
            with self.assertRaisesRegex(RuntimeError, 'offline'):
                mixer.snapshot()

    def test_check_does_not_start_mixer(self):
        with patch.object(mixer.shutil, 'which', return_value='/usr/bin/tool'), \
             patch.object(mixer, 'get_state', return_value=([], [], {}, [], None)), \
             patch.object(mixer, 'mix') as start, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(mixer.main(['--check']), 0)
            start.assert_not_called()

    def test_missing_dependency_does_not_touch_audio(self):
        with patch.object(mixer.shutil, 'which', return_value=None), \
             patch.object(mixer, 'get_state') as state, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(mixer.main([]), 1)
            state.assert_not_called()


if __name__ == '__main__':
    unittest.main()
