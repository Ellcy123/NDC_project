"""Durable, bounded stage handoff; never generates images or grants artistic approval."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
from pathlib import Path
import re
import runpy
import sqlite3
import sys
import time
import uuid

SCHEMA = 'ndc-art-stage-packet/v1'
PLAN = 'ndc-art-stage-pipeline/v1'
KINDS = {'ui_portrait': 'ndc-generate-ui-portraits', 'scene_mj': 'ndc-midjourney-operator'}
ACTIVE_DISPATCH = ('RESERVED', 'SUBMITTING', 'UNKNOWN', 'SETUP_PENDING', 'BOUND', 'CLAIMED')

class PipelineBusy(RuntimeError):
    """A concurrent journal append is retryable, not an asset rejection."""

def consistent_read(packet, callback):
    journal = Path(packet['authority']['journal'])
    lock = journal.with_name(journal.name + '.lock')
    if lock.exists():
        raise PipelineBusy('Original journal is being written; retry after the short writer finishes')
    before = journal.stat()
    def changed():
        after = journal.stat()
        return lock.exists() or (after.st_mtime_ns, after.st_size) != (before.st_mtime_ns, before.st_size)
    try:
        value = callback()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        if changed():
            raise PipelineBusy('Concurrent journal append; retry this read without invalidating the unit') from exc
        raise
    if changed():
        raise PipelineBusy('Journal changed during evidence validation; recheck the stable related jobs')
    return value

def need(condition, reason):
    if not condition:
        raise ValueError(reason)

def text_id(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 250

def stable(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def digest(value):
    return hashlib.sha256(stable(value).encode()).hexdigest()

def file_hash(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write_once(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = stable(data)
    try:
        with path.open('x', encoding='utf-8') as handle:
            handle.write(body)
    except FileExistsError:
        need(path.read_text(encoding='utf-8') == body, 'Immutable evidence file changed: ' + str(path))
    return str(path.resolve())

def files_current(refs, output_root=None):
    need(isinstance(refs, list), 'files must be an array')
    roles = set()
    for ref in refs:
        need(isinstance(ref, dict) and text_id(ref.get('role')), 'File role required')
        need(ref['role'] not in roles, 'Duplicate file role: ' + ref['role'])
        roles.add(ref['role'])
        path = Path(ref.get('path', ''))
        need(path.is_absolute() and path.is_file(), 'Actual absolute file required: ' + str(path))
        if output_root:
            need(path.resolve().is_relative_to(Path(output_root).resolve()), 'Worker output must stay in its assigned directory')
        need(file_hash(path).lower() == str(ref.get('sha256', '')).lower(), 'Changed file: ' + str(path))

def workflow(packet):
    module = Path(packet['project_root']) / 'scripts/ndc-art-workflow/art_workflow_state.py'
    api = runpy.run_path(str(module))
    header, events, _ = api['load'](packet['authority']['journal'])
    need(header['plan']['task_id'] == packet['producer_task_id'], 'Use the original producer journal; do not reset task history')
    jobs = api['state'](header, events)
    declared = packet['authority']['upstream_jobs'] + packet['authority']['downstream_jobs']
    need(set(declared) <= set(jobs), 'Unknown authority job')
    return api, jobs

def _validate_packet(packet):
    need(packet.get('schema') == SCHEMA, 'Unsupported packet schema')
    need(packet.get('pipeline_kind') in KINDS, 'Unsupported pipeline')
    need(packet.get('execution_mode') in ('production', 'validation'), 'execution_mode required')
    need(packet.get('revision', 0) >= 1 and isinstance(packet['revision'], int), 'Positive revision required')
    need(text_id(packet.get('producer_task_id')), 'Real producer task ID required')
    need(bool(packet.get('files')), 'Frozen handoff files required')
    files_current(packet['files'])
    api, jobs = workflow(packet)
    for key in packet['authority']['upstream_jobs']:
        api['current_acceptance'](jobs, key)
    module = importlib.import_module('ui_adapter' if packet['pipeline_kind'] == 'ui_portrait' else 'scene_adapter')
    return module.validate_release(packet, Path(packet['packet_base']))

def validate_packet(packet):
    return consistent_read(packet, lambda: _validate_packet(packet))

def accepted_downstream(packet):
    def verify():
        api, jobs = workflow(packet)
        for job in packet['authority']['downstream_jobs']:
            api['current_acceptance'](jobs, job)
    return consistent_read(packet, verify)

class Pipeline:
    def __init__(self, database):
        self.path = Path(database).resolve()
        need(self.path.is_file(), 'Initialize the pipeline first')
        self.db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA busy_timeout=10000')
        self.plan = read_json_row(self.db.execute('SELECT body FROM meta WHERE id=1').fetchone())
        self.root = Path(self.plan['work_root'])

    @staticmethod
    def initialize(database, plan):
        database = Path(database).resolve()
        need(plan.get('schema') == PLAN and plan.get('pipeline_kind') in KINDS, 'Invalid pipeline plan')
        need(text_id(plan.get('pipeline_id')) and text_id(plan.get('controller_task_id')), 'Pipeline/controller IDs required')
        need(plan.get('execution_mode') in ('production', 'validation'), 'Explicit execution_mode required')
        root = Path(plan['work_root']).resolve()
        project = Path(plan['project_root']).resolve()
        need(root.is_relative_to(project / '工作过程文件') and root != project / '工作过程文件', 'Use an isolated work-process directory')
        need(database == root / 'pipeline.sqlite', 'Use the one canonical pipeline.sqlite inside work_root')
        units = plan.get('units')
        need(isinstance(units, list) and units, 'Full requested unit scope required')
        ids = set()
        for unit in units:
            key = unit.get('unit_id', '')
            need(re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', key) and key not in ('.', '..') and key not in ids, 'Unique stable unit_id required')
            ids.add(key)
            need(text_id(unit.get('producer_task_id')), 'Each unit needs its upstream task ID')
            authority = unit.get('authority', {})
            need(Path(authority.get('journal', '')).is_absolute(), 'Original journal absolute path required')
            for field in ('upstream_jobs', 'downstream_jobs'):
                values = authority.get(field)
                need(isinstance(values, list) and len(values) == len(set(values)) and all(text_id(v) for v in values), 'Invalid job scope')
            need(authority['downstream_jobs'], 'Downstream jobs required')
        need(not database.exists(), 'Pipeline already exists; resume it, never reset its scope or history')
        root.mkdir(parents=True, exist_ok=True)
        # Exclusive creation avoids two initializers replacing one authority.
        database.touch(exist_ok=False)
        db = sqlite3.connect(database)
        try:
            db.executescript('''PRAGMA journal_mode=WAL;
            CREATE TABLE meta(id INTEGER PRIMARY KEY CHECK(id=1),body TEXT NOT NULL);
            CREATE TABLE units(unit_id TEXT PRIMARY KEY,revision INTEGER DEFAULT 0,status TEXT NOT NULL,reason TEXT);
            CREATE TABLE packets(unit_id TEXT,revision INTEGER,body TEXT NOT NULL,sha256 TEXT NOT NULL,path TEXT NOT NULL,PRIMARY KEY(unit_id,revision));
            CREATE TABLE dispatches(dispatch_id TEXT PRIMARY KEY,unit_id TEXT,revision INTEGER,body TEXT NOT NULL,status TEXT NOT NULL);
            CREATE TABLE worker(id INTEGER PRIMARY KEY CHECK(id=1),task_id TEXT NOT NULL);
            CREATE TABLE lease(id INTEGER PRIMARY KEY CHECK(id=1),body TEXT NOT NULL);
            CREATE TABLE events(seq INTEGER PRIMARY KEY AUTOINCREMENT,at REAL,kind TEXT,body TEXT);
            ''')
            db.execute('INSERT INTO meta VALUES(1,?)', (stable(plan),))
            db.executemany('INSERT INTO units(unit_id,status) VALUES(?,?)', [(u['unit_id'], 'WAITING_UPSTREAM') for u in units])
            db.commit()
        finally:
            db.close()
        return {'status': 'INITIALIZED', 'database_path': str(database), 'total_units': len(ids)}

    def close(self):
        self.db.close()

    @contextmanager
    def tx(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def event(self, kind, data):
        clean = {k: v for k, v in data.items() if k != 'token'}
        self.db.execute('INSERT INTO events(at,kind,body) VALUES(?,?,?)', (time.time(), kind, stable(clean)))

    def controller(self, task):
        need(task == self.plan['controller_task_id'], 'Only the declared controller may dispatch or reconcile')

    def unit_plan(self, unit_id):
        found = [u for u in self.plan['units'] if u['unit_id'] == unit_id]
        need(len(found) == 1, 'Unit is outside the full plan scope')
        return found[0]

    def packet(self, unit_id, revision=None):
        if revision is None:
            row = self.db.execute('SELECT revision FROM units WHERE unit_id=?', (unit_id,)).fetchone()
            need(row and row['revision'], 'Unit has no published packet')
            revision = row['revision']
        row = self.db.execute('SELECT * FROM packets WHERE unit_id=? AND revision=?', (unit_id, revision)).fetchone()
        need(row and file_hash(row['path']) == row['sha256'], 'Frozen packet file missing or changed')
        packet = json.loads(row['body'])
        need(digest(packet) == row['sha256'], 'Packet database binding changed')
        return packet, row

    def publish(self, packet, task, base):
        packet = json.loads(stable(packet))
        unit = self.unit_plan(packet.get('unit_id'))
        need(task == unit['producer_task_id'], 'Wrong upstream producer')
        for name in ('producer_task_id', 'authority'):
            need(packet.get(name) == unit[name], 'Packet must retain original ' + name)
        for name in ('project_root', 'pipeline_kind', 'execution_mode'):
            need(packet.get(name, self.plan[name]) == self.plan[name], 'Packet changes frozen plan ' + name)
            packet[name] = self.plan[name]
        packet['packet_base'] = str(Path(base).resolve())
        packet['work_directory'] = str(self.root / 'outputs' / packet['unit_id'] / str(packet['revision']))
        check = validate_packet(packet)
        body_hash = digest(packet)
        frozen = self.root / 'handoffs' / (packet['unit_id'] + '-' + str(packet['revision']) + '-' + body_hash[:12] + '.json')
        # Atomic database publication follows durable immutable packet preparation.
        write_once(frozen, packet)
        with self.tx():
            current = self.db.execute('SELECT * FROM units WHERE unit_id=?', (packet['unit_id'],)).fetchone()
            if current['revision'] == packet['revision']:
                prior = self.db.execute('SELECT sha256 FROM packets WHERE unit_id=? AND revision=?', (packet['unit_id'], packet['revision'])).fetchone()
                need(prior and prior['sha256'] == body_hash, 'Same revision cannot change; publish an explicit new revision')
                return {'status': 'ALREADY_PUBLISHED', 'unit_id': packet['unit_id'], 'revision': packet['revision']}
            need(packet['revision'] == current['revision'] + 1, 'Revisions must append without gaps')
            self.db.execute('INSERT INTO packets VALUES(?,?,?,?,?)', (packet['unit_id'], packet['revision'], stable(packet), body_hash, str(frozen)))
            status = 'WAITING_MANUAL' if check.get('can_execute') is False and not check.get('validation_only') else 'READY'
            self.db.execute('UPDATE units SET revision=?,status=?,reason=? WHERE unit_id=?', (packet['revision'], status, check.get('stop_reason'), packet['unit_id']))
            value = {'status': status, 'unit_id': packet['unit_id'], 'revision': packet['revision'], 'packet_path': str(frozen), 'packet_sha256': body_hash}
            self.event('publish', value)
            return value

    def reserve_dispatch(self, task):
        self.controller(task)
        with self.tx():
            active = self.db.execute('SELECT dispatch_id,status FROM dispatches WHERE status IN (?,?,?,?,?,?)', ACTIVE_DISPATCH).fetchone()
            if active:
                return {'status': 'BLOCKED_EXISTING_DISPATCH', 'dispatch_id': active['dispatch_id'], 'existing_status': active['status']}
            if self.db.execute('SELECT 1 FROM lease').fetchone():
                return {'status': 'WORKER_BUSY'}
            ready = self.db.execute("SELECT * FROM units WHERE status='READY' ORDER BY rowid").fetchall()
            for item in ready:
                try:
                    packet, row = self.packet(item['unit_id'])
                    check = validate_packet(packet)
                    need(not (check.get('can_execute') is False and not check.get('validation_only')), check.get('stop_reason', 'Missing execution authorization'))
                except (ValueError, OSError, KeyError) as exc:
                    self.db.execute("UPDATE units SET status='STALE',reason=? WHERE unit_id=?", (str(exc), item['unit_id']))
                    self.event('source_invalidated', {'unit_id': item['unit_id'], 'reason': str(exc)})
                    continue
                worker = self.db.execute('SELECT task_id FROM worker WHERE id=1').fetchone()
                value = {'dispatch_id': str(uuid.uuid4()), 'pipeline_id': self.plan['pipeline_id'], 'action': 'send' if worker else 'create', 'status': 'RESERVED', 'target_thread_id': worker['task_id'] if worker else None, 'packet_path': row['path'], 'packet_sha256': row['sha256'], 'unit_id': item['unit_id'], 'revision': item['revision'], 'execution_mode': self.plan['execution_mode'], 'database_path': str(self.path), 'downstream_skill': KINDS[self.plan['pipeline_kind']], 'work_directory': packet['work_directory']}
                self.db.execute('INSERT INTO dispatches VALUES(?,?,?,?,?)', (value['dispatch_id'], item['unit_id'], item['revision'], stable(value), 'RESERVED'))
                self.db.execute("UPDATE units SET status='DISPATCH_RESERVED',reason=NULL WHERE unit_id=?", (item['unit_id'],))
                self.event('dispatch_reserved', value)
                return value
            return {'status': 'NO_READY_UNIT', 'total_units': len(self.plan['units'])}

    def dispatch(self, key):
        row = self.db.execute('SELECT * FROM dispatches WHERE dispatch_id=?', (key,)).fetchone()
        need(row, 'Unknown dispatch_id')
        value = json.loads(row['body'])
        value['status'] = row['status']
        return value

    def dispatch_sent(self, task, key):
        self.controller(task)
        with self.tx():
            value = self.dispatch(key)
            need(value['status'] == 'RESERVED', 'Do not repeat create/send after submission may have started')
            packet, _ = self.packet(value['unit_id'])
            need(packet['revision'] == value['revision'], 'Dispatch was superseded before submission')
            validate_packet(packet)
            self.db.execute("UPDATE dispatches SET status='SUBMITTING' WHERE dispatch_id=?", (key,))
            self.event('dispatch_submitting', {'dispatch_id': key})
            return {**value, 'status': 'SUBMITTING', 'instruction': 'Make exactly this one prepared app call; on uncertainty reconcile, never repeat.'}

    def dispatch_unknown(self, task, key, reason):
        self.controller(task)
        need(text_id(reason), 'Actual uncertainty reason required')
        with self.tx():
            value = self.dispatch(key)
            need(value['status'] in ('SUBMITTING', 'UNKNOWN', 'SETUP_PENDING'), 'No submitted dispatch to reconcile')
            self.db.execute("UPDATE dispatches SET status='UNKNOWN' WHERE dispatch_id=?", (key,))
            self.event('dispatch_unknown', {'dispatch_id': key, 'reason': reason})
            return {'status': 'UNKNOWN', 'dispatch_id': key, 'next': 'Inspect actual task setup; do not retry creation.'}

    def bind_dispatch(self, task, key, response):
        self.controller(task)
        result = unwrap_response(response)
        with self.tx():
            value = self.dispatch(key)
            need(value['status'] in ('SUBMITTING', 'UNKNOWN', 'SETUP_PENDING', 'BOUND'), 'Mark dispatch-sent before invoking the app')
            thread = result.get('threadId')
            if not thread and self.plan['execution_mode'] == 'validation' and result.get('validation_transport') == 'collaboration':
                thread = result.get('agent_task_id')
                value['validation_transport'] = 'collaboration'
            if value['status'] == 'BOUND':
                need(not thread or thread == value['target_thread_id'], 'A confirmed destination cannot be changed by a late response')
                return value
            if not thread:
                need(text_id(result.get('clientThreadId')), 'No usable task/setup identity in response')
                value['client_thread_id'] = result['clientThreadId']
                value['status'] = 'SETUP_PENDING'
                self.db.execute('UPDATE dispatches SET status=?,body=? WHERE dispatch_id=?', ('SETUP_PENDING', stable(value), key))
                self.event('setup_pending', value)
                return value
            need(text_id(thread), 'Actual threadId required')
            worker = self.db.execute('SELECT task_id FROM worker WHERE id=1').fetchone()
            need(not worker or worker['task_id'] == thread, 'Reuse the existing downstream task; do not substitute another')
            need(not value['target_thread_id'] or value['target_thread_id'] == thread, 'App response does not match destination')
            self.db.execute('INSERT OR IGNORE INTO worker VALUES(1,?)', (thread,))
            value.update(target_thread_id=thread, status='BOUND')
            self.db.execute("UPDATE dispatches SET status='BOUND',body=? WHERE dispatch_id=?", (stable(value), key))
            self.event('dispatch_bound', value)
            return value

    def cancel_dispatch(self, task, key, evidence):
        self.controller(task)
        with self.tx():
            value = self.dispatch(key)
            need(value['status'] not in ('CLAIMED', 'DONE'), 'Claimed work must return or recover, never cancel its ownership')
            if value['status'] == 'BOUND':
                need(evidence.get('dispatch_id') == key and evidence.get('target_task_id') == value['target_thread_id'] and evidence.get('no_active_turn') is True and evidence.get('confirmed_not_claimed') is True and evidence.get('external_operations_settled') is True and text_id(evidence.get('observation')), 'Observe the delivered task stopped before claiming, with no outstanding operations')
                need(not self.db.execute('SELECT 1 FROM lease').fetchone(), 'A worker already claimed this pipeline')
                packet, _ = self.packet(value['unit_id'], value['revision'])
                self.operations_settled(packet)
            elif value['status'] != 'RESERVED':
                need(evidence.get('dispatch_id') == key and evidence.get('confirmed_not_created_or_delivered') is True and text_id(evidence.get('observation')), 'Reconcile the actual app outcome before releasing a submitted dispatch')
            self.db.execute("UPDATE dispatches SET status='CANCELLED' WHERE dispatch_id=?", (key,))
            self.db.execute("UPDATE units SET status='READY' WHERE unit_id=? AND status='DISPATCH_RESERVED'", (value['unit_id'],))
            self.event('dispatch_cancelled', {'dispatch_id': key, 'evidence': evidence})
            return {'status': 'CANCELLED'}

    def claim(self, task, key):
        with self.tx():
            value = self.dispatch(key)
            need(value['status'] == 'BOUND' and value['target_thread_id'] == task, 'Only the bound real downstream task can claim')
            need(not self.db.execute('SELECT 1 FROM lease').fetchone(), 'One downstream unit at a time')
            packet, row = self.packet(value['unit_id'])
            need(packet['revision'] == value['revision'], 'Stale dispatch version')
            validate_packet(packet)
            lease = {'task_id': task, 'dispatch_id': key, 'unit_id': value['unit_id'], 'revision': value['revision'], 'token': str(uuid.uuid4()), 'claimed_at': time.time(), 'heartbeat_at': time.time()}
            self.db.execute('INSERT INTO lease VALUES(1,?)', (stable(lease),))
            self.db.execute("UPDATE dispatches SET status='CLAIMED' WHERE dispatch_id=?", (key,))
            self.db.execute("UPDATE units SET status='RUNNING' WHERE unit_id=?", (value['unit_id'],))
            Path(packet['work_directory']).mkdir(parents=True, exist_ok=True)
            self.event('claimed', lease)
            return {**lease, 'packet_path': row['path'], 'packet_sha256': row['sha256'], 'work_directory': packet['work_directory']}

    def claim_next(self, task):
        """The already-authorized stage worker drains ready units without a new app call."""
        with self.tx():
            worker = self.db.execute('SELECT task_id FROM worker WHERE id=1').fetchone()
            need(worker and worker['task_id'] == task, 'Only this pipeline\'s existing worker may continue')
            active = self.db.execute('SELECT 1 FROM dispatches WHERE status IN (?,?,?,?,?,?)', ACTIVE_DISPATCH).fetchone()
            if active or self.db.execute('SELECT 1 FROM lease').fetchone():
                return {'status': 'DISPATCH_OR_WORK_PENDING'}
            for item in self.db.execute("SELECT * FROM units WHERE status='READY' ORDER BY rowid").fetchall():
                try:
                    packet, row = self.packet(item['unit_id'])
                    check = validate_packet(packet)
                    need(not (check.get('can_execute') is False and not check.get('validation_only')), 'Original execution authorization missing')
                except (ValueError, OSError, KeyError) as exc:
                    self.db.execute("UPDATE units SET status='STALE',reason=? WHERE unit_id=?", (str(exc), item['unit_id']))
                    self.event('source_invalidated', {'unit_id': item['unit_id'], 'reason': str(exc)})
                    continue
                key = str(uuid.uuid4())
                value = {'dispatch_id': key, 'pipeline_id': self.plan['pipeline_id'], 'action': 'continue', 'status': 'CLAIMED', 'target_thread_id': task, 'unit_id': item['unit_id'], 'revision': item['revision'], 'packet_path': row['path'], 'packet_sha256': row['sha256'], 'execution_mode': self.plan['execution_mode'], 'database_path': str(self.path), 'work_directory': packet['work_directory']}
                lease = {'task_id': task, 'dispatch_id': key, 'unit_id': item['unit_id'], 'revision': item['revision'], 'token': str(uuid.uuid4()), 'claimed_at': time.time(), 'heartbeat_at': time.time()}
                self.db.execute('INSERT INTO dispatches VALUES(?,?,?,?,?)', (key, item['unit_id'], item['revision'], stable(value), 'CLAIMED'))
                self.db.execute('INSERT INTO lease VALUES(1,?)', (stable(lease),))
                self.db.execute("UPDATE units SET status='RUNNING' WHERE unit_id=?", (item['unit_id'],))
                Path(packet['work_directory']).mkdir(parents=True, exist_ok=True)
                self.event('local_continuation', {**value, 'task_id': task})
                return {**lease, 'status': 'CLAIMED', 'packet_path': row['path'], 'packet_sha256': row['sha256'], 'work_directory': packet['work_directory']}
            return {'status': 'WAITING_UPSTREAM', 'next': 'End this worker turn; the active controller will send a new published packet when ready.'}

    def auth(self, context):
        lease = read_json_row(self.db.execute('SELECT body FROM lease WHERE id=1').fetchone())
        need(lease and all(lease.get(k) == context.get(k) for k in ('task_id', 'token', 'dispatch_id', 'revision')), 'Stale or wrong worker lease')
        return lease

    def guard(self, context):
        lease = self.auth(context)
        packet, _ = self.packet(lease['unit_id'])
        need(packet['revision'] == lease['revision'], 'Upstream published a new version; stop and quarantine this result')
        check = validate_packet(packet)
        return {'status': 'CURRENT', 'unit_id': lease['unit_id'], 'revision': lease['revision'], 'execution_mode': packet['execution_mode'], 'release_check': check}

    def heartbeat(self, context):
        with self.tx():
            lease = self.auth(context)
            lease['heartbeat_at'] = time.time()
            self.db.execute('UPDATE lease SET body=? WHERE id=1', (stable(lease),))
            return {'status': 'ALIVE', 'heartbeat_at': lease['heartbeat_at']}

    def operations_settled(self, packet):
        _, jobs = consistent_read(packet, lambda: workflow(packet))
        unresolved = [(key, sid) for key in packet['authority']['downstream_jobs'] for sid, a in jobs[key]['attempts'].items() if a['result'] in ('pending', 'unknown')]
        need(not unresolved, 'Resolve actual generation/tool outcomes in the original journal first: ' + str(unresolved))

    def result(self, context, result):
        with self.tx():
            lease = self.auth(context)
            packet, _ = self.packet(lease['unit_id'], lease['revision'])
            self.operations_settled(packet)
            need(result.get('status') in ('PASS', 'FAIL', 'WAITING_MANUAL', 'VALIDATION_COMPLETE', 'STALE'), 'Explicit result status required')
            need(result.get('unit_id') == lease['unit_id'] and result.get('revision') == lease['revision'], 'Result scope mismatch')
            files_current(result.get('files', []), packet['work_directory'])
            newest, _ = self.packet(lease['unit_id'])
            stale = newest['revision'] != lease['revision']
            if not stale:
                try:
                    validate_packet(packet)
                except (ValueError, OSError, KeyError):
                    stale = True
            status = 'STALE' if stale else result['status']
            if status == 'STALE':
                need(text_id(result.get('reason') or result.get('payload', {}).get('reason')), 'Record why stale work is quarantined')
            else:
                if status == 'VALIDATION_COMPLETE':
                    need(packet['execution_mode'] == 'validation', 'Validation must never complete a production unit')
                if status == 'PASS':
                    need(packet['execution_mode'] == 'production', 'Synthetic validation does not create production PASS')
                adapter = importlib.import_module('ui_adapter' if packet['pipeline_kind'] == 'ui_portrait' else 'scene_adapter')
                consistent_read(packet, lambda: adapter.validate_result(packet, result, Path(packet['packet_base'])))
                if status == 'PASS':
                    accepted_downstream(packet)
            result_path = self.root / 'results' / (lease['dispatch_id'] + '.json')
            write_once(result_path, {**result, 'effective_status': status, 'worker_task_id': lease['task_id']})
            dispatch_data = self.dispatch(lease['dispatch_id'])
            dispatch_data.update(result_path=str(result_path), result_sha256=file_hash(result_path), result_status=status)
            self.db.execute('DELETE FROM lease WHERE id=1')
            self.db.execute("UPDATE dispatches SET status='DONE',body=? WHERE dispatch_id=?", (stable(dispatch_data), lease['dispatch_id']))
            if newest['revision'] == lease['revision']:
                self.db.execute('UPDATE units SET status=?,reason=? WHERE unit_id=?', (status, result.get('reason'), lease['unit_id']))
            self.event('result', {'dispatch_id': lease['dispatch_id'], 'unit_id': lease['unit_id'], 'revision': lease['revision'], 'status': status, 'result_path': str(result_path)})
            return {'status': status, 'result_path': str(result_path), 'worker_available': True}

    def resume(self, task, unit_id, evidence):
        self.controller(task)
        need(evidence.get('unit_id') == unit_id and text_id(evidence.get('reason')), 'Current manual return/rework evidence required')
        with self.tx():
            row = self.db.execute('SELECT * FROM units WHERE unit_id=?', (unit_id,)).fetchone()
            need(row and row['status'] in ('WAITING_MANUAL', 'FAIL'), 'Only a waiting/failed branch can resume')
            packet, _ = self.packet(unit_id)
            check = validate_packet(packet)
            need(not (check.get('can_execute') is False and not check.get('validation_only')), 'Original execution authorization still missing')
            self.operations_settled(packet)
            self.db.execute("UPDATE units SET status='READY',reason=NULL WHERE unit_id=?", (unit_id,))
            self.event('resumed', {'unit_id': unit_id, 'evidence': evidence})
            return {'status': 'READY', 'note': 'Original journal and all cumulative attempts retained.'}

    def recover_worker(self, task, evidence):
        self.controller(task)
        with self.tx():
            lease = read_json_row(self.db.execute('SELECT body FROM lease WHERE id=1').fetchone())
            need(lease and evidence.get('worker_task_id') == lease['task_id'], 'Recovery evidence must identify the current worker')
            need(evidence.get('no_active_turn') is True and evidence.get('external_operations_settled') is True and text_id(evidence.get('observation')), 'Inspect actual task and tool outcomes; elapsed time is not recovery evidence')
            packet, _ = self.packet(lease['unit_id'], lease['revision'])
            self.operations_settled(packet)
            self.db.execute('DELETE FROM lease WHERE id=1')
            self.db.execute("UPDATE dispatches SET status='RECOVERED' WHERE dispatch_id=?", (lease['dispatch_id'],))
            self.db.execute("UPDATE units SET status='WAITING_MANUAL',reason='WORKER_RECOVERY_REVIEW_REQUIRED' WHERE unit_id=? AND revision=?", (lease['unit_id'], lease['revision']))
            self.event('worker_recovered', {'lease': {k:v for k,v in lease.items() if k != 'token'}, 'evidence': evidence})
            return {'status': 'WAITING_MANUAL', 'note': 'Old lease fenced; inspect saved outputs before resume. No attempt was replayed or reset.'}

    def status(self):
        units = [dict(r) for r in self.db.execute('SELECT * FROM units ORDER BY rowid')]
        # Recheck accepted units instead of treating a historical PASS as permanent.
        # This is observational: it never writes a new approval or resets the job.
        for unit in units:
            if unit['status'] not in ('PASS', 'VALIDATION_COMPLETE'):
                continue
            try:
                packet, _ = self.packet(unit['unit_id'])
                validate_packet(packet)
                row = self.db.execute("SELECT dispatch_id,body FROM dispatches WHERE unit_id=? AND revision=? AND status='DONE' ORDER BY rowid DESC LIMIT 1", (unit['unit_id'], unit['revision'])).fetchone()
                need(row, 'Completion record missing')
                result_binding = json.loads(row['body'])
                result_path = self.root / 'results' / (row['dispatch_id'] + '.json')
                need(file_hash(result_path) == result_binding.get('result_sha256'), 'Frozen result receipt changed')
                result = read(result_path)
                need(result.get('effective_status') == result.get('status') == unit['status'] == result_binding.get('result_status'), 'Result no longer matches its completed outcome')
                files_current(result['files'], packet['work_directory'])
                adapter = importlib.import_module('ui_adapter' if packet['pipeline_kind'] == 'ui_portrait' else 'scene_adapter')
                consistent_read(packet, lambda: adapter.validate_result(packet, result, Path(packet['packet_base'])))
                if unit['status'] == 'PASS':
                    accepted_downstream(packet)
            except PipelineBusy as exc:
                unit.update(stored_status=unit['status'], status='BUSY', reason=str(exc))
            except (ValueError, OSError, KeyError, TypeError) as exc:
                unit.update(stored_status=unit['status'], status='STALE', reason=str(exc))
        lease = read_json_row(self.db.execute('SELECT body FROM lease WHERE id=1').fetchone())
        if lease:
            lease = {k:v for k,v in lease.items() if k != 'token'}
            lease['suspected_stale'] = time.time() - lease['heartbeat_at'] > 180
        mode = self.plan['execution_mode']
        done = sum(u['status'] == ('PASS' if mode == 'production' else 'VALIDATION_COMPLETE') for u in units)
        return {'pipeline_id': self.plan['pipeline_id'], 'execution_mode': mode, 'units': units, 'total_units': len(units), 'completed_units': done, 'whole_pipeline_complete': done == len(units), 'worker': lease, 'dispatches': [dict(r) for r in self.db.execute('SELECT dispatch_id,unit_id,revision,status FROM dispatches')], 'meaning': 'Stage handoff state; original artistic gates and actual manual approvals remain authoritative.'}

def read_json_row(row):
    return json.loads(row['body']) if row else None

def unwrap_response(response):
    if response.get('isError') is True:
        raise ValueError('Application call failed; preserve uncertainty and inspect actual state')
    if isinstance(response.get('structuredContent'), dict):
        return response['structuredContent']
    if isinstance(response.get('content'), list):
        for item in response['content']:
            if item.get('type') == 'text':
                try:
                    value = json.loads(item['text'])
                    if isinstance(value, dict):
                        return value
                except (ValueError, KeyError):
                    pass
    return response

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True)
    parser.add_argument('action', choices=['init', 'publish', 'status', 'reserve-dispatch', 'dispatch-sent', 'dispatch-unknown', 'bind-dispatch', 'cancel-dispatch', 'claim', 'claim-next', 'guard', 'heartbeat', 'result', 'resume', 'recover-worker'])
    for option in ('plan', 'packet', 'task', 'dispatch', 'response', 'reason', 'result', 'unit', 'evidence'):
        parser.add_argument('--' + option)
    args = parser.parse_args()
    if args.action == 'init':
        output = Pipeline.initialize(args.db, read(args.plan))
    else:
        pipe = Pipeline(args.db)
        try:
            lease_path = pipe.root / 'leases' / (hashlib.sha256((args.task or '').encode()).hexdigest() + '.json')
            if args.action in ('guard', 'heartbeat', 'result'):
                context = read(lease_path)
                need(context['task_id'] == args.task, 'Wrong local worker context')
            if args.action == 'publish':
                output = pipe.publish(read(args.packet), args.task, Path(args.packet).resolve().parent)
            elif args.action == 'status':
                output = pipe.status()
            elif args.action == 'reserve-dispatch':
                output = pipe.reserve_dispatch(args.task)
            elif args.action == 'dispatch-sent':
                output = pipe.dispatch_sent(args.task, args.dispatch)
            elif args.action == 'dispatch-unknown':
                output = pipe.dispatch_unknown(args.task, args.dispatch, args.reason)
            elif args.action == 'bind-dispatch':
                output = pipe.bind_dispatch(args.task, args.dispatch, read(args.response))
            elif args.action == 'cancel-dispatch':
                output = pipe.cancel_dispatch(args.task, args.dispatch, read(args.evidence) if args.evidence else {})
            elif args.action in ('claim', 'claim-next'):
                output = pipe.claim(args.task, args.dispatch) if args.action == 'claim' else pipe.claim_next(args.task)
                if output.get('token'):
                    lease_path.parent.mkdir(parents=True, exist_ok=True)
                    lease_path.write_text(stable(output), encoding='utf-8')
                    output = {k:v for k,v in output.items() if k != 'token'}
                    output['local_context'] = str(lease_path)
            elif args.action == 'guard':
                output = pipe.guard(context)
            elif args.action == 'heartbeat':
                output = pipe.heartbeat(context)
            elif args.action == 'result':
                output = pipe.result(context, read(args.result))
            elif args.action == 'resume':
                output = pipe.resume(args.task, args.unit, read(args.evidence))
            elif args.action == 'recover-worker':
                output = pipe.recover_worker(args.task, read(args.evidence))
        finally:
            pipe.close()
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    try:
        main()
    except PipelineBusy as error:
        print(json.dumps({'status': 'BUSY', 'retryable': True, 'reason': str(error)}, ensure_ascii=False))
        sys.exit(3)
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as error:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error)}, ensure_ascii=False))
        sys.exit(2)
