import torch
import torch.nn as nn
import torch.nn.functional as F


class BaseDirect2StreamNet(nn.Module):
    def __init__(self, im_channel, dp_channel, direction_dim, num_class):
        super(BaseDirect2StreamNet, self).__init__()
        num_hidden_i = 24
        self.bn_i0 = nn.BatchNorm2d(im_channel)
        self.conv_i1 = nn.Conv2d(im_channel, num_hidden_i, 3, 1, 1)
        self.bn_i1 = nn.BatchNorm2d(num_hidden_i)
        self.conv_i2 = nn.Conv2d(num_hidden_i, num_hidden_i * 2, 3, 1, 1)
        self.bn_i2 = nn.BatchNorm2d(num_hidden_i * 2)
        self.conv_i3 = nn.Conv2d(num_hidden_i * 2, num_hidden_i * 4, 3, 1, 1)
        self.bn_i3 = nn.BatchNorm2d(num_hidden_i * 4)
        self.conv_i4 = nn.Conv2d(num_hidden_i * 4, num_hidden_i * 8, 3, 1, 1)
        self.bn_i4 = nn.BatchNorm2d(num_hidden_i * 8)
        self.conv_i5 = nn.Conv2d(num_hidden_i * 8, num_hidden_i * 16, 3, 1, 1)
        self.bn_i5 = nn.BatchNorm2d(num_hidden_i * 16)
        self.conv_i6 = nn.Conv2d(num_hidden_i * 16, num_hidden_i * 32, 3, 1, 1)
        self.bn_i6 = nn.BatchNorm2d(num_hidden_i * 32)

        num_hidden_d = 16
        self.bn_d0 = nn.BatchNorm2d(dp_channel)
        self.conv_d1 = nn.Conv2d(dp_channel, num_hidden_d, 3, 1, 1)
        self.bn_d1 = nn.BatchNorm2d(num_hidden_d)
        self.conv_d2 = nn.Conv2d(num_hidden_d, num_hidden_d * 2, 3, 1, 1)
        self.bn_d2 = nn.BatchNorm2d(num_hidden_d * 2)
        self.conv_d3 = nn.Conv2d(num_hidden_d * 2, num_hidden_d * 4, 3, 1, 1)
        self.bn_d3 = nn.BatchNorm2d(num_hidden_d * 4)
        self.conv_d4 = nn.Conv2d(num_hidden_d * 4, num_hidden_d * 8, 3, 1, 1)
        self.bn_d4 = nn.BatchNorm2d(num_hidden_d * 8)
        self.conv_d5 = nn.Conv2d(num_hidden_d * 8, num_hidden_d * 16, 3, 1, 1)
        self.bn_d5 = nn.BatchNorm2d(num_hidden_d * 16)
        self.conv_d6 = nn.Conv2d(num_hidden_d * 16, num_hidden_d * 32, 3, 1, 1)
        self.bn_d6 = nn.BatchNorm2d(num_hidden_d * 32)

        self.adapt_avgpool = nn.AdaptiveAvgPool2d(1)
        self.maxpool = nn.MaxPool2d(2, stride=2, return_indices=False, ceil_mode=False)

        num_hidden_di = 24
        self.bn_di0 = nn.BatchNorm1d(direction_dim)
        self.fc_di = nn.Linear(direction_dim, num_hidden_di)
        self.bn_di = nn.BatchNorm1d(num_hidden_di)

        self.fc = nn.Linear(num_hidden_i * 32 + num_hidden_d * 32 + num_hidden_di, num_class)

        self.im_channel = im_channel
        self.dp_channel = dp_channel
        self.direction_dim = direction_dim
        self.n_class = num_class

    def forward(self, images, depths, direction):
        im_feat = []
        for i in range(len(images)):
            x0 = images[i]
            x0 = self.bn_i0(x0)
            x1 = F.relu(self.bn_i1(self.conv_i1(x0)))
            x2 = self.maxpool(x1)
            x2 = F.relu(self.bn_i2(self.conv_i2(x2)))
            x3 = self.maxpool(x2)
            x3 = F.relu(self.bn_i3(self.conv_i3(x3)))
            x4 = self.maxpool(x3)
            x4 = F.relu(self.bn_i4(self.conv_i4(x4)))
            x5 = self.maxpool(x4)
            x5 = F.relu(self.bn_i5(self.conv_i5(x5)))
            x6 = self.maxpool(x5)
            x6 = F.relu(self.bn_i6(self.conv_i6(x6)))
            x = self.adapt_avgpool(x6)
            x = x.view(x.size(0), -1)
            im_feat.append(x)
        x = torch.stack(im_feat, 2)
        im_feat = torch.mean(x, 2)

        dp_feat = []
        for i in range(len(depths)):
            x0 = depths[i]
            x0 = self.bn_d0(x0)
            x1 = F.relu(self.bn_d1(self.conv_d1(x0)))
            x2 = self.maxpool(x1)
            x2 = F.relu(self.bn_d2(self.conv_d2(x2)))
            x3 = self.maxpool(x2)
            x3 = F.relu(self.bn_d3(self.conv_d3(x3)))
            x4 = self.maxpool(x3)
            x4 = F.relu(self.bn_d4(self.conv_d4(x4)))
            x5 = self.maxpool(x4)
            x5 = F.relu(self.bn_d5(self.conv_d5(x5)))
            x6 = self.maxpool(x5)
            x6 = F.relu(self.bn_d6(self.conv_d6(x6)))
            x = self.adapt_avgpool(x6)
            x = x.view(x.size(0), -1)
            dp_feat.append(x)
        x = torch.stack(dp_feat, 2)
        dp_feat = torch.mean(x, 2)

        di0 = self.bn_di0(direction)
        di = F.relu(self.bn_di(self.fc_di(di0)))

        x = torch.cat((im_feat, dp_feat, di), 1)
        pred = self.fc(x)
        return pred, None
