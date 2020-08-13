from bs4 import BeautifulSoup
import requests
import re
import urllib.request as urllib2
import os
import argparse
import sys
import json
import time
import hashlib
from selenium import webdriver
import io
from PIL import Image
import matplotlib.pyplot as plt

"""
Adapted from:
https://gist.github.com/genekogan/ebd77196e4bf0705db51f86431099e57
https://towardsdatascience.com/image-scraping-with-python-a96feda8af2d
"""


def scroll_to_end(wd: object) -> None:
    # helper function for chrome scrolling

    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)


def fetch_urls(query: str, num_images: int, DRIVER_PATH: str) -> set:
    # function to grab urls to download

    wd = webdriver.Chrome(executable_path=DRIVER_PATH)
    search_url = ("https://www.google.com/search?safe=of"
                  "&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img")

    wd.get(search_url.format(q=query))

    urls = set()
    image_count = 0
    results_count = 0

    # while we don't have enough urls
    while image_count < num_images:
        scroll_to_end(wd)

        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        for img in thumbnail_results[results_count:number_results]:

            # try clicking on image
            try:
                img.click()
                time.sleep(1)
            except Exception:
                continue

            # grab all images in the thumbnail results
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    urls.add(actual_image.get_attribute('src'))

            # if we found enough images, break
            image_count = len(urls)
            if len(urls) >= num_images:
                print("found {len_img_urls} links, finishing...".format(len_img_urls=len(urls)))
                break
            else:
                print("found {len_img_urls} links, looking for more...".format(len_img_urls=len(urls)))
                time.sleep(0.1)
                load_more_button = wd.find_element_by_css_selector(".mye4qd")
                if load_more_button:
                    wd.execute_script("document.querySelector('.mye4qd').click();")

            # move the result startpoint further down
            results_count = len(thumbnail_results)
    return urls


def persist_image(folder_path: str, url: str) -> int:
    # Function to attempt and download image url

    try:
        image_content = requests.get(url).content
    except Exception as e:
        print("ERROR - Could not download {url} - {e}".format(e=e, url=url))
    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')

        # if image has not already been downloaded (or at least doesn't collide with known hash)
        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=85)
            print("SUCCESS - saved {url} - as {file_path}".format(url=url, file_path=file_path))
            return 1
        else:
            print("image: {file_path} already exists, skipping".format(file_path=file_path))
            return 0
    except Exception as e:
        print("ERROR - Could not save {url} - {e}".format(e=e, url=url))
        return 0


def main(args: object, DRIVER_PATH: str ="./chromedriver") -> None:

    # create query strings
    query = args.query.split()
    query_prefix = "_".join(query)
    query = "+".join(query)
    num_images = args.num_images

    root_dir = args.data_dir
    idx_json_pth = os.path.join(root_dir, "index.json")
    query_pth = os.path.join(root_dir, query_prefix)

    idx_dict = {}
    print("query: {}".format(query))

    # determine if relevant directories and index.json exist. If not, create them
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if os.path.exists(idx_json_pth):
        with open(idx_json_pth) as f:
            idx_dict = json.load(f)
    if query_prefix in idx_dict:
        prev_num_imgs = idx_dict[query_prefix]
    else:
        prev_num_imgs = 0
        if not os.path.exists(query_pth):
            os.makedirs(query_pth)

    if prev_num_imgs == 1:
        print("currently have {num} image for query: {query} ".format(num=prev_num_imgs, query=query))
    else:
        print("currently have {num} images for query: {query} ".format(num=prev_num_imgs, query=query))

    # grab image urls and count how many were actually downloaded
    urls = fetch_urls(query, num_images, DRIVER_PATH)
    count = 0
    for url in urls:
        count += persist_image(query_pth, url)
    if query_prefix in idx_dict:
        idx_dict[query_prefix] += count
    else:
        idx_dict[query_prefix] = count

    if count == 1:
        print("found {count} new image".format(count=count))
    else:
        print("found {count} new images".format(count=count))

    # re-dump index.json with updated counts
    with open(idx_json_pth, 'w', encoding='utf-8') as f:
        json.dump(idx_dict, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape google images for training data')
    parser.add_argument('--query', type=str, help="search query")
    parser.add_argument('--num_images', default=10, type=int, help='num images to scrape')
    parser.add_argument('--data_dir', default="./data", type=str, help='root directory for data')
    args = parser.parse_args()
    main(args)
