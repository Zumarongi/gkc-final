print("Running PGD Attack...")

# 导入第三方库
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
import numpy as np
import matplotlib.pyplot as plt

# 设置参数及模型参数路径
epsilons = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
pretrained_model = "algorithms/lenet_mnist_model.pth"
use_cuda = True

# 定义模型
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


# 设置 MNIST 测试数据集的数据加载器
test_loader = torch.utils.data.DataLoader(
    datasets.MNIST(
        "./data",
        train=False,
        download=True,
        transform=transforms.Compose(
            [
                transforms.ToTensor(),
            ]
        ),
    ),
    batch_size=1,
    shuffle=True,
)

# 加载预训练模型
print("CUDA Available: ", torch.cuda.is_available())
device = torch.device("cuda" if (use_cuda and torch.cuda.is_available()) else "cpu")
model = Net().to(device)
model.load_state_dict(
    torch.load(pretrained_model, map_location="cpu", weights_only=True)
)
print("Model loaded.")
model.eval()


# PGD攻击代码
def pgd_attack(image, epsilon, data_grad, target, alpha, num_iter=4):
    # 初始对抗样本
    perturbed_image = image.clone().detach()
    for _ in range(num_iter):
        # 梯度上升
        perturbed_image = perturbed_image + alpha * data_grad.sign()
        # 投影到 epsilon-ball 内
        eta = torch.clamp(perturbed_image - image, min=-epsilon, max=epsilon)
        perturbed_image = torch.clamp(image + eta, 0, 1).detach()  # 重新创建叶子节点
        # 重新计算梯度
        perturbed_image.requires_grad = True
        output = model(perturbed_image)
        loss = F.nll_loss(output, target)
        model.zero_grad()
        loss.backward()
        data_grad = perturbed_image.grad.data
    return perturbed_image


# 攻击效果测试代码
def test(model, device, test_loader, epsilon):
    correct = 0
    adv_examples = []
    for data, target in test_loader:
        data, target = data.to(device), target.to(device)
        data.requires_grad = True
        output = model(data)
        init_pred = output.max(1, keepdim=True)[1]  # 获取最大概率的索引
        if init_pred.item() != target.item():
            continue
        loss = F.nll_loss(output, target)
        model.zero_grad()
        loss.backward()
        data_grad = data.grad.data
        # 使用PGD攻击
        perturbed_data = pgd_attack(data, epsilon, data_grad, target, alpha=epsilon / 4)
        output = model(perturbed_data)
        final_pred = output.max(1, keepdim=True)[1]  # 获取最大概率的索引
        if final_pred.item() == target.item():
            correct += 1
            if (epsilon == 0) and (len(adv_examples) < 5):
                adv_ex = perturbed_data.squeeze().detach().cpu().numpy()
                adv_examples.append((init_pred.item(), final_pred.item(), adv_ex))
        else:
            if len(adv_examples) < 5:
                adv_ex = perturbed_data.squeeze().detach().cpu().numpy()
                adv_examples.append((init_pred.item(), final_pred.item(), adv_ex))
    final_acc = correct / float(len(test_loader))
    print(
        "Epsilon: {}\tTest Accuracy = {} / {} = {}".format(
            epsilon, correct, len(test_loader), final_acc
        )
    )
    return final_acc, adv_examples


accuracies = []
examples = []

# 在不同参数下测试攻击性能并绘制图像
for eps in epsilons:
    acc, ex = test(model, device, test_loader, eps)
    accuracies.append(acc)
    examples.append(ex)

plt.figure(figsize=(5, 5))
plt.plot(epsilons, accuracies, "*-")
plt.yticks(np.arange(0, 1.1, step=0.1))
plt.xticks(np.arange(0, 0.35, step=0.05))
plt.title("Accuracy vs Epsilon")
plt.xlabel("Epsilon")
plt.ylabel("Accuracy")

filename = "static/img/PGD/PGD_effect.png"
plt.savefig(filename)
# plt.show()
# plt.close()

# 绘制不同epsilon值下的对抗样本示例
cnt = 0
plt.figure(figsize=(8, 10))
for i in range(len(epsilons)):
    for j in range(len(examples[i])):
        cnt += 1
        plt.subplot(len(epsilons), len(examples[0]), cnt)
        plt.xticks([], [])
        plt.yticks([], [])
        if j == 0:
            plt.ylabel("Eps: {}".format(epsilons[i]), fontsize=14)
        orig, adv, ex = examples[i][j]
        plt.title("{} -> {}".format(orig, adv))
        plt.imshow(ex, cmap="gray")
plt.tight_layout()
filename = "static/img/PGD/PGD_examples.png"
plt.savefig(filename)
# plt.show()
