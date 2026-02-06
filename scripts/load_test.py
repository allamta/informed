#!/usr/bin/env python3

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any
import uuid

DEFAULT_BACKEND_URL = "http://localhost:9030/api"
DEFAULT_LOOPS = 2
TEST_DATA_DIR = Path(__file__).parent.parent / "test-data"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def get_image_files(directory: Path) -> list[Path]:
    files = []
    for ext in IMAGE_EXTENSIONS:
        files.extend(directory.glob(f"*{ext}"))
        files.extend(directory.glob(f"*{ext.upper()}"))
    return sorted(files)


def create_multipart_form_data(image_path: Path) -> tuple[bytes, str]:
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"

    with open(image_path, "rb") as f:
        file_content = f.read()

    ext = image_path.suffix.lower()
    content_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".webp": "image/webp",
    }
    file_content_type = content_type_map.get(ext, "application/octet-stream")

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{image_path.name}"\r\n'
        f"Content-Type: {file_content_type}\r\n"
        f"\r\n"
    ).encode("utf-8")

    body += file_content
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")

    content_type = f"multipart/form-data; boundary={boundary}"

    return body, content_type


def analyze_image(backend_url: str, image_path: Path, timeout: int = 120) -> dict[str, Any]:
    url = f"{backend_url}/analyze"

    body, content_type = create_multipart_form_data(image_path)

    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": content_type},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def run_load_test(backend_url: str, loops: int) -> None:
    print("Load Test Configuration")
    print("=======================")
    print(f"Backend URL: {backend_url}")
    print(f"Test data:   {TEST_DATA_DIR}")
    print(f"Loops:       {loops}")
    print()

    image_files = get_image_files(TEST_DATA_DIR)

    if not image_files:
        print(f"ERROR: No image files found in {TEST_DATA_DIR}")
        sys.exit(1)

    print(f"Found {len(image_files)} images:")
    for img in image_files:
        print(f"  - {img.name}")
    print()

    total_requests = 0
    successful_requests = 0
    failed_requests = 0
    total_time = 0.0

    print("Starting load test...")
    print("-" * 60)

    for loop in range(1, loops + 1):
        print(f"\n[Loop {loop}/{loops}]")

        for image_path in image_files:
            total_requests += 1

            try:
                start_time = time.time()
                result = analyze_image(backend_url, image_path)
                elapsed = time.time() - start_time
                total_time += elapsed
                successful_requests += 1

                ingredient_count = len(result.get("assessments", {}))

                print(f"  OK   {image_path.name:<35} {elapsed:>6.2f}s  ({ingredient_count} ingredients)")

            except urllib.error.HTTPError as e:
                failed_requests += 1
                print(f"  FAIL {image_path.name:<35} HTTP {e.code}: {e.reason[:30]}")
            except urllib.error.URLError as e:
                failed_requests += 1
                print(f"  FAIL {image_path.name:<35} {str(e.reason)[:40]}")
            except Exception as e:
                failed_requests += 1
                print(f"  ERR  {image_path.name:<35} {str(e)[:40]}")

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total requests:      {total_requests}")
    print(f"Successful:          {successful_requests}")
    print(f"Failed:              {failed_requests}")
    if total_requests > 0:
        print(f"Success rate:        {(successful_requests/total_requests*100):.1f}%")
    print(f"Total time:          {total_time:.2f}s")
    if successful_requests > 0:
        print(f"Avg response time:   {(total_time/successful_requests):.2f}s")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Load test script for the Informed backend API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--loops", "-l",
        type=int,
        default=DEFAULT_LOOPS,
        help=f"Number of times to loop through all images (default: {DEFAULT_LOOPS})"
    )
    parser.add_argument(
        "--backend-url", "-u",
        type=str,
        default=DEFAULT_BACKEND_URL,
        help=f"Backend API URL (default: {DEFAULT_BACKEND_URL})"
    )

    args = parser.parse_args()

    run_load_test(backend_url=args.backend_url, loops=args.loops)


if __name__ == "__main__":
    main()
