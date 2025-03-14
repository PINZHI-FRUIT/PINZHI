from math import sqrt
import torch
import torch.nn.functional as F
from torch import nn
from einops import rearrange, repeat
from einops.layers.torch import Rearrange

#---------------------模型组件-----------------------#
def pair(t):
    return t if isinstance(t, tuple) else (t, t)

class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim, dropout = 0.):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, dim),
            nn.Dropout(dropout)
        )
    def forward(self, x):
        return self.net(x)


class LSA(nn.Module):
    def __init__(self, dim, heads = 8, dim_head = 64, dropout = 0.):
        super().__init__()
        inner_dim = dim_head *  heads
        self.heads = heads
        self.temperature = nn.Parameter(torch.log(torch.tensor(dim_head ** -0.5)))#使之可以学习

        self.norm = nn.LayerNorm(dim)
        self.attend = nn.Softmax(dim = -1)
        self.dropout = nn.Dropout(dropout)

        self.to_qkv = nn.Linear(dim, inner_dim * 3, bias = False)

        self.to_out = nn.Sequential(
            nn.Linear(inner_dim, dim),
            nn.Dropout(dropout)
        )

    def forward(self, x):
        x = self.norm(x)
        qkv = self.to_qkv(x).chunk(3, dim = -1)
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h = self.heads), qkv)

        dots = torch.matmul(q, k.transpose(-1, -2)) * self.temperature.exp()

        #对角线为1，其他为0
        mask = torch.eye(dots.shape[-1], device = dots.device, dtype = torch.bool)
        mask_value = -torch.finfo(dots.dtype).max
        dots = dots.masked_fill(mask, mask_value)#使得对角线的数值变大

        attn = self.attend(dots)
        attn = self.dropout(attn)

        out = torch.matmul(attn, v)
        out = rearrange(out, 'b h n d -> b n (h d)')
        return self.to_out(out)


class Transformer(nn.Module):
    def __init__(self, dim, heads, dim_head, mlp_dim, dropout = 0.):
        super().__init__()
        self.layers = nn.ModuleList([])
        for _ in range(6):
            self.layers.append(nn.ModuleList([
                LSA(dim, heads = heads, dim_head = dim_head, dropout = dropout),
                FeedForward(dim, mlp_dim, dropout = dropout)
            ]))
    def forward(self, x):
        results = []
        cnt = 1
        for attn, ff in self.layers:
            x = attn(x)*0.85 + x #改动
            x = ff(x)*0.85 + x
            if cnt == 2 or cnt == 4 or cnt == 6:
                results.append(x)
            cnt+=1
        return results


class SPT(nn.Module):
    def __init__(self, *, dim, patch_size, channels = 3):
        super().__init__()
        patch_dim = patch_size * patch_size * 5 * channels

        self.to_patch_tokens = nn.Sequential(
            Rearrange('b c (h p1) (w p2) -> b (h w) (p1 p2 c)', p1 = patch_size, p2 = patch_size),
            nn.LayerNorm(patch_dim),
            nn.Linear(patch_dim, dim)
        )

    def forward(self, x):
        shifts = ((1, -1, 0, 0), (-1, 1, 0, 0), (0, 0, 1, -1), (0, 0, -1, 1))
        shifted_x = list(map(lambda shift: F.pad(x, shift), shifts))
        x_with_shifts = torch.cat((x, *shifted_x), dim = 1)
        return self.to_patch_tokens(x_with_shifts)

class Conv(nn.Module):
    def __init__(self,in_shape, out_shape, k, s=1, p=1, bias=True):
        super(Conv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels=in_shape,out_channels=out_shape, kernel_size=k,
                      stride=s,padding=p, bias=bias),
            nn.BatchNorm2d(out_shape),
            nn.LeakyReLU(0.1)
        )

    def forward(self, x):
        return self.conv(x)



