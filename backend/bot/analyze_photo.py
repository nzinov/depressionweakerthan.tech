from settings import SUBSCRIPTION_KEY
import requests


FACE_API_URL = "https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect"
PARAMS = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'emotion'
}
# https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognize"
HEADERS = {
    'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
    "Content-Type": "application/octet-stream",
}


def analyze_photo(photo_file_name):
    with open(photo_file_name, 'rb') as photo_file:
        photo_data = photo_file.read()
        response = requests.post(FACE_API_URL, headers=HEADERS, data=photo_data, params=PARAMS)
    faces = response.json()
    if len(faces) == 0:
        raise ValueError('There is no faces!')
    else:
        return faces[0]['faceAttributes']['emotion']
