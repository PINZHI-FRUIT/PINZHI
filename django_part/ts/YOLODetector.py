import base64
import io
import torch
from PIL import Image, ImageDraw, ImageFont
from ts.yolo import YOLO

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class YOLODetector:
    _instance = None  # 单例实例
    yoloCls = ['orange_A', 'orange_B', 'orange_C', 'peach_A', 'peach_B', 'peach_C', 'pear_A', 'pear_B', 'pear_C',
               'apple_A', 'apple_B', 'apple_C', 'tomato_A', 'tomato_B', 'tomato_C', 'watermelon_A', 'watermelon_B', 'watermelon_C',
               'lemon_A', 'lemon_B', 'lemon_C', 'papaya_A', 'papaya_B', 'papaya_C', 'dz_A', 'dz_B', 'dz_C', 'guava_A', 'guava_B', 'guava_C',
               'pomegranate_A', 'pomegranate_B', 'pomegranate_C', 'plum_A', 'plum_B', 'plum_C']

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(YOLODetector, cls).__new__(cls, *args, **kwargs)
            cls._instance.yolo = YOLO()  # 加载模型
        return cls._instance

    def detect(self, image):
        """
        目标检测方法：输入 PIL.Image，返回处理后的图片 (base64) 和检测结果 (JSON)
        """
        position, label = self.yolo.getXY(image)
        if position is None or position.size == 0:
            return {"message": "未检测到目标", "processed_image": None}

        # 处理检测结果
        results = []
        for i in range(len(label)):
            box = position[i].tolist()
            results.append({
                "box": box,
                "class": self.yoloCls[label[i]]
            })

        # 画框
        processed_image = self.draw_boxes(image, [[*item["box"], item["class"]] for item in results])

        # 转 Base64
        buffered = io.BytesIO()
        processed_image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        return {
            "results": results,
            "processed_image": img_base64
        }

    def draw_boxes(self, image, boxes_info):
        """
        在图像上绘制检测框
        """
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 15)
        except IOError:
            font = ImageFont.load_default()

        for box in boxes_info:
            y1, x1, y2, x2, label = box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
            draw.text((x1, y1 - 15), label, fill="red", font=font)

        return image
