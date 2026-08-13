from __future__ import annotations

from pathlib import Path

import yaml


UNIT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = UNIT_DIR / "state"
TARGET_DIR = UNIT_DIR / "state_candidate_v3"


def testimony(
    testimony_id: int,
    name: str,
    speaker: int,
    first_scene: int,
    text: str,
    source_anchor: str,
    *,
    kind: str = "collectible",
    collectible: bool = True,
    acquisition_talk: str | None = None,
    source_markers: tuple[tuple[str, str], ...] = (),
    note: str | None = None,
    persistence: dict | None = None,
) -> dict:
    entry = {
        "id": testimony_id,
        "name": name,
        "speaker": speaker,
        "first_scene": first_scene,
        "kind": kind,
        "collectible": collectible,
        "text": text,
        "source_anchor": source_anchor,
        "source_markers": [
            {"anchor": anchor, "text": marker_text}
            for anchor, marker_text in source_markers
        ],
    }
    if acquisition_talk:
        entry["acquisition_talk"] = acquisition_talk
    if note:
        entry["note"] = note
    if persistence:
        entry["persistence"] = persistence
    return entry


OPENINGS = {
    1: {
        "type": "cutscene_sequence",
        "runtime_root": {
            "table": "ChapterConfig",
            "init_scene": 4001,
            "init_talk": "L1_opening_courthouse_blockade",
        },
        "sequence": [
            {
                "event_id": "courthouse_blockade",
                "talk": "L1_opening_courthouse_blockade",
                "scene_id": 4001,
                "source_anchor": "active outline / Loop1 / 开篇剧情 / 法院东翼",
                "cast": ["Zack", "Emma", "Pierce", "Mickey"],
                "required_beats": [
                    "法院强制要求Mary案改判过失杀人；Zack与Emma为查明原因抵达法院东翼。",
                    "Pierce以现场封锁为由阻止进入；Mickey说明自己也来查Mary为何被改判。",
                    "Mickey确认Harrison前夜死在办公室，目前只能确定死于枪伤。",
                    "Mickey转述档案室消息：Harrison近期一直在翻圣心医院旧案。",
                    "警方仍在外围、尚未进入办公室；Mickey 主动拖住 Pierce。",
                    "Zack 与 Emma 趁窗口进入 Harrison 外间办公室。",
                ],
                "runtime_exit": {
                    "action": "change_scene",
                    "target_scene_id": 4002,
                    "continuation": "release_to_exploration",
                },
            }
        ],
        "player_control_restored_after": "courthouse_blockade",
    },
    2: {
        "type": "cutscene_sequence",
        "runtime_root": {
            "table": "ChapterConfig",
            "init_scene": 4011,
            "init_talk": "L2_opening_thirteen_day_hearing",
        },
        "sequence": [
            {
                "event_id": "thirteen_day_hearing",
                "talk": "L2_opening_thirteen_day_hearing",
                "scene_id": 4011,
                "source_anchor": "active outline / Loop2 / 开篇剧情 / Zack事务所",
                "cast": ["Zack", "Emma", "Rosa", "Mickey"],
                "required_beats": [
                    "Rosa 带着 Isabel 的照片、药盒和医院条件来到事务所。",
                    "Rosa 怀疑自己是否误用药物；现有材料尚不能直接证明她无责。",
                    "Mickey 用死亡对照表申请拖延听证并成为 Rosa 的辩护律师。",
                    "Mickey 邀请 Zack 担任二辩，Emma 与 Zack 立即调查医院和实验室。",
                ],
                "runtime_exit": {"action": "release_to_exploration"},
            }
        ],
        "player_control_restored_after": "thirteen_day_hearing",
    },
    3: {
        "type": "cutscene_sequence",
        "runtime_root": {
            "table": "ChapterConfig",
            "init_scene": 4021,
            "init_talk": "L3_opening_broken_call",
        },
        "sequence": [
            {
                "event_id": "broken_call",
                "talk": "L3_opening_broken_call",
                "scene_id": 4021,
                "source_anchor": "active outline / Loop3 / 开篇剧情 / 事务所深夜",
                "cast": ["Zack", "Emma", "Morrison", "人工接线员"],
                "required_beats": [
                    "人工接线员转入 Morrison 宅邸坚持接 Brennan 的来电。",
                    "电话里先有咳嗽和沉默，Morrison 只说出 Brennan 后断线。",
                    "Zack 认出声音，和 Emma 立即前往宅邸；不提前断言线路被人为切断。",
                ],
                "runtime_exit": {
                    "action": "change_scene",
                    "target_scene_id": 4022,
                    "continuation": "next_talk",
                    "next_talk": "L3_opening_mansion_arrival",
                },
            },
            {
                "event_id": "mansion_arrival",
                "talk": "L3_opening_mansion_arrival",
                "scene_id": 4022,
                "source_anchor": "active outline / Loop3 / 开篇剧情 / 宅邸门口",
                "cast": ["Zack", "Emma", "Mickey"],
                "required_beats": [
                    "23:30，Zack 与 Emma 在宅邸门口撞见 Mickey。",
                    "Mickey 强制声称自己也刚到，是 Morrison 把他叫来的。",
                    "该说法此时不能立刻证伪，但属于 Mickey 的掩护谎言。",
                ],
                "claims": [
                    {
                        "id": "mickey_just_arrived",
                        "speaker": "Mickey",
                        "truth_status": "false",
                        "player_can_disprove_now": False,
                        "withheld_fact": "Mickey在22:58已经进入宅邸，并于23:16枪杀Harold、伪造现场。",
                    }
                ],
                "runtime_exit": {"action": "release_to_exploration"},
            },
        ],
        "player_control_restored_after": "mansion_arrival",
    },
    4: {
        "type": "cutscene_sequence",
        "runtime_root": {
            "table": "ChapterConfig",
            "init_scene": 4031,
            "init_talk": "L4_opening_office_confrontation",
        },
        "sequence": [
            {
                "event_id": "office_confrontation",
                "talk": "L4_opening_office_confrontation",
                "scene_id": 4031,
                "source_anchor": "active outline / Loop4 / 开篇剧情 / Zack事务所",
                "cast": ["Zack", "Emma", "Mickey", "Doris"],
                "required_beats": [
                    "Zack 追问 Mickey 为什么谎报枪位；Mickey 只让他自己想。",
                    "Zack 追问 Morrison 的来电和会面，Mickey 沉默。",
                    "Patrick 冲突升级；Mickey 坚称 Patrick 最后选择了自己。",
                    "Mickey 反击 Zack 曾隐瞒 Emma，离开后 Emma 正面对质 Zack。",
                    "Doris 到场交出 O'Hara 清退通知，众人立即转向现实危险。",
                ],
                "runtime_exit": {
                    "action": "change_scene",
                    "target_scene_id": 4032,
                    "continuation": "release_to_exploration",
                },
            }
        ],
        "player_control_restored_after": "office_confrontation",
    },
    5: {
        "type": "cutscene_sequence",
        "runtime_root": {
            "table": "ChapterConfig",
            "init_scene": 4042,
            "init_talk": "L5_opening_42nd_floor_arrival",
        },
        "sequence": [
            {
                "event_id": "forty_second_floor_arrival",
                "talk": "L5_opening_42nd_floor_arrival",
                "scene_id": 4042,
                "source_anchor": "active outline / Loop5 / 开篇剧情 / 四十二层",
                "cast": ["Zack"],
                "required_beats": [
                    "Zack 根据 Donnelly & Associates 旧信封地址独自来到四十二层。",
                    "Mickey 没有邀请 Zack，办公室暂时无人。",
                    "Zack 进入后直接开始自由探索，不设置破门、潜入、撬锁或其他前置交互。",
                ],
                "runtime_exit": {"action": "release_to_exploration"},
            }
        ],
        "player_control_restored_after": "forty_second_floor_arrival",
    },
}


