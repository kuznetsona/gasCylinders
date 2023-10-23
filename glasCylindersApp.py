import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QVBoxLayout, QFrame
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import pytesseract


# Добавить вывод с двух камер
# и сшивание двух кадров,
# сделать рефакторинг,
# И нормальную точность,
# изменить настройки

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("glasCylinders.ui", self)
        self.initialize_ui()
        self.video_feed()

    def initialize_ui(self):
        self.apply_transformations = False
        self.radioButton.toggled.connect(self.on_radioButton_toggled)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.initialize_sliders()

    def initialize_sliders(self):
        self.slider_contrast.setValue(50)
        self.slider_binary.setValue(50)
        self.slider_noise.setValue(0)
        self.slider_dilation.setValue(0)
        self.slider_closing.setValue(0)
        self.slider_opening.setValue(0)

    def on_radioButton_toggled(self, checked):
        self.apply_transformations = checked

    def video_feed(self):
        self.capture1 = cv2.VideoCapture(0)
        # self.capture2 = cv2.VideoCapture(1)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def stitch_images(self, img1, img2):
        return np.hstack((img1, img2))

    def calculate_accuracy(self, recognized_text, expected_text):
        matched_chars = sum(1 for a, b in zip(recognized_text, expected_text) if a == b)
        return matched_chars / max(len(recognized_text), len(expected_text))

    def update_frame(self):
        ret1, image1 = self.capture1.read()
        # ret2, image2 = self.capture2.read()

        if ret1:
            # if ret1 and ret2:
            # Сшиваем два изображения вместе по горизонтали
            # combined_image = np.hstack((image1, image2))
            combined_image = image1

            gray = cv2.cvtColor(combined_image, cv2.COLOR_BGR2GRAY)
            if self.apply_transformations:
                gray = self.apply_transforms(gray)

            recognized_text = pytesseract.image_to_string(gray)
            self.display_results(gray, recognized_text)

    def apply_transforms(self, img):
        img = self.adjust_contrast(img, self.slider_contrast.value())
        img = self.apply_binary_threshold(img, self.slider_binary.value())
        img = self.apply_dilation(img, self.slider_dilation.value())
        img = self.apply_closing(img, self.slider_closing.value())
        img = self.apply_opening(img, self.slider_opening.value())
        img = self.reduce_noise(img, self.slider_noise.value())
        return img

    def display_results(self, img, recognized_text):
        expected_text = "СВЯТОЙ\nИСТОЧНИК"
        accuracy = self.calculate_accuracy(recognized_text, expected_text)
        accuracy_percentage = round(accuracy * 100, 2)
        self.text_result.setText(recognized_text)
        self.text_accuracy.setText(f"Accuracy: {accuracy_percentage}%")
        height, width = img.shape
        bytes_per_line = width
        q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        pixmap = pixmap.scaled(self.videoContainer.width(), self.videoContainer.height(), Qt.KeepAspectRatio)
        self.videoContainer.setPixmap(pixmap)


    def apply_binary_threshold(self, gray_image, threshold_value):
        new_threshold_value = int((threshold_value / 100) * 255)
        _, binary = cv2.threshold(gray_image, new_threshold_value, 255, cv2.THRESH_BINARY)
        return binary

    def reduce_noise(self, gray_image, noise_value):
        # Разделите noise_value на 10 для более плавного изменения
        adjusted_noise_value = max(1, int(noise_value / 10))
        return cv2.GaussianBlur(gray_image, (adjusted_noise_value | 1, adjusted_noise_value | 1), 0)

    def adjust_contrast(self, image, contrast_value):
        alpha = (contrast_value * 3) / 100.0
        beta = 0
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    def apply_dilation(self, image, dilation_value):
        adjusted_dilation_value = dilation_value // 100
        kernel = np.ones((adjusted_dilation_value, adjusted_dilation_value), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    def apply_closing(self, image, closing_value):
        adjusted_closing_value = closing_value // 100
        kernel = np.ones((adjusted_closing_value, adjusted_closing_value), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

    def apply_opening(self, image, opening_value):
        adjusted_opening_value = opening_value // 100
        kernel = np.ones((adjusted_opening_value, adjusted_opening_value), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    def closeEvent(self, event):
        self.capture1.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())