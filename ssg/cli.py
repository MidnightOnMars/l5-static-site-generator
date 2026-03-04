"""
Command‑line interface for the static site generator.
"""

import argparse
import sys
from . import build as ssg_build, clean as ssg_clean, server

def _add_common_arguments(parser):
    parser.add_argument(
        "-c", "--config", dest="config_path", default=None,
        help="Path to a YAML configuration file (default: site.yaml)."
    )

def main(argv=None):
    parser = argparse.ArgumentParser(prog="ssg", description="Static Site Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build subcommand
    build_parser = subparsers.add_parser("build", help="Build the site")
    _add_common_arguments(build_parser)

    # clean subcommand
    clean_parser = subparsers.add_parser("clean", help="Remove generated output")
    _add_common_arguments(clean_parser)

    # serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Start development server")
    _add_common_arguments(serve_parser)
    serve_parser.add_argument("--host", default="localhost", help="Host to bind (default: localhost)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")

    args = parser.parse_args(argv)

    try:
        if args.command == "build":
            summary = ssg_build(args.config_path)
            print(f"Built {summary['pages_built']} pages into {summary['output_dir']}")
        elif args.command == "clean":
            msg = ssg_clean(args.config_path)
            print(msg)
        elif args.command == "serve":
            server.start_server(host=args.host, port=args.port, config_path=args.config_path)
        else:
            parser.error(f"Unknown command: {args.command}")
    except Exception as exc:
        # User‑facing errors should not show tracebacks
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()