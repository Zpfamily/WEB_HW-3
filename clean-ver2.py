import re
from pathlib import Path
import shutil
import sys
import logging
from time import time
import concurrent.futures

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
trans = dict()

for cyrillic, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    trans[ord(cyrillic)] = latin
    trans[ord(cyrillic.upper())] = latin.upper()
    
def normalize(name: str) -> str:
    translate_name = re.sub(r'\W', '_', name.translate(trans))
    translate_name = ".".join(translate_name.rsplit("_",1))
    return translate_name

JPEG_IMAGES = []
PNG_IMAGES=[]
JPG_IMAGES = []
SVG_IMAGES = []
AVI_VIDEO = []
MP4_VIDEO = []
MOV_VIDEO = []
MKV_VIDEO = []
DOC_DOCUMENTS = []
DOCX_DOCUMENTS = []
TXT_DOCUMENTS = []
PDF_DOCUMENTS = []
XLSX_DOCUMENTS = []
PPTX_DOCUMENTS = []
MP3_AUDIO = []
OGG_AUDIO = []
WAV_AUDIO = []
AMR_AUDIO = []
ARCHIVES = []
MY_OTHERS = []

REGISTER_EXTENSION = {
    'JPEG': JPEG_IMAGES,
    'PNG': PNG_IMAGES,
    'JPG': JPG_IMAGES,
    'SVG': SVG_IMAGES,
    'AVI': AVI_VIDEO,
    'MP4': MP4_VIDEO,
    'MOV': MOV_VIDEO,
    'MKV': MKV_VIDEO,
    'DOC': DOC_DOCUMENTS,
    'DOCX': DOCX_DOCUMENTS,
    'TXT': TXT_DOCUMENTS,
    'PDF': PDF_DOCUMENTS,
    'XLSX': XLSX_DOCUMENTS,
    'PPTX': PPTX_DOCUMENTS,
    'MP3': MP3_AUDIO,
    'OGG': OGG_AUDIO,
    'WAV': WAV_AUDIO,
    'AMR': AMR_AUDIO,
    'ZIP': ARCHIVES,
    'GZ': ARCHIVES,
    'TAR': ARCHIVES,
}

FOLDERS = []
EXTENSIONS = set()
UNKNOWN = set()

def get_extension(name: str) -> str:
    return Path(name).suffix[1:].upper()

def scan(folder: Path):
    for item in folder.iterdir():
        # Робота з папкою
        if item.is_dir():  # перевіріямо чи обєкт папка
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'MY_OTHER'):
                FOLDERS.append(item)
                scan(item)
            continue
        
        # Робота з файлами                    
        extension = get_extension(item.name) # беремо розширення файлу
        full_name = folder / item.name # беремо повний шлях до файлу
        if not extension:
            MY_OTHERS.append(full_name)
        else:
            try:
                ext_reg = REGISTER_EXTENSION[extension]
                ext_reg.append(full_name)
                EXTENSIONS.add(extension)
            except KeyError:
                UNKNOWN.add(extension)
                MY_OTHERS.append(full_name)

def handle_media(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    file_name.replace(target_folder / normalize(file_name.name))
    
def handle_documents(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    file_name.replace(target_folder / normalize(file_name.name))
    
def handle_archive(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(file_name.name.replace(file_name.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(file_name.absolute()), str(folder_for_file.absolute()))
    except shutil.ReadError:
        folder_for_file.rmdir()
        return
    file_name.unlink()

def main(folder: Path):
    scan(folder)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(handle_media, file, folder / 'images' / 'JPEG') for file in JPEG_IMAGES]
        futures += [executor.submit(handle_media, file, folder / 'images' / 'JPG') for file in JPG_IMAGES]
        futures += [executor.submit(handle_media, file, folder / 'images' / 'PNG') for file in PNG_IMAGES]
        futures += [executor.submit(handle_media, file, folder / 'images' / 'SVG') for file in SVG_IMAGES]
        futures += [executor.submit(handle_media, file, folder / 'video' / 'AVI') for file in AVI_VIDEO]
        futures += [executor.submit(handle_media, file, folder / 'video' / 'MP4') for file in MP4_VIDEO]
        futures += [executor.submit(handle_media, file, folder / 'video' / 'MOV') for file in MOV_VIDEO]
        futures += [executor.submit(handle_media, file, folder / 'video' / 'MKV') for file in MKV_VIDEO]
        futures += [executor.submit(handle_media, file, folder / 'documents' / 'DOC') for file in DOC_DOCUMENTS]
        futures += [executor.submit(handle_media, file, folder / 'documents' / 'DOCX') for file in DOCX_DOCUMENTS]
        futures += [executor.submit(handle_media, file, folder / 'documents' / 'TXT') for file in TXT_DOCUMENTS]
        futures += [executor.submit(handle_media, file, folder / 'documents' / 'PDF') for file in PDF_DOCUMENTS]
        futures += [executor.submit(handle_media, file, folder / 'documents' / 'XLSX') for file in XLSX_DOCUMENTS]
        futures += [executor.submit(handle_media, file, folder / 'documents' / 'PPTX') for file in PPTX_DOCUMENTS]
        futures += [executor.submit(handle_media, file, folder / 'audio' / 'MP3') for file in MP3_AUDIO]
        futures += [executor.submit(handle_media, file, folder / 'audio' / 'OGG') for file in OGG_AUDIO]
        futures += [executor.submit(handle_media, file, folder / 'audio' / 'WAV') for file in WAV_AUDIO]
        futures += [executor.submit(handle_media, file, folder / 'audio' / 'AMR') for file in AMR_AUDIO]
        futures += [executor.submit(handle_media, file, folder / 'my_other') for file in MY_OTHERS]
        futures += [executor.submit(handle_media, file, folder / 'archives') for file in ARCHIVES]
    
    for folder in FOLDERS[::-1]:
        try:
            folder.rmdir()
        except OSError:
            print(f'Error during remove: {folder}')
            
              
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_time = time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(main, folder) for folder in FOLDERS]
        concurrent.futures.wait(futures)
    logging.info(f"Cleaning folders took {time() - start_time:.6f} seconds.")
    print("Done!!!")



