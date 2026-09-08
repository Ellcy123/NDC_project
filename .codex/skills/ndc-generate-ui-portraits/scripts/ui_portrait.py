"""Deterministic UI crops. Technical evidence only; never grants visual approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique)


def profiles():
    return read_json(ROOT / "assets/profiles.json")["profiles"]


def point(data, key, size):
    value = data[key]
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{key} must be [x, y]")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in value):
        raise ValueError(f"{key} must be finite numeric coordinates")
    if not (0 <= value[0] < size[0] and 0 <= value[1] < size[1]):
        raise ValueError(f"{key} lies outside source")
    return value


def load_master(source, landmarks):
    source = Path(source).resolve()
    marks = read_json(landmarks)
    if marks.get("source_sha256") != sha(source):
        raise ValueError("Stale landmark source_sha256")
    if not marks.get("reviewer") or not marks.get("note"):
        raise ValueError("Landmarks require reviewer and actual observation note")
    with Image.open(source) as raw:
        raw.load()
        if raw.width * 4 != raw.height * 3:
            raise ValueError("Master must be 3:4")
        if raw.mode not in ("RGB", "RGBA"):
            raise ValueError("Master must be RGB or opaque RGBA")
        if raw.mode == "RGBA" and raw.getchannel("A").getextrema() != (255, 255):
            raise ValueError("Scene-backed master must be fully opaque")
        im = raw.convert("RGB")
    for key in ("left_eye", "right_eye", "chin"):
        point(marks, key, im.size)
    if marks["left_eye"] == marks["right_eye"]:
        raise ValueError("Two separate eye centers are required")
    return im, marks


def geometry(size, marks, profile):
    eye_y = (marks["left_eye"][1] + marks["right_eye"][1]) / 2
    chin_y = marks["chin"][1]
    center_x = marks.get("face_center_x", (marks["left_eye"][0] + marks["right_eye"][0]) / 2)
    if isinstance(center_x, bool) or not isinstance(center_x, (int, float)) or not math.isfinite(center_x) or not 0 <= center_x < size[0]:
        raise ValueError("Invalid face_center_x")
    if chin_y <= max(marks["left_eye"][1], marks["right_eye"][1]):
        raise ValueError("Chin must lie below both eyes")
    scale = (profile["chin_y"] - profile["eye_y"]) / (chin_y - eye_y)
    if not 0 < scale <= 1:
        raise ValueError("Upscaling is prohibited: use a higher-resolution master")
    width, height = profile["size"]
    tx = width / 2 - scale * center_x
    ty = profile["eye_y"] - scale * eye_y
    box = [-tx / scale, -ty / scale, (width - tx) / scale, (height - ty) / scale]
    if box[0] < 0 or box[1] < 0 or box[2] > size[0] or box[3] > size[1]:
        raise ValueError("Crop outside master: regenerate sufficient scene coverage")
    return {"scale": scale, "translation": [tx, ty], "source_box": box,
            "size": [width, height], "eye_target_y": profile["eye_y"],
            "chin_target_y": profile["chin_y"], "resampling": "LANCZOS",
            "resampling_count": 1}


def render(im, transform):
    return im.resize(tuple(transform["size"]), Image.Resampling.LANCZOS, box=tuple(transform["source_box"]))


def safe_output(output, source, landmarks):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Output directory already exists; use a new version")
    if output == ROOT or ROOT in output.parents:
        raise ValueError("Output cannot be inside the Skill")
    for value in (source, landmarks):
        path = Path(value).resolve()
        if path == output or output in path.parents:
            raise ValueError("Output overlaps an input")
    # Respect explicitly configured repositories and the known read-only local sources.
    import os
    blocked = [Path(r"D:/PMH/工作"), Path(r"D:/PMH/ndc")]
    blocked += [Path(os.environ[key]) for key in ("NDC_PLANNING_ROOT", "NDC_ENGINE_ROOT") if os.environ.get(key)]
    for ancestor in [output, *output.parents]:
        if (ancestor / ".git").exists() or (ancestor / "canon_manifest.json").exists():
            raise ValueError("Output must be outside project repositories")
    for root in blocked:
        root = root.resolve()
        if output == root or root in output.parents:
            raise ValueError(f"Output is inside a protected source/repository: {root}")
    return output


def compose(source, landmarks, stem, output, profile="both"):
    if (not stem or stem in (".", "..") or stem.endswith((" ", "."))
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', stem)
            or re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", stem, re.I)):
        raise ValueError("Unsafe filename stem")
    source, landmarks = Path(source).resolve(), Path(landmarks).resolve()
    output = safe_output(output, source, landmarks)
    im, marks = load_master(source, landmarks)
    configs = profiles()
    if profile != "both":
        if not isinstance(profile, str) or profile not in configs:
            raise ValueError("Profile must be both, big or small")
        configs = {profile: configs[profile]}
    transforms = {key: geometry(im.size, marks, p) for key, p in configs.items()}
    # Preflight every requested profile and guide before producing any files.
    guides = {}
    for key, p in configs.items():
        with Image.open(ROOT / "assets" / p["guide"]) as g:
            if g.size != tuple(p["size"]) or g.mode != "RGBA":
                raise ValueError(f"Invalid bundled guide: {key}")
            guides[key] = g.copy()
    receipt = {"schema": "ndc-ui-portrait-composition/v1", "source": {"path": str(source), "sha256": sha(source)},
               "landmarks": {"path": str(landmarks), "sha256": sha(landmarks)},
               "profile_config_sha256": sha(ROOT / "assets/profiles.json"),
               "requested_profiles": list(configs),
               "technical_status": "TECHNICAL_PASS", "visual_status": "NOT_CHECKED", "profiles": {}}
    output.mkdir(parents=True)
    for key, transform in transforms.items():
        result = render(im, transform)
        target = output / key / f"{stem}_{key}.png"
        target.parent.mkdir()
        result.save(target)
        review = output / "review" / key
        review.mkdir(parents=True)
        Image.alpha_composite(result.convert("RGBA"), guides[key]).convert("RGB").save(review / "guide-overlay.png")
        result.resize((result.width * 2, result.height * 2), Image.Resampling.NEAREST).save(review / "whole-200.png")
        receipt["profiles"][key] = {**transform, "path": target.relative_to(output).as_posix(), "sha256": sha(target)}
    (output / "composition.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def audit(receipt_path):
    receipt_path = Path(receipt_path).resolve()
    receipt = read_json(receipt_path)
    if receipt.get("schema") != "ndc-ui-portrait-composition/v1":
        raise ValueError("Unknown receipt schema")
    for key in ("source", "landmarks"):
        if sha(receipt[key]["path"]) != receipt[key]["sha256"]:
            raise ValueError(f"Changed {key}")
    if receipt["profile_config_sha256"] != sha(ROOT / "assets/profiles.json"):
        raise ValueError("Profile configuration changed")
    im, marks = load_master(receipt["source"]["path"], receipt["landmarks"]["path"])
    configs = profiles()
    # Legacy v1 receipts without an explicit scope still represent a full pair.
    requested = receipt.get("requested_profiles", list(configs))
    if (not isinstance(requested, list) or not requested
            or any(not isinstance(key, str) or key not in configs for key in requested)
            or len(set(requested)) != len(requested)):
        raise ValueError("Invalid requested_profiles")
    if set(receipt["profiles"]) != set(requested):
        raise ValueError("Both big and small are required for a pair; profile entries must match requested_profiles")
    configs = {key: configs[key] for key in requested}
    for key, profile in configs.items():
        entry = receipt["profiles"][key]
        expected = geometry(im.size, marks, profile)
        if any(entry.get(k) != v for k, v in expected.items()):
            raise ValueError(f"Altered transform: {key}")
        relative = Path(entry["path"])
        target = (receipt_path.parent / relative).resolve()
        if relative.is_absolute() or receipt_path.parent not in target.parents or len(relative.parts) != 2 or relative.parts[0] != key:
            raise ValueError("Output path must be profile/file.png inside receipt directory")
        if sha(target) != entry["sha256"]:
            raise ValueError(f"Output hash mismatch: {key}")
        with Image.open(target) as actual:
            if actual.format != "PNG" or actual.mode != "RGB" or actual.size != tuple(profile["size"]):
                raise ValueError(f"Invalid PNG format/mode/size: {key}")
            if actual.tobytes() != render(im, expected).tobytes():
                raise ValueError(f"Pixels differ from direct master crop: {key}")
    return {"technical_status": "TECHNICAL_PASS", "visual_status": "NOT_CHECKED",
            "profiles_checked": list(configs), "source_sha256": receipt["source"]["sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("compose")
    for flag in ("input", "landmarks", "stem", "output-dir"):
        create.add_argument("--" + flag, required=True)
    create.add_argument("--profile", choices=("both", "big", "small"), default="both",
                        help="Export only the requested profile; default: both")
    check = sub.add_parser("audit")
    check.add_argument("--receipt", required=True)
    args = parser.parse_args()
    try:
        result = compose(args.input, args.landmarks, args.stem, args.output_dir, args.profile) if args.command == "compose" else audit(args.receipt)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"BLOCKED: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
