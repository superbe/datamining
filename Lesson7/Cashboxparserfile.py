import os
import PyPDF2
import shutil
import time
import pytesseract
from PIL import Image
from pymongo import MongoClient
from datetime import datetime

# Для установки pytesseract
# $ sudo apt update
# $ sudo apt install tesseract-ocr
# После установка нужных языковых пакетов
# $ sudo apt-get install tesseract-ocr-[lang]
# Например:
# $ sudo apt-get install tesseract-ocr-eng
# $ sudo apt-get install tesseract-ocr-rus
# Установка всех языковых пакетов
# $ sudo apt-get install tesseract-ocr-all

mongo_client = MongoClient()


class Recognizer:
    def __init__(self, folder, destination_folder, error_folder, db_name, result_name_collection,
                 empty_result_name_collection, error_name_collection):
        self.__folder = folder
        self.__destination_folder = destination_folder
        self.__error_folder = error_folder
        self.__data_base = mongo_client[db_name]
        self.__result_collection = self.__data_base[result_name_collection]
        self.__empty_result_collection = self.__data_base[empty_result_name_collection]
        self.__error_collection = self.__data_base[error_name_collection]

    def __jpg_recognize(self, file_name):
        try:
            shutil.copy(file_name, self.__destination_folder)
            self.__image_recognize(f'{self.__destination_folder}/{file_name.split("/")[-1]}')

        except IOError as e:
            shutil.copy(file_name, self.__error_folder)
            self.__error_collection.insert({'date': datetime.now(), 'file_name': file_name})

    def __pdf_recognize(self, file_name):
        try:
            file = PyPDF2.PdfFileReader(open(file_name, 'rb'), strict=False)
            for page_number in range(file.getNumPages()):
                page = file.getPage(page_number)
                page_object = page['/Resources']['/XObject'].getObject()
                for obj in page_object:
                    if page_object[obj].get('/Subtype') == '/Image':
                        size = (page_object[obj]['/Width'], page_object[obj]['/Height'])
                        data = page_object[obj]._data
                        mode = 'RGB' if page_object[obj].get('/ColorSpace') == '/DeviceRGB' else 'P'
                        filename, file_extension = os.path.splitext(file_name)
                        filename = f'{self.__destination_folder}/{filename.split("/")[-1]}_{time.time()}_{page_number}'
                        if page_object[obj].get('/Filter') == '/FlateDecode':
                            image = Image.frombytes(mode, size, data)
                            image.save(f'{filename}.png')
                            image.close()
                            self.__image_recognize(f'{filename}.png')
                        elif page_object[obj].get('/Filter') == '/DCTDecode':
                            image = open(f'{filename}.jpg', 'wb')
                            image.write(data)
                            image.close()
                            self.__image_recognize(f'{filename}.jpg')
                        elif page_object[obj].get('/Filter') == '/JPXDecode':
                            image = open(f'{filename}.jp2', 'wb')
                            image.write(data)
                            image.close()
                            self.__image_recognize(f'{filename}.jp2')
        except (PyPDF2.utils.PdfReadError, ValueError) as e:
            shutil.copy(file_name, self.__error_folder)
            self.__error_collection.insert({'date': datetime.now(), 'file_name': file_name})

    def __image_recognize(self, file_name):
        image = Image.open(file_name)
        text = pytesseract.image_to_string(image, lang="rus")
        templates = ['заводской (серийный) номер', 'заводской номер (номера)']
        for template in templates:
            if text.lower().find(template) + 1:
                for index, line in enumerate(text.split('\n')):
                    if line.lower().find(template) + 1:
                        number = pytesseract.image_to_string(image, lang="rus").split('\n')[index].split(' ')[-1]
                        self.__result_collection.insert(
                            {'date': datetime.now(), 'file_name': file_name, 'number': number}
                        )
        image.close()

    def recognize(self):
        for d, directories, files in os.walk(self.__folder):
            for file in files:
                filename, file_extension = os.path.splitext(file)
                file = f'{self.__folder if d == self.__folder else d}/{file}'
                if file_extension == '.jpg':
                    self.__jpg_recognize(file)
                elif file_extension == '.pdf':
                    self.__pdf_recognize(file)


if __name__ == '__main__':
    recognizer = Recognizer('Data/Sources', 'Data/Results', 'Data/Errors', 'Recognizer', 'Results', 'EmptyResults',
                            'Errors')
    recognizer.recognize()
