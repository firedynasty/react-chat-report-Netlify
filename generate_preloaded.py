#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate preloaded reports JSON files for the React app with folder-based categories.

This script scans ./preloaded_reports/ for FOLDERS containing .txt and .md files,
and generates JSON files in ./public/preloaded/ that the React app can fetch.

Each subfolder becomes a category, with its own JSON file.

Usage:
    python generate_preloaded.py

Input structure:
    ./preloaded_reports/
    ├── chess/
    │   ├── openings.txt
    │   └── tactics.md
    ├── basketball/
    │   ├── plays.txt
    │   └── drills.txt

Output:
    ./public/preloaded/index.json - List of available categories (folders)
    ./public/preloaded/<category_name>.json - Contents of each category's files
"""

import os
import json
import argparse

def process_file(file_path):
    """Read a file and return its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"  Warning: Could not read {file_path}: {e}")
        return None

def generate_preloaded_reports(input_dir='./preloaded_reports', output_dir='./public/preloaded'):
    """Generate JSON files from preloaded report folders (subfolders become categories)."""

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Check input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    print(f"Processing categories in: {input_dir}")

    # Get all subdirectories (each becomes a category)
    entries = os.listdir(input_dir)
    folders = [f for f in entries if os.path.isdir(os.path.join(input_dir, f)) and not f.startswith('.')]
    folders.sort(key=lambda x: x.lower())

    if len(folders) == 0:
        print("  No category folders found. Create subfolders with .txt/.md files.")
        return

    categories = []

    for folder_name in folders:
        folder_path = os.path.join(input_dir, folder_name)
        print(f"\n📁 Category: {folder_name}")

        # Get all .txt and .md files in this folder
        files_in_folder = os.listdir(folder_path)
        text_files = [f for f in files_in_folder
                      if (f.endswith('.txt') or f.endswith('.md'))
                      and os.path.isfile(os.path.join(folder_path, f))
                      and not f.startswith('.')]
        text_files.sort(key=lambda x: x.lower())

        if len(text_files) == 0:
            print(f"  (no .txt or .md files)")
            continue

        # Read all files in this category
        files_data = {}
        for filename in text_files:
            file_path = os.path.join(folder_path, filename)
            content = process_file(file_path)
            if content is not None:
                files_data[filename] = content
                print(f"  - {filename} ({len(content):,} chars)")

        if len(files_data) > 0:
            # Save category JSON file
            category_json_path = os.path.join(output_dir, f"{folder_name}.json")
            with open(category_json_path, 'w', encoding='utf-8') as f:
                json.dump(files_data, f, ensure_ascii=False, indent=2)
            print(f"  → Saved to {category_json_path}")

            # Add to categories index
            categories.append({
                "name": folder_name,
                "fileCount": len(files_data),
                "files": list(files_data.keys())
            })

    # Save index.json with list of categories
    index_path = os.path.join(output_dir, 'index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump({"categories": categories}, f, ensure_ascii=False, indent=2)

    total_files = sum(c["fileCount"] for c in categories)
    print(f"\n✅ Generated index.json with {len(categories)} category(s), {total_files} total file(s)")
    print(f"📁 Output directory: {output_dir}")

    return categories

def main():
    parser = argparse.ArgumentParser(description='Generate preloaded reports JSON files with folder categories.')
    parser.add_argument('input_dir', nargs='?', default='./preloaded_reports',
                        help='Input directory containing category folders (default: ./preloaded_reports)')
    parser.add_argument('-o', '--output', default='./public/preloaded',
                        help='Output directory for JSON files (default: ./public/preloaded)')

    args = parser.parse_args()

    generate_preloaded_reports(args.input_dir, args.output)

if __name__ == "__main__":
    main()
