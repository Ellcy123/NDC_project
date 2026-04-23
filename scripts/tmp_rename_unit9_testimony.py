"""一次性脚本：把 Unit9 所有 state 里的 7 位证词 ID 从旧格式 {loop}{npc}{loop}{seq} 改为 {unit=9}{npc}{loop}{seq}。

Whale 同时从 NPC 11 重编为 NPC 09（NPCStaticData 3 位 ID 约束）。
"""
import re
import pathlib
import sys

STATE_DIR = pathlib.Path("d:/NDC_project/剧情设计/Unit9/state")

# {old_id: new_id}
MAPPING = {
    # Loop1
    "1030101": "9031001", "1030102": "9031002", "1030103": "9031003",
    "1040101": "9041001", "1040102": "9041002", "1040103": "9041003", "1040104": "9041004",
    "1060101": "9061001",
    # Loop2
    "2050201": "9052001", "2050202": "9052002", "2050203": "9052003",
    "2070201": "9072001", "2070202": "9072002", "2070203": "9072003",
    # Loop3
    "3030301": "9033001", "3030302": "9033002",
    "3040301": "9043001", "3040302": "9043002",
    "3060301": "9063001", "3060302": "9063002",
    "3070301": "9073001",
    # Loop4
    "4040402": "9044002", "4040403": "9044003",
    "4050401": "9054001", "4050402": "9054002",
    "4060401": "9064001", "4060402": "9064002", "4060403": "9064003",
    "4060404": "9064004", "4060405": "9064005", "4060406": "9064006", "4060407": "9064007",
    # Loop5
    "5050501": "9055001", "5050502": "9055002",
    "5070501": "9075001", "5070502": "9075002",
    "5080501": "9085001", "5080502": "9085002",
    # Loop6 (Whale: NPC 11 → NPC 09)
    "6104001": "9046001", "6104002": "9046002", "6104003": "9046003",
    "6106001": "9066001", "6106002": "9066002",
    "6108001": "9086001",
    "6111001": "9096001",
}

# Loop6 header 专属的固定文本替换（不走 7 位 ID 正则）
LOOP6_HEADER_REPLACEMENTS = [
    (
        "# NPC 编码（来自讨论结论第八节）：\n"
        "#   Emma=102 / Rosa=103 / Morrison=104 / Tommy=105 / Vivian=106 / James=107 / Anna=108 / Whale=111",
        "# NPC 编码（Unit9 NPCStaticData）：\n"
        "#   Emma=902 / Rosa=903 / Morrison=904 / Tommy=905 / Vivian=906 / James=907 / Anna=908 / Whale=909",
    ),
    (
        "# Testimony ID 格式：{loop=6}{npc_code=3位}{seq=2位} = 7 位\n"
        "#   Morrison: 6104xx → 6104001、6104002、6104003\n"
        "#   Vivian:   6106xx → 6106001、6106002\n"
        "#   Anna:     6108xx → 6108001\n"
        "#   Whale:    6111xx → 6111001（插入剧情，不作 condition）",
        "# Testimony ID 格式：{unit=9}{npc_code=2位}{loop=1位}{seq=3位} = 7 位（Unit8 同款）\n"
        "#   Morrison: 9046xxx → 9046001、9046002、9046003\n"
        "#   Vivian:   9066xxx → 9066001、9066002\n"
        "#   Anna:     9086xxx → 9086001\n"
        "#   Whale:    9096xxx → 9096001（插入剧情，不作 condition）",
    ),
]

# 其他 Loop header 里的 "Emma=102" 类 EPI01 NPC 标注 → 改为 Unit9 9xx（可选）
SHARED_HEADER_REPLACEMENTS = [
    (
        "Emma=102, Rosa=103, Morrison=104, Tommy=105, Vivian=106, James=107, Anna=108",
        "Emma=902, Rosa=903, Morrison=904, Tommy=905, Vivian=906, James=907, Anna=908, Whale=909",
    ),
]


def main(dry_run: bool):
    # 验证映射无冲突（new ID 不能重复、不能撞回原表）
    new_ids = list(MAPPING.values())
    assert len(set(new_ids)) == len(new_ids), "new id 有重复"
    assert not (set(MAPPING.keys()) & set(new_ids)), "new id 与 old id 撞了"

    # 预编译：词边界保护
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in MAPPING) + r")\b")

    files = sorted(STATE_DIR.glob("loop*_state.yaml"))
    total_replaced = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        orig = text

        # Loop6 header 专属修复
        if f.name == "loop6_state.yaml":
            for old, new in LOOP6_HEADER_REPLACEMENTS:
                if old in text:
                    text = text.replace(old, new)

        # 共享 header 修复
        for old, new in SHARED_HEADER_REPLACEMENTS:
            if old in text:
                text = text.replace(old, new)

        # 7 位 ID 替换
        count = 0
        def _sub(m):
            nonlocal count
            count += 1
            return MAPPING[m.group(1)]

        text = pattern.sub(_sub, text)
        total_replaced += count

        if text != orig:
            if dry_run:
                print(f"[dry-run] {f.name}: 替换 {count} 处")
            else:
                f.write_text(text, encoding="utf-8")
                print(f"[write]   {f.name}: 替换 {count} 处")
        else:
            print(f"[skip]    {f.name}: 无变化")

    print(f"\n总计替换 {total_replaced} 处 ID")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
