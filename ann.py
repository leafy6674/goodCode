"""純 Python 實作的小型全連接神經網路（不依賴 numpy）。

用法：
    python ann.py simple-data.csv

CSV 格式：第一列為標題，前 N-1 欄為特徵，最後一欄為目標值。
"""
import csv
import math
import random
import sys


# ---------------------------------------------------------------- 網路層

class LinearLayer:
    def __init__(self, input_size, output_size):
        self.input_size = input_size
        self.output_size = output_size
        # He 初始化：讓 ReLU 網路的訊號在各層間維持合理的大小
        limit = math.sqrt(6 / input_size)
        self.weights = [[random.uniform(-limit, limit) for _ in range(input_size)]
                        for _ in range(output_size)]
        self.biases = [0.0] * output_size
        self.weight_grads = [[0.0] * input_size for _ in range(output_size)]
        self.bias_grads = [0.0] * output_size
        self.inputs = None

    def forward(self, x):
        self.inputs = x
        return [sum(w * xi for w, xi in zip(row, x)) + b
                for row, b in zip(self.weights, self.biases)]

    def backward(self, output_grads):
        # 累加梯度（支援 mini-batch），由 zero_grad() 清除
        for o, g in enumerate(output_grads):
            row = self.weight_grads[o]
            for i, xi in enumerate(self.inputs):
                row[i] += g * xi
            self.bias_grads[o] += g
        # 傳給前一層的梯度
        return [sum(output_grads[o] * self.weights[o][i] for o in range(self.output_size))
                for i in range(self.input_size)]

    def step(self, lr):
        for o in range(self.output_size):
            w, g = self.weights[o], self.weight_grads[o]
            for i in range(self.input_size):
                w[i] -= lr * g[i]
            self.biases[o] -= lr * self.bias_grads[o]

    def zero_grad(self):
        for row in self.weight_grads:
            for i in range(len(row)):
                row[i] = 0.0
        for o in range(self.output_size):
            self.bias_grads[o] = 0.0


class ReLULayer:
    def forward(self, x):
        self.inputs = x
        return [v if v > 0 else 0.0 for v in x]

    def backward(self, output_grads):
        return [g if v > 0 else 0.0 for g, v in zip(output_grads, self.inputs)]

    def step(self, lr):
        pass  # 沒有參數

    def zero_grad(self):
        pass


class ANN:
    def __init__(self, layers):
        self.layers = layers

    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x

    __call__ = forward

    def backward(self, grads):
        for layer in reversed(self.layers):
            grads = layer.backward(grads)
        return grads

    def step(self, lr):
        for layer in self.layers:
            layer.step(lr)

    def zero_grad(self):
        for layer in self.layers:
            layer.zero_grad()


class MSELoss:
    def forward(self, pred, y):
        self.pred, self.y = pred, y
        return sum((p - t) ** 2 for p, t in zip(pred, y)) / len(pred)

    def backward(self):
        n = len(self.pred)
        return [2 * (p - t) / n for p, t in zip(self.pred, self.y)]


# ---------------------------------------------------------------- 資料處理

def load_csv(path):
    xs, ys = [], []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # 跳過標題
        for row in reader:
            if not row:
                continue
            values = [float(v) for v in row]
            xs.append(values[:-1])
            ys.append(values[-1:])
    return xs, ys


class Standardizer:
    """把每個欄位轉成平均 0、標準差 1，讓學習率不必調得極小。"""

    def fit(self, rows):
        cols = list(zip(*rows))
        self.mean = [sum(c) / len(c) for c in cols]
        self.std = [math.sqrt(sum((v - m) ** 2 for v in c) / len(c)) or 1.0
                    for c, m in zip(cols, self.mean)]
        return self

    def transform(self, rows):
        return [[(v - m) / s for v, m, s in zip(r, self.mean, self.std)] for r in rows]

    def inverse(self, row):
        return [v * s + m for v, m, s in zip(row, self.mean, self.std)]


def evaluate(model, loss_fn, xs, ys):
    return sum(loss_fn.forward(model(x), y) for x, y in zip(xs, ys)) / len(xs)


def train(model, loss_fn, xs, ys, epochs=300, lr=0.01, batch_size=16,
          val_xs=None, val_ys=None, log_every=10):
    data = list(zip(xs, ys))
    for epoch in range(1, epochs + 1):
        random.shuffle(data)  # 每個 epoch 打亂順序
        total = 0.0
        for start in range(0, len(data), batch_size):
            batch = data[start:start + batch_size]
            model.zero_grad()
            for x, y in batch:
                total += loss_fn.forward(model(x), y)
                model.backward(loss_fn.backward())
            model.step(lr / len(batch))  # 對 batch 取平均梯度
        if epoch % log_every == 0 or epoch == 1 or epoch == epochs:
            msg = f'epoch {epoch:4d}  train loss {total / len(data):.6f}'
            if val_xs:
                msg += f'  val loss {evaluate(model, loss_fn, val_xs, val_ys):.6f}'
            print(msg)


# ---------------------------------------------------------------- 主程式

def main(path='simple-data.csv', seed=42):
    random.seed(seed)
    xs, ys = load_csv(path)
    print(f'loaded {len(xs)} samples, {len(xs[0])} features')

    # 切出 20% 作為驗證集
    idx = list(range(len(xs)))
    random.shuffle(idx)
    cut = int(len(idx) * 0.8)
    train_x = [xs[i] for i in idx[:cut]]
    train_y = [ys[i] for i in idx[:cut]]
    val_x = [xs[i] for i in idx[cut:]]
    val_y = [ys[i] for i in idx[cut:]]

    # 只用訓練集計算統計量，避免資料洩漏
    x_scaler = Standardizer().fit(train_x)
    y_scaler = Standardizer().fit(train_y)
    train_x, val_x = x_scaler.transform(train_x), x_scaler.transform(val_x)
    train_y, val_y = y_scaler.transform(train_y), y_scaler.transform(val_y)

    model = ANN([
        LinearLayer(len(xs[0]), 8),
        ReLULayer(),
        LinearLayer(8, 1),
    ])
    loss_fn = MSELoss()
    train(model, loss_fn, train_x, train_y, epochs=300, lr=0.05, batch_size=16,
          val_xs=val_x or None, val_ys=val_y or None, log_every=25)

    # 範例預測（換算回原始單位）
    x0 = xs[idx[0]]
    pred = y_scaler.inverse(model(x_scaler.transform([x0])[0]))
    print(f'example: input {x0} -> pred {pred[0]:.4f}, actual {ys[idx[0]][0]:.4f}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'simple-data.csv')
