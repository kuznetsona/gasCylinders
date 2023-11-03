import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QVBoxLayout, QFrame
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import pytesseract



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
        config = '--oem 1 --psm 11'
        self.initialize_sliders()

        self.initialize_frames()

        self.selectingRegion = True
        self.selectRegionButton.clicked.connect(self.toggle_region_selection)
        self.ROI = None

        self.apply_transformations = [False, False, False, False]
        for i in range(4):
            self.videoContainers[i].mousePressEvent = lambda event, index=i: self.toggle_transformation(index)

    def toggle_region_selection(self):
        self.selectingRegion = True

    def initialize_sliders(self):
        self.slider_contrast.setValue(50)
        self.slider_binary.setValue(50)
        self.slider_noise.setValue(0)
        # может так и не надо делать
        self.slider_dilation.setValue(1)
        self.slider_closing.setValue(1)
        self.slider_opening.setValue(1)


    def initialize_frames(self):

        self.videoContainers = [self.videoContainer_0,
                                self.videoContainer_1,
                                self.videoContainer_2,
                                self.videoContainer_3]

        self.text_results = [self.text_result_0,
                             self.text_result_1,
                             self.text_result_2,
                             self.text_result_3]


    def toggle_transformation(self, index):
        self.apply_transformations[index] = not self.apply_transformations[index]


    def on_radioButton_toggled(self, checked):
        self.apply_transformations = checked

    def video_feed(self):
        # Список камер
        self.cameras = [cv2.VideoCapture(0),
                        cv2.VideoCapture(1),
                        cv2.VideoCapture(2),
                        cv2.VideoCapture(3)]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def calculate_accuracy(self, recognized_text, expected_text):
        matched_chars = sum(1 for a, b in zip(recognized_text, expected_text) if a == b)
        return matched_chars / max(len(recognized_text), len(expected_text))

    def update_frame(self):
        if self.selectingRegion:
            self.select_regions()

        for i, camera in enumerate(self.cameras):
            if camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    frame = self.process_frame(frame, i)
                    self.display_frame(frame, i)

    def select_regions(self):
        self.ROIs = []
        for camera in self.cameras:
            if camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    r = cv2.selectROI(f"Select ROI for Camera {self.cameras.index(camera)}", frame, False)
                    cv2.destroyWindow(f"Select ROI for Camera {self.cameras.index(camera)}")

                    if r[2] != 0 and r[3] != 0:
                        self.ROIs.append(r)
                    else:
                        self.ROIs.append(None)
        self.selectingRegion = False

    def process_frame(self, frame, index):
        if self.ROIs and self.ROIs[index]:
            r = self.ROIs[index]
            frame = frame[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.apply_transformations[index]:
            gray_frame = self.apply_transforms(gray_frame)

        return gray_frame

    def display_frame(self, gray_frame, index):
        height, width = gray_frame.shape
        bytes_per_line = gray_frame.strides[0]
        q_image = QImage(gray_frame.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

        pixmap = QPixmap.fromImage(q_image)
        pixmap = pixmap.scaled(self.videoContainers[index].width(), self.videoContainers[index].height(),
                               Qt.KeepAspectRatio)
        self.videoContainers[index].setPixmap(pixmap)

        recognized_text = pytesseract.image_to_string(gray_frame, config='--oem 1 --psm 11')
        self.text_results[index].setText(recognized_text)


    def apply_transforms(self, img):
        img = self.adjust_contrast(img, self.slider_contrast.value())
        img = self.apply_binary_threshold(img, self.slider_binary.value())
        #img = cv2.bitwise_not(img)
        img = self.apply_dilation(img, self.slider_dilation.value())
        img = self.apply_closing(img, self.slider_closing.value())
        img = self.apply_opening(img, self.slider_opening.value())
        img = self.reduce_noise(img, self.slider_noise.value())
        return img

    def display_results(self, images, recognized_texts):
        for i, (img, recognized_text) in enumerate(zip(images, recognized_texts)):
            if i == 0:
                container = self.videoContainer_0
            elif i == 1:
                container = self.videoContainer_1
            elif i == 2:
                container = self.videoContainer_2
            elif i == 3:
                container = self.videoContainer_3
            else:
                continue

            expected_text = "СВЯТОЙ\nИСТОЧНИК"
            accuracy = self.calculate_accuracy(recognized_text, expected_text)
            accuracy_percentage = round(accuracy * 100, 2)
            self.text_result.setText(recognized_text)

            height, width = img.shape
            bytes_per_line = width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            pixmap = pixmap.scaled(container.width(), container.height(), Qt.KeepAspectRatio)
            container.setPixmap(pixmap)

    def apply_binary_threshold(self, gray_image, threshold_value):
        new_threshold_value = int((threshold_value / 100) * 255)
        _, binary = cv2.threshold(gray_image, new_threshold_value, 255, cv2.THRESH_BINARY)
        return binary

    def reduce_noise(self, gray_image, noise_value):
        adjusted_noise_value = max(1, int(noise_value / 20))
        return cv2.GaussianBlur(gray_image, (adjusted_noise_value | 1, adjusted_noise_value | 1), 0)

    def adjust_contrast(self, image, contrast_value):
        alpha = (contrast_value * 3) / 100.0
        beta = 0
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    def apply_dilation(self, image, dilation_value):
        adjusted_dilation_value = dilation_value // 10
        kernel = np.ones((adjusted_dilation_value, adjusted_dilation_value), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    def apply_closing(self, image, closing_value):
        adjusted_closing_value = closing_value // 10
        kernel = np.ones((adjusted_closing_value, adjusted_closing_value), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

    def apply_opening(self, image, opening_value):
        adjusted_opening_value = opening_value // 10
        kernel = np.ones((adjusted_opening_value, adjusted_opening_value), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    def closeEvent(self, event):
        for camera in self.cameras:
            if camera.isOpened():
                camera.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())