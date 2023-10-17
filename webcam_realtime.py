import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    text = pytesseract.image_to_string(frame, lang='rus')

    str = "ЧИСТЫЙ\nКОД\n\nСОЗДАНИЕ, АНАЛИЗ\nИ РЕФАКТОРИНГ"

    matches = sum(1 for a, b in zip(str, text) if a == b)
    percentage = (matches / len(str)) * 100

    print("Распознанный текст:", text)
    print("Процент совпадений:", percentage)
    print("--------------------------------")
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q', чтобы выйти из цикла
        break

cap.release()
cv2.destroyAllWindows()