COVERAGE = {
    1: [
        ("L1_B01", "Loop1 / 开篇剧情", "merged", "opening.sequence.courthouse_blockade"),
        ("L1_B02", "Loop1 / 调查 / Harrison办公室与档案室", "exact", "scenes.4002_4003"),
        ("L1_B03", "Loop1 / 指证 Watts", "exact", "expose.watts"),
        ("L1_B04", "Loop1 / 指证后 / 保险柜材料", "exact", "expose.post_expose.safe"),
        ("L1_B05", "Loop1 / 指证后 / Morrison犹豫", "exact", "expose.post_expose.morrison"),
        ("L1_B06", "Loop1 / 指证后 / Rosa次日听证", "exact", "expose.post_expose.rosa_hook"),
    ],
    2: [
        ("L2_B01", "Loop2 / 开篇剧情", "merged", "opening.sequence.thirteen_day_hearing"),
        ("L2_B02", "Loop2 / 自由调查", "exact", "scenes.4011_4015"),
        ("L2_B03", "Loop2 / 指证 Whitfield", "exact", "expose.whitfield"),
        ("L2_B04", "Loop2 / 指证后 / Rosa拒签与回执", "exact", "expose.post_expose.rosa_resolution"),
        ("L2_B05", "Loop2 / 指证后 / Morrison走廊接触", "exact", "expose.post_expose.morrison_hook"),
    ],
    3: [
        ("L3_B01", "Loop3 / 开篇剧情 / 事务所来电", "exact", "opening.sequence.broken_call"),
        ("L3_B02", "Loop3 / 开篇剧情 / 宅邸门口", "exact", "opening.sequence.mansion_arrival"),
        ("L3_B03", "Loop3 / 宅邸调查", "exact", "scenes.4022"),
        ("L3_B04", "Loop3 / 强制撤离与爆炸", "exact", "scenes.4022.evacuation"),
        ("L3_B05", "Loop3 / 爆炸后调查", "exact", "scenes.4023_4026"),
        ("L3_B06", "Loop3 / 指证 Doris", "exact", "expose.doris"),
        ("L3_B07", "Loop3 / 指证后 / 相反枪位证词与自杀结案", "exact", "expose.post_expose.official_close"),
    ],
    4: [
        ("L4_B01", "Loop4 / 开篇剧情", "merged", "opening.sequence.office_confrontation"),
        ("L4_B02", "Loop4 / O'Hara清退与暂停执行", "exact", "scenes.4032_4033"),
        ("L4_B03", "Loop4 / Sarah转移至Rosa家", "exact", "scenes.4033.sarah_relocation"),
        ("L4_B04", "Loop4 / Margaret调查与指证", "exact", "expose.margaret"),
        ("L4_B05", "Loop4 / 指证后 / Patrick真相与遗物匣", "exact", "expose.post_expose.patrick_truth"),
        ("L4_B06", "Loop4 / 结尾 / Zack独自前往四十二层", "exact", "expose.post_expose.l5_handoff"),
    ],
    5: [
        ("L5_B01", "Loop5 / 开篇剧情", "exact", "opening.sequence.forty_second_floor_arrival"),
        ("L5_B02", "Loop5 / 自由探索与三条身份链", "exact", "special_mechanics.identity_lock"),
        ("L5_B03", "Loop5 / Mickey返回与逻辑指证", "exact", "expose.mickey"),
        ("L5_B04", "Loop5 / 身份承认与价值对话", "exact", "expose.post_expose.value_dialogue"),
        ("L5_B05", "Loop5 / Miller条件与坠落", "exact", "expose.post_expose.fall"),
        ("L5_B06", "非Loop终幕 / 离开四十二层", "exact", "ending_sequence.ending_4043"),
        ("L5_B07", "非Loop终幕 / 安全地点拆档", "exact", "ending_sequence.ending_4044"),
        ("L5_B08", "非Loop终幕 / O'Hara家门外硬停", "exact", "ending_sequence.ending_4045"),
    ],
}

NPC_MARKERS = {
    1: [
        ("L1_NPC_WATTS", "Watts", 4002, "L1_scene4002_watts", "L1_scene4002_watts", "Loop1 / 自由探索 / Harrison外间办公室 / NPC Watts"),
        ("L1_NPC_MORRISON", "Morrison", 4002, "L1_scene4002_harold", "L1_scene4002_harold", "Loop1 / 自由探索 / Harrison外间办公室 / NPC Morrison"),
        ("L1_NPC_ARCHIVIST", "档案管理员", 4003, "L1_scene4003_archivist", "L1_scene4003_archivist", "Loop1 / 自由探索 / 法院档案室 / NPC 档案管理员"),
    ],
    2: [
        ("L2_NPC_ROSA", "Rosa", 4011, "L2_scene4011_rosa", "L2_scene4011_rosa", "Loop2 / 自由探索 / Zack侦探事务所 / NPC Rosa"),
        ("L2_NPC_FOSTER", "Foster", 4013, "L2_scene4013_foster", "L2_scene4013_foster", "Loop2 / 自由探索 / 法医实验室 / NPC Foster"),
        ("L2_NPC_WHITFIELD", "Whitfield", 4014, "L2_scene4014_whitfield", "L2_scene4014_whitfield", "Loop2 / 自由探索 / 法院预审走廊 / NPC Whitfield"),
        ("L2_NPC_MICKEY", "Mickey", 4015, "L2_scene4015_mickey", "L2_scene4015_mickey", "Loop2 / 自由探索 / 法院会客室 / NPC Mickey"),
    ],
    3: [
        ("L3_NPC_DORIS_PRE", "Doris", 4022, "L3_scene4022_doris", "L3_scene4022_doris", "Loop3 / 自由探索 / Morrison书房 / NPC Doris"),
        ("L3_NPC_MICKEY_POST", "Mickey", 4023, "L3_scene4023_mickey", "L3_scene4023_mickey", "Loop3 / 爆炸后回收区 / NPC Mickey"),
        ("L3_NPC_DORIS_POST", "Doris", 4023, "L3_scene4023_doris", "L3_scene4023_doris", "Loop3 / 爆炸后回收区 / NPC Doris"),
    ],
    4: [
        ("L4_NPC_OHARA", "O'Hara", 4032, "L4_scene4032_ohara", "L4_scene4032_ohara", "Loop4 / 自由探索 / O'Hara家门口 / NPC O'Hara"),
        ("L4_NPC_SARAH", "Sarah", 4033, "L4_scene4033_sarah", "L4_scene4033_sarah", "Loop4 / 自由探索 / O'Hara家 / NPC Sarah"),
        ("L4_NPC_MARGARET", "Margaret", 4034, "L4_scene4034_margaret", "L4_scene4034_margaret", "Loop4 / 自由探索 / Margaret家 / NPC Margaret"),
    ],
    5: [],
}

