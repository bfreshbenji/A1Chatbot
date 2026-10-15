#!/usr/bin/env python3
"""YouTube link -> MP3, as a tiny local web app or a command-line tool.

    python app.py                 # opens http://127.0.0.1:8765 in your browser
    python app.py URL [URL ...]   # downloads MP3s into ./downloads

Needs yt-dlp (pip install yt-dlp) and ffmpeg on your PATH.
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

try:
    import yt_dlp
except ImportError:
    sys.exit("yt-dlp is missing. Install it with:  pip install yt-dlp")

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8765"))
BITRATES = {"128", "192", "256", "320"}


def download_mp3(url, out_dir, bitrate="192"):
    """Download one video's audio as an MP3 into out_dir and return its path."""
    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(out_dir) / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": False,
        "windowsfilenames": True,
        "writethumbnail": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": bitrate},
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base = Path(ydl.prepare_filename(info)).with_suffix(".mp3")
    if not base.exists():
        raise RuntimeError("Conversion finished but no MP3 was produced.")
    return base


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("  " + fmt % args + "\n")

    def _json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            return self._json(404, {"error": "Not found"})
        body = (HERE / "index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/convert":
            return self._json(404, {"error": "Not found"})
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self._json(400, {"error": "Bad request."})
        url = str(data.get("url", "")).strip()
        bitrate = str(data.get("bitrate", "192"))
        if not url.startswith(("http://", "https://")):
            return self._json(400, {"error": "Paste a full YouTube link (https://…)."})
        if bitrate not in BITRATES:
            bitrate = "192"

        tmp = tempfile.mkdtemp(prefix="yt-mp3-")
        try:
            mp3 = download_mp3(url, tmp, bitrate)
            size = mp3.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(mp3.name)}")
            self.end_headers()
            with open(mp3, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
        except yt_dlp.utils.DownloadError as e:
            msg = str(e).replace("ERROR: ", "").strip()
            self._json(422, {"error": msg or "Couldn't download that video."})
        except Exception as e:  # noqa: BLE001 - surface any failure to the page
            self._json(500, {"error": str(e)})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is missing. Install it (e.g. `brew install ffmpeg`, `winget install ffmpeg`, `apt install ffmpeg`).")

    urls = sys.argv[1:]
    if urls:
        out = Path.cwd() / "downloads"
        out.mkdir(exist_ok=True)
        for url in urls:
            print(f"Downloading {url} …")
            try:
                print(f"  saved {download_mp3(url, out)}")
            except Exception as e:  # noqa: BLE001
                print(f"  failed: {e}")
        return

    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    link = f"http://127.0.0.1:{PORT}"
    print(f"YouTube → MP3 running at {link}  (Ctrl+C to stop)")
    threading.Timer(0.5, lambda: webbrowser.open(link)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
