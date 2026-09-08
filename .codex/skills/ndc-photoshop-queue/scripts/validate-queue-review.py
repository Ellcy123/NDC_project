"""Use the existing NDC visual validator; preserve real failed reviews as failed."""
import json
from pathlib import Path
import runpy
import sys

binding = json.loads(Path(__file__).with_name('runtime-binding.json').read_text(encoding='utf-8'))
validator = runpy.run_path(binding['visual_validator'])
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
