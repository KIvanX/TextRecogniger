import gc
import logging
import shutil
import zipfile
from urllib.parse import urlencode

import requests
import os
from recognizer import image_to_text


async def walker(src, dest, mes):
    os.makedirs(dest)

    i = 0
    for root, dirs, files in os.walk(src):
        relative_path = os.path.relpath(root, src)
        src_dir = os.path.join(src, relative_path)
        dest_dir = os.path.join(dest, relative_path)
        os.makedirs(dest_dir, exist_ok=True)

        for file_name in files:
            src_file_path = src_dir + '/' + file_name
            dest_file_path = os.path.join(dest_dir, file_name)
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                try:
                    extracted_text = await image_to_text(src_file_path)
                except Exception as e:
                    logging.error(e)
                    extracted_text = 'Ошибка'

                with open(dest_file_path[:-4] + '.txt', 'w') as f:
                    f.write(extracted_text)

                i += 1
                try:
                    await mes.edit_text(f"🔍 Распознаем файлы... ({i})")
                except:
                    pass
            else:
                open(dest_file_path, 'a').close()


def downloader(url):
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

    final_url = base_url + urlencode(dict(public_key=url))
    response = requests.get(final_url)
    download_url = response.json()['href']

    part = download_url.split('filename=')[1]
    filename = part[:part.find('&')]

    download_response = requests.get(download_url)

    with open(f'static/{filename}', 'wb') as f:
        f.write(download_response.content)

    download_response.close()
    del download_response
    gc.collect()

    return filename


def upload_file_to_yandex_disk(file_path, yandex_disk_path):
    headers = {"Authorization": 'OAuth ' + os.environ['YANDEX_KEY']}
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    params = {"path": yandex_disk_path, "overwrite": "true"}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return logging.error(f"Upload file to yandex disk init error ({response.status_code}): " + response.text)

    with open(file_path, 'rb') as file:
        upload_response = requests.put(response.json().get("href"), files={'file': file})

    if not (200 <= upload_response.status_code < 300):
        logging.error(f"Upload file to yandex disk error ({upload_response.status_code}): " + upload_response.text)

    return publish_file_on_yandex_disk(yandex_disk_path)


def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Проходим по всем файлам и подпапкам в указанной папке
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Получаем полный путь к файлу
                file_path = os.path.join(root, file)
                # Добавляем файл в zip архив
                # Параметр arcname позволяет избежать записи полного пути в zip архив
                zipf.write(file_path, os.path.relpath(file_path, folder_path))


def clear_directory(directory_path):
    if not os.path.exists(directory_path):
        logging.warning(f"Директория {directory_path} не существует.")
        return

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def publish_file_on_yandex_disk(yandex_disk_path):
    headers = {"Authorization": 'OAuth ' + os.environ['YANDEX_KEY']}
    url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
    params = {"path": yandex_disk_path}
    response = requests.put(url, headers=headers, params=params)

    if response.status_code != 200:
        logging.error(f"Publish file error ({response.status_code}): " + response.text)
        return None

    return get_public_link(yandex_disk_path)


def get_public_link(yandex_disk_path):
    headers = {"Authorization": 'OAuth ' + os.environ['YANDEX_KEY']}
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": yandex_disk_path, "fields": "public_url"}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        public_url = response.json().get('public_url')
        if public_url:
            return public_url
        else:
            logging.error("File is not published.")
    else:
        logging.error(f"Get public link error ({response.status_code}): " + response.text)

    return None
