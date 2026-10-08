from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import webbrowser
import os
import json
import threading
from pathlib import Path
from urllib.parse import urlsplit


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
WISHES_FILE = Path(
    os.environ.get(
        "WISHES_FILE",
        Path(__file__).with_name("wishes.json")
    )
)
WISHES_LOCK = threading.Lock()


class JiminHandler(SimpleHTTPRequestHandler):

    def send_json(self, status, data):

        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


    def read_wishes(self):

        try:
            wishes = json.loads(WISHES_FILE.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, OSError):
            return []

        if not isinstance(wishes, list):
            return []

        return [wish for wish in wishes if isinstance(wish, str)]


    def do_GET(self):

        if urlsplit(self.path).path == "/api/wishes":
            with WISHES_LOCK:
                wishes = self.read_wishes()

            self.send_json(200, wishes)
            return

        super().do_GET()


    def do_POST(self):

        if urlsplit(self.path).path != "/api/wishes":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 1_000_000:
                self.send_json(413, {"error": "Invalid request size"})
                return

            payload = json.loads(self.rfile.read(content_length))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": "Invalid JSON"})
            return

        if not isinstance(payload, dict):
            self.send_json(400, {"error": "Invalid request"})
            return

        additions = payload.get("wishes", [])
        if not isinstance(additions, list):
            additions = []

        text = payload.get("text")
        if isinstance(text, str):
            additions.append(text)

        additions = [wish.strip() for wish in additions if isinstance(wish, str)]
        additions = [wish for wish in additions if wish]

        if not additions:
            self.send_json(400, {"error": "A message is required"})
            return

        try:
            with WISHES_LOCK:
                wishes = self.read_wishes()
                wishes.extend(additions)
                temporary_file = WISHES_FILE.with_suffix(".tmp")
                temporary_file.write_text(
                    json.dumps(wishes, ensure_ascii=False),
                    encoding="utf-8"
                )
                os.replace(temporary_file, WISHES_FILE)
        except OSError:
            self.send_json(500, {"error": "Could not save messages"})
            return

        self.send_json(201, wishes)

    def end_headers(self):
        self.send_header(
            "Cache-Control",
            "no-store, no-cache, must-revalidate"
        )

        self.send_header(
            "Pragma",
            "no-cache"
        )

        self.send_header(
            "Expires",
            "0"
        )

        super().end_headers()


def main():

    os.chdir(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    server = ThreadingHTTPServer(
        (HOST, PORT),
        JiminHandler
    )

    browser_host = "127.0.0.1" if HOST in ("0.0.0.0", "::") else HOST
    url = f"http://{browser_host}:{PORT}"

    print()
    print("=" * 55)
    print("       JIMIN BIRTHDAY WEBSITE")
    print("=" * 55)
    print()
    print(f"Website running at:")
    print(url)
    print()
    print("Press CTRL + C to stop the server.")
    print("=" * 55)
    print()

    if os.environ.get("OPEN_BROWSER", "1") != "0":
        webbrowser.open(url)

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print("Server stopped.")

        server.server_close()


if __name__ == "__main__":
    main()