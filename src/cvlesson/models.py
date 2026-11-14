"""初心者向けのResNet分類・回帰Estimator。PyTorchは利用時に読み込む。"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Iterable, Sequence


class ModelError(RuntimeError):
    """モデルの準備・学習・予測で発生したエラー。"""


def available_devices() -> dict[str, bool]:
    """CPU・CUDA・Apple Silicon MPSの利用可否を返す。"""
    try:
        import torch
    except ImportError as exc:
        raise ModelError("ResNetにはPyTorchが必要です。python -m pip install 'cv-data-lesson[torch]'を実行してください。") from exc
    return {
        "cpu": True,
        "cuda": bool(torch.cuda.is_available()),
        "mps": bool(getattr(getattr(torch.backends, "mps", None), "is_available", lambda: False)()),
    }


def _image_rows(X: Any, *, allow_pairs: bool) -> list[Any]:
    """画像パス/Pillow画像列またはDataFrameを正規化する。"""
    columns = getattr(X, "columns", ())
    if "image_path" in columns:
        X = X["image_path"].tolist()
    elif allow_pairs and {"image_before_path", "image_after_path"}.issubset(set(columns)):
        X = list(zip(X["image_before_path"].tolist(), X["image_after_path"].tolist()))
    elif isinstance(X, (str, Path)):
        X = [X]
    elif _is_pillow_image(X):
        X = [X]
    else:
        try:
            X = list(X)
        except TypeError as exc:
            raise ValueError("Xは画像パスの列またはDatasetBundle.to_df()の結果で指定してください。") from exc

    rows: list[Any] = []
    expected_pair: bool | None = None
    for index, row in enumerate(X):
        is_pair = isinstance(row, (tuple, list))
        if is_pair:
            if not allow_pairs:
                raise ValueError("分類では各サンプルを画像パス1つで指定してください。")
            if len(row) != 2:
                raise ValueError(f"X[{index}]は食前・食後など2つの画像パスで指定してください。")
            paths = (_normalize_image_input(row[0], index), _normalize_image_input(row[1], index))
            normalized: Any = paths
        else:
            normalized = _normalize_image_input(row, index)
            paths = (normalized,)
        if expected_pair is not None and expected_pair != is_pair:
            raise ValueError("Xには単画像と画像ペアを混在できません。")
        expected_pair = is_pair
        rows.append(normalized)
    if not rows:
        raise ValueError("Xに画像がありません。")
    return rows


def _is_pillow_image(value: Any) -> bool:
    try:
        from PIL import Image
    except ImportError:
        return False
    return isinstance(value, Image.Image)


def _load_rgb_image(source: Any):
    from PIL import Image

    if isinstance(source, Path):
        with Image.open(source) as opened:
            return opened.convert("RGB")
    return source.convert("RGB").copy()


def _normalize_image_input(value: Any, index: int) -> Any:
    if isinstance(value, (str, Path)):
        path = Path(value).expanduser()
        if not path.is_file():
            raise ValueError(f"画像ファイルが見つかりません: {path}")
        return path
    try:
        from PIL import Image
    except ImportError as exc:
        raise ValueError(
            f"X[{index}]は画像パスまたはPillow Imageで指定してください。Pillowにはpython -m pip install 'cv-data-lesson[torch]'が必要です。"
        ) from exc
    if isinstance(value, Image.Image):
        return value.copy()
    raise ValueError(f"X[{index}]は画像パスまたはPillow Imageで指定してください。NumPy配列は未対応です。")


def _target_values(y: Any) -> list[Any]:
    if hasattr(y, "tolist"):
        y = y.tolist()
    try:
        values = list(y)
    except TypeError as exc:
        raise ValueError("yは各画像に対応するラベルまたは数値の列で指定してください。") from exc
    if not values:
        raise ValueError("yに正解値がありません。")
    return values


class _ResNetEstimator:
    _task = ""

    def __init__(
        self,
        *,
        device: str = "cpu",
        epochs: int = 5,
        batch_size: int = 16,
        learning_rate: float = 1e-3,
        image_size: int = 224,
        weights: Any = "IMAGENET1K_V1",
        random_state: int = 42,
    ) -> None:
        if device not in {"cpu", "cuda", "mps"}:
            raise ValueError("deviceは'cpu'、'cuda'、'mps'のいずれかです。")
        if isinstance(epochs, bool) or not isinstance(epochs, int) or epochs < 1:
            raise ValueError("epochsは1以上の整数で指定してください。")
        if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size < 1:
            raise ValueError("batch_sizeは1以上の整数で指定してください。")
        if not isinstance(learning_rate, (int, float)) or not math.isfinite(learning_rate) or learning_rate <= 0:
            raise ValueError("learning_rateは0より大きい有限値で指定してください。")
        if isinstance(image_size, bool) or not isinstance(image_size, int) or image_size < 32:
            raise ValueError("image_sizeは32以上の整数で指定してください。")
        if isinstance(random_state, bool) or not isinstance(random_state, int):
            raise ValueError("random_stateは整数で指定してください。")
        if weights not in (None, "IMAGENET1K_V1", "DEFAULT") and not hasattr(weights, "meta"):
            raise ValueError("weightsはIMAGENET1K_V1、DEFAULT、None、またはTorchvisionの重みで指定してください。")
        self.device = device
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = float(learning_rate)
        self.image_size = image_size
        self.weights = weights
        self.random_state = random_state
        self.is_fitted_ = False

    def _create_runtime(self, *, output_size: int, paired: bool):
        try:
            import torch
            from torchvision import models, transforms
        except (ImportError, RuntimeError) as exc:
            raise ModelError(
                "ResNetには対応するPyTorchとTorchvisionが必要です。python -m pip install 'cv-data-lesson[torch]'を実行してください。"
            ) from exc

        devices = available_devices()
        if not devices.get(self.device, False):
            raise ModelError(f"device={self.device!r}はこの環境で利用できません。available_devices()で確認してください。")
        torch.manual_seed(self.random_state)

        weight_enum = models.ResNet18_Weights
        if self.weights is None:
            weights = None
            mean, std = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
        elif isinstance(self.weights, str):
            weights = weight_enum.IMAGENET1K_V1
            preset = weights.transforms()
            mean, std = preset.mean, preset.std
        else:
            weights = self.weights
            preset = weights.transforms()
            mean, std = preset.mean, preset.std

        backbone = models.resnet18(weights=weights)
        feature_size = backbone.fc.in_features
        backbone.fc = torch.nn.Identity()
        for parameter in backbone.parameters():
            parameter.requires_grad = False

        class FrozenFeatureHead(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.backbone = backbone
                self.head = torch.nn.Linear(feature_size * (2 if paired else 1), output_size)

            def forward(self, *images):
                with torch.no_grad():
                    features = [self.backbone(image) for image in images]
                return self.head(torch.cat(features, dim=1) if len(features) > 1 else features[0])

        transform = transforms.Compose([
            transforms.Resize(self.image_size),
            transforms.CenterCrop(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])
        self._torch = torch
        self._net = FrozenFeatureHead().to(self.device)
        self._transform = transform
        self._paired = paired

    def _loader(self, paths: Sequence[Any], targets: Any = None, *, shuffle: bool = False):
        torch = self._torch
        transform = self._transform

        class ImagePathDataset(torch.utils.data.Dataset):
            def __len__(self):
                return len(paths)

            def __getitem__(self, index):
                item = paths[index]
                image_inputs = item if isinstance(item, tuple) else (item,)
                tensors = []
                for image_input in image_inputs:
                    image = _load_rgb_image(image_input)
                    tensors.append(transform(image))
                images = tuple(tensors) if len(tensors) == 2 else tensors[0]
                if targets is None:
                    return images
                return images, targets[index]

        generator = torch.Generator().manual_seed(self.random_state) if shuffle else None
        return torch.utils.data.DataLoader(
            ImagePathDataset(), batch_size=self.batch_size, shuffle=shuffle,
            num_workers=0, generator=generator,
        )

    def _forward_batch(self, images: Any):
        if isinstance(images, (tuple, list)):
            return self._net(*(image.to(self.device) for image in images))
        return self._net(images.to(self.device))

    def _train(self, paths, targets, criterion) -> None:
        torch = self._torch
        target_tensor = torch.as_tensor(targets)
        loader = self._loader(paths, target_tensor, shuffle=True)
        optimizer = torch.optim.Adam(self._net.head.parameters(), lr=self.learning_rate)
        self.loss_history_ = []
        for _ in range(self.epochs):
            self._net.eval()
            self._net.head.train()
            total_loss = 0.0
            total_items = 0
            for images, target in loader:
                target = target.to(self.device)
                optimizer.zero_grad(set_to_none=True)
                prediction = self._forward_batch(images)
                loss = criterion(prediction, target)
                loss.backward()
                optimizer.step()
                count = len(target)
                total_loss += float(loss.detach().cpu()) * count
                total_items += count
            self.loss_history_.append(total_loss / total_items)
        self._net.eval()
        self.is_fitted_ = True

    def _predict_values(self, X: Any):
        if not self.is_fitted_:
            raise ModelError("先にfit(X, y)で学習してください。")
        paths = _image_rows(X, allow_pairs=self._task == "regression")
        if any(isinstance(path, tuple) != self._paired for path in paths):
            expected = "画像ペア" if self._paired else "画像パス1つ"
            raise ValueError(f"このモデルは各サンプルを{expected}で受け取ります。")
        outputs = []
        self._net.eval()
        with self._torch.no_grad():
            for images in self._loader(paths):
                outputs.append(self._forward_batch(images).cpu())
        return self._torch.cat(outputs, dim=0).numpy()


class ResNetClassifier(_ResNetEstimator):
    """ResNet18の特徴抽出部を固定し、分類用出力層だけを学習する。"""

    _task = "classification"

    def fit(self, X: Any, y: Any):
        """画像パスとラベルで学習する。XにはDataFrameも指定できる。"""
        paths = _image_rows(X, allow_pairs=False)
        labels = _target_values(y)
        if len(paths) != len(labels):
            raise ValueError("Xの画像数とyのラベル数が一致しません。")
        classes = list(dict.fromkeys(labels))
        try:
            classes = sorted(classes)
        except TypeError:
            pass
        if len(classes) < 2:
            raise ValueError("分類には2種類以上のラベルが必要です。")
        label_to_id = {label: index for index, label in enumerate(classes)}
        encoded = [label_to_id[label] for label in labels]
        self.classes_ = classes
        self._create_runtime(output_size=len(classes), paired=False)
        self._train(paths, encoded, self._torch.nn.CrossEntropyLoss())
        return self

    def predict(self, X: Any):
        """画像ごとの予測ラベルを返す。"""
        indices = self._predict_values(X).argmax(axis=1).tolist()
        import numpy as np

        return np.asarray([self.classes_[index] for index in indices])

    def predict_proba(self, X: Any):
        """各クラスに属する確率の目安を返す。"""
        logits = self._predict_values(X)
        tensor = self._torch.as_tensor(logits)
        return self._torch.softmax(tensor, dim=1).numpy()

    def score(self, X: Any, y: Any) -> float:
        """正解ラベルと一致した割合を返す。"""
        expected = _target_values(y)
        predicted = self.predict(X).tolist()
        if len(expected) != len(predicted):
            raise ValueError("Xの画像数とyのラベル数が一致しません。")
        return sum(actual == guess for actual, guess in zip(expected, predicted)) / len(expected)


class ResNetRegressor(_ResNetEstimator):
    """ResNet18の特徴抽出部を固定し、回帰用出力層だけを学習する。"""

    _task = "regression"

    def fit(self, X: Any, y: Any):
        """画像パスまたは画像ペアと数値で学習する。Xには対応DataFrameを指定できる。"""
        paths = _image_rows(X, allow_pairs=True)
        values = _target_values(y)
        if len(paths) != len(values):
            raise ValueError("Xの画像数とyの数値数が一致しません。")
        paired = isinstance(paths[0], tuple)
        if any(isinstance(path, tuple) != paired for path in paths):
            raise ValueError("Xには単画像と画像ペアを混在できません。")
        if hasattr(values, "__iter__") and values and isinstance(values[0], (list, tuple)):
            target_rows = [list(row) for row in values]
            output_size = len(target_rows[0])
            if output_size < 1 or any(len(row) != output_size for row in target_rows):
                raise ValueError("yの各行は同じ数の数値で指定してください。")
            flat_values = [value for row in target_rows for value in row]
            if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in flat_values):
                raise ValueError("yには有限の数値だけを指定してください。")
            self._target_was_1d = False
        else:
            target_rows = values
            output_size = 1
            if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in target_rows):
                raise ValueError("yには有限の数値だけを指定してください。")
            self._target_was_1d = True
        self.n_outputs_ = output_size
        self._create_runtime(output_size=output_size, paired=paired)
        dtype = self._torch.float32
        if output_size == 1 and self._target_was_1d:
            target_tensor = self._torch.tensor(target_rows, dtype=dtype).reshape(-1, 1)
        else:
            target_tensor = self._torch.tensor(target_rows, dtype=dtype)
        self._train(paths, target_tensor, self._torch.nn.MSELoss())
        return self

    def predict(self, X: Any):
        """画像ごとの予測値を返す。単一出力は1次元配列。"""
        values = self._predict_values(X)
        return values[:, 0] if self._target_was_1d else values

    def score(self, X: Any, y: Any) -> float:
        """決定係数R²を返す。"""
        import numpy as np

        expected = np.asarray(_target_values(y), dtype=float)
        predicted = np.asarray(self.predict(X), dtype=float)
        if expected.shape != predicted.shape:
            raise ValueError("Xからの予測形状とyの数値形状が一致しません。")
        expected_2d = expected.reshape(len(expected), -1)
        predicted_2d = predicted.reshape(len(predicted), -1)
        scores = []
        for column in range(expected_2d.shape[1]):
            truth = expected_2d[:, column]
            residual = float(((truth - predicted_2d[:, column]) ** 2).sum())
            total = float(((truth - truth.mean()) ** 2).sum())
            scores.append(1.0 - residual / total if total else (1.0 if residual == 0 else 0.0))
        return float(np.mean(scores))


__all__ = ["ModelError", "ResNetClassifier", "ResNetRegressor", "available_devices"]
