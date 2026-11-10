"""Serve the reference player on loopback, with UTF-8 VTT and byte-range video."""

import argparse
import functools
import http.server
import re
import shutil
import webbrowser
from pathlib import Path


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".vtt": "text/vtt; charset=utf-8",
        ".html": "text/html; charset=utf-8",
        ".mp4": "video/mp4",
    }

    def log_message(self, format, *args):
        # The viewer console shows the local URL; individual range requests
        # are routine and do not need a console line for every seek.
        pass

    def send_head(self):
        self.remaining = None
        path = Path(self.translate_path(self.path))
        header = self.headers.get("Range")
        if not header or not path.is_file():
            return super().send_head()
        size = path.stat().st_size
        match = re.fullmatch(r"bytes=(\d+)-(\d*)", header)
        if not match:
            self.send_error(416)
            return None
        start = int(match[1])
        end = min(int(match[2]) if match[2] else size - 1, size - 1)
        if start > end or start >= size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return None
        stream = path.open("rb")
        stream.seek(start)
        self.remaining = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(path)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(self.remaining))
        self.end_headers()
        return stream

    def copyfile(self, source, outputfile):
        try:
            self.copy_range(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            # Browsers cancel the preceding range when the viewer seeks.
            pass

    def copy_range(self, source, outputfile):
        if self.remaining is None:
            return shutil.copyfileobj(source, outputfile)
        remaining = self.remaining
        while remaining:
            chunk = source.read(min(1024 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    handler = functools.partial(Handler, directory=str(args.directory.resolve()))
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        url = f"http://127.0.0.1:{server.server_port}/player.html"
        print(url, flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
