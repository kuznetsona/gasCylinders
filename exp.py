import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np

class ImagePreprocessor:
    def __init__(self, image_path, output_path):
        self.image_path = image_path
        self.output_path = output_path

    def enhance_contrast(self):
        img = cv2.imread(self.image_path, 1)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced_img = cv2.merge((l, a, b))
        enhanced_img = cv2.cvtColor(enhanced_img, cv2.COLOR_LAB2BGR)
        return enhanced_img

    def to_grayscale(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray_img

    def binarize(self, img):
        _, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary_img

    def denoise(self, img):
        denoised_img = cv2.medianBlur(img, 3)
        return denoised_img

    def enhance_sharpness(self, img):
        img_pil = Image.fromarray(img)
        enhancer = ImageEnhance.Sharpness(img_pil)
        enhanced_img = enhancer.enhance(2.0)
        return enhanced_img

    def preprocess(self):
        img = self.enhance_contrast()
        img = self.to_grayscale(img)
        img = self.binarize(img)
        img = self.denoise(img)
        img = self.enhance_sharpness(img)
        img = np.array(img)
        cv2.imwrite(self.output_path, img)
        return img


class TesseractOCR:
    def __init__(self, config):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.config = config

    def image_to_string(self, image_path):
        text = pytesseract.image_to_string(image_path, config=self.config)
        return text

    def image_to_data(self, image_path):
        data = pytesseract.image_to_data(image_path, output_type=pytesseract.Output.DICT, config=self.config)
        return data


if __name__ == "__main__":
    config = '--oem 1 --psm 6 -c tessedit_create_hocr=1 -c tessedit_write_images=True'

    image_path = 'ballon1.jpg'
    output_path = 'preprocessed_' + image_path

    preprocessor = ImagePreprocessor(image_path, output_path)
    preprocessed_img = preprocessor.preprocess()

    ocr = TesseractOCR(config)
    text = ocr.image_to_string(output_path)
    print(text)

    #print(data)

    #for key, value in data.items():
    #    print(f'{key}: {value}')


