import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QVBoxLayout, QFrame
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import pytesseract
from imutils import rotate_bound, rotate
from image_processing import apply_binary_threshold, reduce_noise, adjust_contrast, apply_dilation, apply_closing, apply_opening
import os
from datetime import datetime


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("glasCylinders_v2.ui", self)
        self.initialize_ui()
        self.video_feed()

    def initialize_ui(self):
        #self.apply_transformations = False
        self.radioButton.toggled.connect(self.on_radioButton_toggled)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        config = '--oem 1 --psm 11'
        self.initialize_sliders()

        self.initialize_frames()

        self.current_frame_index = None

        self.select_region_index = None
        self.ROIs = [None] * len(self.videoContainers)

        self.apply_transformations = [False] * len(self.videoContainers)

        #self.pushButton_apply = self.findChild(QPushButton, 'pushButton_apply')
        self.pushButton_apply.clicked.connect(self.save_frames)


        self.selectRegionButton.clicked.connect(self.toggle_region_selection)

        self.selectingRegion = False

        self.slider_rotation.setMinimum(-90)
        self.slider_rotation.setMaximum(90)
        self.slider_rotation.valueChanged.connect(self.slider_changed)



        self.slider_binary.valueChanged.connect(self.slider_changed)
        self.slider_noise.valueChanged.connect(self.slider_changed)
        self.slider_dilation.valueChanged.connect(self.slider_changed)
        self.slider_closing.valueChanged.connect(self.slider_changed)
        self.slider_opening.valueChanged.connect(self.slider_changed)


        for i in range(len(self.videoContainers)):
            self.videoContainers[i].mousePressEvent = lambda event, index=i: self.select_frame(index)


    def initialize_sliders(self):

        self.slider_rotation.setValue(0)

        self.slider_binary.setValue(50)
        self.slider_noise.setValue(0)
        # может так и не надо делать
        self.slider_dilation.setValue(1)
        self.slider_closing.setValue(1)
        self.slider_opening.setValue(1)


    def initialize_frames(self):

        self.videoContainers = [self.videoContainer_00,
                                self.videoContainer_01,
                                self.videoContainer_02,
                                self.videoContainer_03,
                                self.videoContainer_10,
                                self.videoContainer_11,
                                self.videoContainer_12,
                                self.videoContainer_13,
                                self.videoContainer_14,
                                self.videoContainer_15,
                                self.videoContainer_16,
                                self.videoContainer_17,
                                self.videoContainer_18,
                                self.videoContainer_19,
                                self.videoContainer_20,
                                self.videoContainer_21,
                                self.videoContainer_22,
                                self.videoContainer_23,
                                self.videoContainer_24]

        self.text_results = [self.text_result_00,
                             self.text_result_01,
                             self.text_result_02,
                             self.text_result_03,
                             self.text_result_10,
                             self.text_result_11,
                             self.text_result_12,
                             self.text_result_13,
                             self.text_result_14,
                             self.text_result_15,
                             self.text_result_16,
                             self.text_result_17,
                             self.text_result_18,
                             self.text_result_19,
                             self.text_result_20,
                             self.text_result_21,
                             self.text_result_22,
                             self.text_result_23,
                             self.text_result_24]


        # соответствие видеоконтейнеров и камер
        # self.camera_container_map = {
        #     0: 0, 1: 1, 2: 1, 3: 2,
        #     4: 0, 5: 0, 6: 1, 7: 1, 8: 2, 9: 2, 10: 2, 11: 0, 12: 0, 13: 0,
        #     14: 0, 15: 0, 16: 1, 17: 2, 18: 2
        # }

        self.camera_container_map = {
            0: 0, 1: 0, 2: 0, 3: 0,
            4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0,
            14: 0, 15: 0, 16: 0, 17: 0, 18: 0
        }

        self.frames_ground_truth = {
            0: None, 1: None, 2: None, 3: None,
            4: None, 5: 'BAR', 6: 1, 7: 'BAR', 8: 2, 9: 2, 10: 2,
            11: 'ISO', 12: 0, 13: 1, 14: 2, 15: 2
        }

        # словарь предобработки кажждого фрейма
        self.preprocessing_settings = {i: {
            'binary': self.slider_binary.value(),
            'rotation': self.slider_rotation.value(),
            'dilation': self.slider_dilation.value(),
            'closing': self.slider_closing.value(),
            'opening': self.slider_opening.value(),
            'noise': self.slider_noise.value()
        } for i in range(len(self.videoContainers))}


    def video_feed(self):
        # Список камер
        self.cameras = [cv2.VideoCapture(0)]
                        #cv2.VideoCapture(1),
                        #cv2.VideoCapture(2)]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(600)


    def select_frame(self, index):
        if self.selectingRegion:
            self.select_region_index = index
            self.select_regions()
        else:
            self.current_frame_index = index
            self.update_frame_display()

    def slider_changed(self):
        if self.current_frame_index is not None:
            self.save_preprocessing_settings(self.current_frame_index)
            self.update_selected_frame()

    def update_frame_display(self):
        camera_index = self.current_frame_index % len(self.cameras)
        camera = self.cameras[camera_index]
        if camera.isOpened():
            ret, frame = camera.read()
            if ret:
                frame = self.process_frame(frame, self.current_frame_index)
                self.display_frame(frame, self.current_frame_index)

    def toggle_region_selection(self):
        self.selectingRegion = not self.selectingRegion
        if not self.selectingRegion:
            self.select_region_index = None

    def toggle_transformation(self, index):
        self.apply_transformations[index] = not self.apply_transformations[index]
        self.save_preprocessing_settings(index)

    def rotate_image(self, image, angle):
        return rotate_bound(image, angle)
        #return rotate(image, angle)

    def save_preprocessing_settings(self, index):
        self.preprocessing_settings[index] = {
            'binary': self.slider_binary.value(),
            'rotation': self.slider_rotation.value(),
            'dilation': self.slider_dilation.value(),
            'closing': self.slider_closing.value(),
            'opening': self.slider_opening.value(),
            'noise': self.slider_noise.value()
        }

    def on_radioButton_toggled(self, checked):
        if self.current_frame_index is not None:
            self.apply_transformations[self.current_frame_index] = checked

    def calculate_accuracy(self, recognized_text, expected_text):
        matched_chars = sum(1 for a, b in zip(recognized_text, expected_text) if a == b)
        return matched_chars / max(len(recognized_text), len(expected_text))

    def update_frame(self):
        for i, video_container in enumerate(self.videoContainers):
            camera_index = self.camera_container_map[i]
            camera = self.cameras[camera_index]
            if camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    frame = self.process_frame(frame, i)
                    self.display_frame(frame, i)

    def update_selected_frame(self):
        camera_index = self.camera_container_map[self.current_frame_index]
        camera = self.cameras[camera_index]
        if camera.isOpened():
            ret, frame = camera.read()
            if ret:
                frame = self.process_frame(frame, self.current_frame_index)
                self.display_frame(frame, self.current_frame_index)

    def select_regions(self):
        if self.selectingRegion and self.select_region_index is not None:
            camera_index = self.camera_container_map[self.select_region_index]
            camera = self.cameras[camera_index]
            if camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    r = cv2.selectROI(f"Select ROI for Camera {camera_index}", frame, False)
                    cv2.destroyWindow(f"Select ROI for Camera {camera_index}")

                    if r[2] and r[3]:
                        self.ROIs[self.select_region_index] = r
                    else:
                        self.ROIs[self.select_region_index] = None

                    self.selectingRegion = False
                    self.select_region_index = None


    def process_frame(self, frame, index):
        if self.ROIs and self.ROIs[index]:
            r = self.ROIs[index]
            frame = frame[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.apply_transformations[index]:
            gray_frame = self.apply_transforms(gray_frame, index)
        return gray_frame

    def display_frame(self, gray_frame, index):
        height, width = gray_frame.shape
        bytes_per_line = gray_frame.strides[0]
        q_image = QImage(gray_frame.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

        pixmap = QPixmap.fromImage(q_image)
        pixmap = pixmap.scaled(self.videoContainers[index].width(), self.videoContainers[index].height(),
                               Qt.KeepAspectRatio)
        self.videoContainers[index].setPixmap(pixmap)

        # if self.radioButton_recognition.isChecked():
        #     recognized_text = pytesseract.image_to_string(gray_frame, config='--oem 1 --psm 7')
        # else:
        #     recognized_text = ""
        #recognized_text = ""

        #self.text_results[index].setText(recognized_text)

    def apply_transforms(self, img, index):
        settings = self.preprocessing_settings[index]
        #img = apply_binary_threshold(img, settings['binary'])
        if 'rotation' in settings:
            img = self.rotate_image(img, settings['rotation'])
        #img = apply_dilation(img, settings['dilation'])
        #img = apply_closing(img, settings['closing'])
        #img = apply_opening(img, settings['opening'])
        #img = reduce_noise(img, settings['noise'])
        return img

    #убрать
    def display_results(self, images, recognized_texts):
        for i, (img, recognized_text) in enumerate(zip(images, recognized_texts)):
            if i == 0:
                container = self.videoContainer_00
            elif i == 1:
                container = self.videoContainer_01
            elif i == 2:
                container = self.videoContainer_02
            elif i == 3:
                container = self.videoContainer_03
            else:
                continue

            expected_text = "мяу"
            accuracy = self.calculate_accuracy(recognized_text, expected_text)
            accuracy_percentage = round(accuracy * 100, 2)
            self.text_result.setText(recognized_text)

            height, width = img.shape
            bytes_per_line = width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            pixmap = pixmap.scaled(container.width(), container.height(), Qt.KeepAspectRatio)
            container.setPixmap(pixmap)




    def save_frames(self):
        nameList = ['00_M18X1.5',  '01_CN_ZN',  '02_id000494',  '03_MN',
                    '10_PW', '11_200', '12_BAR', '13_PH', '14_300',
                    '15_BAR', '16_0.52', '17_KG', '18_0.36', '19_L',
                    '20_ISO', '21_7866', '22_D', '23_2022_10', '24_0035']

        folder_name = f"saved_frames_{datetime.now().strftime('%H_%M_%S')}"
        os.makedirs(folder_name, exist_ok=True)

        for i, container in enumerate(self.videoContainers):
            pixmap = container.pixmap()
            if pixmap:
                frame = self.pixmap_to_cv(pixmap)
                frame_name = nameList[i]
                frame_path = os.path.join(folder_name, f"{frame_name}.jpg")
                cv2.imwrite(frame_path, frame)
                print(f"Saved: {frame_path}")

    def pixmap_to_cv(self, pixmap):
        qimage = pixmap.toImage()
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)
        arr = np.array(ptr).reshape((height, width, 4))
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)



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