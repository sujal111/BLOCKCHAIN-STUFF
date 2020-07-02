import hashlib
import docx2txt
from PIL import Image
import imagehash
import distance
from mp3hash import mp3hash


def txt_hash(upload):
    file = upload
    BLOCK_SIZE = 65536

    file_hash = hashlib.sha3_256()
    with open(file, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb.strip())
            fb = f.read(BLOCK_SIZE)

    return file_hash.hexdigest()


def word_hash(upload):
    result = docx2txt.process(upload).strip()
    return hashlib.sha3_256(result.encode('utf-8')).hexdigest()


def image_hash(upload):
    file = imagehash.phash(Image.open(upload))
    return str(file)


def audio_hash(upload):
    file = upload
    return mp3hash(file, None, hashlib.sha3_256())


def image_dist(a, b):
    return distance.hamming(a, b)
