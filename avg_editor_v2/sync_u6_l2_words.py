"""Sync trial dialogue wording and English display names to local preview tables."""
from pathlib import Path
import argparse
import json
import re
import copy

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'剧情设计/试验单元/U1_五Loop试验版/L2_完整对白.md'
TABLE=HERE/'data/table/Talk.json'
REPORT=HERE/'data/_table_drafts/Unit6/integration_report.json'
NPC_TABLE=HERE/'data/table/NPCStaticData.json'
# User-approved display names for this trial only; IDs and other chapters stay intact.
NAMES={'601':'Zack','602':'Emma','603':'Rosa','604':'Webb','605':'Tommy',
       '606':'Vivian','607':'James','608':'Rita','609':'服务员','610':'老鼓手'}

def parse():
    blocks={}; current=None; node=None
    for line in SOURCE.read_text(encoding='utf-8').splitlines():
        if line.startswith('## dialogue: '):
            key=line.split(': ',1)[1]; assert key not in blocks
            current=blocks.setdefault(key,[])
        elif current is not None:
            actor=re.fullmatch(r'\*\*(.+?)\*\*',line.strip())
            if actor:
                node={'speaker':actor[1],'text':'','grants':[]};current.append(node)
            elif line.startswith('**'):
                raise ValueError('Action or invalid speaker markup: '+line)
            elif line.startswith('>'):
                assert node is not None
                node['text']+=('\n' if node['text'] else '')+line[1:].strip()
            elif line.startswith('@get '):node['grants'].append(line[5:].strip())
    assert len(blocks)==43 and sum(map(len,blocks.values()))==239
    return blocks

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    blocks=parse(); report=json.loads(REPORT.read_text(encoding='utf-8'))
    rows=json.loads(TABLE.read_text(encoding='utf-8'));before=copy.deepcopy(rows);byid={r['id']:r for r in rows}
    touched=set();words_changed=0;actions_removed=0
    for key,nodes in blocks.items():
        tid=report['dialogues'][key]
        # The native opening includes two silent prior-loop grants before the MD's first line.
        if key=='opening':
            while not (byid[tid].get('Words') or [''])[0]:tid=byid[tid]['next']
        for node in nodes:
            row=byid[tid]
            assert row['videoEpisode']=='EPI06' and row['videoLoop']=='loop2'
            assert NAMES[str(row['Speaker']['id'])]==node['speaker'],(key,tid,'speaker changed')
            assert tid not in touched and node['text']
            if node['grants']:
                assert row['script']=='3'
                assert [row['Parameters'][0]['ParameterInt']]==[report['items'][k] for k in node['grants']]
            else:assert row.get('script')!='3',(key,tid,'grant moved')
            words_changed+=row['Words'][0]!=node['text']; row['Words'][0]=node['text']
            actions_removed+=bool(row.get('cnAction') or row.get('enAction'))
            row['cnAction']=''
            if 'enAction' in row:row['enAction']=''
            touched.add(tid);tid=row.get('next')
    assert len(touched)==239
    names_changed=0
    trial_ids=set()
    for row in rows:
        if row.get('videoEpisode')=='EPI06' and row.get('videoLoop')=='loop2':
            trial_ids.add(row['id'])
            speaker=row.get('Speaker')
            if speaker:
                name=NAMES[str(speaker['id'])]
                names_changed+=speaker['Name'][0]!=name
                speaker['Name'][0]=name
    npc_rows=json.loads(NPC_TABLE.read_text(encoding='utf-8'))
    for npc in npc_rows:
        if str(npc['id']) in NAMES:
            assert npc['Chapter']=='EPI06'
            npc['Name'][0]=NAMES[str(npc['id'])]
    # No structural changes; other units are identical and control nodes only change display names.
    for old,new in zip(before,rows):
        if old['id'] not in trial_ids:assert old==new
        else:
            for field in set(old)|set(new):
                if field not in ('Words','cnAction','enAction','Speaker'):assert old.get(field)==new.get(field)
            expected_speaker=copy.deepcopy(old.get('Speaker'))
            if expected_speaker:expected_speaker['Name'][0]=NAMES[str(expected_speaker['id'])]
            assert expected_speaker==new.get('Speaker')
            assert old['Words'][1:]==new['Words'][1:]
            if old['id'] not in touched:assert old['Words']==new['Words']
    result={'nodes':len(touched),'wordsChanged':words_changed,'speakerNamesChanged':names_changed,'actionFieldsCleared':actions_removed,'structureUnchanged':True,'otherUnitsUnchanged':True}
    print(json.dumps(result))
    if args.write:
        TABLE.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        NPC_TABLE.write_text(json.dumps(npc_rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (REPORT.parent/'language_polish_report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
