import torch
from PIL import Image, ImageDraw, ImageFont
from ts.yolo import YOLO

device = torch.device('cuda')  # 用gpu请改cuda

yoloCls = ['orange_A', 'orange_B', 'orange_C', 'peach_A', 'peach_B', 'peach_C', 'pear_A', 'pear_B', 'pear_C',
           'apple_A', 'apple_B', 'apple_C', 'tomato_A', 'tomato_B', 'tomato_C', 'watermelon_A', 'watermelon_B', 'watermelon_C',
           'lemon_A', 'lemon_B', 'lemon_C', 'papaya_A', 'papaya_B', 'papaya_C', 'dz_A', 'dz_B', 'dz_C', 'guava_A', 'guava_B', 'guava_C',
           'pomegranate_A', 'pomegranate_B', 'pomegranate_C', 'plum_A', 'plum_B', 'plum_C']
clsDict = {0: 'apple_A', 1: 'apple_B', 2: 'apple_C', 3: 'dz_A', 4: 'dz_B', 5: 'dz_C', 6: 'guava_A', 7: 'guava_B', 8: 'guava_C', 9: 'lemon_A',
           10: 'lemon_B', 11: 'lemon_C', 12: 'orange_A', 13: 'orange_B', 14: 'orange_C', 15: 'papaya_A', 16: 'papaya_B', 17: 'papaya_C',
           18: 'peach_A', 19: 'peach_B', 20: 'peach_C', 21: 'pear_A', 22: 'pear_B', 23: 'pear_C', 24: 'plum_A', 25: 'plum_B', 26: 'plum_C',
           27: 'pomegranate_A', 28: 'pomegranate_B', 29: 'pomegranate_C', 30: 'tomato_A', 31: 'tomato_B', 32: 'tomato_C', 33: 'watermelon_A',
           34: 'watermelon_B', 35: 'watermelon_C'}

def predictNewModel(originImg):
    yolo = YOLO()
    # image = Image.open(originImg)
    position, label = yolo.getXY(originImg)
    print(position, label)
    return position, label

# 画框
def drawBoxes(image, boxes_info):
    draw = ImageDraw.Draw(image)

    # 加载字体（如果找不到arial.ttf，则使用默认字体）
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    # 逐个画框
    for box in boxes_info:
        y1, x1, y2, x2, label = box
        # 画框
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        # 标类别
        draw.text((x1, y1 - 15), label, fill="red", font=font)

    return image


# 单张图片
def singleImg(originImg):
    position, label = predictNewModel(originImg)
    resList = []
    if position is not None:
        for i in range(len(label)):
            c = label[i]
            box = position[i]
            resItem = box.tolist()
            resItem.append(yoloCls[c])
            resList.append(resItem)
    else:
        print("未检测到")
    return drawBoxes(originImg, resList)

if __name__ == '__main__':
    image_path = r"img/guava_6.jpg"
    image = Image.open(image_path)
    processedImg = singleImg(image)
    processedImg.show()