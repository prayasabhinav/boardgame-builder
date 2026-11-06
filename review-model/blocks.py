"""Writes review-model/blocks.json, each block's id, slot, name and ? text, for embed.mjs. Usage: python3 review-model/blocks.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palette import DIMENSIONS
from block_meta import meta_for
json.dump([{"id": b["id"], "slot": d["id"], "display": b["display"], "description": meta_for(b["id"])["description"]} for d in DIMENSIONS for b in d["blocks"]],
          open("review-model/blocks.json", "w"), indent=1, ensure_ascii=False)
