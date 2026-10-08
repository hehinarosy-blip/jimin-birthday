from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import webbrowser
import os
import json
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


class JiminHandler(SimpleHTTPRequestHandler):

    def send_json(self, status, data):

        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


    def supabase_request(self, method, query="", payload=None):

        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError("Supabase environment variables are missing")

        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
        }
        body = None

        if payload is not None:
            headers["Content-Type"] = "application/json"
            headers["Prefer"] = "return=representation"
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        request = Request(
            f"{SUPABASE_URL}/rest/v1/wishes{query}",
            data=body,
            headers=headers,
            method=method
        )

        with urlopen(request, timeout=20) as response:
            response_body = response.read()

        return json.loads(response_body) if response_body else []


    def fetch_wishes(self):

        rows = self.supabase_request(
            "GET",
            "?select=message&order=id.asc"
        )

        return [
            row["message"]
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("message"), str)
        ]


    def do_GET(self):

        if urlsplit(self.path).path == "/api/wishes":
            try:
                wishes = self.fetch_wishes()
            except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError):
                self.send_json(503, {"error": "Messages are temporarily unavailable"})
                return

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
            self.supabase_request(
                "POST",
                payload=[{"message": wish} for wish in additions]
            )
            wishes = self.fetch_wishes()
        except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError):
            self.send_json(503, {"error": "Could not save messages"})
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