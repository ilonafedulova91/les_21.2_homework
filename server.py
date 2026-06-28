import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parent
CONTACTS_FILE = ROOT / "contacts.html"


def load_contacts_page() -> bytes:
    with open(CONTACTS_FILE, "r", encoding="utf-8") as file:
        return file.read().encode("utf-8")


def make_error_page(status_code: int, title: str, message: str) -> bytes:
    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow-sm">
          <div class="card-body p-4 text-center">
            <h1 class="display-4">{status_code}</h1>
            <h2 class="h4 mb-3">{title}</h2>
            <p class="text-muted mb-0">{message}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""
    return html.encode("utf-8")


class ContactsHandler(BaseHTTPRequestHandler):
    def _send_contacts_page(self) -> None:
        page = load_contacts_page()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def _send_error_page(self, status_code: int, title: str, message: str) -> None:
        page = make_error_page(status_code, title, message)
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def do_GET(self):
        if self.path == "/404":
            self._send_error_page(
                404, "Страница не найдена", "Запрошенный URL не существует."
            )
            return
        if self.path == "/500":
            self._send_error_page(
                500, "Ошибка сервера", "Возникла внутренняя ошибка сервера."
            )
            return
        self._send_contacts_page()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8", errors="replace")

        print(f"POST {self.path}")
        print(f"Headers: {dict(self.headers)}")
        print(f"Raw body: {body}")

        content_type = self.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                print("Parsed JSON:", json.loads(body))
            except json.JSONDecodeError:
                print("Parsed JSON: invalid payload")
        elif "application/x-www-form-urlencoded" in content_type:
            print("Parsed form data:", parse_qs(body))

        self._send_contacts_page()

    def log_message(self, format, *args):
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8000), ContactsHandler)
    print("Serving on http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
