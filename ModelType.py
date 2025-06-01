from enum import IntEnum


class ModelType(IntEnum):
    CHECKPOINT = 1
    TEXTUAL_INVERSION = 2
    HYPERNETWORK = 3
    AESTHETIC_GRADIENT = 4
    LORA = 5
    LYCORIS = 6
    CONTROLNET = 7
    POSES = 8
    WILDCARDS = 9
    OTHER = 10

    def desc(self):
        descriptions = {
            self.CHECKPOINT: "基础模型",
            self.TEXTUAL_INVERSION: "文本反演",
            self.HYPERNETWORK: "超网络",
            self.AESTHETIC_GRADIENT: "美学渐变",
            self.LORA: "LoRA 模型",
            self.LYCORIS: "LyCORIS 模型",
            self.CONTROLNET: "控制网络",
            self.POSES: "姿势模型",
            self.WILDCARDS: "通配符",
            self.OTHER: "其他类型"
        }
        return descriptions[self]

    # 对应文件路径
    def file_path(self):
        file_paths = {
            # self.CHECKPOINT: "checkpoints",
            self.CHECKPOINT: "ckpt",  # Nootbook中checkpoints为关键字，改为ckpt
            self.TEXTUAL_INVERSION: "textual_inversion",
            self.HYPERNETWORK: "hypernetworks",
            self.AESTHETIC_GRADIENT: "aesthetic_gradients",
            self.LORA: "loras",
            self.LYCORIS: "lycoris",
            self.CONTROLNET: "controlnet",
            self.POSES: "poses",
            self.WILDCARDS: "wildcards",
            self.OTHER: "others"
        }
        return file_paths[self]

    @classmethod
    def from_value(cls, value):
        try:
            return cls(int(value))
        except (ValueError, KeyError):
            raise ValueError(f"无效的 modelType 值：{value}")
