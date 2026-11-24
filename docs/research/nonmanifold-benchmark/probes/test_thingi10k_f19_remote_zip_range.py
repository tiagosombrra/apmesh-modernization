"""Hermetic HTTP range and safe archive-selection tests; no public downloads."""
from __future__ import annotations

import contextlib
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import re
import tempfile
import threading
import unittest
import zipfile

from thingi10k_f19_remote_zip_range import (HTTPRangeFile, _parse_content_range, _safe_member,
    _safe_url, acquire, select_members)


def make_zip(records: dict[str, bytes]) -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zip_stream:
        for filename, content in records.items():
            zip_stream.writestr(filename, content)
    return out.getvalue()


class SyntheticRangeServer(BaseHTTPRequestHandler):
    content = b''
    allow_range = True
    etag = '"fixed-fixture"'
    range_calls = 0
    bytes_served = 0
    broken_etag_after = -1

    def do_GET(self):
        parent = type(self)
        parent.range_calls += 1
        m = re.fullmatch(r'bytes=(\d+)-(\d+)', self.headers.get('Range', ''))
        if parent.allow_range and m:
            a, b = map(int, m.groups())
            if a < 0 or b < a or b >= len(parent.content):
                self.send_response(416)
                self.end_headers()
                return
            payload = parent.content[a:b + 1]
            self.send_response(206)
            self.send_header('Content-Range', f'bytes {a}-{b}/{len(parent.content)}')
        else:
            payload = parent.content
            self.send_response(200)
        etag = '"other-fixture"' if parent.broken_etag_after >= 0 and parent.range_calls > parent.broken_etag_after else parent.etag
        self.send_header('ETag', etag)
        self.send_header('Last-Modified', 'Wed, 05 Nov 2025 16:00:00 GMT')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
            parent.bytes_served += len(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args):
        return


@contextlib.contextmanager
def server(payload: bytes, *, allow_range=True, broken_etag_after=-1):
    class Instance(SyntheticRangeServer):
        pass
    Instance.content = payload
    Instance.allow_range = allow_range
    Instance.etag = '"pinned-object"'
    Instance.range_calls = 0
    Instance.bytes_served = 0
    Instance.broken_etag_after = broken_etag_after

    httpd = ThreadingHTTPServer(('127.0.0.1', 0), Instance)
    worker = threading.Thread(target=httpd.serve_forever, daemon=True)
    worker.start()
    try:
        yield f'http://127.0.0.1:{httpd.server_port}/fake.zip', Instance
    finally:
        httpd.shutdown()
        worker.join(timeout=2)
        httpd.server_close()


