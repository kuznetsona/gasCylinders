import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QVBoxLayout, QFrame
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("glasCylinders.ui", self)

        # Инициализация слайдеров и их начальные значения
        self.slider_contrast.setValue(50)
        self.slider_binary.setValue(50)  # Начальное значение для порога бинаризации
        self.slider_noise.setValue(0)  # Начальное значение для сглаживания шума

        self.video_feed()

    def video_feed(self):
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, image = self.capture.read()
        if ret:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            image = self.adjust_contrast(image, self.slider_contrast.value())
            binary = self.apply_binary_threshold(gray, self.slider_binary.value())
            noise_reduced = self.reduce_noise(binary, self.slider_noise.value())

            height, width = noise_reduced.shape
            bytes_per_line = width
            q_image = QImage(noise_reduced.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            pixmap = pixmap.scaled(self.videoContainer.width(), self.videoContainer.height(), Qt.KeepAspectRatio)
            self.videoContainer.setPixmap(pixmap)

    def apply_binary_threshold(self, gray_image, threshold_value):
        new_threshold_value = int((threshold_value / 100) * 255)
        _, binary = cv2.threshold(gray_image, new_threshold_value, 255, cv2.THRESH_BINARY)
        return binary

    def reduce_noise(self, gray_image, noise_value):
        # Пример использования GaussianBlur для сглаживания
        return cv2.GaussianBlur(gray_image, (noise_value | 1, noise_value | 1),
                                0)  # noise_value|1 гарантирует нечетное значение

    def adjust_contrast(self, image, contrast_value):
        alpha = contrast_value / 100.0
        beta = 0  # не меняем яркость
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
