"""Implementation of categorical variables related to tabular data."""

from collections import namedtuple
from enum import Enum

_DevPhaseInfo = namedtuple("_DevPhaseInfo", ["eng", "ja", "ja_long"])
_CalcMethodInfo = namedtuple("_CalcMethodInfo", ["eng", "ja"])
_ClassificationInfo = namedtuple("_ClassificationInfo", ["eng", "ja"])


class DevPhase(Enum):
    """Enum class for development phase."""

    RD = _DevPhaseInfo("requirements definition", "要件定義", "要件定義")
    DES1 = _DevPhaseInfo("basic design", "基本設計", "基本設計")
    DES2 = _DevPhaseInfo("detailed design", "詳細設計", "詳細設計")
    IMPL = _DevPhaseInfo("implementation/unit test", "実装・単テ", "実装・単体テスト")
    INT = _DevPhaseInfo("integration test", "結テ", "結合テスト")
    ST = _DevPhaseInfo("system test", "ST", "システムテスト")

    @classmethod
    def from_ja(cls, ja: str) -> "DevPhase":
        """Return the enum instance corresponding to the Japanese name."""
        for phase in cls:
            if phase.ja == ja:
                return phase
        raise ValueError(f"Invalid Japanese name: {ja}")

    @property
    def ja(self):
        return self.value.ja

    @property
    def ja_long(self):
        return self.value.ja_long

    @property
    def all_descriptions(self):
        """英語表記、日本語短表記、日本語長表記を返す"""
        return (self.value.eng, self.value.ja, self.value.ja_long)


class CalcMethod(Enum):
    """Enum class for calculation method."""

    SUM = _CalcMethodInfo("sum", "合計値")
    AVG = _CalcMethodInfo("average", "平均値")
    MED = _CalcMethodInfo("median", "中央値")

    @property
    def ja(self):
        return self.value.ja


class Classification(Enum):
    """Enum class for classification."""

    BOTH = _ClassificationInfo("new and modified", "全体")
    NEW = _ClassificationInfo("new", "新規")
    MOD = _ClassificationInfo("modified", "修正")

    @property
    def ja(self):
        return self.value.ja
