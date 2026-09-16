#!/usr/bin/env python3
"""Build derived knowledge indexes from the authoritative DM2 sources.

Reads (committed, human-curated sources):
  dm2-reference/dm2-data-dictionary.yaml   — 279 terms + monster matrix
  dm2-reference/dm2-metamodel-2.02.yaml    — 19 submodels, taxonomy, tuples

Emits (shipped, runtime-loaded compact indexes under dm2-reference/core/):
  terms.json              — 279×{id, term, definition, aliases, groups, association, status, erd}
  associations.json       — binary associations {label, endpoints, homes}
  taxonomy.json           — super-subtype parents/children + powertype pairs
  view-content-spec.json  — per-view necessary/optional terms + necessary associations

Deterministic and zero-LLM: runtime never parses the 840 KB source YAMLs.
Run after editing either source:  python3 scripts/build_knowledge_indexes.py
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "dm2-reference"
CORE = REF / "core"

DD_PATH = REF / "dm2-data-dictionary.yaml"
MM_PATH = REF / "dm2-metamodel-2.02.yaml"

# ── submodel (dictionary x-marks) → 17 data-group scheme ──────────────────
SUBMODEL_TO_GROUPS = {
    "performer": ["01-performer"],
    "capability": ["03-capability"],
    "measure": ["06-measure"],
    "location": ["07-location"],
    "services": ["08-services"],
    "project": ["09-project"],
    "resource-flow": ["11-resource-flow"],
    "information-and-data": ["16-information-data"],
    "information-pedigree": ["13-information-pedigree"],
    "organizational-structure": ["14-org-structure"],
    "pedigree": ["12-pedigree"],
    "reification-levels": ["15-reification"],
    "dm2-foundation": ["00-foundation"],
    "ideas-foundation": ["00-foundation"],
    # "rules" splits by term name — handled in reconcile_groups()
}

GUIDANCE_NAME_HINTS = ("Guidance", "Standard", "Agreement")

OPTIONAL_TERMS_CAP = 30


def short(curie: str) -> str:
    """dodaf:Performer → Performer ; ideas:tuple → tuple."""
    if not curie:
        return ""
    return curie.split(":", 1)[1] if ":" in curie else curie


def reconcile_groups(term: dict) -> list:
    """Map a dictionary term to its 17-scheme data-group ids (sorted, unique)."""
    groups = []
    for submodel, mark in (term.get("submodels") or {}).items():
        if mark != "x":
            continue
        if submodel == "rules":
            name = term.get("term", "")
            if any(hint in name for hint in GUIDANCE_NAME_HINTS):
                groups.append("05-guidance")
            else:
                groups.append("10-rules")
        else:
            groups.extend(SUBMODEL_TO_GROUPS.get(submodel, []))
    # Synthetic attribution: the 17-group scheme has Activity/Resource groups
    # that have no counterpart in the dictionary's submodel list.
    name = term.get("term", "")
    if name == "Activity" or name.startswith(("activity", "Activity")):
        groups.append("02-activity")
    if name in ("Resource", "Materiel") or "esource" in name or "ateriel" in name:
        groups.append("04-resource")
    return sorted(set(groups))


# ── terms.json ────────────────────────────────────────────────────────────
def build_terms(dd_terms: list) -> list:
    terms = []
    for t in dd_terms:
        terms.append({
            "id": t.get("id", ""),
            "term": t.get("term", ""),
            "definition": t.get("definition", "") or "",
            "aliases": t.get("aliases") or [],
            "groups": reconcile_groups(t),
            "association": bool(t.get("association")),
            "status": t.get("status", ""),
            "erd": bool(t.get("erd_diagram")),
        })
    return terms


# ── associations.json ─────────────────────────────────────────────────────
def _parse_role(raw: str):
    """'<<place1Type>>|consumer' → ('place1Type', 'consumer'); '1' → ('','')."""
    if not raw:
        return "", ""
    ideas_role = ""
    domain_role = ""
    if "|" in raw:
        ideas_part, _, domain_part = raw.partition("|")
        domain_role = domain_part.strip()
        raw = ideas_part
    m = re.match(r"<<(.+?)>>", raw)
    if m:
        ideas_role = m.group(1)
    elif raw.strip() and not raw.strip().isdigit():
        ideas_role = raw.strip()  # bare role like 'place1Type'
    return ideas_role, domain_role


def build_associations(mm: dict) -> list:
    catalog = {}  # label -> entry
    for sub_name, sub in mm["submodels"].items():
        for cls in sub.get("classes", []):
            if cls.get("ideas_type") != "Tuple":
                continue
            label = cls.get("label") or short(cls.get("id", ""))
            couples = [
                c for c in (cls.get("couples") or [])
                if c.get("uml_metaclass") == "NavigableAssociation"
            ]
            entry = catalog.setdefault(label, {
                "label": label,
                "endpoints": [],
                "homes": [],
            })
            if sub_name not in entry["homes"]:
                entry["homes"].append(sub_name)
            if not entry["endpoints"] and len(couples) == 2:
                endpoints = []
                for cp in couples:
                    ideas_role, domain_role = _parse_role(cp.get("role", ""))
                    endpoints.append({
                        "type": short(cp.get("participant", "")),
                        "ideas_role": ideas_role,
                        "domain_role": domain_role,
                        "multiplicity": cp.get("multiplicityParticipant", ""),
                    })
                entry["endpoints"] = endpoints
    return sorted(catalog.values(), key=lambda e: e["label"])


# ── taxonomy.json ─────────────────────────────────────────────────────────
def build_taxonomy(mm: dict) -> dict:
    parents = {}   # child -> [parents]
    children = {}  # parent -> [children]
    powertype_pairs = []

    def add_edge(child, parent):
        parents.setdefault(child, [])
        children.setdefault(parent, [])
        if parent not in parents[child]:
            parents[child].append(parent)
        if child not in children[parent]:
            children[parent].append(child)

    for sub in mm["submodels"].values():
        for rel in sub.get("relations", []):
            stereo = rel.get("stereotype", "")
            src, tgt = short(rel.get("source", "")), short(rel.get("target", ""))
            if stereo in ("<<super-subtype>>", "<<superSubtype>>"):
                # naming convention: ruleSubtypeOfGuidance — source is subtype
                add_edge(src, tgt)
            elif stereo == "<<powertypeInstance>>":
                pair = {"individual": src, "powertype": tgt}
                if pair not in powertype_pairs:
                    powertype_pairs.append(pair)

    for d in (parents, children):
        for k in d:
            d[k] = sorted(set(d[k]))
    return {
        "parents": dict(sorted(parents.items())),
        "children": dict(sorted(children.items())),
        "powertype_pairs": sorted(powertype_pairs, key=lambda p: (p["individual"], p["powertype"])),
    }


# ── view-content-spec.json ───────────────────────────────────────────────
VIEW_ID_RE = re.compile(
    r"^(AV-\d+|CV-\d+|DIV-\d+|OV-\d+[a-c]?|SV-\d+[a-c]?|SvcV-\d+[a-c]?|PV-\d+|Standards View-\d+)"
)


def normalize_view_id(column: str):
    m = VIEW_ID_RE.match(column.strip())
    if not m:
        return None
    vid = m.group(1)
    if vid.startswith("Standards View"):
        vid = "StdV-" + vid.split("-")[1]
    return vid


def build_view_content_spec(dd_terms: list, associations: list) -> dict:
    assoc_by_label = {a["label"]: a for a in associations}

    # view_id -> {"necessary_terms": [], "optional_terms": [],
    #             "necessary_associations": []}
    spec = {}
    for t in dd_terms:
        term_name = t.get("term", "")
        is_assoc = bool(t.get("association"))
        for column, mark in (t.get("view_products") or {}).items():
            vid = normalize_view_id(column)
            if not vid or mark not in ("n", "o"):
                continue
            bucket = spec.setdefault(vid, {
                "necessary_terms": [],
                "optional_terms": [],
                "necessary_associations": [],
            })
            if mark == "n":
                if is_assoc:
                    cat = assoc_by_label.get(term_name)
                    if cat and cat["endpoints"]:
                        bucket["necessary_associations"].append({
                            "label": term_name,
                            "endpoint_types": [e["type"] for e in cat["endpoints"]],
                            "roles": [
                                {"ideas": e["ideas_role"], "domain": e["domain_role"]}
                                for e in cat["endpoints"]
                            ],
                        })
                    else:
                        bucket["necessary_associations"].append({"label": term_name})
                else:
                    bucket["necessary_terms"].append(term_name)
            else:
                bucket["optional_terms"].append(term_name)

    for vid, bucket in spec.items():
        bucket["necessary_terms"] = sorted(set(bucket["necessary_terms"]))
        bucket["optional_terms"] = sorted(set(bucket["optional_terms"]))[:OPTIONAL_TERMS_CAP]
        bucket["necessary_associations"].sort(key=lambda a: a["label"])
    return dict(sorted(spec.items()))


# ── group template relationship reconciliation ───────────────────────────
# Domain submodels (real homes) → 17-group. Foundation pages that merely
# repeat tuples (foundation_for_associations / domain_class_hierarchy) are
# NOT homes.
SUBMODEL_HOME_GROUP = {
    "performer": "01-performer",
    "capability": "03-capability",
    "services": "08-services",
    "measure": "06-measure",
    "location": "07-location",
    "project": "09-project",
    "resource_flow": "11-resource-flow",
    "organizational_structure": "14-org-structure",
    "information_and_data": "16-information-data",
    "information_pedigree": "13-information-pedigree",
    "pedigree": "12-pedigree",
}
# Tuples modeled only on foundation pages → meta groups
FOUNDATION_HOME_GROUP = {
    "ideas_toplevel": "00-foundation",
    "common_patterns": "00-foundation",
    "naming_and_description": "00-foundation",
    "temporal_part_and_boundaries": "00-foundation",
    "reification_levels": "15-reification",
}
GUIDANCE_TYPES = {"Guidance", "Rule", "Standard", "FunctionalStandard",
                  "TechnicalStandard", "Agreement", "SecurityAttributeGroup",
                  "Constraint"}
# Groups without their own metamodel submodel: anchor by endpoint/label.
ACTIVITY_ANCHOR_TYPES = {"Activity", "SingletonActivity", "IndividualActivity"}
RESOURCE_ANCHOR_TYPES = {"Resource", "Materiel", "SingletonResource"}


def project_group_associations(associations: list, taxonomy: dict) -> dict:
    """Group id → sorted association labels projected for that group's template."""
    children = taxonomy.get("children", {})

    def closure(t):
        s, stack = {t}, [t]
        while stack:
            for c in children.get(stack.pop(), []):
                if c not in s:
                    s.add(c)
                    stack.append(c)
        return s

    groups = {}

    def add(gid, label):
        groups.setdefault(gid, set()).add(label)

    for assoc in associations:
        endpoints = assoc.get("endpoints") or []
        if len(endpoints) != 2:
            continue
        label = assoc["label"]
        # Template keys must be clean ASCII identifiers (skip localized labels).
        if not label.isascii() or not label.isidentifier():
            continue
        types = [e["type"] for e in endpoints]
        homes = assoc.get("homes", [])

        # 1) domain submodel homes
        for h in homes:
            gid = SUBMODEL_HOME_GROUP.get(h)
            if gid:
                add(gid, label)
            elif h == "rules":
                # guidance split: endpoints on the Guidance subtree → 05, else 10
                if any(t in GUIDANCE_TYPES for t in types):
                    add("05-guidance", label)
                add("10-rules", label)

        # 2) foundation pattern vocabulary (additive — these are the
        #    cross-cutting pattern tuples, owned by the meta groups)
        for h in homes:
            gid = FOUNDATION_HOME_GROUP.get(h)
            if gid:
                add(gid, label)

        # 3) submodel-less vault groups: Activity and Resource anchors
        if any(t in ACTIVITY_ANCHOR_TYPES for t in types) or label.lower().startswith("activity"):
            add("02-activity", label)
        if any(t in RESOURCE_ANCHOR_TYPES for t in types) \
                or "resource" in label.lower() or "materiel" in label.lower():
            add("04-resource", label)

    return {gid: sorted(labels) for gid, labels in sorted(groups.items())}


