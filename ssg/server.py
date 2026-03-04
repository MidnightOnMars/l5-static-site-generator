"""
Simple development server with polling rebuild.
"""

import http.server
import socketserver
import threading
import time
from pathlib import Path
from . import build

def _watch_and_rebuild(config_path: str = None, interval: float = 1.0):
    """
    Poll the content and template directories for changes.
    If any file's modification time changes, trigger a rebuild.
    """
    cfg = build.load_config(config_path) if hasattr(build, "load_config") else None
    if cfg is None:
        from .config import load_config
        cfg = load_config(config_path)

    content_dir = Path(cfg["content_dir"])
    template_dir = Path(cfg["template_dir"])

    # Record initial mtimes
    def snapshot():
        mtimes = {}
        for p in content_dir.rglob("*"):
            if p.is_file():
                mtimes[p] = p.stat().st_mtime
        for p in template_dir.rglob("*"):
            if p.is_file():
                mtimes[p] = p.stat().st_mtime
        return mtimes

    last_snapshot = snapshot()
    while True:
        time.sleep(interval)
        current = snapshot()
        if current != last_snapshot:
            try:
                build.build(config_path)
                print("[ssg] Rebuilt site due to changes.")
            except Exception as e:
                print(f"[ssg] Rebuild failed: {e}")
            last_snapshot = current

def start_server(host: str = "localhost", port: int = 8000, config_path: str = None):
    """
    Start an HTTP server serving the output directory and watch for changes.
    """
    cfg = build.load_config(config_path) if hasattr(build, "load_config") else None
    if cfg is None:
        from .config import load_config
        cfg = load_config(config_path)

    output_dir = Path(cfg["output_dir"])
    if not output_dir.is_dir():
        # Ensure at least one build so the directory exists
        build.build(config_path)

    handler = http.server.SimpleHTTPRequestHandler
    handler.directory = str(output_dir)

    httpd = socketserver.TCPServer((host, port), handler)

    watcher = threading.Thread(target=_watch_and_rebuild, args=(config_path,), daemon=True)
    watcher.start()

    print(f"[ssg] Serving {output_dir} at http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[ssg] Server stopped.")
    finally:
        httpd.server_close()