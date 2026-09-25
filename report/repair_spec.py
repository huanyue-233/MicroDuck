import json
from pathlib import Path
p = Path(r'C:\Users\Administrator\Desktop\MicroDuck\report')
spec = json.loads((p/'deck_spec.json').read_text(encoding='utf-8'))
spec['language'] = '简体中文'
spec['goal'] = '面向机器人研究与工程评审的 MicroDuck 复现方案学术汇报，说明开源资料、路线比较、实施方法和验收标准。'
spec['deck_context'] = {
    'source': '复现方案总结报告.md，资料截止 2026-09-24；官方与社区项目分别标注。',
    'core_claim': 'MicroDuck 复现是机械、电气、运行时、策略与仿真五层系统集成。首次实体复现推荐 HD-1910 社区结构配合官方运行时思想，执行器参数需实测并重训。',
    'evidence_boundary': '区分官方公开资料、社区逆向、台架实测和计划工作。不能声称 HD-1910 复刻已经稳定行走。生成式机器人图只是概念示意，不是实物证据。',
    'canonical_terms': ['MicroDuck','HD-1910','XL330','Radxa Zero 3W','RPI Robot HAT','imu_to_dxl','MJCF','MuJoCo','BAM','ONNX','sim2real']
}
spec['style'] = {
    'name': '清爽科研专业风（已批准样例）',
    'visual_direction': '参考已批准的第 3 页：16:9 中国机器人学术汇报；白色/浅灰底、深海军蓝标题、青色与橙色点缀、淡技术网格、细线图标、留白充足。统一视觉但每页布局按内容变化，不复制五层堆栈。',
    'color_palette': '白色 #FFFFFF，浅灰 #F7F9FC，深蓝 #0D2445，青色 #15A9B8，克制的橙色 #E98B39',
    'typography': '清晰的简体中文无衬线字体；大标题、短标签、可投影阅读的正文。必须正确书写汉字，禁止问号或乱码。',
    'density': '每页一个核心结论、3–5 个短标签，避免段落、微小脚注和过密图文。',
    'image_treatment': '矢量感科研信息图；机器人形象仅作概念示意，不作为已验证实物照片。'
}
spec['approved_style_reference'] = {'path': str(p/'origin_image'/'slide_03.png'), 'role': '已批准样例，仅用于视觉风格参照', 'fidelity': '匹配配色、字重、密度和信息图气质；不复制页面布局或文字'}
spec['sample_generation_method']['input_context_preparation'] = '工作者先查看第 3 页样例，然后用完整文字风格说明调用 Wokey 文生图；样例不是严格输入资产。'
spec['sample_generation_method']['handoff_rule'] = '沿用 Wokey gpt-image-2.5 直接 API、支持异步任务。不得用本地绘图叠字；API 不可用时报告阻塞。'
slides = [
(1, 'MicroDuck 复现方案', '封面', '建立主题和研究目标', ['从开源资料到可运行实体', '机械 × 电控 × 实时控制 × 强化学习', '资料截止：2026-09-24'], '左侧大标题和两行副标题，右侧为实验室中的双足鸭形机器人概念插画。留白充分。', '概念插画不是官方机器人实物照片。'),
(2, '为什么复现 MicroDuck 很难', '问题定义', '指出跨层依赖和证据缺口', ['资料分散在多个仓库', '官方策略绑定执行器与动力学', '能打印 ≠ 能站立 ≠ 能稳定行走', '区分官方事实与社区推断'], '左到右的“资料碎片 → 系统集成”流程图，四个简洁问题卡片。', '不得暗示社区 HD-1910 已经稳定行走。'),
(3, 'MicroDuck 的五层系统模型', '系统架构', '解释五层系统及接口', ['机械：15 舵机与双足机构', '电气：总线、IMU、HAT、电池', '运行时：Rust daemon、50 Hz', '策略：61 维观测 → 14 维动作', '仿真：MJCF、MuJoCo、PPO'], '此页已批准，保留原图，不重新生成。', '已接受样例。'),
(4, '开源资料与社区项目地图', '项目谱系', '区分官方资产、社区复刻、方法参考', ['官方：microduck / microduck_rl / RPI Robot HAT', '复刻：microduck-replica / replica-cad', '衍生：OpenMicroDuck / HD-1910 RL fork', '方法参考：Open Duck Mini v2', '缺口：生产 BOM、完整 CAD、IMU 转接'], '官方基础 → 社区复刻 → 方法参考的三列谱系图；每项只有简短标签。', 'Open Duck Mini v2 不是 Microduck 的兼容件。'),
(5, '四条复现路线比较', '路线比较', '根据目标比较工程取舍', ['官方 XL330：策略接近，成本较高', '社区 HD-1910：实物资料多，需重训', 'OpenMicroDuck：结构优化，需集成', 'Open Duck Mini v2：方法参考，非兼容件', '首次实体复现：优先 HD-1910'], '四列路线卡片，HD-1910 用青色强调；标签对比官方一致性、采购与策略复用，不要虚构精确分数。', '此处是定性建议，不是实测量化排名。'),
(6, '推荐硬件方案：HD-1910 路线', '硬件架构', '呈现推荐硬件组合', ['HD-1910-C001 × 15', 'Radxa Zero 3W 2 GB', '官方 RPI Robot HAT + 社区 imu_to_dxl', 'URT2 + 限流电源：先桌面调试', '摄像头 / 2S 电池：整机阶段'], '中间为简化机器人示意，周围是主控、HAT、电池、IMU、舵机总线模块；电源与数据箭头明确。', '不是具体引脚接线图，IMU 小板不承载电机供电电流。'),
(7, '从仿真到实体的实施路线', '实施流程', '按风险递增设置关口', ['① 锁定版本与 BOM', '② 仿真与 ONNX 推理', '③ 打印装配与舵机标定', '④ 总线 / IMU / 50 Hz 控制', '⑤ 执行器辨识与重训', '⑥ 支架测试 → 站姿 → 行走'], '六阶段路线图，每阶段一个图标和验收关口，线条简洁。', '阶段名称是计划，不是已完成事项。'),
(8, '软件与 sim2real 关键契约', '控制闭环', '解释硬件替换时必须保持的接口', ['61 维观测 → ONNX → 14 维动作', '50 Hz 控制环与 IMU 同步', 'HD-1910：协议、零位、回差、延迟', '实测质量 / 惯量 / 摩擦进入 MJCF', '官方 XL330 策略不可直接照搬'], '大型闭环图：仿真模型 → 策略 → 运行时 → 舵机/IMU → 观测；用橙色标识不一致风险。', '不要虚构具体误差数值或延迟测量结果。'),
(9, '风险、踩坑与安全边界', '风险矩阵', '突出可能损伤硬件的错误', ['ID / 零位 / 方向：逐颗标定', '供电与反灌：限流、共地、分配电流', '串口：检查 /dev/ttyS2 占用', '结构版本：XL330 与 HD-1910 不混用', '真机：支架、限位、急停与回退'], '风险 → 后果 → 预防的五行矩阵，橙色为警示，不要拥挤。', '电气提示不能代替最终硬件规格核对。'),
(10, '验收标准与预期成果', '分层验收', '定义可重复的完成条件', ['仿真：MJCF、61→14、ONNX 回放', '总线：15 舵机唯一 ID、持续读写', '主控：冷启动、50 Hz、日志与温度', '机械：无干涉、接触稳定、可重复装配', '行为：站姿、坐站、低速行走、急停'], '仿真 → 台架 → 整机 → 行为的阶梯图；方框为计划验收条件，不画成已完成勾选。', '不能把计划验收画成已经通过。'),
(11, '结论与下一步', '结论', '归纳推荐路线和立即行动', ['首版优先：HD-1910 社区复刻', '保留官方 50 Hz 控制与安全层', '重新辨识执行器并训练策略', '冻结 BOM → 台架 → 站姿', 'Q&A'], '左侧一句推荐路线，右侧为简洁的里程碑路径或概念机器人；结尾留白。', '不得声称实体方案已全部完成。')
]
spec['slides'] = []
for n,title,role,intent,points,composition,caveat in slides:
    slide = {
        'number':n, 'title':title, 'role':role, 'intent':intent, 'key_points':points,
        'local_context':{'caveat':caveat},
        'layout':{'intent':intent,'composition':composition},
        'visual_elements':{'rendering':'与已批准样例一致的清爽科研信息图，图标语言统一'},
        'constraints':['仅使用给定中文标题和短标签，禁止编造额外结论。','汉字必须正确，不得出现问号、乱码、虚假引用、水印、logo 或页码。','16:9 横版，投影可读，保留安全边距。','每页变化布局，但与第 3 页配色和视觉层次一致。']
    }
    if n == 3: slide['sample_approved'] = True
    spec['slides'].append(slide)
assert len(spec['slides']) == 11
text = json.dumps(spec, ensure_ascii=False, indent=2) + '\n'
assert '?' not in text and '\ufffd' not in text
assert sum('\u4e00' <= c <= '\u9fff' for c in text) > 500
(p/'deck_spec.json').write_text(text, encoding='utf-8')
print('Rebuilt deck_spec.json: slides=',len(spec['slides']),'CJK=',sum('\u4e00' <= c <= '\u9fff' for c in text))
