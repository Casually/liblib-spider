from enum import IntEnum

class BaseModelType(IntEnum):
    SD_1_5 = 1              # 基础算法 v1.5
    SD_2_1 = 2              # 基础算法 v2.1
    SD_XL = 3               # 基础算法 XL
    SD_3 = 7                # 基础算法 v3
    PIXART_SIGMA = 9        # PixArt Σ
    PONY = 10               # Pony
    HUNYUAN_DIT = 12        # 混元DiT v1.1
    PIXART_ALPHA = 13       # PixArt α
    SD_F_1 = 19             # 基础算法 F.1
    SD_3_5M = 20            # 基础算法 v3.5M
    SD_3_5L = 21            # 基础算法 v3.5L

    def desc(self):
        """返回该基模类型的中文描述"""
        descriptions = {
            self.SD_1_5: "基础算法 v1.5",
            self.SD_2_1: "基础算法 v2.1",
            self.SD_XL: "基础算法 XL",
            self.SD_3: "基础算法 v3",
            self.PIXART_SIGMA: "PixArt Σ",
            self.PONY: "Pony",
            self.HUNYUAN_DIT: "混元DiT v1.1",
            self.PIXART_ALPHA: "PixArt α",
            self.SD_F_1: "基础算法 F.1",
            self.SD_3_5M: "基础算法 v3.5M",
            self.SD_3_5L: "基础算法 v3.5L"
        }
        return descriptions[self]

    @classmethod
    def from_value(cls, value):
        """根据整数值构造 BaseModelType 实例"""
        try:
            return cls(int(value))
        except (ValueError, KeyError):
            raise ValueError(f"无效的 base model type 值：{value}")
