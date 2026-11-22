#!/usr/bin/env python3
"""Selectively inspect/download a QuadWild ZIP member using strictly verified HTTP ranges.

No data is silently repaired. HTTP 200 full-body responses fail closed. The user
must independently verify permissions and prove a QuadWild source/output pair.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

DEFAULT_ARCHIVE = 'https://www.quadmesh.cloud/thingi10k-quad-dataset.zip'
DEFAULT_CHUNK = 256 * 1024
MAX_REQUESTS = 1024
MAX_BYTES_TRANSFERRED = 80 * 1024 * 1024
MAX_ENTRIES = 50_000
MAX_MEMBER_BYTES = 200 * 1024 * 1024
ALLOWED_SUFFIXES = {'.obj', '.npz'}


def _parse_content_range(raw: str) -> tuple[int, int, int]:
    match = re.fullmatch(r'bytes\s+(\d+)-(\d+)/(\d+)', raw.strip(), flags=re.I)
    if not match:
        raise ValueError('Missing/invalid HTTP Content-Range')
    return tuple(map(int, match.groups()))


def _safe_url(url: str, localhost_for_tests: bool = False) -> None:
    url_parts = urllib.parse.urlsplit(url)
    if url_parts.scheme == 'https' and url_parts.hostname:
        return
    if (localhost_for_tests and url_parts.scheme == 'http' and
            url_parts.hostname in {'127.0.0.1', 'localhost'}):
        return
    raise ValueError('Only HTTPS archive URLs are allowed')


class HTTPRangeFile(io.RawIOBase):
    """Bounded, cached and seekable HTTP range reader for Python's ZIP64 parser."""

    def __init__(self, url: str, *, chunk: int = DEFAULT_CHUNK,
                 max_requests: int = MAX_REQUESTS,
                 max_transfer: int = MAX_BYTES_TRANSFERRED,
                 timeout: int = 25, allow_http_localhost: bool = False):
        super().__init__()
        _safe_url(url, allow_http_localhost)
        if not 4096 <= chunk <= (4 << 20):
            raise ValueError('Chunk size must be between 4096 bytes and 4 MiB')
        self.url = url
        self.allow_http_localhost = allow_http_localhost
        self.chunk = chunk
        self.max_requests = max_requests
        self.max_transfer = max_transfer
        self.timeout = timeout
        self.requests = 0
        self.transferred = 0
        self.cache: collections.OrderedDict[int, bytes] = collections.OrderedDict()
        self.cache_limit = 8
        self.etag = None
        self.last_modified = None
        # Verify that the server actually implements RFC 7233 byte ranges.
        data, headers = self._fetch_raw(0, 0, initial=True)
        if len(data) != 1:
            raise ValueError('Range probe returned an unexpected body')
        a, b, total = _parse_content_range(headers.get('Content-Range', ''))
        if (a, b) != (0, 0) or total < 22 or total > (1 << 41):
            raise ValueError('Malformed or unreasonable remote archive length')
        self.length = total
        self.etag = headers.get('ETag')
        self.last_modified = headers.get('Last-Modified')
        self.position = 0

    def _fetch_raw(self, start: int, end: int, *, initial: bool = False):
        if self.requests >= self.max_requests:
            raise ValueError('HTTP range request budget exceeded')
        if end - start + 1 + self.transferred > self.max_transfer:
            raise ValueError('HTTP transfer budget exceeded')
        headers = {'Range': f'bytes={start}-{end}', 'Accept-Encoding': 'identity',
                   'User-Agent': 'apmesh-research-range-auditor/1.0'}
        if not initial and self.etag and not self.etag.startswith('W/'):
            headers['If-Range'] = self.etag
        elif not initial and self.last_modified:
            headers['If-Range'] = self.last_modified
        req = urllib.request.Request(self.url, headers=headers, method='GET')
        self.requests += 1
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                _safe_url(response.url, self.allow_http_localhost)
                if response.status != 206:
                    raise ValueError('Server did not honor Range (HTTP 206 required)')
                cr = _parse_content_range(response.headers.get('Content-Range', ''))
                if cr[0] != start or cr[1] != end or (not initial and cr[2] != self.length):
                    raise ValueError('Remote archive Content-Range inconsistent')
                if not initial and self.etag and response.headers.get('ETag') != self.etag:
                    raise ValueError('Remote archive ETag changed during acquisition')
                if (not initial and self.last_modified and
                        response.headers.get('Last-Modified') != self.last_modified):
                    raise ValueError('Remote archive Last-Modified changed')
                size = end - start + 1
                data = response.read(size + 1)
                if len(data) != size:
                    raise ValueError('Server returned wrong number of bytes for range')
                self.transferred += len(data)
                return data, response.headers
        except urllib.error.HTTPError as error:
            raise ValueError(f'Range request failed with HTTP {error.code}') from error

    def _chunk(self, index: int) -> bytes:
        if index in self.cache:
            self.cache.move_to_end(index)
            return self.cache[index]
        start = index * self.chunk
        end = min(self.length, start + self.chunk) - 1
        part, _ = self._fetch_raw(start, end)
        self.cache[index] = part
        if len(self.cache) > self.cache_limit:
            self.cache.popitem(last=False)
        return part

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if self.closed:
            raise ValueError('Closed remote reader')
        if whence == os.SEEK_SET:
            position = offset
        elif whence == os.SEEK_CUR:
            position = self.position + offset
        elif whence == os.SEEK_END:
            position = self.length + offset
        else:
            raise ValueError('Invalid seek direction')
        if position < 0 or position > self.length:
            raise ValueError('Remote archive seek outside source bounds')
        self.position = position
        return position

    def tell(self) -> int:
        return self.position

    def read(self, size: int = -1) -> bytes:
        if self.closed:
            raise ValueError('Closed remote reader')
        if size is None or size < 0:
            size = self.length - self.position
        size = min(size, self.length - self.position)
        out = bytearray()
        while size:
            i = self.position // self.chunk
            start = self.position % self.chunk
            piece = self._chunk(i)
            take = min(size, len(piece) - start)
            if take <= 0:
                raise ValueError('Unexpected zero progress reading ZIP')
            out += piece[start:start + take]
            self.position += take
            size -= take
        return bytes(out)


