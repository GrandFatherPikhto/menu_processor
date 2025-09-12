#!/usr/bin/env python3
"""
menu_generator.py
Generates menu.c and menu.h from menu_config.json (or YAML).
Requirements:
  pip install jinja2 pyyaml
Usage:
  python menu_generator.py menu_config.json
"""
import sys
import json
import os
from jinja2 import Environment, FileSystemLoader, Template
from textwrap import dedent

# optional YAML support
try:
    import yaml
except Exception:
    yaml = None

# ---------- Generator logic ----------
# Allowed types:
EDITABLE_TYPES = {
    "action_bool",
    "action_int",
    "action_float",
    "action_int_factor",
    "action_int_step",
    "action_float_step",
    # action_callback is not editable (but can be in actions)
}

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    # try JSON first
    try:
        cfg = json.loads(text)
        return cfg
    except json.JSONDecodeError as e:
        # report line/col
        print(f"JSON parse error: {e.msg} at line {e.lineno} column {e.colno}")
        # try YAML if available
        if yaml:
            try:
                cfg = yaml.safe_load(text)
                return cfg
            except Exception as ye:
                print("Also YAML parse error:", ye)
                raise
        raise

def walk_and_flatten(nodes, parent=-1, flat=None, enum_prefix="ROOT"):
    if flat is None:
        flat = []
    for node in nodes:
        idx = len(flat)
        name = node.get("name")
        if not name:
            raise ValueError("Menu node without 'name' field")
        enum = (enum_prefix + "_" + name).upper().replace(" ", "_")
        ent = {
            "id": idx,
            "title": name,
            "enum": enum,
            "parent": parent,
            "child": -1,
            "next": -1,
            "prev": -1,
            "type": node.get("type", "submenu"),
            "screen": node.get("screen", None),
            "action": True if node.get("type","").startswith("action") else False,
            "callback": node.get("callback"),
            # fields for editable types
            "min": node.get("min"),
            "max": node.get("max"),
            "default": node.get("default"),
            "step": node.get("step", 1),
            "factors": node.get("factors"),
            "default_factor_idx": node.get("default_factor_idx", 0),
            "values": node.get("values")
        }
        flat.append(ent)
        children = node.get("children") or node.get("submenu")
        if children:
            # link child later after flattening children; but remember first child index
            child_start = len(flat)
            walk_and_flatten(children, idx, flat, enum)
            if child_start < len(flat):
                flat[idx]["child"] = child_start
    # after single level appended, set siblings (prev/next)
    # compute siblings per parent
    return flat

def assign_siblings(flat):
    by_parent = {}
    for n in flat:
        by_parent.setdefault(n["parent"], []).append(n)
    for siblings in by_parent.values():
        for i, n in enumerate(siblings):
            if i>0:
                n["prev"] = siblings[i-1]["id"]
            if i < len(siblings)-1:
                n["next"] = siblings[i+1]["id"]

def find_root(flat):
    # root is the first element with parent == -1
    for n in flat:
        if n["parent"] == -1:
            return n
    return flat[0] if flat else None

def connectivity_check(flat, root_id):
    reachable = set()
    stack = [root_id]
    while stack:
        cur = stack.pop()
        if cur in reachable: continue
        reachable.add(cur)
        n = flat[cur]
        # add child and siblings and parent links to traverse
        if n["child"] != -1:
            stack.append(n["child"])
        if n["next"] != -1:
            stack.append(n["next"])
        if n["prev"] != -1:
            stack.append(n["prev"])
        if n["parent"] != -1:
            stack.append(n["parent"])
    orphans = [n for n in flat if n["id"] not in reachable]
    return orphans

