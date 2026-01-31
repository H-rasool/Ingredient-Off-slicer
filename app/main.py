from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse
from .core.config import get_mongo_collection, PORT
from .models import IngredientOut, ParsedItem, ParsedResponse
from .parsing.slicer_adapter import parse_piece
from .utils import smart_split, strip_tags

client, coll = get_mongo_collection()
app = FastAPI(title="OFF Ingredients API – ingredient-slicer only")

@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------- Helpers --------------------
def coalesce_ingredients(doc: dict) -> Optional[str]:
    return doc.get("ingredients_text_en") or doc.get("ingredients_text") or None

def parse_text_common(text: str) -> ParsedResponse:
    parts = smart_split(text)
    parsed: List[dict] = []
    for p in parts:
        try:
            parsed.append(parse_piece(p))
        except Exception as e:
            parsed.append({"raw": p, "name": None, "amount": None,
                           "preparation": None, "comment": None,
                           "confidence": None, "error": str(e)})
    return {"barcode": "adhoc", "ingredients_raw": text, "parsed": parsed}

# -------------------- Ad-hoc endpoints (no Mongo required) --------------------
@app.get("/parse", response_model=ParsedResponse)
def parse_get(text: str = Query(..., min_length=1)):
    return parse_text_common(text)

@app.post("/parse", response_model=ParsedResponse)
def parse_post(payload: dict = Body(...)):
    text = payload.get("text") if isinstance(payload, dict) else None
    if not text:
        raise HTTPException(422, detail="Provide 'text' in body")
    return parse_text_common(text)

@app.get("/parse/html", response_class=HTMLResponse)
def parse_html(text: str = Query(..., min_length=1)):
    result = parse_text_common(text)
    rows = "\n".join(
        f"<tr><td>{i+1}</td>"
        f"<td>{(p.get('raw') or '').replace('<','&lt;').replace('>','&gt;')}</td>"
        f"<td>{p.get('name') or ''}</td>"
        f"<td>{(p.get('amount') or {}).get('quantity','')}</td>"
        f"<td>{(p.get('amount') or {}).get('unit','')}</td>"
        f"<td>{p.get('preparation') or ''}</td>"
        f"<td>{p.get('comment') or ''}</td>"
        f"<td>{p.get('confidence') if p.get('confidence') is not None else ''}</td>"
        f"<td>{p.get('error') or ''}</td>"
        f"</tr>"
        for i, p in enumerate(result["parsed"]) )
    raw_safe = (result["ingredients_raw"] or "").replace("<", "&lt;").replace(">", "&gt;")
    return f"""
    <html>
      <head>
        <title>Parsed Ingredients – slicer</title>
        <meta charset=\"utf-8\" />
        <style>
          body {{ font-family: system-ui, Segoe UI, Arial; padding: 20px; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
          th {{ background: #f5f5f5; text-align: left; }}
          caption {{ text-align: left; margin-bottom: 8px; font-weight: 600; }}
          code {{ background:#f6f8fa; padding:2px 4px; border-radius:4px; }}
        </style>
      </head>
      <body>
        <h2>Ad-hoc Parsing (ingredient-slicer)</h2>
        <p><b>Raw:</b> <code>{raw_safe}</code></p>
        <table>
          <caption>Parsed Items</caption>
          <thead>
            <tr>
              <th>#</th><th>Raw</th><th>Name</th><th>Qty</th><th>Unit</th>
              <th>Prep</th><th>Comment</th><th>Conf.</th><th>Error</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </body>
    </html>
    """

# -------------------- Mongo-backed endpoints (enabled only if MONGO_URI set) --------------------
@app.get("/ingredients/{barcode}", response_model=IngredientOut)
def get_by_barcode(barcode: str):
    if coll is None:
        raise HTTPException(503, detail="Mongo not configured")
    doc = coll.find_one({"$or": [{"_id": barcode}, {"code": barcode}]},
                        {"ingredients_text_en": 1, "ingredients_text": 1, "_id": 1})
    if not doc:
        raise HTTPException(404, detail="Product not found")
    return {"barcode": str(doc.get("_id")), "ingredients": coalesce_ingredients(doc)}