# ── template frontmatter + prose rewriting ───────────────────────────────
_REL_BLOCK_RE = re.compile(r"(^relationships:\n)((?:[ \t]+.*\n)*)", re.M)
_AUTHORITATIVE_BLOCK = "## DM2 关联清单（元模型权威）"

# 正文土话关系标题 → 权威关联名（按组裁定；语义无法对应的条目不映射，保留原样）
VERNACULAR_TO_CATALOG = {
    "01-performer": {
        "performs": "activityPerformedByPerformer",
        "partOf": "wholePart", "hasPart": "wholePart",
        "providesService": "serviceEnablesAccessToResource",
        "locatedAt": "resourceInLocationType",
        "measuredBy": "measureOfTypeResource",
    },
    "02-activity": {
        "consumes": "activityConsumesResource", "produces": "activityProducesResource",
        "partOf": "activityPartOfCapability", "hasPart": "activityPartOfCapability",
        "prerequisite": "beforeAfter", "successor": "beforeAfter",
        "measuredBy": "measureTypeApplicableToActivity",
    },
    "03-capability": {
        "composedOf": "activityPartOfCapability", "contributesTo": "desiredEffectOfCapability",
        "desiredEffect": "desiredEffect", "measuredBy": "measureOfTypeResource",
        "performs": "activityPerformedByPerformer", "partOf": "activityPartOfCapability",
    },
    "04-resource": {
        "producedBy": "activityProducesResource", "consumedBy": "activityConsumesResource",
        "storedAt": "resourceInLocationType", "locatedIn": "resourceInLocationType",
        "accessedVia": "serviceEnablesAccessToResource",
    },
    "05-guidance": {
        "constrains": "ruleConstrainsActivity", "derivedFrom": "superSubtype",
    },
    "06-measure": {
        "measures": "measureOfTypeResource", "partOf": "wholePart",
        "contributesTo": "desiredEffectOfCapability",
    },
    "07-location": {
        "hosts": "resourceInLocationType", "locatedAt": "resourceInLocationType",
        "partOf": "wholePart", "hasPart": "wholePart",
        # adjacentTo / connectedTo：拓扑关系不在 DM2 关联目录，不映射
    },
    "08-services": {
        "providesService": "serviceEnablesAccessToResource",
        "hasPort": "portPartOfPerformer", "operatesOn": "activityConsumesResource",
    },
    "09-project": {
        "realizesCapability": "desiredEffectIsRealizedByProjectType",
        "performedBy": "activityPerformedByPerformer",
    },
    "10-rules": {
        "appliesTo": "ruleConstrainsActivity", "derivedFromGuidance": "superSubtype",
    },
    "12-pedigree": {
        "derivedFrom": "superSubtype", "hasDerivative": "superSubtype",
    },
    "14-org-structure": {
        "reportsTo": "overlap", "partOf": "wholePart", "hasPart": "wholePart",
    },
    "16-information-data": {
        "structures": "describedBy", "dataElementOf": "wholePart",
    },
}

