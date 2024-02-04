import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
import string
import hashlib
import os
import time
import magic

def generate_random_numbers(count):
    return ''.join(random.choices(string.digits, k=count))

def generate_random_characters(count):
    return ''.join(random.choices(string.ascii_letters, k=count))

def get_random_screenshot_url():
    base_url = "https://prnt.sc/"
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=2)) + generate_random_numbers(4)
    random_url = f"{base_url}{random_suffix}"
    return random_url

def download_image(url, filename, headers=None):
    response = requests.get(url, stream=True, headers=headers)
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)

def hash_file(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def is_html_content(file_path):
    mime = magic.Magic()
    file_type = mime.from_file(file_path)
    return 'HTML document' in file_type

def fetch_and_process(iterations, thread_num):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    blocked_image_hashes = [
        "1a0a4a92f1f52631d5332ddb3f88702a",
        "12362ed2ecb31e0bc9c1e3e911f3c82f",
        "d835884373f4d6c8f24742ceabe74946"
    ]
    if not os.path.exists("images"):
        os.makedirs("images")

    for i in range(iterations):
        time.sleep(1)
        random_url = get_random_screenshot_url()
        response = requests.get(random_url, headers=headers, stream=True)
        
        if response.status_code == 404:
            print(f"Thread {thread_num}, Iteration {i + 1}: 404 Error - Image not found on {random_url}")
        elif response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            image_element = soup.find('img', {'class': 'screenshot-image'})
            
            if image_element:
                image_url = urljoin(random_url, image_element['src'])
                random_filename = f"images/downloaded_image_{i}.png"
                download_image(image_url, random_filename, headers=headers)
                
                if hash_file(random_filename) in blocked_image_hashes:
                    print(f"Thread {thread_num}, Iteration {i + 1}: Image hash is in the block list. Removing file.")
                    os.remove(random_filename)
                else:
                    print(f"Thread {thread_num}, Iteration {i + 1}: Image downloaded from {image_url}")

                    if is_html_content(random_filename):
                        print(f"Thread {thread_num}, Iteration {i + 1}: HTML content detected. Removing file.")
                        os.remove(random_filename)
            else:
                print(f"Thread {thread_num}, Iteration {i + 1}: No image found on the page.")
        else:
            print(f"Thread {thread_num}, Iteration {i + 1}: Failed to fetch the page. Status code: {response.status_code}")

def main(iterations_per_thread, num_threads):
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=fetch_and_process, args=(iterations_per_thread, i + 1))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    iterations_per_thread = 25000
    num_threads = int(input("How many threads to run? more than 8 could result IP ban!!!:"))
    main(iterations_per_thread, num_threads)

