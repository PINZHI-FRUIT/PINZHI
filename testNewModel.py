import torch
import cv2
from torch import optim, nn
import visdom
import torchvision
from torch.utils.data import DataLoader
import os
from PIL import Image, ImageDraw, ImageFont

import ViT.ViTForWithLSDandSPT as ViTForWithLSDandSPT

from torchvision import transforms
from PIL import Image
from yolo import YOLO
from nets.yolo import YoloBody

device = torch.device('cpu')#用gpu请改gpu

yoloCls=['orange_A','orange_B','orange_C','peach_A','peach_B','peach_C','pear_A','pear_B','pear_C'
        ,'apple_A','apple_B','apple_C','tomato_A','tomato_B','tomato_C','watermelon_A','watermelon_B','watermelon_C','lemon_A','lemon_B','lemon_C'
        ,'papaya_A','papaya_B','papaya_C','dz_A','dz_B','dz_C','guava_A','guava_B','guava_C'
        ,'pomegranate_A','pomegranate_B','pomegranate_C','plum_A','plum_B','plum_C']
clsDict={0: 'apple_A', 1: 'apple_B', 2: 'apple_C', 3: 'dz_A', 4: 'dz_B', 5: 'dz_C', 6: 'guava_A', 7: 'guava_B', 8: 'guava_C', 9: 'lemon_A', 10: 'lemon_B', 11: 'lemon_C', 12: 'orange_A', 13: 'orange_B', 14: 'orange_C', 15: 'papaya_A', 16: 'papaya_B', 17: 'papaya_C', 18: 'peach_A', 19: 'peach_B', 20: 'peach_C', 21: 'pear_A', 22: 'pear_B', 23: 'pear_C', 24: 'plum_A', 25: 'plum_B', 26: 'plum_C', 27: 'pomegranate_A', 28: 'pomegranate_B', 29: 'pomegranate_C', 30: 'tomato_A', 31: 'tomato_B', 32: 'tomato_C', 33: 'watermelon_A', 34: 'watermelon_B', 35: 'watermelon_C'}
OriginImg=""
ImgForVitList=[]
resList=[]
outputDir=r"cutImgForVit"#分割图的存放目录
outPutImg=r"afterDrawImg\res1.jpg"

def GetImg(path,size):
    tf = transforms.Compose([
        lambda x: Image.open(x).convert('RGB'),
        transforms.Resize((int(size* 1.25), int(size * 1.25))),
        transforms.RandomRotation(15),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.630, 0.461, 0.297],
                             std=[0.195, 0.205, 0.201])
    ])
    img=tf(path)
    return img


def draw_boxes(image_path, boxes_info, output_path):
    # 打开图片
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # 加载字体
    font = ImageFont.load_default()

    # 逐个画框
    for box in boxes_info:
        y1,x1,y2,x2,label = box
        # 画框
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        # 标类别
        draw.text((x1, y1 - 15), label, fill="red", font=font)

    # 保存结果
    img = img.convert('RGB')
    img.save(output_path)
    print("Image with boxes saved to:", output_path)
    return img

def predictNewModel(OriginImg,yolo):
    # model = Model2(
    #     image_size=416,
    #     patch_size=16,
    #     num_classes=36,
    #     dim=1024,
    #     depth=6,
    #     heads=16,
    #     mlp_dim=2048,
    #     dropout=0.1,
    #     emb_dropout=0.1)
    # modelPath = r"..\logs\8715.pth"
    # model.load_state_dict(torch.load(modelPath, map_location=device),strict=False)

    # model=YoloBody([[6, 7, 8], [3, 4, 5], [0, 1, 2]], 36)
    # #图片预处理
    # img=GetImg(OriginImg,size=416)
    # img = img.unsqueeze(0)
    # print("img.shape:"+str(img.shape)) #img.shape:torch.Size([1, 3, 416, 416])
    #
    #
    # #过一遍forward
    # model.eval()
    # res1,res2,res3=model(img)
    #
    # print("res1.shape:"+str(res1.shape))
    # print("res2.shape:"+str(res2.shape))
    # print("res3.shape:"+str(res3.shape))

    # 处理3个res 为 x0,y0,x1,y1,cls



    image=Image.open(OriginImg)
    position,label=yolo.getXY(image)
    print(position)
    print(label)
    return position,label


#单张
def main():
    OriginImg=r"img\tomato_44.jpg"
    outputImg=r"img\output2_tomato_44.png"
    yolo = YOLO()
    position,label=predictNewModel(OriginImg,yolo)
    resList=[]
    if position is not None:
        for i in range(len(label)):
            c = label[i]
            box = position[i]
            resItem = box.tolist()
            resItem.append(yoloCls[c])
            resList.append(resItem)
    else:
        print("未检测到")
    draw_boxes(OriginImg,resList,outputImg)
    return resList


import os
from glob import glob

import os
import shutil

def copy_selected_images(txt_file, src_folder, dest_folder):
    # 确保目标文件夹存在
    os.makedirs(dest_folder, exist_ok=True)

    # 读取需要的图片名称
    with open(txt_file, "r") as f:
        image_names = [line.strip() + ".jpg" for line in f.readlines()]  # 加上 .jpg 扩展名

    # 遍历并复制符合条件的图片
    for image_name in image_names:
        src_path = os.path.join(src_folder, image_name)
        dest_path = os.path.join(dest_folder, image_name)

        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"复制: {src_path} -> {dest_path}")
        else:
            print(f"文件不存在: {src_path}")


#批量
def main2():
    #先挑出测试集图片
    # txt_file = r"img/docs/test.txt"  # 记录所需图片的文本文件
    # src_folder = r"img/JPEGImages"  # 源图片文件夹
    # dest_folder = r"img\input"  # 目标文件夹
    #
    # copy_selected_images(txt_file, src_folder, dest_folder)


    #
    input_folder = r"img\appleInput"
    output_folder = r"img\appleOutput"

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 读取 input 文件夹内所有图片文件（假设是 png/jpg/jpeg）
    image_files = glob(os.path.join(input_folder, "*.*"))
    yolo = YOLO()
    for image_path in image_files:
        # 获取文件名（不含扩展名）
        file_name = os.path.splitext(os.path.basename(image_path))[0]
        # 生成对应的输出文件路径
        output_img = os.path.join(output_folder, f"{file_name}_output.png")

        # 进行预测
        position, label = predictNewModel(image_path,yolo)
        resList = []

        if position is not None:
            for i in range(len(label)):
                c = label[i]
                box = position[i]
                resItem = box.tolist()
                resItem.append(yoloCls[c])
                resList.append(resItem)
        else:
            print(f"未检测到物体: {image_path}")

        # 绘制结果并保存
        draw_boxes(image_path, resList, output_img)
        print(f"处理完成: {image_path} -> {output_img}")





if __name__=='__main__':
    # l=main()   #单张
    # print(l)
    main2()    #批量

