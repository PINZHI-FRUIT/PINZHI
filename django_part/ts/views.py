import torch.cuda
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect
import json
from ts.YOLODetector import YOLODetector
from ts.models import userInfo
from PIL import Image,ImageEnhance
import io
# from ts.predictImg import singleImg
# Create your views here.
def login(request):
    if request.method == "GET":
        return render(request,"login.html")
    elif request.method == "POST":
        name = request.POST.get("loginUsername")
        pwd = request.POST.get("loginPassword")
        user = userInfo.objects.filter(name=name,pwd=pwd).first()
        if user:
            return redirect('/home')
        else:
            return redirect('/login')

def register(request):
    if request.method == "GET":
        return render(request,"register.html")
    elif request.method == "POST":
        name = request.POST.get("registerUsername")
        pwd = request.POST.get("registerPassword")
        print(name,pwd)
        user = userInfo.objects.create(name=name,pwd=pwd)
        print(user)
        if user:
            return redirect('/home')
        else:
            return redirect('/register')

def home(request):
    if request.method == "GET":
        return render(request,"home.html")
    elif request.method == "POST":
        image = request.FILES.get('image')
        if image:
            print(image)
            return JsonResponse({"message": "上传成功"})
        else:
            return JsonResponse({"message": "上传失败，未找到图片"}, status=400)

# def process_image(request):
#     if request.method == "GET":
#         return render(request,'pics.html')
#     if request.method == "POST" and request.FILES.get("image"):
#         uploaded_image = request.FILES["image"]
#         image = Image.open(uploaded_image)
#         print(image)
#
#         #处理图片
#         processedImg = singleImg(image)
#
#         # 转换为 BytesIO 对象
#         img_io = io.BytesIO()
#         processedImg.save(img_io, format="PNG")
#         img_io.seek(0)
#         return HttpResponse(img_io.getvalue(), content_type="image/png")

def detect_image(request):
    if request.method == "GET":
        return render(request,"pics.html")
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]
        image = Image.open(uploaded_file)

        # 调用检测类
        detector = YOLODetector()
        response_data = detector.detect(image)
        response_data["processed_image"] = str(response_data["processed_image"])
        print(response_data)
        return JsonResponse(response_data, json_dumps_params={"ensure_ascii": False},content_type="application/json",safe=False)
    return JsonResponse({"error": "请使用 POST 上传图片"}, status=400)

