import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)


def preprocess_frame(frame):
    frame = cv2.convertScaleAbs(frame, alpha=1, beta=10)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return binary


def process_frame(frame, str_target):
    preprocessed_frame = preprocess_frame(frame)

    #text = pytesseract.image_to_string(preprocessed_frame, lang='rus')
    text = pytesseract.image_to_string(frame)
    matches = sum(1 for a, b in zip(str_target, text) if a == b)
    percentage = (matches / len(str_target)) * 100
    text_to_display = f"Accuracy: {percentage:.2f}%\n{text}"

    cv2.putText(frame, text_to_display, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    #cv2.putText(preprocessed_frame, text_to_display, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    return frame, preprocessed_frame, text_to_display



str_target = "Святой источник"

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret1 or not ret2:
        break

    processed_left, preprocessed_left, text_to_display1 = process_frame(frame1, str_target)
    processed_right, preprocessed_right, text_to_display2 = process_frame(frame2, str_target)

    #cv2.imshow(f'Camera left - Processed', processed_left)
    #cv2.imshow('Camera left - Preprocessed', preprocessed_left)
    cv2.imshow(f'Camera right - Processed', processed_right)
    cv2.imshow('Camera right - Preprocessed', preprocessed_right)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap1.release()
cap2.release()
cv2.destroyAllWindows()
