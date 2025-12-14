import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io

def improve_image(image_bytes):
    """
    Основная функция для улучшения размытых изображений.
    Принимает изображение в виде байтов, возвращает улучшенное изображение в виде байтов.
    """
    
    # Конвертируем байты в изображение OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Метод 1: Увеличение резкости с помощью фильтра Unsharp Mask
    blurred = cv2.GaussianBlur(img, (0, 0), 3)
    sharpened = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
    
    # Метод 2: Улучшение контраста с помощью CLAHE (ограниченного адаптивного выравнивания гистограммы)
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Применяем CLAHE к L-каналу (яркость)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    
    # Объединяем каналы обратно
    lab_enhanced = cv2.merge([l_enhanced, a, b])
    result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    
    # Метод 3: Легкое шумоподавление
    result = cv2.fastNlMeansDenoisingColored(result, None, 10, 10, 7, 21)
    
    # Конвертируем обратно в байты
    _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return buffer.tobytes()

def simple_sharpen(image_bytes):
    """
    Упрощенная версия для быстрой обработки.
    Хорошо работает с слегка размытыми изображениями.
    """
    # Открываем изображение с помощью PIL
    image = Image.open(io.BytesIO(image_bytes))
    
    # Увеличиваем резкость
    enhancer = ImageEnhance.Sharpness(image)
    sharpened = enhancer.enhance(2.0)  # Коэффициент 2.0 увеличивает резкость
    
    # Увеличиваем контраст
    contrast_enhancer = ImageEnhance.Contrast(sharpened)
    final_image = contrast_enhancer.enhance(1.2)  # Немного увеличиваем контраст
    
    # Сохраняем в байты
    byte_arr = io.BytesIO()
    final_image.save(byte_arr, format='JPEG', quality=95)
    return byte_arr.getvalue()

def get_image_info(image_bytes):
    """Возвращает информацию об изображении"""
    image = Image.open(io.BytesIO(image_bytes))
    return {
        'format': image.format,
        'size': image.size,
        'mode': image.mode
    }