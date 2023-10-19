import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
cap = cv2.VideoCapture(1)


def preprocess_frame(frame):
    frame = cv2.convertScaleAbs(frame, alpha=1, beta=10)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return binary
    #return gray


while True:
    ret, frame = cap.read()

    if not ret:
        break

    preprocessed_frame = preprocess_frame(frame)

    text = pytesseract.image_to_string(preprocessed_frame, lang='rus')

    str_target = "Святой источник"

    matches = sum(1 for a, b in zip(str_target, text) if a == b)
    percentage = (matches / len(str_target)) * 100

    # print("Распознанный текст:", text)
    # print("Процент совпадений:", percentage)
    # print("--------------------------------")

    text_to_display = f"Accuracy: {percentage:.2f}%\n{text}"

    cv2.putText(frame, text_to_display, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    cv2.putText(preprocessed_frame, text_to_display, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    cv2.imshow('Original', frame)
    cv2.imshow('Preprocessed', preprocessed_frame)

    #print(text)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q', чтобы выйти из цикла
        break

cap.release()
cv2.destroyAllWindows()