@app.get("/ingredients/{barcode}/parsed", response_model=ParsedResponse)
def parse_by_barcode(barcode: str):
    if coll is None:
        raise HTTPException(503, detail="Mongo not configured")
    doc = coll.find_one({"$or": [{"_id": barcode}, {"code": barcode}]},
                        {"ingredients_text_en": 1, "ingredients_text": 1, "_id": 1})
    if not doc:
        raise HTTPException(404, detail="Product not found")
    raw = coalesce_ingredients(doc)
    raw = strip_tags(raw) if raw else raw
    if not raw:
        return {"barcode": str(doc["_id"]), "ingredients_raw": None, "parsed": []}
    parts = smart_split(raw)
    parsed: list[dict] = []
    for p in parts:
        try:
            parsed.append(parse_piece(p))
        except Exception as e:
            parsed.append({"raw": p, "name": None, "amount": None,
                           "preparation": None, "comment": None,
                           "confidence": None, "error": str(e)})
    return {"barcode": str(doc["_id"]), "ingredients_raw": raw, "parsed": parsed}

@app.get("/ingredients/parsed", response_model=list[ParsedResponse])
def parse_batch(limit: int = Query(10, ge=1, le=50)):
    if coll is None:
        raise HTTPException(503, detail="Mongo not configured")
    cursor = coll.find({}, {"ingredients_text_en": 1, "ingredients_text": 1, "_id": 1}).limit(limit)
    out: list[ParsedResponse] = []
    for doc in cursor:
        raw = coalesce_ingredients(doc)
        raw = strip_tags(raw) if raw else raw
        parts = smart_split(raw) if raw else []
        parsed: list[dict] = []
        for p in parts:
            try:
                parsed.append(parse_piece(p))
            except Exception as e:
                parsed.append({"raw": p, "name": None, "amount": None,
                               "preparation": None, "comment": None,
                               "confidence": None, "error": str(e)})
        out.append({"barcode": str(doc["_id"]), "ingredients_raw": raw, "parsed": parsed})
    return out


@app.get("/ingredients/{barcode}/parsed/html", response_class=HTMLResponse)
def parse_html_barcode(barcode: str):
    # Reuse existing JSON logic so behavior stays identical
    result = parse_by_barcode(barcode)

    # Build table rows
    rows = "\n".join(
        f"<tr>"
        f"<td>{i+1}</td>"
        f"<td>{(p.get('raw') or '').replace('<','&lt;').replace('>','&gt;')}</td>"
        f"<td>{p.get('name') or ''}</td>"
        f"<td>{(p.get('amount') or {}).get('quantity','')}</td>"
        f"<td>{(p.get('amount') or {}).get('unit','')}</td>"
        f"<td>{p.get('preparation') or ''}</td>"
        f"<td>{p.get('comment') or ''}</td>"
        f"<td>{p.get('confidence') if p.get('confidence') is not None else ''}</td>"
        f"<td>{p.get('error') or ''}</td>"
        f"</tr>"
        for i, p in enumerate(result["parsed"])
    )

    raw_safe = (result["ingredients_raw"] or "").replace("<","&lt;").replace(">","&gt;")

    return f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Parsed Ingredients – {result['barcode']}</title>
        <style>
          :root {{ color-scheme: light dark; }}
          body {{ font-family: system-ui, Segoe UI, Arial; margin: 24px; }}
          h2 small {{ font-weight: normal; color: #666; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
          th {{ background: #f5f5f5; text-align: left; }}
          code {{ background:#f6f8fa; padding:2px 4px; border-radius:4px; }}
        </style>
      </head>
      <body>
        <h2>Barcode: {result['barcode']} <small>(ingredient-slicer)</small></h2>
        <p><b>Raw:</b> <code>{raw_safe}</code></p>
        <table>
          <thead>
            <tr>
              <th>#</th><th>Raw</th><th>Name</th><th>Qty</th><th>Unit</th>
              <th>Prep</th><th>Comment</th><th>Conf.</th><th>Error</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </body>
    </html>
    """