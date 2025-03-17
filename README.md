## README

### 品智——基于YOLOv3和ViT的多种水果品质等级分类系统 

——网上水果识别检测的项目已经可以说是烂大街了，但是品质检测的比较少一点(*╹▽╹*)

#### 0.preview

![945b08bdee58efaa462794f6516f267](.\preview\preview.png)

#### 1.model_part

- 我们使用了带预训练权重的YOLOv3模型（Github链接：[bubbliiiing/yolo3-pytorch: 这是一个yolo3-pytorch的源码，可以用于训练自己的模型。](https://github.com/bubbliiiing/yolo3-pytorch)），但是对其中的backbone部分进行了修改，见model_part/nets/new_model.py
- 在backbone部分使用ViT模型，为的是将整张的图片分块后采用NLP中类似LSTM的思想和Attention机制来**处理局部信息和全局信息**
- 在datasets中有我们自制的数据集，里面包含了12种水果：苹果、橙子、梨、桃子、西红柿、石榴、冬枣、番石榴、李子、木瓜、西瓜、柠檬的A 、B、C三个类别，共36个类别的**图片和水果实例位置标注信息**，位置标注使用xml格式进行存储，训练集和数据集的划分用了原YOLOv3模型提供的voc_annatation.py文件进行处理（可能这个数据集是我们最重要的资源了╮(╯▽╰)╭）、
- 如果进行训练，需要把数据集放在\VOCdevkit\VOC2007路径下（其他一些细节参考**原YOLO模型**给出的README和问题汇总啦）
- logs文件夹中我们提供了一些我们训练出来的模型权重，在训练过程中我们最好达到了**验证集上87.15%**的准确率，应该基本够用(其实是燃尽了，炼丹只能到这个地步了)我们使用的是8631tmt.pth，因为87.15%的那个权重对西红柿识别率有点差，后面优化西红柿数据集后练出了8631tmt数据集，表示模型在验证集上的准确率达到86.31%，是针对tomato(简写为tmt嘻嘻\(\*^▽^*))优化了的模型权重
- my_utils文件夹下有一些我们项目过程中使用过的一些脚本，比如将各种图片**转为jpg图片格式、数据增强**等的函数，而其他文件夹都是原YOLOv3相关的一些py文件

#### 2.django_part

- 在这里用Python Django架构进行后端开发，运行这个项目你可以访问127.0.0.1:端口号/pics来访问这个项目页面，在页面中可以上传水果图片进行识别，能够识别的水果种类包括：**苹果、橙子、梨、桃子、西红柿、石榴、冬枣、番石榴、李子、木瓜、西瓜、柠檬**，每种水果分**A 、B、C三个类别**，后端会实例化模型进行识别和检测
- 当然，这里的视图函数需要一点修改（但是最近太忙），在分发出去的process_image函数中还调用了predictImg函数的接口，而在predictImg中又会实例化修改后的YOLO模型，这样每次请求都会去实例化并加载模型，而加载模型需要一点时间，应该在**项目启动时实例化一个模型**并让每次进来的请求都给这个实例去识别就行了，这样处理的时间会短很多

#### 3.一点未来的展望

- 我们的项目只能检测我们制作了数据集的这12种水果的3个等级，但是为了泛化模型的性能，采用当下热门的零样本学习（Zero-Shot Learning, ZSL）和少样本学习（Few-Shot Learning, FSL）方案可能可以让模型给其他水果种类进行等级分类✿✿ヽ(°▽°)ノ✿
