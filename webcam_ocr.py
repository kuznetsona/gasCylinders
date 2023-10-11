import cv2
import os
import pytesseract
from PIL import Image, ImageEnhance
import numpy as np

class ImagePreprocessor:
    def __init__(self, image_path, output_path):
        self.image_path = image_path
        self.output_path = output_path

    def _read_image(self):
        return cv2.imread(self.image_path, 1)

    def enhance_contrast(self, img):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced_img = cv2.merge((l, a, b))
        return cv2.cvtColor(enhanced_img, cv2.COLOR_LAB2BGR)

    def to_grayscale(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def binarize(self, img):
        _, binary_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary_img

    def denoise(self, img):
        return cv2.medianBlur(img, 3)

    def enhance_sharpness(self, img):
        img_pil = Image.fromarray(img)
        enhancer = ImageEnhance.Sharpness(img_pil)
        enhanced_img = enhancer.enhance(2.0)
        return np.array(enhanced_img)

    def brighten_shadows(self, img):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def preprocess(self):
        img = self._read_image()
        img = self.enhance_contrast(img)
        #img = self.brighten_shadows(img)
        img = self.to_grayscale(img)
        img = self.binarize(img)
        img = self.enhance_sharpness(img)
        cv2.imwrite(self.output_path, img)
        return img

class TesseractOCR:
    def __init__(self, config):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.config = config

    def image_to_string(self, image_path):
        return pytesseract.image_to_string(image_path, config=self.config, lang="rus")

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Couldn't read frame from webcam.")
        exit()

    project_directory = os.path.dirname(os.path.abspath(__file__))

    image_filename = 'ballon_webcam.jpg'
    image_path = os.path.join(project_directory, image_filename)
    cv2.imwrite(image_path, frame)
    print(f"Image saved as {image_path}")

    output_filename = 'preprocessed_' + image_filename
    output_path = os.path.join(project_directory, output_filename)

    preprocessor = ImagePreprocessor(image_path, output_path)
    preprocessor.preprocess()

    config = '--oem 1 --psm 6 -c tessedit_create_hocr=1 -c tessedit_write_images=True'
    ocr = TesseractOCR(config)
    text = ocr.image_to_string(output_path)
    print(text)

    #data = pytesseract.image_to_data(output_path, config=config)
    #data = ocr.image_to_data(output_path)
    #boxes = pytesseract.image_to_boxes(output_path, config=config)
    #print(boxes)
    #print(data)
    #for key, value in data.items():
    #    print(f'{key}: {value}')

