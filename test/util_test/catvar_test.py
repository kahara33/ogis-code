from util.catvar import CalcMethod, Classification, DevPhase


def test_dev_phase():
    assert DevPhase.RD.ja == DevPhase.RD.ja_long == "要件定義"
    assert DevPhase.DES1.ja == DevPhase.DES1.ja_long == "基本設計"
    assert DevPhase.DES2.ja == DevPhase.DES2.ja_long == "詳細設計"
    assert DevPhase.IMPL.ja == "実装・単テ"
    assert DevPhase.IMPL.ja_long == "実装・単体テスト"
    assert DevPhase.INT.ja == "結テ"
    assert DevPhase.INT.ja_long == "結合テスト"
    assert DevPhase.ST.ja == "ST"
    assert DevPhase.ST.ja_long == "システムテスト"


def test_calc_method():
    assert CalcMethod.SUM.ja == "合計値"
    assert CalcMethod.AVG.ja == "平均値"
    assert CalcMethod.MED.ja == "中央値"


def test_classification():
    assert Classification.BOTH.ja == "全体"
    assert Classification.NEW.ja == "新規"
    assert Classification.MOD.ja == "修正"
