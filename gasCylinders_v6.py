from PyQt5 import uic
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QDialog


class SelectRegionDialog(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        uic.loadUi('ui_files/selectRegionWidget.ui', self)
        print("Original Pixmap Size:", pixmap.size())

        ixmap_original_size = pixmap.size()
        self.pixmap_original_width = pixmap.width()
        self.pixmap_original_height = pixmap.height()
        print(f"height '{self.pixmap_original_height}' width '{self.pixmap_original_width}' ")

        self.scaled_pixmap = pixmap.scaled(400, 300)
        # self.scaled_pixmap = pixmap.scaled(pixmap.size())
        print("ScaledPixmap Size:", self.scaled_pixmap.size())

        self.scaled_pixmap_width = self.scaled_pixmap.width()
        self.scaled_pixmap_height = self.scaled_pixmap.height()
        print(f"height '{self.scaled_pixmap_height}' width '{self.scaled_pixmap_width}' ")

        self.label.setPixmap(self.scaled_pixmap)
        self.selected_region = None
        self.start_point = None
        self.end_point = None
        self.is_selecting = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = True
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        temp_pixmap = self.scaled_pixmap.copy()
        painter = QPainter(temp_pixmap)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)
        if self.start_point and self.end_point:
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
        painter.end()
        self.label.setPixmap(temp_pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = self.end_point.x(), self.end_point.y()
            x2 = min(x2, self.scaled_pixmap_width)
            y2 = min(y2, self.scaled_pixmap_height)
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x1 - x2)
            height = abs(y1 - y2)
            x_scale = 640 / self.scaled_pixmap_width
            y_scale = 480 / self.scaled_pixmap_height
            orig_x = round(x * x_scale)
            orig_y = round(y * y_scale)
            orig_width = round(width * x_scale)
            orig_height = round(height * y_scale)
            self.selected_region = QRect(orig_x, orig_y, orig_width, orig_height)
            self.close()

    def get_selected_region(self):
        return self.selected_region


class Effect:
    def __init__(self):
        pass

    def apply(self, image: QImage) -> QImage:
        raise Exception("Should be implemented")


class CropEffect(Effect):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def apply(self, image: QImage) -> QImage:
        return


class ContainerEffects:
    def __init__(self, crop_effect: CropEffect):
        self.crop_effect = crop_effect


