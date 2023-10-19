import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

font_path = "path_to_your_font.ttf"
font_size = 30
font = ImageFont.truetype(font_path, font_size)

str_target = "ЧИСТЫЙ\nКОД\n\nСОЗДАНИЕ, АНАЛИЗ\nИ РЕФАКТОРИНГ"


def process_frame(frame, cam_name):
    text = pytesseract.image_to_string(frame, lang='rus')
    matches = sum(1 for a, b in zip(str_target, text) if a == b)
    percentage = (matches / len(str_target)) * 100

    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)
    draw.text((10, 10), f"{cam_name} Accuracy: {percentage:.2f}%", font=font, fill=(0, 255, 0))

    return cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR), percentage


while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret1 or not ret2:
        break

    frame1, percentage1 = process_frame(frame1, "Camera 1")
    frame2, percentage2 = process_frame(frame2, "Camera 2")

    #print(f"Camera 1 Percentage: {percentage1:.2f}%")
    #print(f"Camera 2 Percentage: {percentage2:.2f}%")
    #print(f"Overall Percentage: {(percentage1 + percentage2) / 2:.2f}%")
    #print("--------------------------------")

    cv2.imshow('Camera 1', frame1)
    cv2.imshow('Camera 2', frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap1.release()
cap2.release()
cv2.destroyAllWindows()