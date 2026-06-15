"""Main entry point for the unified document and font optimization tool suite."""

import argparse
import sys

# Modular file structural references
import fitz_wrapper
import pdf_optimizer
import font_subsetter
import pipeline_workflow


def main():
    """Parse command-line arguments and dispatch to the appropriate utility function."""
    parser = argparse.ArgumentParser(
        description="Unified Document & Font Optimization Tool suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Target Utility"
    )

    # 1. PyMuPDF CLI Wrapper
    mupdf_p = subparsers.add_parser(
        "pdf-cli", help="Direct PyMuPDF/MuPDF native command wrapper tools"
    )
    mupdf_p.add_argument("action", choices=["clean", "info"], help="Action to execute")
    mupdf_p.add_argument("pdf_path", type=str, help="Target PDF filename path")

    # 2. Aggressive PDF Compressor
    compress_p = subparsers.add_parser(
        "pdf-compress",
        help="Aggressive stream compression & garbage collection algorithms",
    )
    compress_p.add_argument("pdf_path", type=str, help="Source PDF filepath")
    compress_p.add_argument("-o", "--output", type=str, help="Custom export location")

    # 3. FontTools Subset Wrapper
    subset_p = subparsers.add_parser(
        "font-subset", help="Raw CLI wrapper shortcut targeting font subsetting tables"
    )
    subset_p.add_argument(
        "font_path", type=str, help="Source font filepath (.ttf or .otf)"
    )
    subset_p.add_argument(
        "--chars", type=str, help="Literal text character string to retain"
    )
    subset_p.add_argument(
        "--unicodes", type=str, help="Target Unicode numeric ranges (e.g., U+0020-007E)"
    )

    # 4. Multi-Library Pipeline Workflow
    pipe_p = subparsers.add_parser(
        "pipeline",
        help="Advanced multi-pass: extract text character lists via fitz and subset via fontTools",
    )
    pipe_p.add_argument("epub_path", type=str, help="Source book template file (.epub)")
    pipe_p.add_argument("font_path", type=str, help="Source base font file template")

    args = parser.parse_args()

    try:
        if args.command == "pdf-cli":
            fitz_wrapper.run(args.action, args.pdf_path)
        elif args.command == "pdf-compress":
            pdf_optimizer.run(args.pdf_path, args.output)
        elif args.command == "font-subset":
            font_subsetter.run(args.font_path, args.chars, args.unicodes)
        elif args.command == "pipeline":
            pipeline_workflow.run(args.epub_path, args.font_path)
    except Exception as e:
        print(f"\n[❌ RUNTIME FAULT] Pipeline stopped: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