class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('ui_files/glasCylinders_v5.ui', self)

        self.camera_dict = {
            "Camera 1": r"@device:pnp:\\?\usb#vid_32e6&pid_9005&mi_00#6&19df1aaf&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global",
            "Camera 2": r"@device:pnp:\\?\usb#vid_32e6&pid_9005&mi_00#6&7256a0a&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global",
            "Camera 3": r"@device:pnp:\\?\usb#vid_1902&pid_8301&mi_00#6&2111536c&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global",
            "webcam": r"@device:pnp:\\?\usb#vid_0bda&pid_58d2&mi_00#6&26b38be2&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global",
            "red cam": r"@device:pnp:\\?\usb#vid_0bda&pid_58b0&mi_00#6&25249c4a&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global"

        }
        # с хабом
        # self.camera_dict = {
        #     "Camera 1": r"@device:pnp:\\?\usb#vid_32e6&pid_9005&mi_00#7&1427508e&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global",
        #     "Camera 3": r"@device:pnp:\\?\usb#vid_1902&pid_8301&mi_00#7&256e0bc&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global",
        #     "Camera 2": r"@device:pnp:\\?\usb#vid_32e6&pid_9005&mi_00#7&16d9fe9&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global",
        #     "webcam": r"@device:pnp:\\?\usb#vid_0bda&pid_58d2&mi_00#6&26b38be2&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global"
        # }

        self.find_camera_by_name()

        self.videoContainers_1 = [
            self.videoContainer_00,
            self.videoContainer_10, self.videoContainer_11, self.videoContainer_12,
            self.videoContainer_20
        ]
        self.effects_1 = [
            ContainerEffects([CropEffect(0, 0, 1e5, 1e5)]) for vc in self.videoContainers_1
        ]

        self.videoContainers_2 = [
            self.videoContainer_01,
            self.videoContainer_13, self.videoContainer_14, self.videoContainer_15,
            self.videoContainer_21, self.videoContainer_22
        ]
        self.effects_2 = [
            ContainerEffects([CropEffect(0, 0, 1e5, 1e5)]) for vc in self.videoContainers_2
        ]
        self.videoContainers_3 = [
            self.videoContainer_02, self.videoContainer_03,
            self.videoContainer_16, self.videoContainer_17, self.videoContainer_18, self.videoContainer_19,
            self.videoContainer_23, self.videoContainer_24
        ]
        self.effects_3 = [
            ContainerEffects([CropEffect(0, 0, 1e5, 1e5)]) for vc in self.videoContainers_3
        ]

        self.camera_container_map = {
            0: "webcam", 1: "Camera 1", 2: "Camera 2", 3: "Camera 3"
        }
        self.cameras = {}
        self.camera_name_list = ["red cam", "webcam", "Camera 3"]
        self.videoContainers_list = [self.videoContainers_1, self.videoContainers_2, self.videoContainers_3]
        # self.all_containers_effects = [self.effects_1, self.effects_2, self.effects_3]
        #
        # x, y
        # vc = self.videoContainers_list[x][y]
        # effects = self.all_containers_effects[x][y]
        # effects.crop_effect=CropEffect(x1=,)

        self.camera_connected = {}

        self.camera_states = {}
        self.message_boxes = {}
        self.search_timers = {}

        self.ROIs = {}

        self.initialize_and_start_cameras()

        self.pushButton_apply.clicked.connect(self.save_frames)

        for videoContainers in self.videoContainers_list:
            for i, container in enumerate(videoContainers):
                container.mouseDoubleClickEvent = lambda event, container=container: self.select_frame_region(
                    container)
            # for i, container in enumerate(videoContainers):
            #     container.mouseDoubleClickEvent = lambda event, index=i, vc=videoContainers: self.select_frame_region(
            #         index, vc)

    def select_frame_region(self, container):
        #container = videoContainers[index]
        pixmap = container.pixmap()
        if pixmap:
            dialog = SelectRegionDialog(pixmap)
            dialog.exec_()

            selected_region = dialog.get_selected_region()
            if selected_region:
                self.set_ROI_for_container(container, selected_region)
            print("select_frame_region :", selected_region)

    # def get_something(self, index: index) ->:

    def set_ROI_for_container(self, container, roi):
        self.ROIs[container] = roi
        print("self.ROIs[index] :", self.ROIs[container])

    def initialize_and_start_cameras(self):
        for i, camera_name in enumerate(self.camera_name_list):
            self.camera_connected[camera_name] = True
            self.init_camera(camera_name, self.videoContainers_list[i])

    def init_camera(self, camera_name, video_containers):
        camera = self.get_camera_by_name(camera_name)
        if camera is None:
            print(f"Camera named '{camera_name}' not found.")
            return

        camera.statusChanged.connect(lambda status: self.handle_camera_status_change(camera_name, status))

        capture = QCameraImageCapture(camera)
        capture.imageCaptured.connect(lambda id, image: self.display_image(id, image, video_containers))

        timer = QTimer(self)
        timer.timeout.connect(capture.capture)
        timer.start(100)

        camera.start()

        self.cameras[camera_name] = {'camera': camera, 'capture': capture, 'timer': timer}

    def handle_camera_status_change(self, camera_name, status):

        # self.camera_connected[camera_name] = True
        if status == QCamera.UnloadedStatus:
            print(f"Camera '{camera_name}' disconnected.")
            print(f"'{camera_name}' status '{status}'")
            self.camera_connected[camera_name] = False
            self.inform_user_and_search_camera(camera_name)

        elif (status in (QCamera.ActiveStatus, QCamera.LoadedStatus)
              and not self.camera_connected[camera_name]):
            print(f"Camera '{camera_name}' reconnected.")
            # self.camera_connected[camera_name] = True
            # self.reinitialize_camera(camera_name)

    def reinitialize_camera(self, camera_info, camera_name):
        if camera_info is not None:
            if hasattr(self, 'message_box') and self.message_box.isVisible():
                self.message_box.accept()
                del self.message_box
                print("Closing message box.")
            camera = QCamera(camera_info)
            camera_index = self.camera_name_list.index(camera_name)
            video_containers = self.videoContainers_list[camera_index]
            self.init_camera(camera_name, video_containers)

        else:
            print("Camera info is not available for reinitialization.")

    def search_for_camera(self, camera_name):
        camera_device = self.camera_dict.get(camera_name)
        available_cameras = QCameraInfo.availableCameras()
        for camera_info in available_cameras:
            if camera_info.deviceName() == camera_device:
                self.search_timer.stop()
                self.reinitialize_camera(camera_info, camera_name)
                break

    def inform_user_and_search_camera(self, camera_name):
        self.message_box = QMessageBox(self)
        self.message_box.setWindowTitle("Camera Disconnected")
        self.message_box.setStyleSheet("color: black;")
        self.message_box.setText(f"Camera '{camera_name}' has been disconnected. Please reconnect it.")
        self.message_box.setStandardButtons(QMessageBox.NoButton)  # Убираем стандартные кнопки
        self.message_box.show()

        self.search_timer = QTimer(self)
        self.search_timer.timeout.connect(lambda: self.search_for_camera(camera_name))
        self.search_timer.start(3000)

    def get_camera_by_name(self, camera_name):
        device_name = self.camera_dict.get(camera_name)
        if device_name:
            for camera_info in QCameraInfo.availableCameras():
                if camera_info.deviceName() == device_name:
                    return QCamera(camera_info)
        return None

    def capture_image(self):
        self.capture.capture()

    def display_image(self, id, image, video_containers):
        image = image.convertToFormat(QImage.Format_Grayscale8)

        for i, container in enumerate(video_containers):
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaledToWidth(container.width())  # Масштабируем по умолчанию

            if container in self.ROIs:
                roi = self.ROIs[container]
                #if roi_containers is video_containers:
                x, y, width, height = roi.getRect()
                cropped_pixmap = pixmap.copy(x, y, width, height)
                scaled_pixmap = cropped_pixmap.scaledToWidth(
                    container.width())

            container.setPixmap(scaled_pixmap)

    # def display_frame(self, gray_frame, index):
    #     height, width = gray_frame.shape
    #     bytes_per_line = gray_frame.strides[0]
    #     q_image = QImage(gray_frame.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
    #
    #     pixmap = QPixmap.fromImage(q_image)
    #     pixmap = pixmap.scaled(self.videoContainers[index].width(), self.videoContainers[index].height(),
    #                            Qt.KeepAspectRatio)
    #     self.videoContainers[index].setPixmap(pixmap)

    def find_camera_by_name(self):
        available_cameras = QCameraInfo.availableCameras()
        for camera_info in available_cameras:
            print('deviceName ', camera_info.deviceName())
            print('description ', camera_info.description())
            print('position  ', camera_info.position())
            print('defaultCamera ', camera_info.defaultCamera())
            print('-------')
        return None

    def on_camera_reconnected(self, camera_name):
        print(f"Camera '{camera_name}' reconnected. Resuming capture...")
        camera_index = self.camera_name_list.index(camera_name)
        video_containers = self.videoContainers_list[camera_index]
        self.init_camera(camera_name, video_containers)

    def get_video_containers_by_camera_name(self, camera_name):
        index = self.camera_name_list.index(camera_name)
        return self.videoContainers_list[index]

    def save_frames(self):
        nameList = ['00_M18X1.5', '01_CN_ZN', '02_id000494', '03_MN',
                    '10_PW', '11_200', '12_BAR', '13_PH', '14_300',
                    '15_BAR', '16_0.52', '17_KG', '18_0.36', '19_L',
                    '20_ISO', '21_7866', '22_D', '23_2022_10', '24_0035']

        folder_name = f"saved_frames_{datetime.now().strftime('%H_%M_%S')}"
        os.makedirs(folder_name, exist_ok=True)

        index = 0
        for videoContainers in self.videoContainers_list:
            for container in videoContainers:
                if index >= len(nameList):
                    print("Not enough names for all video containers.")
                    break

                pixmap = container.pixmap()
                if pixmap:
                    frame_name = nameList[index]
                    frame_path = os.path.join(folder_name, f"{frame_name}.jpg")
                    pixmap.save(frame_path, "JPEG")  # Сохраняем QPixmap напрямую
                    print(f"Saved: {frame_path}")

                index += 1

    def closeEvent(self, event):
        for camera_name, camera_info in self.cameras.items():
            camera_check_thread = camera_info.get('check_thread')
            if camera_check_thread and camera_check_thread.isRunning():
                camera_check_thread.stop()
                camera_check_thread.wait()
        super(CameraWindow, self).closeEvent(event)


app = QApplication(sys.argv)
window = CameraWindow()
window.show()
sys.exit(app.exec_())
