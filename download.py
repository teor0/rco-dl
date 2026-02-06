from playwright.sync_api import sync_playwright
from PIL import Image
import costants
import io
import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from tqdm import tqdm


def download_comic(base_url):

    if not base_url:
        print("Invalid URL")
        return

    BYTE_TO_SKIP = 817
    SIZE_TO_SKIP = (200, 200)

    hq_url=base_url+costants.HQ_FILTER
    parsed_url = urlparse(hq_url)
    comic_name = parsed_url.path.strip("/Comic").replace("/", "_")
    print(f"Start download of {comic_name}")

    download_dir = Path.home() / "Downloads"
    SAVE_DIR = download_dir / comic_name
    os.makedirs(SAVE_DIR, exist_ok=True)

    all_images = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # block useless resource
        page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["font", "stylesheet", "media"] else route.continue_())

        def handle_response(response):

            if response.request.resource_type != "image":
                return

            size = int(response.headers.get("content-length", 0))

            if (costants.IMG_URL not in response.url) or size <= BYTE_TO_SKIP:
                return

            # actual routine to download the image
            try:
                body = response.body()
                img = Image.open(io.BytesIO(body))
                w, h = img.size
                if (w, h) == SIZE_TO_SKIP:
                    return
            except Exception:
                print(f"\n Cannot download any image")
                return

            if response.url in all_images:
                return

            all_images.add(response.url)

            # retrive original filename
            cd = response.headers.get("content-disposition", "")
            match = re.search(r'filename="(.+)"', cd)
            filename = match.group(1) if match else os.path.basename(response.url).split("?")[0]

            save_path = os.path.join(SAVE_DIR, filename)
            with open(save_path, "wb") as f:
                f.write(body)

        page.on("response", handle_response)

        # retrieve the number of pages
        page.goto(f"{hq_url}#1", wait_until="domcontentloaded")
        options = page.query_selector_all("#selectPage option")
        if not options:
            print("Cannot find selectPage")
            return
        total_pages = int(options[-1].inner_text().strip())
        print(f"Number of pages: {total_pages}")

        # loop that "visit" each page
        for page_num in tqdm(range(1, total_pages+1), desc="Downloading pages"):
            url = f"{hq_url}#{page_num}"
            page.goto(url, wait_until="networkidle")

            # force lazy-load images
            page.evaluate("document.querySelector('#divImage img')?.scrollIntoView();")
            page.click("#divImage")
            # MANDATORY TIMEOUT
            page.wait_for_timeout(800)

        print(f"\n Number of unique pages downloaded: {len(all_images)}")
        browser.close()


def main():
    comic_list=open("list.txt", "r")
    for line in comic_list:
        download_comic(line.strip())
    comic_list.close()


if __name__ == "__main__":
    main()