# 正文出现的土话标题模式（### 标题 / - **粗体** / 表格单元格 "X →"）
_VERN_H3_RE = re.compile(r"^### ([a-zA-Z]+)（([^）]*)）", re.M)
_VERN_BOLD_RE = re.compile(r"^- \*\*([a-zA-Z]+)\*\*", re.M)
_VERN_TABLE_RE = re.compile(r"\|\s*([a-zA-Z]+)\s+→")


def _authoritative_block(gid: str, projection: dict, assoc_by_label: dict) -> str:
    """生成统一权威关联清单块（frontmatter 后注入，幂等）。"""
    labels = projection.get(gid, [])
    if not labels:
        return ""
    lines = [f"{_AUTHORITATIVE_BLOCK}", "> 本组权威关联（来自 dm2-metamodel-2.02.yaml 关联目录）："]
    for label in labels:
        assoc = assoc_by_label.get(label)
        if assoc and len(assoc.get("endpoints") or []) == 2:
            eps = " ─▶ ".join(e["type"] for e in assoc["endpoints"])
            lines.append(f"> - {label}: {eps}")
        else:
            lines.append(f"> - {label}")
    lines.append("")
    return "\n".join(lines)


def _replace_vernacular_in_text(text: str, gid: str, mapping: dict) -> tuple[str, list]:
    """替换正文中的土话标题为权威关联名；返回 (新文本, 替换记录)。"""
    replaced = []
    vern = VERNACULAR_TO_CATALOG.get(gid, {})

    def _map(name):
        """土话 → 权威关联名；自身映射或无合法目标返回 None。"""
        target = vern.get(name)
        if not target or target == name or target not in mapping:
            return None
        return target

    def _sub_h3(m):
        name, cn = m.group(1), m.group(2)
        target = _map(name)
        if target:
            replaced.append((name, target))
            return f"### {target}（{cn}）"
        return m.group(0)

    def _sub_bold(m):
        name = m.group(1)
        target = _map(name)
        if target:
            replaced.append((name, target))
            return f"- **{target}**"
        return m.group(0)

    def _sub_table(m):
        name = m.group(1)
        target = _map(name)
        if target:
            replaced.append((name, target))
            return f"| {target} →"
        return m.group(0)

    text = _VERN_H3_RE.sub(_sub_h3, text)
    text = _VERN_BOLD_RE.sub(_sub_bold, text)
    text = _VERN_TABLE_RE.sub(_sub_table, text)
    return text, replaced


