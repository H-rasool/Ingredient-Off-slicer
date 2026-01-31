from app.parsing.slicer_adapter import parse_piece

def test_parse_simple():
    out = parse_piece("3 tbsp unsalted butter, softened")
    assert out["name"] in ("unsalted butter", "butter", None)
    amt = out.get("amount") or {}
    assert "quantity" in amt
    assert "unit" in amt
