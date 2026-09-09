"""Use the existing NDC visual validator; preserve real failed reviews as failed."""
import json
import os
from pathlib import Path
import runpy
import sys

script_dir = Path(__file__).resolve().parent
override = os.environ.get("NDC_STAGE_VISUAL_VALIDATOR")
validator_path = Path(override).resolve() if override else (
    script_dir.parent.parent / "ndc-prop-delivery-review" / "scripts" / "stage_visual_check.py"
).resolve()
if not validator_path.is_file():
    raise FileNotFoundError(
        "The bundled sibling visual validator is missing. Reinstall the complete Skills bundle "
        "or set NDC_STAGE_VISUAL_VALIDATOR."
    )
validator = runpy.run_path(str(validator_path))
record_path, output_path = map(Path, sys.argv[1:3])
data = json.loads(record_path.read_text(encoding='utf-8-sig'))
errors = validator['validate_record'](record_path, [output_path])
# A complete FAIL record can finish this image's inspection but never passes its descendants.
if data.get('visual_check_status') == 'FAIL':
    errors = [e for e in errors if not e.startswith('visual_check_status: formal progression requires PASS')]
    failed_indices = {
        i for i, item in enumerate(data.get('criteria', []))
        if isinstance(item, dict) and item.get('applicable') is True and item.get('status') == 'FAIL'
    }
    errors = [e for e in errors if e not in {
        f'criteria[{i}]: applicable criterion must PASS' for i in failed_indices
    }]
    if not failed_indices:
        errors.append('FAIL record must contain an explicit applicable failed finding')
print(json.dumps({'valid': not errors, 'errors': errors}, ensure_ascii=False))
