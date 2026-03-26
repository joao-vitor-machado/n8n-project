"""Dev server: PYTHONPATH=src python -m api"""

from wsgiref.simple_server import make_server

from main import app


def main() -> None:
    host = "0.0.0.0"
    port = 8000
    with make_server(host, port, app) as httpd:
        print(f"Serving on http://{host}:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
