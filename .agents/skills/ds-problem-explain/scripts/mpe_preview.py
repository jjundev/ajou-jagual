"""Serve staged files at their eventual publication URLs on loopback."""
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import quote, unquote, urlsplit

from mpe_assets import SHARED_ROOT, verify_shared_assets
from mpe_source import inside
from mpe_types import ExplainError


@contextmanager
def preview_server(artifacts_list, port=0):
    files, pages = {}, []
    for artifacts in artifacts_list:
        manifest = json.loads(artifacts.manifest.read_text(encoding='utf-8'))
        stage = artifacts.html.parent.resolve()
        repo = Path(manifest['repo']).resolve()
        destination = inside(Path(manifest['destination']), repo).relative_to(repo)
        if verify_shared_assets(repo, manifest):
            for name in manifest['shared_assets']['files']:
                path = SHARED_ROOT / name
                files['/' + path.as_posix()] = repo / path
        for file in artifacts.files:
            source = inside(file, stage)
            path = '/' + (destination / source.relative_to(stage)).as_posix()
            if path in files and files[path] != source:
                raise ExplainError(f'미리보기 경로 충돌: {path}')
            files[path] = source
        pages.append(quote('/' + (destination / artifacts.html.name).as_posix(), safe='/'))

    class PreviewHandler(SimpleHTTPRequestHandler):
        def send_head(self):
            if unquote(urlsplit(self.path).path) not in files:
                self.send_error(404)
                return None
            return super().send_head()

        def translate_path(self, path):
            return str(files[unquote(urlsplit(path).path)])

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def log_message(self, format, *args):
            pass

    with ThreadingHTTPServer(('127.0.0.1', port), PreviewHandler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server, pages
        finally:
            server.shutdown()
            thread.join()
