# MicroDuck

MicroDuck（双足鸭机器人）复现项目的资料与工作目录。

## 目录结构

```
MicroDuck/
├── docs/                        # 调研与方案文档
│   ├── list.md                  # BOM 物料清单
│   ├── microduck.md             # 官方 MicroDuck 项目资料
│   ├── microduck-rl.md          # MicroDuck RL 训练库资料
│   ├── Related Repo.md          # 社区复刻仓库地址
│   ├── 三个复现差异分析.md        # 三个社区复现项目差异分析
│   ├── 复现方案总结报告.md        # 复现方案总结报告（主报告）
│   └── 术语.md                  # 术语表
├── report/                      # 学术汇报 PPT 项目
│   ├── microduck_academic_report.pptx   # 最终成品 PPT
│   ├── outline.md               # 汇报大纲
│   ├── speech.md                # 演讲词
│   ├── deck_spec.json           # PPT 规格
│   ├── slide_jobs.json          # 幻灯片生成任务记录
│   ├── prompts/                 # 每页幻灯片的生成提示词
│   ├── origin_image/            # 最终采用的幻灯片图片
│   ├── qa_contact_sheet.jpg     # QA 联系表
│   └── *.py                     # 生成/校验脚本
├── output/                      # 杂项输出（如图片生成测试）
├── .env                         # API 密钥（勿提交）
└── .gitignore
```

## 说明

- 根目录文档已整理进 `docs/`。
- 学术汇报相关文件集中在 `report/`（原 `microduck_academic_report/`）。
- 生成脚本输出目录统一为 `report/origin_image/`。