class HTTPRangeTests(unittest.TestCase):
    def test_content_range_parses(self):
        self.assertEqual(_parse_content_range('bytes 3-5/32'), (3, 5, 32))

    def test_content_range_rejects_ambiguous(self):
        for value in ('bytes */32', 'items 1-4/33', 'bytes 1-3/*', 'bytes 1-3/16\nBAD'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                _parse_content_range(value)

    def test_https_only_by_default(self):
        with self.assertRaises(ValueError):
            _safe_url('http://127.0.0.1/fake.zip')
        _safe_url('http://127.0.0.1/fake.zip', localhost_for_tests=True)

    def test_range_reader_seek_and_slice(self):
        archive = make_zip({'58012_quadrangulation_smooth.obj': b'v 1 2 3\nf 1 2 3 4\n'})
        with server(archive) as (url, srv):
            with HTTPRangeFile(url, chunk=4096, allow_http_localhost=True) as reader:
                self.assertEqual(reader.seek(-22, 2), len(archive) - 22)
                self.assertEqual(reader.read(22), archive[-22:])
                self.assertEqual(reader.seek(0), 0)
                self.assertEqual(reader.read(30), archive[:30])
                self.assertEqual(reader.length, len(archive))
            self.assertGreaterEqual(srv.range_calls, 2)

    def test_no_range_server_fails_closed(self):
        archive = make_zip({'58012.obj': b'a' * 100})
        with server(archive, allow_range=False) as (url, _):
            with self.assertRaisesRegex(ValueError, 'HTTP 206 required'):
                HTTPRangeFile(url, allow_http_localhost=True)

    def test_mutated_etag_is_rejected(self):
        archive = make_zip({'58012.obj': b'x' * 10000})
        with server(archive, broken_etag_after=1) as (url, _):
            with self.assertRaisesRegex(ValueError, 'ETag changed'):
                with HTTPRangeFile(url, chunk=4096, allow_http_localhost=True) as reader:
                    reader.read(40)

    def test_byte_budget_is_hard_limit(self):
        archive = make_zip({'58012.obj': b'abc' * 1000})
        with server(archive) as (url, _):
            with HTTPRangeFile(url, chunk=4096, max_transfer=100, allow_http_localhost=True) as reader:
                with self.assertRaisesRegex(ValueError, 'budget'):
                    reader.read(50)

    def test_reject_traversal(self):
        self.assertFalse(_safe_member('../58012.obj'))
        self.assertFalse(_safe_member('/58012.obj'))
        self.assertFalse(_safe_member('folder\\58012.obj'))
        self.assertTrue(_safe_member('quad/58012.obj'))

    def test_id_boundaries(self):
        with zipfile.ZipFile(io.BytesIO(make_zip({
            '58012_accepted.obj': b'aaa', '580123.obj': b'bbb',
            'xx/1580123.obj': b'ccc', 'x_58012_smooth.npz': b'npz',
            'extras/58012_notes.txt': b'notes'
        }))) as zf:
            self.assertEqual({z.filename for z in select_members(zf.infolist(), 58012)},
                             {'58012_accepted.obj', 'x_58012_smooth.npz'})

    def test_list_does_not_extract_and_reduces_transfer(self):
        # The filler has mixed deterministic-looking bytes to limit compression ratio.
        filler = hashlib.shake_256(b"range-download-fixture").digest(4 * 1024 * 1024)
        archive = make_zip({'misc/filler.bin': filler,
                            'quad/58012_quadrangulation_smooth.obj': b'v 0 0 0\nf 1 2 3 4\n'})
        with server(archive) as (url, _):
            result = acquire(url, 58012, output_dir=None, list_only=True,
                             chunk=4096, allow_http_localhost=True)
            self.assertEqual(result['status'], 'REMOTE_ZIP_CENTRAL_DIRECTORY_INSPECTED_ONLY')
            self.assertEqual(len(result['candidate_members']), 1)
            self.assertLess(result['bytes_transferred'], len(archive) // 8)
            self.assertGreater(len(archive), 4 * 1024 * 1024)

    def test_select_exact_member_and_hash(self):
        archive = make_zip({'other.obj': b'foo',
                            'models/58012_quadrangulation.obj': b'v 1 0 0\nf 1 2 3 4\n',
                            'models/58012_quadrangulation_smooth.obj': b'v 0 1 0\nf 1 2 3 4\n'})
        with tempfile.TemporaryDirectory() as directory, server(archive) as (url, _):
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                acquire(url, 58012, output_dir=Path(directory),
                        allow_http_localhost=True)
            name = 'models/58012_quadrangulation_smooth.obj'
            result = acquire(url, 58012, member=name, output_dir=Path(directory),
                             allow_http_localhost=True)
            self.assertEqual(result['status'], 'ONE_ORIGINAL_OUTPUT_MEMBER_EXTRACTED_NOT_PAIR_VERIFIED')
            self.assertEqual(result['selected_member'], name)
            self.assertTrue(Path(result['output_local_file']).exists())
            self.assertFalse(result['source_output_pair_verified'])
            with self.assertRaisesRegex(ValueError, 'already exists'):
                acquire(url, 58012, member=name, output_dir=Path(directory),
                        allow_http_localhost=True)

    def test_zip_bomb_declared_size_rejects(self):
        archive = make_zip({'58012_quadrangulation.obj': b'a' * (2 * 1024 * 1024)})
        with tempfile.TemporaryDirectory() as directory, server(archive) as (url, _):
            with self.assertRaisesRegex(ValueError, 'compression ratio'):
                acquire(url, 58012, output_dir=Path(directory),
                        allow_http_localhost=True)

    def test_bad_zip_rejected(self):
        with server(b'not actually a ZIP but sufficiently long') as (url, _):
            with self.assertRaises(zipfile.BadZipFile):
                acquire(url, 58012, output_dir=None, list_only=True,
                        allow_http_localhost=True)

    def test_no_id_match_fails_closed(self):
        archive = make_zip({'other_99999.obj': b'abc'})
        with tempfile.TemporaryDirectory() as directory, server(archive) as (url, _):
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                acquire(url, 58012, output_dir=Path(directory),
                        allow_http_localhost=True)


if __name__ == '__main__':
    unittest.main()
