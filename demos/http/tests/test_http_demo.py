import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_DEMO_PATH = Path(__file__).resolve().parents[1] / "demo.py"
_SPEC = spec_from_file_location("http_demo_module", _DEMO_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
run_http_demo = _MODULE.run_http_demo


class HTTPDemoTest(unittest.TestCase):
    def test_http_demo_runs_with_jws_and_anchor(self) -> None:
        summary = run_http_demo(print_output=False)

        self.assertEqual(summary["provider_card_status"], 200)
        self.assertEqual(summary["a2a_status"], 200)
        self.assertEqual(summary["a2a_response"]["handshake"]["reason"], "ACCEPTED")
        self.assertEqual(summary["a2a_response"]["result"]["status"], "completed")
        self.assertEqual(len(summary["a2a_response"]["ipr"]["hash"]), 64)
        self.assertEqual(summary["a2a_response"]["anchor"]["anchor_type"], "in_memory_reputation_registry")
        self.assertEqual(summary["anchor_count"], 1)


if __name__ == "__main__":
    unittest.main()
