import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import webbrowser

HOST = "127.0.0.1"
PORT = 8000
ROOT_DIR = Path(__file__).resolve().parent


class StaticHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        route_map = {
            "/": "/index.html",
            "/index": "/index.html",
            "/posts": "/posts.html",
            "/post": "/post_detail.html",
        }

        if parsed.path.startswith("/posts/"):
            user_id = parsed.path[len("/posts/") :].strip("/")
            if user_id.isdigit():
                self.path = f"/posts.html?userId={user_id}"
                return super().do_GET()

        if parsed.path.startswith("/post/"):
            post_id = parsed.path[len("/post/") :].strip("/")
            if post_id.isdigit():
                self.path = f"/post_detail.html?id={post_id}"
                return super().do_GET()

        if parsed.path in route_map:
            target = route_map[parsed.path]
            if parsed.query:
                target = f"{target}?{parsed.query}"
            self.path = target

        return super().do_GET()


def build_open_url(page: str, post_id: int, user_id: int, host: str, port: int) -> str:
    if page == "index":
        return f"http://{host}:{port}/"

    if page == "posts":
        return f"http://{host}:{port}/posts/{user_id}"

    return f"http://{host}:{port}/post/{post_id}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve this folder and open albums, user posts, or post detail."
    )
    parser.add_argument(
        "--page",
        choices=["index", "posts", "detail"],
        default="index",
        help="Which page to open in the browser.",
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=1,
        help="User ID used when --page posts is selected.",
    )
    parser.add_argument(
        "--post-id",
        type=int,
        default=1,
        help="Post ID used when --page detail is selected.",
    )
    parser.add_argument(
        "--host",
        default=HOST,
        help="Host/interface for the local server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=PORT,
        help="Port for the local server.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.post_id < 1 or args.user_id < 1:
        raise ValueError("--post-id and --user-id must be positive integers.")

    server = ThreadingHTTPServer((args.host, args.port), StaticHandler)
    url = build_open_url(args.page, args.post_id, args.user_id, args.host, args.port)

    print(f"Serving {ROOT_DIR} at {url}")
    print("Press Ctrl+C to stop the server.")

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
