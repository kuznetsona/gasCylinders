import cv2
import numpy as np


def apply_binary_threshold(gray_image, threshold_value):
    new_threshold_value = int((threshold_value / 100) * 255)
    _, binary = cv2.threshold(gray_image, new_threshold_value, 255, cv2.THRESH_BINARY)
    return binary


def reduce_noise(gray_image, noise_value):
    adjusted_noise_value = max(1, int(noise_value / 20))
    return cv2.GaussianBlur(gray_image, (adjusted_noise_value | 1, adjusted_noise_value | 1), 0)


def adjust_contrast(image, contrast_value):
    alpha = (contrast_value * 3) / 100.0
    beta = 0
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def apply_dilation(image, dilation_value):
    adjusted_dilation_value = dilation_value // 10
    kernel = np.ones((adjusted_dilation_value, adjusted_dilation_value), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


def apply_closing(image, closing_value):
    adjusted_closing_value = closing_value // 10
    kernel = np.ones((adjusted_closing_value, adjusted_closing_value), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)


def apply_opening(image, opening_value):
    adjusted_opening_value = opening_value // 10
    kernel = np.ones((adjusted_opening_value, adjusted_opening_value), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)