TESTIMONY_MARKERS = {
    1: [
        (
            "L1_T_WATTS_CLERK",
            4041004,
            "Loop1 / 自由探索 / Harrison外间办公室 / NPC Watts / ⚪",
            "Watts是法官Harrison的书记员",
            "exact",
        ),
    ],
    2: [
        (
            "L2_T_WHITFIELD_IDENTITY",
            4092004,
            "Loop2 / 自由探索 / 法院预审走廊 / Whitfield / ⚪",
            "Whitfield 是医院的慈善负责人",
            "exact",
        ),
    ],
    3: [
        (
            "L3_T_DORIS_RETURN",
            4063006,
            "Loop3 / 自由探索 / Morrison书房 / Doris / ⚪",
            "23:18 前一直在外，返家后才发现丈夫死亡；她没有看见访客离开。",
            "exact",
        ),
        (
            "L3_T_DORIS_IDENTITY",
            4063007,
            "Loop3 / 自由探索 / Morrison书房 / Doris / ⚪",
            "Morrison 的妻子。",
            "exact",
        ),
        (
            "L3_T_MICKEY_BOMB_REACTION",
            4033001,
            "Loop3 / 爆炸后回收区 / Mickey / ⚪",
            "怎么会有炸弹，难道说他们连我也要……",
            "exact",
        ),
        (
            "L3_T_DORIS_GAS_WORKERS",
            4063001,
            "Loop3 / 爆炸后回收区 / Doris / ⚪",
            "自己没有申报故障，但 18:12 有两名穿市政工作服的人来检查壁炉管线。",
            "exact",
        ),
        (
            "L3_T_MORRISON_LAST_CALL",
            4153001,
            "Loop3 / 夜班电话交换台 / ⚪",
            "Morrison最后通话记录",
            "exact",
        ),
        (
            "L3_T_MORRISON_LEFT_HAND",
            4063002,
            "Loop3 / 指证后剧情 / ⚪",
            "Morrison 惯用左手的生活证词",
            "exact",
        ),
    ],
    4: [
        (
            "L4_T_OHARA_REFUSAL",
            4114001,
            "Loop4 / 自由探索 / O'Hara家门口 / O'Hara / ⚪",
            "Margaret劝说O'Hara 接受报价，但Ohara没听，她说自己无论如何都不会卖房子",
            "exact",
        ),
        (
            "L4_T_OHARA_HELP_PATH",
            4114002,
            "Loop4 / 自由探索 / O'Hara家门口 / O'Hara / ⚪",
            "Margaret 明确要求 O'Hara 不找 Zack，并邀请Ohara和自己一起搬去北边教会的小公寓住",
            "exact",
        ),
        (
            "L4_T_PATRICK_NO_HANDOFF",
            4104005,
            "Loop4 / 自由探索 / Margaret家 / Margaret / ⚪",
            "Patrick送医后始终没有恢复可交流意识，于次日凌晨因内伤去世；不存在未被记录的临终交接窗口。",
            "exact",
        ),
        (
            "L4_T_PATRICK_UNKNOWN_RESCUE",
            4104001,
            "Loop4 / 指证后剧情 / Margaret / ⚪",
            "你父亲当时并不知道那个人是Mickey……他只是为了工人，觉得那是他的工友，就牺牲了自己的生命",
            "merged",
        ),
        (
            "L4_T_PATRICK_RETURN_SUMMARY",
            4104001,
            "Loop4 / 指证后剧情 / Margaret正式摘要 / ⚪",
            "Margaret 关于 Patrick 折返的证词",
            "merged",
        ),
    ],
    5: [],
}

TESTIMONY_TITLE_MARKERS = {
    "L3_T_MORRISON_LAST_CALL",
    "L3_T_MORRISON_LEFT_HAND",
    "L4_T_PATRICK_RETURN_SUMMARY",
}