def _safe_member(name: str) -> bool:
    """Reject escaping paths, absolute paths, backslashes and control characters."""
    p = PurePosixPath(name)
    return (bool(name) and not name.startswith('/') and '\\' not in name and
            all(x not in {'.', '..'} for x in name.split('/')) and
            all(ord(ch) >= 32 for ch in name) and not p.is_absolute())


def select_members(items: list[zipfile.ZipInfo], model_id: int,
                   *, allow_any_extension: bool = False) -> list[zipfile.ZipInfo]:
    if model_id < 1:
        raise ValueError('Invalid Thingi10K file ID')
    # Avoid accidentally matching Thingiverse ID 580123 or an unrelated numeric code.
    model_pattern = re.compile(r'(?<![0-9])' + str(model_id) + r'(?![0-9])')
    return [m for m in items if not m.is_dir() and _safe_member(m.filename)
            and model_pattern.search(m.filename)
            and (allow_any_extension or PurePosixPath(m.filename).suffix.lower() in ALLOWED_SUFFIXES)]


def acquire(url: str, file_id: int, *, output_dir: Path | None,
            member: str | None = None, max_transfer: int = MAX_BYTES_TRANSFERRED,
            chunk: int = DEFAULT_CHUNK, allow_http_localhost: bool = False,
            list_only: bool = False) -> dict:
    """Inspect remote ZIP index, optionally extract one original member to a private path."""
    with HTTPRangeFile(url, chunk=chunk, max_transfer=max_transfer,
                       allow_http_localhost=allow_http_localhost) as reader:
        with zipfile.ZipFile(reader, 'r', allowZip64=True) as zf:
            entries = zf.infolist()
            if len(entries) > MAX_ENTRIES:
                raise ValueError('Too many archive entries')
            candidates = select_members(entries, file_id, allow_any_extension=list_only)
            base = {
                'schema': 'apmesh-quadwild-f19-range-index-v1',
                'status': 'REMOTE_ZIP_CENTRAL_DIRECTORY_INSPECTED_ONLY',
                'original_thin_archive_url': url,
                'remote_archive_length': reader.length,
                'remote_archive_etag': reader.etag,
                'remote_archive_last_modified': reader.last_modified,
                'full_remote_archive_sha256_verified': False,
                'thingi10k_file_id': file_id,
                'candidate_members': [{'name': i.filename, 'zip_uncompressed_bytes': i.file_size,
                                      'zip_compressed_bytes': i.compress_size, 'zip_crc32': i.CRC}
                                     for i in candidates],
                'matched_published_quad_output': False,
                'source_output_pair_verified': False,
                'apmesh_executed': False
            }
            if list_only:
                base['bytes_transferred'] = reader.transferred
                base['range_requests'] = reader.requests
                return base
            if member is not None:
                matches = [i for i in candidates if i.filename == member]
            else:
                matches = candidates
            if len(matches) != 1:
                raise ValueError('Expected exactly one OBJ/NPZ member for ID; use --list-model and --member to disambiguate')
            target = matches[0]
            if target.file_size < 1 or target.file_size > MAX_MEMBER_BYTES:
                raise ValueError('Selected member size exceeds configured limits')
            if target.compress_size == 0 or target.file_size > max(1000 * target.compress_size, 1 << 20):
                raise ValueError('Suspicious ZIP compression ratio')
            if output_dir is None or not output_dir.is_dir():
                raise ValueError('Specify an existing private output directory')
            suffix = PurePosixPath(target.filename).suffix.lower()
            source_stem = PurePosixPath(target.filename).stem
            safe_stem = re.sub('[^a-zA-Z0-9_.-]+', '_', source_stem)[:75]
            if not safe_stem.startswith(str(file_id)):
                safe_stem = str(file_id) + '_' + safe_stem
            output = output_dir / f'{safe_stem}{suffix}'
            if output.exists():
                raise ValueError('Output already exists; refusing overwrite')
            digest = hashlib.sha256()
            try:
                with output.open('xb') as f, zf.open(target, 'r') as source:
                    received = 0
                    while True:
                        piece = source.read(1 << 20)
                        if not piece:
                            break
                        received += len(piece)
                        if received > MAX_MEMBER_BYTES or received > target.file_size:
                            raise ValueError('Member decompression exceeded predeclared size')
                        f.write(piece)
                        digest.update(piece)
                if received != target.file_size:
                    raise ValueError('Extracted member length mismatch')
            except Exception:
                output.unlink(missing_ok=True)
                raise
            base.update({
                'status': 'ONE_ORIGINAL_OUTPUT_MEMBER_EXTRACTED_NOT_PAIR_VERIFIED',
                'selected_member': target.filename,
                'output_local_file': str(output),
                'selected_member_original_sha256': digest.hexdigest(),
                'selected_member_original_bytes': received,
                'bytes_transferred': reader.transferred,
                'range_requests': reader.requests,
            })
            return base


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--url', default=DEFAULT_ARCHIVE)
    ap.add_argument('--model-id', type=int, required=True)
    ap.add_argument('--list-model', action='store_true')
    ap.add_argument('--member', help='Exact internal archive path; required if ID has multiple outputs')
    ap.add_argument('--output-dir', type=Path)
    ap.add_argument('--receipt', type=Path)
    ap.add_argument('--max-transfer-mib', type=int, default=80)
    ap.add_argument('--chunk-kib', type=int, default=256)
    args = ap.parse_args(argv)
    if not args.list_model and (args.output_dir is None or args.receipt is None):
        ap.error('Output directory and JSON receipt path are mandatory for extraction')
    if args.max_transfer_mib < 1 or args.max_transfer_mib > 1024:
        ap.error('Transfer MiB must be in range [1, 1024]')
    result = acquire(args.url, args.model_id, output_dir=args.output_dir, member=args.member,
                     max_transfer=args.max_transfer_mib * (1 << 20),
                     chunk=args.chunk_kib * 1024, list_only=args.list_model)
    if args.receipt is not None:
        with args.receipt.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, zipfile.BadZipFile, OSError) as exc:
        print(f'F19 source gate BLOCKED: {exc}', file=sys.stderr)
        raise SystemExit(2)
