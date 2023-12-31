import numpy as np
from pathlib import Path
import pandas as pd
from PIL import Image
from pprint import pprint
import webbrowser


def read_calib_kitty(calib_path: Path) -> list[np.ndarray]:
    
    with open(calib_path, "r") as f:
        lines = [list(line.strip().split(" ")) for line in f.readlines()]
    
    calib_data = {
        line[0]: line[1:] for line in lines
    }

    calib_data = {
        k: [float(v) for v in val] for k, val in calib_data.items()
    }

    calib_data = {
        k: np.array(P).reshape((3, 4)) if len(P) == 12 else P
        for k, P in calib_data.items()
    }

    calib_data = {
        k: np.array(R).reshape((3, 3)) if len(R) == 9 else R
        for k, R in calib_data.items()
    }

    return calib_data


class KittyDataset:
    def __init__(
        self,
        p_imgs: str,
        calib_path: str = None,
        timestamps: str = None,
        grayscale: bool = False,
    ) -> None:
        assert Path(p_imgs).exists(), "Dataset path does not exist"
        self.p_imgs = p_imgs
        self.calib_data = read_calib_kitty(calib_path)
        self.camera_matrix = self.calib_data[f"K_0{self.p_imgs[-1]}:"]
        self.idx = int(p_imgs.split("_")[-1])
        self.timestamps = pd.read_csv(timestamps, header=None, names=["timestamp"])
        self.imgs = Path(self.p_imgs).rglob("*.png")
        self.imgs = sorted([str(img) for img in self.imgs])
        self.grayscale = grayscale

    @property
    def get_timestamps(self) -> pd.DataFrame:
        return self.timestamps

    @property
    def get_raw_extrinsics(self) -> np.ndarray:
        cam_mat = self.camera_matrix
        fx, fy, cx, cy = cam_mat[0, 0], cam_mat[1, 1], cam_mat[0, 2], cam_mat[1, 2]
        return fx, fy, cx, cy

    @property
    def get_hw(self) -> tuple:
        img = Image.open(self.imgs[0])
        h, w = img.size
        return h, w

    def __len__(self) -> int:
        return len(self.imgs)

    def __getitem__(self, idx):
        img = Image.open(self.imgs[idx])
        if self.grayscale:
            img = img.convert("L")
        img = np.array(img)
        return img


if __name__ == "__main__":
    kitty_dataset = KittyDataset(
        "datasets/2011_09_26/2011_09_26_drive_0018_extract/image_02",
        "datasets/2011_09_26/calib_cam_to_cam.txt",
        "datasets/2011_09_26/2011_09_26_drive_0018_extract/image_00/timestamps.txt",
    )
    webbrowser.open(kitty_dataset.imgs[0])
