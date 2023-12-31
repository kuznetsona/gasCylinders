import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    text = pytesseract.image_to_string(frame, lang='rus')

    str_target = "какая-то строка"

    matches = sum(1 for a, b in zip(str_target, text) if a == b)
    percentage = (matches / len(str_target)) * 100

    # print("Распознанный текст:", text)
    # print("Процент совпадений:", percentage)
    # print("--------------------------------")

    text_to_display = f"Accuracy: {percentage:.2f}%\n{text}"

    cv2.putText(frame, text_to_display, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)


    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q', чтобы выйти из цикла
        break

cap.release()
cv2.destroyAllWindows()