class CLF(nn.Module):
    def __init__(self, dim):
        super(CLF, self).__init__()

        self.global_avg_pooling = nn.AdaptiveAvgPool2d(1)
        self.bn = nn.BatchNorm2d(dim)
        self.relu = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(dim, 36)

    def forward(self, res1, res2, res3):
        x1 = self.global_avg_pooling(res1)
        x2 = self.global_avg_pooling(res2)
        x3 = self.global_avg_pooling(res3)
        x1 = x1.view(x1.size(0), -1)
        x2 = x2.view(x2.size(0), -1)
        x3 = x3.view(x3.size(0), -1)
        x = torch.cat((x1, x2, x3), dim=1)
        x = self.bn(x.unsqueeze(-1).unsqueeze(-1)).squeeze(-1).squeeze(-1)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc(x)
        return x

#----------------------------主要网络-----------------------#
class Model2(nn.Module):
    def __init__(self, *, image_size, patch_size, num_classes, dim, depth, heads, mlp_dim, pool = 'cls',
                 channels = 3, dim_head = 64, dropout = 0., emb_dropout = 0.):
        super(Model2,self).__init__()
        image_height, image_width = pair(image_size)
        patch_height, patch_width = pair(patch_size)
        assert image_height % patch_height == 0 and image_width % patch_width == 0, 'Image dimensions must be divisible by the patch size.'
        num_patches = (image_height // patch_height) * (image_width // patch_width)
        patch_dim = channels * patch_height * patch_width
        assert pool in {'cls', 'mean'}, 'pool type must be either cls (cls token) or mean (mean pooling)'

        #-----------------ViT主干用于编码---------------------#
        self.to_patch_embedding = SPT(dim = dim, patch_size = patch_size, channels = channels)
        self.pos_embedding = nn.Parameter(torch.randn(1, num_patches + 1, dim))
        self.cls_token = nn.Parameter(torch.randn(1, 1, dim))
        self.dropout = nn.Dropout(emb_dropout)
        self.transformer = Transformer(dim, heads, dim_head, mlp_dim, dropout)

        #endregion
        #-------------一些组件----------------#
        self.conv_transpose1 = nn.ConvTranspose2d(in_channels=1024, out_channels=256, kernel_size=4, stride=2, padding=1)
        self.conv_transpose2 = nn.ConvTranspose2d(in_channels=1024, out_channels=512, kernel_size=1, stride=1, padding=0)
        self.conv_transpose3 = nn.Conv2d(1024, 1024, kernel_size=3, stride=2, padding=1)

    def forward(self,img):

        x = self.to_patch_embedding(img)
        b, n, _ = x.shape

        x += self.pos_embedding[:, :n]
        x = self.dropout(x)
        x = self.transformer(x)

        temp1, temp2, temp3 = x
        temp1 = rearrange(temp1, 'b (m n) d -> b d m n', m=26)  # 变为 (2, 1024, 26, 26)
        res1 = self.conv_transpose1(temp1)  # 输出形状 (2, 256, 52, 52)
        temp2 = rearrange(temp2, 'b (m n) d -> b d m n', m=26)  # 变为 (2, 1024, 26, 26)
        res2 = self.conv_transpose2(temp2)  # 输出形状应为 (2, 512, 26, 26)
        temp3 = rearrange(temp3, 'b (m n) d -> b d m n', m=26)  # 变为 (2, 1024, 13, 13)
        res3 = self.conv_transpose3(temp3)  # 输出形状应为 (2, 1024, 13, 13)

        return res1,res2,res3


def get_model():
    model = Model2(
        image_size=416,
        patch_size=16,
        num_classes=36,
        dim=1024,
        depth=6,
        heads=16,
        mlp_dim=2048,
        dropout=0.1,
        emb_dropout=0.1)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return model.to(device)


if __name__ == '__main__':
    print(torch.cuda.is_available())
    x = torch.randn(2,3,416,416)
    # image_size, patch_size, num_classes, dim, depth, heads, mlp_dim,
    # pool = 'cls', channels = 3, dim_head = 64, dropout = 0., emb_dropout = 0
    net = Model2(
        image_size=416,
        patch_size=16,
        num_classes=36,
        dim=1024,
        depth=6,
        heads=16,
        mlp_dim=2048,
        dropout=0.1,
        emb_dropout=0.1)
    res = net(x)
    for i in res:
        print(i.shape)
