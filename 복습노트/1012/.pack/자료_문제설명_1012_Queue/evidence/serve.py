from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote,urlsplit
import json
repo=Path.cwd();folder=Path(__file__).resolve().parent.parent
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  rel=unquote(urlsplit(path).path).lstrip('/');stage=folder/json.loads((folder/'stage.json').read_text())['stage'];prefix='복습노트/1012/'
  if rel.startswith(prefix):
   candidate=stage/rel[len(prefix):]
   if candidate.is_file():return str(candidate)
  return str(repo/rel)
 def do_GET(self):
  if urlsplit(self.path).path=='/favicon.ico':self.send_response(204);self.end_headers();return
  super().do_GET()
ThreadingHTTPServer(('127.0.0.1',18764),Handler).serve_forever()