TESTIMONY_DEFINITIONS = {
    1: [
        testimony(
            4041001,
            "Harrison最近只是工作繁忙的说法",
            404,
            4002,
            "Harrison最近只是工作繁忙，没有秘密重查旧案。",
            "active outline / Loop1 / 自由探索 / Harrison外间办公室 / Watts谎言",
            kind="collectible_lie_anchor",
            acquisition_talk="L1_scene4002_watts",
        ),
        testimony(
            4041002,
            "即使调阅旧案也是查别人问题的说法",
            404,
            4002,
            "即使Harrison调阅旧案，也是在查别人的问题。",
            "active outline / Loop1 / 指证 Watts / R2",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
        testimony(
            4041003,
            "Harrison不会公开材料的说法",
            404,
            4002,
            "Harrison不会真正违抗法院，更不会公开材料。",
            "active outline / Loop1 / 指证 Watts / R3",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
        testimony(
            4041004,
            "Watts的书记员身份",
            404,
            4002,
            "Watts是法官Harrison的书记员",
            "active outline / Loop1 / 自由探索 / Harrison外间办公室 / NPC Watts / ⚪",
            acquisition_talk="L1_scene4002_watts",
            source_markers=(
                (
                    "active outline / Loop1 / 自由探索 / Harrison外间办公室 / NPC Watts / ⚪",
                    "Watts是法官Harrison的书记员",
                ),
            ),
        ),
        testimony(
            4051001,
            "Harrison办公室应由警方接管的说法",
            405,
            4002,
            "Harrison的办公室属于死亡调查现场，钥匙与卷宗应由警方接管。",
            "active outline / Loop1 / 自由探索 / Harrison外间办公室 / Morrison",
            acquisition_talk="L1_scene4002_harold",
        ),
        testimony(
            4161001,
            "Harrison连续调阅旧档案的记录证词",
            416,
            4003,
            "Harrison连续两个月亲自调阅医院、地产与旧赔偿档案；索引只记录档号、日期和签收手续。",
            "active outline / Loop1 / 自由探索 / 法院档案室 / 档案管理员",
            acquisition_talk="L1_scene4003_archivist",
        ),
    ],
    2: [
        testimony(
            4082001,
            "Foster关于十三日实际用量的技术证词",
            408,
            4013,
            "按瓶体标定与剩余量核对，十三日实际消耗不存在规定剂量之外的一次额外注射缺口。",
            "active outline / Loop2 / 自由探索 / 法医实验室 / 容量核对",
            acquisition_talk="L2_scene4013_foster",
        ),
        testimony(
            4092001,
            "Rosa擅自加量的说法",
            409,
            4014,
            "Rosa在每日规定剂量之外擅自增加了药量。",
            "active outline / Loop2 / 法院预审走廊 / Whitfield谎言",
            kind="collectible_lie_anchor",
            acquisition_talk="L2_scene4014_whitfield",
        ),
        testimony(
            4092002,
            "Isabel只是单一药物事故的说法",
            409,
            4014,
            "即使没有加量，Isabel也只是单一药物事故。",
            "active outline / Loop2 / 指证 Whitfield / R2",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
        testimony(
            4092003,
            "问题批次未进入正式项目的说法",
            409,
            4014,
            "问题批次没有进入正式项目，可能来自护士私领或家庭转手。",
            "active outline / Loop2 / 指证 Whitfield / R3",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
        testimony(
            4092004,
            "Whitfield的医院慈善负责人身份",
            409,
            4014,
            "Whitfield 是医院的慈善负责人",
            "active outline / Loop2 / 自由探索 / 法院预审走廊 / Whitfield / ⚪",
            acquisition_talk="L2_scene4014_whitfield",
            source_markers=(
                (
                    "active outline / Loop2 / 自由探索 / 法院预审走廊 / Whitfield / ⚪",
                    "Whitfield 是医院的慈善负责人",
                ),
            ),
        ),
        testimony(
            4032002,
            "Mickey关于正式项目链与第十九页边界的证词",
            403,
            4015,
            "采购单、入库号与慈善发放清单构成正式项目链；副本缺失第十九页，使更高层批准暂时无法核验；现有材料足以先阻止Whitfield把责任推给Rosa。",
            "active outline / Loop2 / 自由探索 / 法院会客室 / Mickey",
            acquisition_talk="L2_scene4015_mickey",
        ),
    ],
    3: [
        testimony(
            4153001,
            "Morrison最后通话记录",
            415,
            4024,
            "22:36，Morrison致电Brennan事务所，无人接听后称会自行过去；22:43，他改接Donnelly & Associates，称自己准备去找Brennan，并要求对方若仍想体面收尾就现在过来；23:15再次接通Brennan事务所，只说出Zack的姓。线路记录不确认Donnelly端接听人。",
            "active outline / Loop3 / 夜班电话交换台 / ⚪",
            acquisition_talk="L3_scene4024_operator",
            source_markers=(
                (
                    "active outline / Loop3 / 夜班电话交换台 / ⚪",
                    "Morrison最后通话记录",
                ),
            ),
            note="R1主力；L5访客链复用，只确认线路去向与口信",
            persistence={
                "scope": "chapter",
                "reset_policy": "retain_across_loops",
                "required_by": ["identity_lock.chain_4503"],
            },
        ),
        testimony(
            4063001,
            "Doris关于18:12假市政工入宅的证词",
            406,
            4023,
            "自己没有申报故障，但 18:12 有两名穿市政工作服的人来检查壁炉管线。",
            "active outline / Loop3 / 爆炸后回收区 / Doris / ⚪",
            acquisition_talk="L3_scene4023_doris",
            source_markers=(
                (
                    "active outline / Loop3 / 爆炸后回收区 / Doris / ⚪",
                    "自己没有申报故障，但 18:12 有两名穿市政工作服的人来检查壁炉管线。",
                ),
            ),
        ),
        testimony(
            4063002,
            "Morrison惯用左手的生活证词",
            406,
            4023,
            "Doris 与 Morrison 都惯用左手，因此家中的家具与常用物件长期按左侧动线摆放。",
            "active outline / Loop3 / 指证后剧情 / ⚪",
            kind="post_expose",
            acquisition_talk="L3_post_expose_official_suicide",
            source_markers=(
                (
                    "active outline / Loop3 / 指证后剧情 / ⚪",
                    "Morrison 惯用左手的生活证词",
                ),
            ),
        ),
        testimony(
            4063003,
            "Harold当晚准备留家的说法",
            406,
            4022,
            "Harold当晚没有打算离开，准备一直在家里休息。",
            "active outline / Loop3 / Morrison书房 / Doris谎言",
            kind="collectible_lie_anchor",
            acquisition_talk="L3_scene4022_doris",
        ),
        testimony(
            4063004,
            "家里没有第二人的说法",
            406,
            4022,
            "家里没有来过除了Doris以外的第二个人。",
            "active outline / Loop3 / 指证 Doris / R2",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
        testimony(
            4063005,
            "Harold没有留下材料的说法",
            406,
            4022,
            "Harold没有留下任何准备交给Zack的材料。",
            "active outline / Loop3 / 指证 Doris / R3",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
        testimony(
            4063006,
            "Doris返家时间与所见边界",
            406,
            4022,
            "23:18 前一直在外，返家后才发现丈夫死亡；她没有看见访客离开。",
            "active outline / Loop3 / 自由探索 / Morrison书房 / Doris / ⚪",
            acquisition_talk="L3_scene4022_doris",
            source_markers=(
                (
                    "active outline / Loop3 / 自由探索 / Morrison书房 / Doris / ⚪",
                    "23:18 前一直在外，返家后才发现丈夫死亡；她没有看见访客离开。",
                ),
            ),
        ),
        testimony(
            4063007,
            "Doris的Morrison妻子身份",
            406,
            4022,
            "Morrison 的妻子。",
            "active outline / Loop3 / 自由探索 / Morrison书房 / Doris / ⚪",
            acquisition_talk="L3_scene4022_doris",
            source_markers=(
                (
                    "active outline / Loop3 / 自由探索 / Morrison书房 / Doris / ⚪",
                    "Morrison 的妻子。",
                ),
            ),
        ),
        testimony(
            4033001,
            "Mickey对爆炸的惊惧反应",
            403,
            4023,
            "怎么会有炸弹，难道说他们连我也要……",
            "active outline / Loop3 / 爆炸后回收区 / Mickey / ⚪",
            acquisition_talk="L3_scene4023_mickey",
            source_markers=(
                (
                    "active outline / Loop3 / 爆炸后回收区 / Mickey / ⚪",
                    "怎么会有炸弹，难道说他们连我也要……",
                ),
            ),
        ),
    ],
    4: [
        testimony(
            4114001,
            "O'Hara明确拒绝出售的证词",
            411,
            4032,
            "Margaret劝说O'Hara 接受报价，但Ohara没听，她说自己无论如何都不会卖房子",
            "active outline / Loop4 / 自由探索 / O'Hara家门口 / O'Hara / ⚪",
            acquisition_talk="L4_scene4032_ohara",
            source_markers=(
                (
                    "active outline / Loop4 / 自由探索 / O'Hara家门口 / O'Hara / ⚪",
                    "Margaret劝说O'Hara 接受报价，但Ohara没听，她说自己无论如何都不会卖房子",
                ),
            ),
        ),
        testimony(
            4114002,
            "O'Hara关于Margaret阻止求助的证词",
            411,
            4032,
            "Margaret 明确要求 O'Hara 不找 Zack，并邀请Ohara和自己一起搬去北边教会的小公寓住",
            "active outline / Loop4 / 自由探索 / O'Hara家门口 / O'Hara / ⚪",
            acquisition_talk="L4_scene4032_ohara",
            source_markers=(
                (
                    "active outline / Loop4 / 自由探索 / O'Hara家门口 / O'Hara / ⚪",
                    "Margaret 明确要求 O'Hara 不找 Zack，并邀请Ohara和自己一起搬去北边教会的小公寓住",
                ),
            ),
        ),
        testimony(
            4104001,
            "Margaret关于Patrick折返的正式摘要",
            410,
            4034,
            "你父亲当时并不知道那个人是Mickey……他只是为了工人，觉得那是他的工友，就牺牲了自己的生命",
            "active outline / Loop4 / 指证后剧情 / Margaret / ⚪",
            kind="post_expose",
            acquisition_talk="L4_post_expose_patrick_truth",
            source_markers=(
                (
                    "active outline / Loop4 / 指证后剧情 / Margaret / ⚪",
                    "你父亲当时并不知道那个人是Mickey……他只是为了工人，觉得那是他的工友，就牺牲了自己的生命",
                ),
                (
                    "active outline / Loop4 / 指证后剧情 / Margaret正式摘要 / ⚪",
                    "Margaret 关于 Patrick 折返的证词",
                ),
            ),
        ),
        testimony(
            4104005,
            "Patrick送医后未恢复意识的证词",
            410,
            4034,
            "Patrick送医后始终没有恢复可交流意识，于次日凌晨因内伤去世；不存在未被记录的临终交接窗口。",
            "active outline / Loop4 / 自由探索 / Margaret家 / Margaret / ⚪",
            acquisition_talk="L4_scene4034_margaret",
            source_markers=(
                (
                    "active outline / Loop4 / 自由探索 / Margaret家 / Margaret / ⚪",
                    "Patrick送医后始终没有恢复可交流意识，于次日凌晨因内伤去世；不存在未被记录的临终交接窗口。",
                ),
            ),
        ),
        testimony(
            4104002,
            "O'Hara已准备接受报价的说法",
            410,
            4034,
            "O'Hara已经准备接受报价，Margaret只是在帮她安排搬家。",
            "active outline / Loop4 / Margaret家 / R1",
            kind="collectible_lie_anchor",
            acquisition_talk="L4_scene4034_margaret",
        ),
        testimony(
            4104003,
            "没有阻止O'Hara求助的说法",
            410,
            4034,
            "Margaret没有让O'Hara瞒着Zack，是O'Hara自己不想麻烦他。",
            "active outline / Loop4 / 指证 Margaret / R2",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
        testimony(
            4104004,
            "Patrick因知道里面是Mickey才折返的说法",
            410,
            4034,
            "Patrick当年是为了救Mickey才折返，并因此去世。",
            "active outline / Loop4 / 指证 Margaret / R3",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
    ],
    5: [
        testimony(
            4035001,
            "Donnelly只代客户处理账务的说法",
            403,
            4042,
            "Donnelly只替客户处理账务；1919-A不是Mickey的账户，他也不能决定资金用途。",
            "active outline / Loop5 / 指证 Mickey / R1",
            kind="collectible_lie_anchor",
            acquisition_talk="L5_scene4042_mickey",
        ),
        testimony(
            4035002,
            "爆炸前从未进入Morrison家的说法",
            403,
            4042,
            "Mickey知道Morrison现场的事，是Pierce事后告诉他的；爆炸前他从未进入Morrison家。",
            "active outline / Loop5 / 指证 Mickey / R2",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
        testimony(
            4035003,
            "Whale只是匿名客户的说法",
            403,
            4042,
            "Whale是Mickey的匿名客户；Mickey只是替他保存记录、把他的决定变成合法文件。",
            "active outline / Loop5 / 指证 Mickey / R3",
            kind="expose_dynamic_lie",
            collectible=False,
        ),
    ],
}


CONTINUITY = {
    1: [
        ("u4_l1_opening", "Loop1 / 开篇剧情", "法院东翼封锁，Zack与Emma尚未取得调查控制", [], ["Pierce封锁", "Mickey拖住Pierce", "进入办公室"], "玩家进入4002自由调查", "u4_l1_investigation", ["opening.sequence.courthouse_blockade"]),
        ("u4_l1_investigation", "Loop1 / 调查", "Harrison死亡且材料可能被接管", ["u4_l1_opening"], ["查明夜间出入、资金与辞职材料"], "Watts三轮指证条件成立", "u4_l1_expose", ["scenes"]),
        ("u4_l1_expose", "Loop1 / 指证 Watts", "玩家掌握三组矛盾", ["u4_l1_investigation"], ["击穿Watts三层退守"], "Watts交出钥匙", "u4_l1_post_expose", ["expose"]),
        ("u4_l1_post_expose", "Loop1 / 指证后", "保险柜可开启", ["u4_l1_expose"], ["取得4117-4121", "Morrison犹豫", "建立Rosa紧急听证"], "次日Rosa来到事务所", "u4_l2_opening", ["expose.post_expose"]),
    ],
    2: [
        ("u4_l2_opening", "Loop2 / 开篇剧情", "Rosa面临当日下午庭审", ["u4_l1_post_expose"], ["Mickey争取窗口并组建辩护分工"], "同场释放自由调查", "u4_l2_investigation", ["opening.sequence.thirteen_day_hearing"]),
        ("u4_l2_investigation", "Loop2 / 调查", "需证明无加量、非单例、正式入院", ["u4_l2_opening"], ["先向Rosa自由询问红线用药并取得4211、4212", "再取得医院、实验室与法院材料"], "Whitfield三轮指证条件成立", "u4_l2_expose", ["scenes"]),
        ("u4_l2_expose", "Loop2 / 指证 Whitfield", "记者在场且Rosa拒签前", ["u4_l2_investigation"], ["击穿家属误用版本"], "Rosa取得暂停追究回执", "u4_l2_post_expose", ["expose"]),
        ("u4_l2_post_expose", "Loop2 / 指证后", "Rosa案进入重审", ["u4_l2_expose"], ["确认真实胜利", "Morrison私下留下接触口"], "23:15 Morrison来电", "u4_l3_opening", ["expose.post_expose"]),
    ],
    3: [
        ("u4_l3_opening", "Loop3 / 开篇剧情", "Morrison试图接通Brennan事务所", ["u4_l2_post_expose"], ["异常来电", "赶赴宅邸", "Mickey刚到口径"], "宅邸调查开始", "u4_l3_investigation", ["opening.sequence.broken_call", "opening.sequence.mansion_arrival"]),
        ("u4_l3_investigation", "Loop3 / 宅邸调查与爆炸", "Mickey口径暂不可证伪", ["u4_l3_opening"], ["检查尸体与现场", "完成撤离", "爆炸后分别询问Mickey与Doris", "取得18:12假市政工证词并保存记录"], "Doris三轮指证条件成立", "u4_l3_expose", ["scenes"]),
        ("u4_l3_expose", "Loop3 / 指证 Doris", "材料显示Morrison准备开口", ["u4_l3_investigation"], ["击穿Doris三层退守"], "取得惯用左手生活证词", "u4_l3_post_expose", ["expose"]),
        ("u4_l3_post_expose", "Loop3 / 指证后", "Zack持有右手私人观察", ["u4_l3_expose"], ["Mickey给出左手正式陈述", "Pierce按自杀结案"], "清退材料指向O'Hara", "u4_l4_opening", ["expose.post_expose"]),
    ],
    4: [
        ("u4_l4_opening", "Loop4 / 开篇剧情", "自杀结案与Mickey枪位矛盾未解", ["u4_l3_post_expose"], ["追问Mickey", "Emma对质Zack", "Doris送达通知"], "立即前往O'Hara家", "u4_l4_ohara", ["opening.sequence.office_confrontation"]),
        ("u4_l4_ohara", "Loop4 / O'Hara清退", "O'Hara与Sarah面临执行", ["u4_l4_opening"], ["取得暂停执行", "通过Sarah自由Talk建立Rosa安全屋关系", "O'Hara留下", "Sarah转移到Rosa家"], "Zack前往Margaret家", "u4_l4_expose", ["scenes"]),
        ("u4_l4_expose", "Loop4 / 指证 Margaret", "玩家掌握Patrick相关矛盾", ["u4_l4_ohara"], ["击穿保护性隐瞒"], "Margaret交出遗物匣", "u4_l4_post_expose", ["expose"]),
        ("u4_l4_post_expose", "Loop4 / 指证后", "Patrick未指定继承人的事实成立", ["u4_l4_expose"], ["建立密码方向", "Emma拒绝同行", "Zack主动赴四十二层"], "Zack抵达Mickey空办公室", "u4_l5_opening", ["expose.post_expose"]),
    ],
    5: [
        ("u4_l5_opening", "Loop5 / 开篇剧情", "Zack独自抵达且办公室无人", ["u4_l4_post_expose"], ["直接进入4042自由探索"], "三条身份链开放", "u4_l5_identity_lock", ["opening.sequence.forty_second_floor_arrival"]),
        ("u4_l5_identity_lock", "Loop5 / 身份锁", "Mickey尚未返回", ["u4_l5_opening"], ["完成4501、4502、4503"], "Mickey返回并锁定探索", "u4_l5_expose", ["special_mechanics.identity_lock"]),
        ("u4_l5_expose", "Loop5 / 指证 Mickey", "三条身份链全部完成", ["u4_l5_identity_lock"], ["玩家先证明Mickey等于Whale"], "Mickey承认身份", "u4_l5_post_expose", ["expose"]),
        ("u4_l5_post_expose", "Loop5 / 身份承认至坠落", "身份事实已经由玩家证明", ["u4_l5_expose"], ["价值对话", "拒绝Miller条件", "主动松手", "Emma救回Zack"], "从楼梯撤离", "u4_l5_ending_4043", ["expose.post_expose"]),
        ("u4_l5_ending_4043", "非Loop终幕 / 4043", "Mickey坠落且档案仍封存", ["u4_l5_post_expose"], ["Watts接应", "车上只交代身份与坠落"], "抵达安全地点", "u4_l5_ending_4044", ["ending_sequence.ending_4043"]),
        ("u4_l5_ending_4044", "非Loop终幕 / 4044", "三人共同查看外卷", ["u4_l5_ending_4043"], ["Zack独拆内封", "共享4517", "扣下4518与4519", "公开O'Hara清退危险"], "前往O'Hara街区", "u4_l5_ending_4045", ["ending_sequence.ending_4044"]),
        ("u4_l5_ending_4045", "非Loop终幕 / 4045", "街区已出现中毒症状", ["u4_l5_ending_4044"], ["Zack交出4519", "Watts启动公共卫生联络", "Zack与Emma跑到门外"], "U4在门外硬停", "enter_ohara_house", ["ending_sequence.ending_4045"]),
    ],
}


def load_state(loop_number: int) -> dict:
    path = SOURCE_DIR / f"loop{loop_number}_state.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_coverage(loop_number: int) -> list[dict]:
    coverage = [
        {
            "beat_id": beat_id,
            "source_anchor": f"active outline / {anchor}",
            "mapping": mapping,
            "primary_landing": landing,
        }
        for beat_id, anchor, mapping, landing in COVERAGE[loop_number]
    ]
    coverage.extend(
        {
            "beat_id": marker_id,
            "marker_id": marker_id,
            "source_anchor": f"active outline / {anchor}",
            "mapping": "exact",
            "primary_landing": f"scenes.{scene_id}.npcs.{npc_key}",
            "dialogue_required": True,
            "npc_name": npc_name,
            "scene_id": scene_id,
            "npc_key": npc_key,
            "talk": talk,
        }
        for marker_id, npc_name, scene_id, npc_key, talk, anchor in NPC_MARKERS[
            loop_number
        ]
    )
    for marker_id, testimony_id, anchor, source_text, mapping in TESTIMONY_MARKERS[
        loop_number
    ]:
        coverage.append(
            {
                "beat_id": marker_id,
                "marker_id": marker_id,
                "source_anchor": f"active outline / {anchor}",
                "source_text": source_text,
                "mapping": mapping,
                "primary_landing": f"testimony_ids.{testimony_id}",
                "testimony_required": True,
                "testimony_id": testimony_id,
                "verbatim_required": marker_id not in TESTIMONY_TITLE_MARKERS,
            }
        )
    return coverage


def build_continuity(loop_number: int) -> list[dict]:
    fields = (
        "id",
        "source_anchor",
        "entry_state",
        "consumes",
        "required_beats",
        "exit_state",
        "hands_off_to",
        "covers",
    )
    return [dict(zip(fields, row, strict=True)) for row in CONTINUITY[loop_number]]


def scene(state: dict, scene_id: int) -> dict:
    return next(entry for entry in state["scenes"] if entry["id"] == scene_id)


def inline_testimony(definition: dict) -> dict:
    entry = {
        "id": definition["id"],
        "content": definition["text"],
        "kind": definition["kind"],
        "speaker": definition["speaker"],
        "source_anchor": definition["source_anchor"],
    }
    if definition.get("acquisition_talk"):
        entry["acquisition_talk"] = definition["acquisition_talk"]
    if definition.get("note"):
        entry["note"] = definition["note"]
    if definition.get("persistence"):
        entry["persistence"] = definition["persistence"]
    return entry


def inline_testimony_definitions(state: dict, definitions: list[dict]) -> None:
    definition_by_id = {entry["id"]: entry for entry in definitions}
    attached_ids: set[int] = set()
    for scene_entry in state.get("scenes", []):
        for npc in (scene_entry.get("npcs") or {}).values():
            testimony_ids = npc.get("testimony_ids")
            if not isinstance(testimony_ids, list):
                continue
            inline_entries: list[dict] = []
            dynamic_ids: list[int] = []
            for testimony_ref in testimony_ids:
                if isinstance(testimony_ref, dict):
                    inline_entries.append(testimony_ref)
                    attached_ids.add(testimony_ref["id"])
                    continue
                definition = definition_by_id.get(testimony_ref)
                if definition is None:
                    raise ValueError(
                        f"testimony {testimony_ref} has no inline definition"
                    )
                if definition.get("kind") == "expose_dynamic_lie":
                    dynamic_ids.append(testimony_ref)
                    continue
                inline_entries.append(inline_testimony(definition))
                attached_ids.add(testimony_ref)
            npc["testimony_ids"] = inline_entries
            if dynamic_ids:
                npc["expose_lie_ids"] = dynamic_ids

    post_expose = state.get("expose", {}).get("post_expose")
    for definition in definitions:
        testimony_id = definition["id"]
        if definition.get("kind") == "expose_dynamic_lie":
            continue
        if testimony_id in attached_ids:
            continue
        if definition.get("kind") != "post_expose" or not isinstance(post_expose, dict):
            raise ValueError(
                f"collectible testimony {testimony_id} has no acquisition location"
            )
        post_expose.setdefault("testimony_ids", []).append(
            inline_testimony(definition)
        )
        attached_ids.add(testimony_id)

    state.pop("testimony_registry", None)


def revise_loop1(state: dict) -> None:
    watts = scene(state, 4002)["npcs"]["L1_scene4002_watts"]
    watts["active_topics"].append(
        "Watts是法官Harrison的书记员；Harrison不让他碰最后几晚的材料"
    )
    watts["testimony_ids"].append(4041004)
    next(entry for entry in state["evidence_registry"] if entry["id"] == 4701)["type"] = "item"
    post = state["expose"]["post_expose"]
    post["event_id"] = "harrison_safe_and_rosa_hook"
    post["talk"] = "L1_post_expose_harrison_safe"
    post["required_beats"] = [
        "Watts交出钥匙并开启保险柜，4117至4121只取得一次。",
        "Morrison得知Harrison因材料而死后沉默；Zack问是否告知Pierce，他只说需要考虑。",
        "Watts说明Harrison另一件急务是Rosa案，次日必须在庭审前行动。",
    ]
    post["player_control_restored_after"] = "harrison_safe_and_rosa_hook"


def revise_loop2(state: dict) -> None:
    for evidence_id in (4702, 4703):
        next(
            entry for entry in state["evidence_registry"] if entry["id"] == evidence_id
        )["type"] = "item"
    office = scene(state, 4011)
    office["npcs"] = {
        "L2_scene4011_rosa": {
            "name": "Rosa Martinez",
            "talk": "L2_scene4011_rosa",
            "is_liar": False,
            "motive": "把自己实际如何按护士红线用药说清，并交出仍可核验的药盒、注射器和回收药瓶",
            "mindset": "自责仍在，但只回答自己亲手做过的步骤；不替医院判断药剂来源",
            "active_topics": [
                "自己不识剂量单位，只会把药液抽到护士画出的红线",
                "十三格药盒每天按日开启并留下指纹确认",
                "自己从未拿到第二只药瓶",
            ],
            "withheld_topics": [
                "无；Rosa不知道问题批次为何进入医院，也不知道Whitfield或Miller的上层责任"
            ],
            "player_inquiry": [
                "每次如何确定抽取剂量",
                "十三日药盒如何开启",
                "是否存在第二只药瓶或额外注射",
            ],
            "testimony_ids": [],
            "grants_evidence": [4211, 4212],
        }
    }
    for evidence in office["evidence"]:
        if evidence["id"] in (4211, 4212):
            evidence["acquisition"] = {
                "kind": "dialogue",
                "talk": "L2_scene4011_rosa",
            }
    for evidence in state["evidence_registry"]:
        if evidence["id"] in (4211, 4212):
            evidence["acquisition"] = {
                "kind": "dialogue",
                "talk": "L2_scene4011_rosa",
            }

    court_scene = scene(state, 4014)
    whitfield = court_scene["npcs"]["L2_scene4014_whitfield"]
    whitfield["active_topics"].append("Whitfield是医院的慈善负责人")
    whitfield["testimony_ids"].append(4092004)
    court_scene.get("npcs", {}).pop("L2_scene4014_harold_followup", None)

    post = state["expose"]["post_expose"]
    post["description"] = (
        "Rosa 在 Zack 与 Mickey 的支持下拒绝签署家属误用说明。Whitfield 要求记者停止广播和录音，"
        "Emma 明确告知现场记者并不受他控制，事实已无法被走廊口径收回。书记员交付暂停追究 Rosa、"
        "重审 Isabel 死因的回执。Mickey 对 Rosa 的关心和这场胜利都必须是真的。散庭后 Morrison "
        "在走廊拐角告诉 Zack，自己没有把 Harrison 材料告知 Pierce，并留下以后私下接触的口子；"
        "这不等于完整坦白。"
    )
    post["event_id"] = "rosa_result_and_morrison_hook"
    post["talk"] = "L2_post_expose_court_result"
    post["required_beats"] = [
        "Whitfield要求停止广播和录音，Emma说明已经来不及。",
        "Rosa拒签并取得暂停追究、重审死因的回执。",
        "Mickey真实地松一口气并托住滑落的照片。",
        "Morrison在走廊留下下一次私下接触的口子。",
    ]
    post["player_control_restored_after"] = "rosa_result_and_morrison_hook"


def revise_loop3(state: dict) -> None:
    if not any(entry["id"] == 4021 for entry in state["scenes"]):
        state["scenes"].insert(
            0,
            {
                "id": 4021,
                "name": "Zack 侦探事务所 / 深夜来电",
                "type": "cutscene",
                "design_tags": ["opening", "transition"],
                "description": "仅承载接线员转入Morrison来电、Brennan一词与立即出发，不提供自由调查。",
                "npcs": {},
            },
        )

    mansion = scene(state, 4022)
    mansion.get("npcs", {}).pop("L3_scene4022_mickey", None)
    doris_pre = mansion.get("npcs", {}).get("L3_scene4022_doris")
    if doris_pre:
        doris_pre["active_topics"] = [
            topic
            for topic in doris_pre.get("active_topics", [])
            if "18:12" not in topic and "市政工作服" not in topic
        ]
        doris_pre["testimony_ids"] = [
            testimony_id
            for testimony_id in doris_pre.get("testimony_ids", [])
            if testimony_id != 4063001
        ]
        doris_pre["active_topics"].append("Doris是Morrison的妻子")
        doris_pre["testimony_ids"].extend([4063006, 4063007])

    mansion["event_triggers"] = [
        {
            "id": "mansion_evacuation_and_explosion",
            "condition": "required_scene_investigation_complete",
            "talk": "L3_event_mansion_evacuation",
            "forced": True,
            "locks_player_control": True,
            "required_beats": [
                "Emma依据已检查的接线、阀门与窗缝异常组织撤离。",
                "Zack、Emma、Mickey与Doris撤到安全边界后爆炸发生。",
            ],
            "runtime_exit": {
                "action": "change_scene",
                "target_scene_id": 4023,
                "continuation": "next_talk",
                "next_talk": "L3_event_pierce_takeover",
            },
        }
    ]

    aftermath = scene(state, 4023)
    aftermath.get("npcs", {}).pop("L3_scene4023_pierce", None)
    aftermath["npcs"] = {
        "L3_scene4023_mickey": {
            "name": "Mickey Donnelly",
            "talk": "L3_scene4023_mickey",
            "is_liar": False,
            "motive": "确认爆炸不是自己预期的行动，同时照看Doris并判断上层是否也把自己视为可接受损耗",
            "mindset": "第一次出现真实裂缝；对爆炸无知与恐惧是真的，但仍不公开Whale身份和枪杀责任",
            "active_topics": [
                "自己不知道宅邸里有爆炸装置",
                "爆炸同样可能杀死在场的自己",
                "先留在门口照看Doris，让Zack与Emma继续调查",
            ],
            "withheld_topics": [
                "自己22:58已经进入宅邸",
                "自己23:16枪杀Harold并伪造自杀现场",
                "自己是Whale",
            ],
            "player_inquiry": [
                "Mickey是否预料到爆炸",
                "Mickey为什么认为上层可能绕过自己行动",
            ],
            "testimony_ids": [4033001],
        },
        "L3_scene4023_doris": {
            "name": "Doris Morrison",
            "talk": "L3_scene4023_doris",
            "is_liar": False,
            "motive": "在宅邸被毁后补充当天确实发生过的市政检修，让眼前危险先得到调查",
            "mindset": "惊魂未定；这一条陈述真实，但不代表她放弃了让Harold尽快按自杀结案的立场",
            "active_topics": [
                "自己没有申报煤气故障",
                "18:12有两名穿市政工作服的人进入宅邸检查壁炉管线",
            ],
            "withheld_topics": [
                "她仍不愿公开Harold留下材料和访客痕迹",
                "她不知道两名人员身份、装置命令源或Mickey责任",
            ],
            "player_inquiry": [
                "是否申报过故障",
                "两名市政人员抵达时间和检查位置",
            ],
            "testimony_ids": [4063001],
        },
    }
    aftermath["event_triggers"] = [
        {
            "id": "pierce_scene_takeover",
            "condition": "first_enter_after_mansion_explosion",
            "talk": "L3_event_pierce_takeover",
            "forced": True,
            "locks_player_control": True,
            "required_beats": [
                "Pierce到场接管现场、证人和记录。",
                "Zack保留私人调查记录，但右手枪位不再能由官方复核。",
            ],
            "runtime_exit": {"action": "release_to_exploration"},
        }
    ]

    post = state["expose"]["post_expose"]
    post.pop("new_testimony_gained", None)
    post["event_id"] = "official_suicide_close"
    post["talk"] = "L3_post_expose_official_suicide"
    post["required_beats"] = [
        "Doris确认Harold惯用左手。",
        "Mickey正式陈述初见尸体时枪在左手，与Zack的右手记录冲突。",
        "Pierce以原始现场已毁、证词冲突为由拒绝启动他杀调查并按自杀结案。",
    ]
    post["player_control_restored_after"] = "official_suicide_close"


def revise_loop4(state: dict) -> None:
    margaret = scene(state, 4034)["npcs"]["L4_scene4034_margaret"]
    margaret["testimony_ids"].append(4104005)

    ohara_home = scene(state, 4033)
    ohara_home["npcs"] = {
        "L4_scene4033_sarah": {
            "name": "Sarah O'Hara",
            "talk": "L4_scene4033_sarah",
            "is_liar": False,
            "motive": "确认自己熟悉Rosa家，也理解母亲希望她暂时离开危险现场的安排",
            "mindset": "害怕但不哭诉；只提供孩子真正知道的邻里关系和留宿经验",
            "active_topics": [
                "Rosa与O'Hara同属南区家长互助会",
                "自己以前在Rosa家留宿过",
                "去Rosa家不是被送往陌生地点",
            ],
            "withheld_topics": [
                "无；Sarah不知道清退系统、井区风险或Margaret与Patrick的旧事"
            ],
            "player_inquiry": [
                "Sarah是否认识Rosa",
                "她是否曾在Rosa家留宿",
            ],
            "testimony_ids": [],
        }
    }
    ohara_home["event_triggers"] = [
        {
            "id": "sarah_relocation_before_margaret",
            "condition": "stop_order_received",
            "talk": "L4_event_sarah_relocation",
            "forced": True,
            "required_beats": [
                "O'Hara选择留下，Sarah同意暂时离开。",
                "Emma先把Sarah送到熟悉的Rosa家住一晚。",
                "完成安置后Zack才前往Margaret家。",
            ],
            "runtime_exit": {
                "action": "change_scene",
                "target_scene_id": 4034,
                "continuation": "release_to_exploration",
            },
        }
    ]

    post = state["expose"]["post_expose"]
    post.pop("new_testimony_gained", None)
    post["description"] = (
        "Margaret给出4104001正式摘要并主动交出Patrick遗物匣。她说明自己真正害怕的是Zack也像Patrick"
        "一样把自己的命排在最后。她没有突然和解，也没有认可Zack独自追查。Sarah此前已经由Emma送到"
        "Rosa家；Emma仍在继续处理O'Hara的安全安排。Zack决定不再等待Mickey规定谈话边界，独自前往"
        "四十二层。Emma只回“你自己去吧，我忙着呢”。"
    )
    post["event_id"] = "patrick_truth_and_42nd_floor_handoff"
    post["talk"] = "L4_post_expose_patrick_truth"
    post["required_beats"] = [
        "Patrick折返前不知道被困者是Mickey，也不存在临终交接。",
        "Margaret交出4418遗物匣且只取得一次。",
        "Zack主动决定前往四十二层，Emma因现实安置工作不同行。",
    ]
    post["player_control_restored_after"] = "patrick_truth_and_42nd_floor_handoff"


def revise_loop5(state: dict) -> None:
    state["scenes"] = [entry for entry in state["scenes"] if entry["id"] != 4041]
    office = scene(state, 4042)
    triggers = office.get("event_triggers", [])
    for trigger in triggers:
        if trigger.get("id") == "emma_changes_course":
            trigger["condition"] = "Zack 长时间未回电话，Emma基于持续不安自主改变决定"
            trigger["effect"] = (
                "Emma先决定前往四十二层；抵达楼下后才发现Miller车辆与人员增加，因此改走楼梯。"
                "她不参与身份锁与三轮Expose，只在坠落时抵达并抓住Zack。"
            )

    post = state["expose"]["post_expose"]
    post["event_id"] = "identity_value_dialogue_and_fall"
    post["talk"] = "L5_post_expose_identity_and_fall"
    post["player_control_restored_after"] = "identity_value_dialogue_and_fall"

    registry_4517 = next(entry for entry in state["evidence_registry"] if entry["id"] == 4517)
    registry_4517["visibility"] = "Zack独自拆内封后取得，并在4044向Emma与Watts共享"
    registry_4519 = next(entry for entry in state["evidence_registry"] if entry["id"] == 4519)
    registry_4519["visibility"] = "仅Zack在4044看见并扣下；4045发现街区症状后立即交给Watts"

    ending_4043, ending_4044, ending_4045 = state["ending_sequence"]["scenes"]
    ending_4043["talk"] = "L5_ending_departure"
    ending_4043["runtime_exit"] = {
        "action": "change_scene",
        "target_scene_id": 4044,
        "continuation": "next_talk",
        "next_talk": "L5_ending_archive_review",
    }
    ending_4044["talk"] = "L5_ending_archive_review"
    ending_4044["runtime_exit"] = {
        "action": "change_scene",
        "target_scene_id": 4045,
        "continuation": "next_talk",
        "next_talk": "L5_ending_ohara_door",
    }
    ending_4045["talk"] = "L5_ending_ohara_door"
    ending_4045["runtime_exit"] = {
        "action": "chapter_end",
        "next_unit_entry": "enter_ohara_house",
    }

    inner = ending_4044.pop("inner_envelope_visible_to_zack")
    inner["shared_evidence"] = [4517]
    inner["concealed_evidence"] = [4518, 4519]
    ending_4044["inner_envelope_opened_by_zack"] = inner
    ending_4044["description"] = (
        "三人共同检查4516外卷。Zack留在主档案桌前整理，发现暗部封夹并独自拆开内封套，取得4517、"
        "4518、4519。他向Emma与Watts共享4517的地基材料替换事实，但扣下4518与4519；随后只从"
        "外卷公开O'Hara的优先清退危险。"
    )
    for npc_key in ("L5_ending4044_emma", "L5_ending4044_watts"):
        npc = ending_4044["npcs"][npc_key]
        npc["known_information"].append("4517证明1912事故前承重材料被主动降级")
        npc["withheld_information"] = [
            "无；此时不知道4518、4519，且不知道Zack曾在此刻扣下它们"
        ]


REVISERS = {
    1: revise_loop1,
    2: revise_loop2,
    3: revise_loop3,
    4: revise_loop4,
    5: revise_loop5,
}


def remove_deprecated_fields(value) -> None:
    if isinstance(value, dict):
        value.pop("trap_evidence", None)
        for child in value.values():
            remove_deprecated_fields(child)
    elif isinstance(value, list):
        for child in value:
            remove_deprecated_fields(child)


def generate() -> None:
    raise RuntimeError(
        "DEPRECATED: this one-off candidate generator encodes superseded Unit4 event, "
        "evidence-acquisition, and ending contracts. Use the unit-state-generator skill "
        "against the Manifest active outline and validate 剧情设计/Unit4/state directly."
    )
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for loop_number in range(1, 6):
        state = load_state(loop_number)
        state["opening"] = OPENINGS[loop_number]
        state["outline_coverage"] = build_coverage(loop_number)
        state["narrative_continuity"] = build_continuity(loop_number)
        state["expose"]["lie_source_semantics"] = {
            "round_1": {
                "kind": "collectible_lie_anchor",
                "collectible_testimony": True,
                "boundary": "R1 lie_source必须先在普通Talk中说出并取得，Expose只回放同一原话。",
            },
            "later_rounds": {
                "kind": "dynamic_expose_lie",
                "collectible_testimony": False,
                "boundary": "R2及以后是NPC在Expose中被击穿后主动退守的新谎言，不得在普通Talk预收集。",
            },
            "requires_doubt_condition": False,
            "usable_evidence_boundary": (
                "lie_source不作为击穿材料；每轮usable_evidence仍必须进入疑点或身份链。"
            ),
        }
        REVISERS[loop_number](state)
        inline_testimony_definitions(
            state,
            TESTIMONY_DEFINITIONS[loop_number],
        )
        remove_deprecated_fields(state)
        output = TARGET_DIR / f"loop{loop_number}_state.yaml"
        output.write_text(
            yaml.safe_dump(
                state,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    generate()