def build_outputs(flat, out_c, out_h):
    # build lists for actions, screens, factors, editable entries
    actions = [n for n in flat if n["type"].startswith("action")]
    screens = [n for n in flat if n.get("screen")]
    factors_map = {}  # map factor enum -> {values, len}
    data_entries = []
    for n in flat:
        if n["type"] in ("action_int_factor",):
            # store factor table
            if not n.get("factors"):
                raise ValueError(f"Node {n['title']} type action_int_factor requires 'factors' array")
            fenum = n["enum"] + "_FACTORS"
            factors_map[n["enum"]] = {"enum": n["enum"], "values": n["factors"], "len": len(n["factors"])}
        if n["type"] in EDITABLE_TYPES:
            # create data entry
            typ = "MD_TYPE_INT"
            val_field = "i"
            val = 0
            factor_idx = -1
            step = n.get("step", 1)
            if n["type"] == "action_bool":
                typ = "MD_TYPE_BOOL"
                val_field = "b"
                val = "true" if n.get("default", False) else "false"
            elif n["type"] in ("action_int", "action_int_factor", "action_int_step"):
                typ = "MD_TYPE_INT"
                val_field = "i"
                val = int(n.get("default", 0))
                if n["type"] == "action_int_factor":
                    factor_idx = int(n.get("default_factor_idx", 0))
            elif n["type"] in ("action_float", "action_float_step"):
                typ = "MD_TYPE_FLOAT"
                val_field = "f"
                val = float(n.get("default", 0.0))
            entry = {
                "id": n["id"],
                "type": typ,
                "val_field": val_field,
                "val": val,
                "min": int(n.get("min", 0)) if n.get("min") is not None else 0,
                "max": int(n.get("max", 0)) if n.get("max") is not None else 0,
                "step": int(n.get("step", 1)),
                "factor_idx": factor_idx if factor_idx is not None else -1,
                # keep factor enum relation if needed in C for factors_map
                "factor_enum": n["enum"] if n["type"] == "action_int_factor" else None
            }
            data_entries.append(entry)

    # prepare context
    ctx = {
        "flat": flat,
        "actions": actions,
        "screens": screens,
        "factor_defs": [{"enum": k, "len": v["len"], "values": v["values"]} for k, v in factors_map.items()],
        "factors_map": {k: {"enum": k, "len": v["len"], "values": v["values"]} for k, v in factors_map.items()},
        "editable_count": len(data_entries),
        "data_entries": data_entries,
        "root_id": find_root(flat)["id"] if flat else 0,
        "root_id_enum": find_root(flat)["enum"] if flat else "ROOT",
    }

    # шаблоны ищем в папке "templates"
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

    ctx = {"flat": flat}

    # menu.c
    tmpl_c = env.get_template("template.c.j2")
    with open(out_c, "w", encoding="utf-8") as f:
        f.write(tmpl_c.render(**ctx))

    # menu.h
    tmpl_h = env.get_template("template.h.j2")
    with open(out_h, "w", encoding="utf-8") as f:
        f.write(tmpl_h.render(**ctx))

def main():
    path = "config/menu_config_02.json"
    cfg = load_config(path)
    if not isinstance(cfg, dict) or "menu" not in cfg:
        print("Config must be an object with key 'menu' (array).")
        return
    out_c = "menu.c"
    out_h = "menu.h"
    if isinstance(cfg.get("output"), dict):
        out_c = cfg["output"].get("c", out_c)
        out_h = cfg["output"].get("h", out_h)

    flat = walk_and_flatten(cfg["menu"])
    assign_siblings(flat)
    # connectivity check
    root = find_root(flat)
    root_id = root["id"] if root else 0
    orphans = connectivity_check(flat, root_id)
    if orphans:
        print("Connectivity check: found orphan nodes (not reachable from root):")
        for o in orphans:
            print(f" - id={o['id']} name='{o['title']}' parent={o['parent']}")
        print("Please fix menu_config. Aborting generation.")
        return
    # finalize: set action flag and screen boolean consistently
    for n in flat:
        n["action"] = (n["type"].startswith("action"))
        # screen string: if screen present, also set screen function name
        if n.get("screen"):
            n["screen_func"] = "screen_" + n["enum"].lower()
        else:
            n["screen_func"] = None
    # generate outputs
    build_outputs(flat, out_c, out_h)


if __name__ == "__main__":
    main()
