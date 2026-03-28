# Active Session

Last updated: 2026-03-28 14:38:40

## Recently Modified Files
.agents/skills/asset-naming/skill.md
.agents/skills/config-table-assistant/skill.md
.agents/skills/cycle-expose-designer/skill.md
.agents/skills/daily-summary/skill.md
.agents/skills/episode-outline-generator/skill.md
.agents/skills/episode-story-extractor/skill.md
.agents/skills/premium-puzzle-assistant/CHANGELOG.md
.agents/skills/premium-puzzle-assistant/skill.md
.claude/agents/content-director.md
.claude/commands/connoisseur.md
.claude/commands/generate-dialogue.md
.claude/commands/generate-state.md
.claude/commands/review-dialogue.md
.claude/settings.json
CLAUDE.md
preview_new2/data/Unit3/talk_summary.yaml
preview_new2/data/table/NPCStaticData.json
preview_new2/data/table/SceneConfig.json
preview_new2/index.html
preview_new2/state_to_preview.py

## Unstaged Changes
 .agents/skills/asset-naming/skill.md               |  296 -----
 .agents/skills/config-table-assistant/skill.md     |  436 -------
 .agents/skills/cycle-expose-designer/skill.md      |  443 -------
 .agents/skills/daily-summary/skill.md              |  511 --------
 .agents/skills/episode-outline-generator/skill.md  |  480 --------
 .agents/skills/episode-story-extractor/skill.md    |  446 -------
 .../skills/premium-puzzle-assistant/CHANGELOG.md   |  141 ---
 .agents/skills/premium-puzzle-assistant/skill.md   |  484 --------
 .claude/agents/content-director.md                 |  169 ++-
 .claude/commands/connoisseur.md                    |  283 -----
 .claude/commands/generate-dialogue.md              |  361 ------
 .claude/commands/generate-state.md                 |  608 ----------
 .claude/commands/review-dialogue.md                |  275 -----
 .claude/settings.json                              |   25 +-
 CLAUDE.md                                          |    4 +-
 preview_new2/data/Unit3/talk_summary.yaml          |    2 +-
 preview_new2/data/table/NPCStaticData.json         |   78 +-
 preview_new2/data/table/SceneConfig.json           |  122 +-
 preview_new2/index.html                            |  471 +++++++-
 preview_new2/state_to_preview.py                   |   10 +-
 production/session-state/active.md                 |   35 +-
 ...270\203\345\261\200\350\256\276\350\256\241.md" |  127 +-
 ...270\203\345\261\200\350\256\276\350\256\241.md" |    6 +-
 ...270\203\345\261\200\350\256\276\350\256\241.md" |   12 +-
 ...270\203\345\261\200\350\256\276\350\256\241.md" |    4 +-
 ...270\203\345\261\200\350\256\276\350\256\241.md" |   42 +-
 .../README.md"                                     |  119 --
 ...270\203\345\261\200\350\256\276\350\256\241.md" |  630 ----------
 ...270\203\345\261\200\350\256\276\350\256\241.md" | 1119 ------------------
 ...270\203\345\261\200\350\256\276\350\256\241.md" | 1162 -------------------
 ...270\203\345\261\200\350\256\276\350\256\241.md" | 1106 ------------------
 ...270\203\345\261\200\350\256\276\350\256\241.md" | 1221 --------------------
 ...270\203\345\261\200\350\256\276\350\256\241.md" | 1031 -----------------
 ...72\262_\344\277\256\350\256\242\347\211\210.md" |   12 +-
 ...226\221\347\202\271\350\256\276\350\256\241.md" |   42 +-
 .../Unit3/state/loop3_state.yaml"                  |   14 +-
 .../Unit3/state/loop4_state.yaml"                  |    4 +-
 .../Unit3/state/loop6_state.yaml"                  |    2 +-
 .../liam.md"                                       |  149 ---
 ...272\214\346\245\274\350\265\260\345\273\212.md" |   10 +-
 ...234\272\346\231\257\346\200\273\350\247\210.md" |   10 +-
 ...214\207\350\257\201\350\256\276\350\256\241.md" |   38 +-
 ...276\216\346\234\257\350\265\204\344\272\247.md" |    4 +-
 ...272\213\344\270\215\345\207\272\351\227\250.md" |    2 +-
 44 files changed, 883 insertions(+), 11663 deletions(-)
