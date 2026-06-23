from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2


@dataclass
class PlateResult:
    processed_filename: str
    crop_filename: str
    plate_text: str
    status: str


def _safe_read(image_path: Path):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError("无法读取图片，请检查图片路径或文件格式。")
    return image


def process_image(image_path: Path, processed_dir: Path) -> PlateResult:
    processed_dir.mkdir(parents=True, exist_ok=True)

    image = _safe_read(image_path)
    original = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 100, 200)

    contours, _ = cv2.findContours(
        edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

    candidate = None
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.018 * perimeter, True)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h) if h else 0

        # 适合大学生项目展示的简单筛选逻辑
        if len(approx) == 4 and 2.0 <= aspect_ratio <= 6.0 and w > 60 and h > 20:
            candidate = (x, y, w, h)
            break

    stem = image_path.stem
    processed_filename = f"{stem}_processed.jpg"
    crop_filename = f"{stem}_plate.jpg"
    processed_path = processed_dir / processed_filename
    crop_path = processed_dir / crop_filename

    if candidate:
        x, y, w, h = candidate
        plate_crop = original[y : y + h, x : x + w]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite(str(crop_path), plate_crop)
        plate_text = "DEMO-PLATE"
        status = "识别成功（演示结果）"
    else:
        fallback = original.copy()
        h, w = fallback.shape[:2]
        crop = fallback[max(0, h // 3) : min(h, h // 3 * 2), max(0, w // 4) : min(w, w // 4 * 3)]
        cv2.imwrite(str(crop_path), crop)
        plate_text = "未识别"
        status = "未检测到明确车牌区域"

    cv2.imwrite(str(processed_path), image)

    return PlateResult(
        processed_filename=processed_filename,
        crop_filename=crop_filename,
        plate_text=plate_text,
        status=status,
    )