def reconcile_group_templates(projection: dict, associations: list, taxonomy: dict,
                              fix: bool = False):
    """Check (or --fix) template relationships block AND prose relationship headings.

    1. frontmatter `relationships:` 块重写为目录投影（既有逻辑）
    2. 正文土话关系标题替换为权威关联名（VERNACULAR_TO_CATALOG 按组映射）
    3. frontmatter 后注入统一权威关联清单块（幂等）
    4. 01-performer 的 dm2-subtype 与正文子类型行同步为 taxonomy 子类
    """
    assoc_by_label = {a["label"]: a for a in associations}
    templates = sorted(CORE.glob("groups/*/*Template.md"))
    drift = []
    for tpl in templates:
        gid = tpl.parent.name
        expected = projection.get(gid, [])
        text = tpl.read_text(encoding="utf-8")

        # ── 1. relationships frontmatter block ──
        m = _REL_BLOCK_RE.search(text)
        old_slots = re.findall(r"^  ([\w-]+):", m.group(0), re.M) if m else []
        if set(old_slots) != set(expected):
            drift.append((gid, tpl.name, "relationships", sorted(set(old_slots)), expected))
            if fix and m:
                new_block = "relationships:\n" + "".join(f"  {label}: []\n" for label in expected)
                text = text[:m.start()] + new_block + text[m.end():]

        # ── 2. prose vernacular headings → authoritative labels ──
        text, replaced = _replace_vernacular_in_text(text, gid, assoc_by_label)
        if replaced:
            drift.append((gid, tpl.name, "prose", [r[0] for r in replaced],
                          [r[1] for r in replaced]))

        # ── 3. authoritative block injection (idempotent) ──
        if _AUTHORITATIVE_BLOCK not in text and fix:
            block = _authoritative_block(gid, projection, assoc_by_label)
            if block:
                # 注入在 frontmatter 结束（---\n）之后的正文开头
                fm_end = text.find("---\n", text.find("---\n") + 1)
                if fm_end != -1:
                    text = text[:fm_end + 4] + "\n" + block + text[fm_end + 4:]
                    drift.append((gid, tpl.name, "authoritative-block", [], []))

        # ── 4. 01-performer subtype sync from taxonomy ──
        if gid == "01-performer":
            subs = sorted(taxonomy.get("children", {}).get("Performer", []))
            if subs:
                subtype_str = " | ".join(subs)
                m_fm = re.search(r"^dm2-subtype:.*$", text, re.M)
                if m_fm and m_fm.group(0) != f"dm2-subtype: {subtype_str}":
                    text = re.sub(r"^dm2-subtype:.*$", f"dm2-subtype: {subtype_str}",
                                  text, count=1, flags=re.M)
                    drift.append((gid, tpl.name, "dm2-subtype", [], [subtype_str]))
                m_prose = re.search(r"^\| 子类型 \|.*$", text, re.M)
                if m_prose and subtype_str not in m_prose.group(0):
                    text = re.sub(r"^\| 子类型 \|.*$", f"| 子类型 | {subtype_str} |",
                                  text, count=1, flags=re.M)

        if fix:
            tpl.write_text(text, encoding="utf-8")
    return drift


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build derived DM2 knowledge indexes.")
    parser.add_argument("--check-templates", action="store_true",
                        help="Check group template relationships blocks against associations.json")
    parser.add_argument("--fix-templates", action="store_true",
                        help="Rewrite group template relationships blocks from catalog projection")
    args = parser.parse_args()

    if not DD_PATH.exists() or not MM_PATH.exists():
        sys.exit(f"Source YAMLs missing under {REF}/")

    dd = yaml.safe_load(DD_PATH.read_text(encoding="utf-8"))
    dd_terms = dd if isinstance(dd, list) else dd.get("terms", [])
    mm = yaml.safe_load(MM_PATH.read_text(encoding="utf-8"))

    terms = build_terms(dd_terms)
    associations = build_associations(mm)
    taxonomy = build_taxonomy(mm)
    content_spec = build_view_content_spec(dd_terms, associations)

    CORE.mkdir(parents=True, exist_ok=True)
    outputs = {
        "terms.json": terms,
        "associations.json": associations,
        "taxonomy.json": taxonomy,
        "view-content-spec.json": content_spec,
    }
    for name, data in outputs.items():
        (CORE / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )

    # ── coverage report ──
    binary = [a for a in associations if len(a["endpoints"]) == 2]
    dd_assoc = {t["term"] for t in dd_terms if t.get("association")}
    assoc_labels = {a["label"] for a in binary}
    n_views = len(content_spec)
    resolved = sum(1 for v in content_spec.values()
                   for a in v["necessary_associations"] if a.get("endpoint_types"))
    total_nassoc = sum(len(v["necessary_associations"]) for v in content_spec.values())
    print("Index build complete:")
    print(f"  terms.json:               {len(terms)} terms")
    print(f"  associations.json:        {len(associations)} tuples "
          f"({len(binary)} binary; {len(dd_assoc & assoc_labels)}/{len(dd_assoc)} "
          f"dictionary associations resolved)")
    print(f"  taxonomy.json:            {len(taxonomy['parents'])} subtypes, "
          f"{len(taxonomy['powertype_pairs'])} powertype pairs")
    print(f"  view-content-spec.json:   {n_views} views, {total_nassoc} necessary "
          f"associations ({resolved} with endpoint types)")

    # ── group template relationship reconciliation ──
    if args.check_templates or args.fix_templates:
        projection = project_group_associations(associations, taxonomy)
        drift = reconcile_group_templates(projection, associations, taxonomy,
                                          fix=args.fix_templates)
        mode = "fixed" if args.fix_templates else "checked"
        if not drift:
            print(f"  group templates:           in sync ({mode})")
        else:
            print(f"  group templates:           {len(drift)} with drift ({mode})")
            for gid, tpl_name, section, old, expected in drift:
                print(f"    [{gid}] {tpl_name} ({section})")
                if section == "relationships":
                    removed = sorted(set(old) - set(expected))
                    added = sorted(set(expected) - set(old))
                    if removed:
                        print(f"      no-catalog-basis / renamed away: {removed}")
                    if added:
                        print(f"      catalog-projected: {added}")
                elif section == "prose":
                    print(f"      vernacular→authoritative: {list(zip(old, expected))}")
                else:
                    print(f"      {expected}")
            if args.check_templates and not args.fix_templates:
                sys.exit(1)


if __name__ == "__main__":
    main()
