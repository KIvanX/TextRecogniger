import requests

HOST = "https://rehand.ru"
API_KEY = "f85e7725-c3ba-40d4-9bd0-2df849a92692"
PATH_TO_FILE = "static/photo.jpg"
FILE_NAME = "static/photo.jpg"
TYPE_VALUE = "handwriting"  # or "regular"

response = requests.post(
    f"{HOST}/api/v1/upload",
    files={
        "file": (FILE_NAME, open(PATH_TO_FILE, "rb"))
    },
    data={
        "type": TYPE_VALUE
    },
    headers={"Authorization": API_KEY}
)

print(response.json())
