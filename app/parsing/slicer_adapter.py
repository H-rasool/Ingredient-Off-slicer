from typing import Any, Dict, Optional
import ingredient_slicer

def parse_piece(text: str) -> Dict[str, Any]:
    s = ingredient_slicer.IngredientSlicer(text)
    js = s.to_json()
    prep = js.get("prep")
    if isinstance(prep, list):
        prep_str = ", ".join(prep)
    else:
        prep_str = prep if prep else None
    qty = js.get("quantity")
    unit = js.get("unit")
    amount = {"quantity": qty, "unit": unit} if (qty is not None or unit) else None
    return {
        "raw": js.get("ingredient") or text,
        "name": js.get("food"),
        "amount": amount,
        "preparation": prep_str,
        "comment": None,
        "confidence": None
    }
