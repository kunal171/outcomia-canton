"""Supply-chain boundary checks; no external network requests."""
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("fetcher", Path(__file__).with_name("fetch-token-standard.py"))
fetcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetcher)


class FetchTests(unittest.TestCase):
    def test_verified_cache_never_needs_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "api.dar"
            path.write_bytes(b"PKverified")
            def offline(*args, **kwargs):
                self.fail("Verified cache must work offline")
            fetcher.fetch_artifact("https://example.invalid", path, hashlib.sha256(path.read_bytes()).hexdigest(), offline)

    def test_bad_download_does_not_replace_existing_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "api.dar"
            path.write_bytes(b"old cache")
            with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
                fetcher.fetch_artifact("https://example.invalid", path, "0" * 64, lambda *a, **kw: io.BytesIO(b"PKwrong"))
            self.assertEqual(path.read_bytes(), b"old cache")
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_non_archive_response_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "api.dar"
            with self.assertRaisesRegex(ValueError, "Invalid or oversized DAR"):
                fetcher.fetch_artifact("https://example.invalid", path, "0" * 64, lambda *a, **kw: io.BytesIO(b"<html>error</html>"))
            self.assertFalse(path.exists())

    def test_manifest_cannot_redirect_downloads_or_traverse_paths(self):
        valid = dict(repository="canton-network/splice", revision="a" * 40, directory="daml/dars", artifacts=[dict(name="api.dar", sha256="b" * 64)])
        for change in [dict(repository="attacker/splice"), dict(revision="main"), dict(directory="elsewhere"), dict(artifacts=[dict(name="../api.dar", sha256="b" * 64)])]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                fetcher.locked_urls(valid | change)


if __name__ == "__main__":
    unittest.main()
