"""One-time migration of the approved L2 draft into the editor's shared tables.

No Unity writes. Refuses collisions and never replaces existing configuration rows.
After migration the shared tables, not the retired experiment manifest, own edits.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TABLES = HERE / 'data/table'
REPORT = HERE / 'data/_table_drafts/Unit6/integration_report.json'
SOURCE = ROOT / '剧情设计/试验单元/U1_五Loop试验版/L2_完整对白.md'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def parse():
    out = {}; block = None; node = None
    for line in SOURCE.read_text(encoding='utf-8').splitlines():
        if line.startswith('## dialogue: '):
            key = line.split(': ', 1)[1]; block = out.setdefault(key, []); node = None
        elif block is not None:
            actor = re.fullmatch(r'\*\*(.+?)\*\*(?:\s*\[(.*?)\])?', line.strip())
            if actor:
                node = dict(speaker=actor[1], action=actor[2] or '', text='', grants=[]); block.append(node)
            elif line.startswith('>'):
                node['text'] += ('\n' if node['text'] else '') + line[1:].strip()
            elif line.startswith('@get '):
                node['grants'].append(line[5:].strip())
    assert len(out) == 43 and sum(map(len, out.values())) == 239
    return out

def build():
    source = read(HERE / 'experiments/u1-five-loop/manifest.json')
    blocks = parse()
    names = {'zack':('601','扎克·布伦南','Zack Brennan'), 'emma':('602','艾玛·奥马利',"Emma O'Malley"),
             'rosa':('603','罗莎','Rosa'), 'webb':('604','韦伯','Webb'), 'tommy':('605','汤米·康纳利','Tommy Connelly'),
             'vivian':('606','薇薇安','Vivian'), 'james':('607','詹姆斯·奥沙利文',"James O'Sullivan"),
             'rita':('608','丽塔','Rita'), 'waitress':('609','服务员','Waitress'), 'drummer':('610','老鼓手','Drummer')}
    ids = dict(gun_check='6208', private_ledger='6201', public_ledger='6202', demand_letter='6203',
               photo_raw='6204', photo_amounts='6701', vip_photo='6205', pay_stub='6206',
               rosa_claim='6032001', signature_statement='6052001', accounts_claim='6052002',
               tommy_night_statement='6052003', james_pay_statement='6072001', james_night_statement='6072002')
    nrows = {k:dict(id=v[0],Name=[v[1],v[2]],role='4' if k in ('zack','emma') else '2',Chapter='EPI06',
                    ArtRequirement='',showInRelationshipNetwork='0' if k=='zack' else '1',showInTimeline='0' if k=='zack' else '1') for k,v in names.items()}
    byspeaker = {v[1]:k for k,v in names.items()}
    bg = dict(street='SC9022_bg_StreetCorner',lobby='SC010_bg_BarLobby',tommy='SC003_bg_TommyOffice',
              kitchen='SC011_bg_JimmyKitchen',hall='SC009_bg_BarCabaret',booth='SC9006_bg_SmallBox',webb='SC008_bg_WebbOffice')
    sceneids = {k:str(6200+i) for i,k in enumerate(bg)}
    owners = {t['id']:k for k,n in source['npcs'].items() for t in n['topics']}
    def context(key):
        if key=='opening': return 'street'
        if key.startswith(('rita','waitress','lobby')): return 'lobby'
        if key.startswith(('tommy','expose')) or key=='ending' or key in ('inspect_public','inspect_letter'): return 'tommy'
        if key.startswith('james') or key=='inspect_wage': return 'kitchen'
        if key.startswith('drummer'): return 'hall'
        if key.startswith(('emma','booth','camera','photo')): return 'booth'
        return 'webb'
    groups = {}; talks=[]
    for group,(key,nodes) in enumerate(blocks.items(),1):
        owner = owners.get(key, next((n for n in names if key.startswith(n+'_')), 'zack'))
        vs = 'loop2_tommy' if key.startswith('expose_') and not key.endswith('wrong') else key
        rows=[]
        for seq,node in enumerate(nodes,1):
            speaker = byspeaker[node['speaker']]
            tid = f'{names[owner][0]}{group:03d}{seq:03d}'
            row=dict(id=tid,step=str(seq),isRight='true' if speaker=='zack' else 'false',waitTime='0',
                Speaker=copy.deepcopy(nrows[speaker]),Location=[{'street':'酒吧外的街角','lobby':'酒吧大堂','tommy':'Tommy 办公室','kitchen':'厨房','hall':'歌舞厅','booth':'私人小包厢','webb':'Webb 办公室'}[context(key)],''],Words=[node['text'],''],
                cnAction=node['action'],next='',script='',Parameters=[],videoEpisode='EPI06',videoLoop='loop2',videoScene=vs,videoId=tid)
            if node['grants']:
                assert len(node['grants'])==1
                grant=ids[node['grants'][0]]
                row.update(script='3',Parameters=[dict(ParameterInt=grant,ParameterStr=('TIM' if len(grant)==7 else 'EV')+grant)])
            if rows: rows[-1]['next']=tid
            rows.append(row)
        groups[key]=rows; talks.extend(rows)
    first=lambda k:groups[k][0]['id']
    carry=[]
    for seq,key in enumerate(source['initialItems'],1):
        row=copy.deepcopy(groups['opening'][0]); tid=f'601000{seq:03d}'
        row.update(id=tid,videoId=tid,Words=['',''],cnAction='',script='3',Parameters=[dict(ParameterInt=ids[key],ParameterStr=('TIM' if len(ids[key])==7 else 'EV')+ids[key])])
        carry.append(row)
    carry[0]['next']=carry[1]['id']; carry[1]['next']=first('opening')
    groups['opening'][:0]=carry; talks.extend(carry)
    # One shared menu per NPC; first visit and repeat both reach it.
    menus={}
    for k,n in source['npcs'].items():
        menu=copy.deepcopy(groups[n['intro']][-1]); menu.update(id=names[k][0]+'800001',Words=['',''],cnAction='',script='1',next='',Parameters=[])
        menu['videoId']=menu['id']; menu['videoScene']=n['intro']; menu['step']='800'
        end=copy.deepcopy(menu); end.update(id=names[k][0]+'800002',videoId=names[k][0]+'800002',step='801',script='2',Parameters=[])
        for t in n['topics']:
            param=dict(ParameterStr=t['title'],ParameterInt=first(t['id']))
            menu['Parameters'].append(param)
            groups[t['id']][-1]['next']=menu['id']
        menu['Parameters'].append(dict(ParameterStr='结束交谈',ParameterInt=end['id']))
        groups[n['intro']][-1]['next']=menu['id']; groups[n['repeat']][-1]['next']=menu['id']
        talks.extend([menu,end]); menus[k]=menu['id']
    # Opening, accusation and ending use the same native next/script convention as Unit1.
    groups['opening'][-1]['next']=first('lobby_arrival')
    chain=['expose_open','expose_r1_lie','expose_r1_success','expose_r2_lie','expose_r2_success','ending']
    for a,b in zip(chain,chain[1:]): groups[a][-1]['next']=first(b)
    exposes=[]
    for i,answer in enumerate([['private_ledger','public_ledger'],['demand_letter']],1):
        groups[f'expose_r{i}_lie'][-1].update(script='7',Parameters=[dict(ParameterStr=','.join('EV'+ids[x] for x in answer),ParameterInt='0'),dict(ParameterInt=str(1 if i==1 else 3))])
        exposes.append(dict(id=str(6200+i),testimony=ids['accounts_claim'] if i==1 else '0',item=[ids[x] for x in answer],talkId=first(f'expose_r{i}_success')))
    groups['expose_r2_success'][-1]['script']='11'
    groups['ending'][-1].update(script='15',next='')
    exp_step=0
    for k in chain[:-1]:
        for row in groups[k]: exp_step+=1; row['step']=str(exp_step)
    items=[]; testimony=[]
    for k,card in source['items'].items():
        if len(ids[k])==7:
            testimony.append(dict(id=ids[k],testimonyType='1',testimony=[card['text'],''],truth=['',''],triggerType='None',triggerParam=ids[k][:3],shortDesc=[card['name'],''],shortTruth=['',''],HiddenStuff='false'))
        else:
            row=dict(id=ids[k],Name=[card['name'],''],itemType='3',canAnalyzed='true' if k=='photo_raw' else 'false',canCombined='false',
                Describe=[card['text'],''],ShortDescribe=[card['text'],''],location=[card['source'],''],Chapter='EPI06',Loop=2,
                folderPath='',desSpritePath='',mapSpritePath='',iconPath='',Position=['0','0','-3'],HiddenStuff='false',ArtRequirement='',obtainMethod='dialog' if k=='gun_check' else 'manual')
            if k=='photo_raw': row['analysedEvidence']=ids['photo_amounts']
            if k=='photo_amounts': row.update(beforeAnalysedEvidence=ids['photo_raw'],obtainMethod='auto')
            items.append(row)
    def ref(key):
        t=groups[key][0]; return {x:t[x] for x in ('id','videoEpisode','videoLoop','videoScene')}
    scenes=[]; npcLoops=[]
    for k,sid in sceneids.items():
        src=next((s for s in source['scenes'] if s['id']==k),source['openingScene'])
        row=dict(sceneId=sid,location=dict(id=sid,Name=[src['name'],''],sceneType='1',backgroundImage=('Art/Scene/Backgrounds/EPI01/'+bg[k]).replace('/',chr(92))),
                 loop=2,openInLoops=[2],isOpen=k!='street',ItemIDs=[],NPCInfos=[],note='五 Loop 试验版 L2；复用现有美术。',previewTalks=[])
        for npc in src.get('npcs',[]):
            n=source['npcs'][npc]; info=dict(id='62'+names[npc][0],NPC=copy.deepcopy(nrows[npc]),TalkInfo=ref(n['intro']),LoopTalkInfo=ref(n['repeat']),IsinRight='false',ResPath='',ClickResPath='',PosX='0',Posy='0',PosZ='-2')
            row['NPCInfos'].append(info); npcLoops.append(copy.deepcopy(info))
        if k=='street': row['previewTalks'].append(dict(title='街角开场',**ref('opening')))
        if src.get('entry'): row['previewTalks'].append(dict(title='首次进入',**ref(src['entry'])))
        for o in src.get('objects',[]):
            row['ItemIDs'].append(ids[o['item']]); row['previewTalks'].append(dict(title=o['name'],**ref(o['dialogue'])))
        if k=='booth': row['previewTalks'].append(dict(title='照片分析对白',**ref('photo_analyze')))
        if k=='tommy':
            for i in (1,2): row['previewTalks'].append(dict(title=f'指证第{i}轮错误回应',**ref(f'expose_r{i}_wrong')))
        scenes.append(row)
    doubts=[dict(id='6201',isFragment=False,text='两本账的说法',condition=[dict(type='1',param=ids[x]) for x in ['private_ledger','public_ledger']]+[dict(type='4',param=ids['accounts_claim'])]),
            dict(id='6202',isFragment=False,text='经手的催款事务',condition=[dict(type='1',param=ids['demand_letter']),dict(type='4',param=ids['signature_statement'])])]
    chapter=dict(id='602',chapterTitle=['体面人的账本',''],chapterBrief=['五 Loop 试验版 L2：查清 Webb 的生意及 Tommy 经手的事务。',''],chapterGoal=['查清 Webb 的生意。',''],
        summaryTitle=['账上的名字',''],summaryContent=['Tommy 承认签发过以客人私生活为条件的催款函；是否寄达及实际收款仍未确认。',''],newDoubtTitle=['案发现场',''],newDoubtContent=['现场仍有问题没有回答。',''],
        initTalk=first('opening'),initScene=sceneids['lobby'],openingScene=sceneids['street'],explorationEntryScene=sceneids['lobby'],
        doubts=copy.deepcopy(doubts),clearDoubts=['6201','6202'],exposes=copy.deepcopy(exposes),exposeNpcId='605',exposeScene=sceneids['tommy'],
        topBg='Art/Scene/Backgrounds/EPI01/'+bg['tommy'],map2Scenes=[dict(mapId='601',sceneId=sceneids['lobby'])],
        postExposeSegments=[dict(order=1,type='talk',title='L2 收束',sceneId=sceneids['tommy'],entryTalkId=first('ending'),videoScene='ending',videoEpisode='EPI06',videoLoop='loop2')],previewStatus='experimental_table_preview')
    full_testimony=[]
    for t in testimony:
        grant=next(row for row in talks if row['script']=='3' and row['Parameters'][0]['ParameterInt']==t['id'])
        npc=next(n for n in nrows.values() if n['id']==t['id'][:3])
        full_testimony.append(dict(id=grant['id'],npc=copy.deepcopy(npc),chapter='602',words=t['testimony'],evidenceItem=[copy.deepcopy(t)]))
    rows=dict(ChapterConfig=[chapter],SceneConfig=scenes,ItemStaticData=items,NPCStaticData=list(nrows.values()),NPCLoopData=npcLoops,Talk=talks,Testimony=full_testimony,TestimonyItem=testimony,DoubtConfig=doubts,ExposeData=exposes,MapConfig=[dict(id='601',Name=['蓝月亮·试验版',''],icon='',position=['0','0','0'])])
    return rows,dict(unit='Unit6',episode='EPI06',loop='loop2',source=str(SOURCE.relative_to(ROOT)),items=ids,dialogues={k:first(k) for k in blocks},menus=menus,sourceNodes=239,topics=13)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--write',action='store_true'); args=parser.parse_args()
    rows,report=build(); planned={}; preserved={}
    if REPORT.exists():
        raise SystemExit('Already migrated. Edit shared tables directly; do not overwrite them from the retired manifest.')
    for table,additions in rows.items():
        path=TABLES/(table+'.json'); before=read(path); key='sceneId' if table=='SceneConfig' else 'id'
        old={str(r[key]) for r in before}; added=[str(r[key]) for r in additions]
        assert not old.intersection(added),(table,'ID collision'); assert len(set(added))==len(added)
        preserved[table]=hashlib.sha256(json.dumps(before,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        planned[path]=before+additions
    report['branchUnlockConfig'] = {'rules': [{'talkId':int(report['dialogues']['emma_camera']), 'npcId':602, 'matchMode':0, 'requiredItemIds':[6204,6701], 'requiredTestimonyIds':[]}]}
    assert not (TABLES/'TalkBranchUnlockConfig.json').exists(), 'Branch config exists; do not replace it'
    report.update(counts={k:len(v) for k,v in rows.items()},addedIds={k:[str(r.get('id',r.get('sceneId'))) for r in v] for k,v in rows.items()},preservedRowsSha256=preserved)
    print(json.dumps(report['counts']))
    if args.write:
        for path,data in planned.items(): write(path,data)
        write(TABLES/'TalkBranchUnlockConfig.json',report['branchUnlockConfig'])
        write(REPORT,report)

if __name__=='__main__': main()
