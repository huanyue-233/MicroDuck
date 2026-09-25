# Microduck RL 项目资料整理

## 一、项目定位

Microduck RL（`pollen-robotics/microduck_rl`）是 Microduck 双足机器人的**强化学习训练环境仓库**，与负责真机运行时和 SDK 的 `pollen-robotics/microduck` 仓库形成上下游关系。它的核心产出是：在仿真中训练神经网络策略，导出为 ONNX 格式，再由真机运行时以 50 Hz 频率加载执行。

该仓库完整编码了 sim2real 配方——包括 BAM 执行器物理建模、域随机化、齿隙模拟，以及经过验证的奖励设计经验（见 `AGENTS.md` 中的提炼版 playbook）。

------

## 二、技术栈

| 组件           | 说明                                                  |
| :------------- | :---------------------------------------------------- |
| **仿真引擎**   | MuJoCo / MuJoCo Warp（GPU 并行后端）                  |
| **训练框架**   | mjlab（MuJoCo Warp 之上的 RL 环境框架）               |
| **RL 算法**    | PPO（rsl_rl 实现）                                    |
| **执行器建模** | BAM（Better Actuator Models）M6，针对 Dynamixel XL330 |
| **包管理**     | uv（Python 包与环境管理器）                           |
| **实验跟踪**   | WandB / TensorBoard                                   |
| **策略导出**   | ONNX                                                  |

策略在 50 Hz 频率下训练，与真机控制回路频率一致，确保 sim2real 节奏匹配。依赖版本方面，关键包包括 torch 2.9.1+cu128、warp-lang 1.12.0、mjlab 1.3.0、rsl-rl-lib 5.0.1 以及 BAM 模型（`better-actuator-models`）。

------

## 三、快速开始

### 3.1 环境要求

需要 **CUDA GPU**（训练通过 MuJoCo Warp 运行）和 **uv**。仓库要求 Python >=3.12, <3.13（因为依赖的 bam 包锁定了 <3.13；uv 会自动管理解释器，无需手动切换系统 Python）。

在 ARM 设备（DGX Spark / GB10、Jetson）上，`uv sync` 首次运行会下载约 2 GB 的 CUDA wheel，uv 默认的 30 秒 HTTP 超时可能中断下载。需要设置 `UV_HTTP_TIMEOUT=600` 再执行首次同步。

### 3.2 安装

bash

```
git clone https://github.com/pollen-robotics/microduck_rl
cd microduck_rl
uv sync   # 首次约 6 分钟，下载 ~2GB
```



### 3.3 环境验证（三步）

bash

```
# 1) 确认 torch 能看见 GPU
uv run python -c "import torch; print(torch.cuda.is_available())"

# 2) 确认任务注册正常
uv run list-envs

# 3) 运行仓库测试套件
uv run --with pytest pytest tests/
```



预期结果：torch 输出 `True`；`list-envs` 列出全部 MicroDuck 任务；测试套件 166 passed, 1 skipped（skipped 的是 aarch64 专用测试，x86_64 上预期跳过）。

### 3.4 训练行走策略

bash

```
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096
```



在 4096 个并行环境下，约 1–2 小时可得到可用的步态。**建议先跑冒烟测试**：

bash

```
uv run train <TASK_ID> --env.scene.num-envs 64 --agent.max_iterations 5
```



在 64 个环境下跑 5 次迭代的冒烟测试可捕获约 95% 的配置错误，成本极低，不要跳过。

------

## 四、任务清单

`uv run list-envs` 打印实时任务注册表。部分任务有 Flat / Rough 地形变体：

| 任务 ID                                   | 地形       | 描述                                              |
| :---------------------------------------- | :--------- | :------------------------------------------------ |
| `Mjlab-Velocity-{Flat,Rough}-MicroDuck`   | flat/rough | **主任务**：速度指令行走 + 头部姿态指令           |
| `Mjlab-VelStand-{Flat,Rough}-MicroDuck`   | flat/rough | 行走 + 跌倒恢复，单一策略                         |
| `Mjlab-StandUp-{Flat,Rough}-MicroDuck`    | flat/rough | 从趴倒/仰倒/坐姿站起，然后保持站立 + 身体姿态控制 |
| `Mjlab-SitStand-{Flat,Rough}-MicroDuck`   | flat/rough | 指令化坐 ↔ 站，单一策略，可控制头部               |
| `Mjlab-GroundPick-{Flat,Rough}-MicroDuck` | flat/rough | 蹲下用喙尖触地，然后回到站立                      |
| `Mjlab-BallKick-Flat-MicroDuck`           | flat       | 向前踢一个 70 mm / 15 g 的球（actor 对球盲视）    |
| `Mjlab-Roulade-Flat-MicroDuck`            | flat       | 前滚翻，用头部翻转后回到脚上站立                  |
| `Mjlab-Velocity-Flat-MicroDuck-Rollers`   | flat       | 轮滑模式的速度跟踪                                |

每个主任务都有一个 **Backlash 孪生变体**，为 14 个舵机关节中的每一个添加 ±1° 的齿轮间隙，编码器读数位于间隙的输出侧，使观测与真实硬件匹配。

------

## 五、Sim2Real 核心技术

### 5.1 BAM 执行器建模

普通做法把舵机当作理想 PD 控制器；microduck_rl 使用 BAM 将 Dynamixel XL330 建模到**电压控制律级别**，包括：

- **反电动势**
- **库仑摩擦 / 静摩擦 / 负载相关摩擦**
- **电池电压与负载压降**（`vin_range=(6.5, 8.2)` 每环境采样）
- **固件 PD 增益**（`kp_fw=200`）

所有任务使用 BAM M6 执行器模型，反射转子惯量也纳入建模（armature 被设置而非归零）。

### 5.2 域随机化

域随机化通过环境配置顶部的 `ENABLE_*` 布尔开关启用，随机化参数包括：

| 参数                        | 说明                                                         |
| :-------------------------- | :----------------------------------------------------------- |
| 电池电压波动                | 每环境采样不同电压                                           |
| 电压压降（voltage sag）     | 负载条件下的电压下降                                         |
| 指令延迟（command latency） | 控制指令传输延迟                                             |
| 摩擦系数变化                | 通过 `FrictionDRBamActuator.friction_scale` 按环境缩放 BAM 摩擦预算 |

其目的是让训练出的策略在真机上更“抗造”，避免训练中出现不可迁移的 exploit。

### 5.3 齿隙模拟（Backlash）

XL330 的编码器位于转子侧，无法感知齿轮间隙——这正是 microduck_rl 必须添加 `passive_*_backlash` 铰链并模拟“固件位置环透过齿隙读取”行为的原因。每个主任务都有对应的 Backlash 变体，覆盖 ±1° 的齿轮间隙。

### 5.4 观测归一化器烘焙

导出 ONNX 时，观测归一化器会被烘焙进模型中，这是**强制路径**，保证训练和部署时观测处理的一致性。

------

## 六、训练与部署工作流

### 6.1 训练

bash

```
# 正式训练
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096

# 从检查点恢复
uv run train Mjlab-Velocity-Flat-MicroDuck --env.scene.num-envs 4096 \
  --agent.run-name resume \
  --agent.load-checkpoint model_29999.pt \
  --agent.resume True
```



没有本地 GPU 时，在任意训练命令后添加 `--hf-jobs` 可将训练提交到 Hugging Face Jobs。

### 6.2 在查看器中观察训练好的策略

bash

```
uv run play Mjlab-Velocity-Flat-MicroDuck --wandb-run-path <entity/project/run_id>
```



### 6.3 导出 ONNX

bash

```
uv run scripts/export.py Mjlab-Velocity-Flat-MicroDuck --wandb-run-path <...>
```



### 6.4 部署排练（CPU MuJoCo）

bash

```
uv run scripts/infer_policy.py --walking output.onnx
```



使用与训练时相同的 BAM M6 执行器，在 CPU MuJoCo 中进行部署排练；加 `--no-bam` 可切换为 XML PD 模式。

### 6.5 发布到 Hugging Face Hub

bash

```
uv run publish --onnx output.onnx \
  --repo <user>/microduck-<name> \
  --kind episodic --duration-s 4.0
```



该命令生成 `policy.onnx` + schema-2 `manifest.json` + README，发布到 Hugging Face Hub。机器人端通过 `robotctl policy add` 加载。

------

## 七、代码结构

| 路径                                               | 内容                                                         |
| :------------------------------------------------- | :----------------------------------------------------------- |
| `src/mjlab_microduck/tasks/mdp.py`                 | **全部自定义 MDP 函数**（奖励、事件、观测、指令、课程学习），7000+ 行 |
| `src/mjlab_microduck/tasks/microduck_*_env_cfg.py` | 每个任务族一个配置模块；`microduck_velocity_env_cfg.py` 是主行走配方兼共享基础 |
| `src/mjlab_microduck/tasks/__init__.py`            | 任务注册（基础 + Backlash 变体）                             |
| `src/mjlab_microduck/tasks/backlash.py`            | 将任意环境配置包装为 Backlash 孪生体                         |
| `src/mjlab_microduck/robot/microduck_constants.py` | 机器人配置、HOME 姿态、BAM 执行器参数                        |
| `src/mjlab_microduck/robot/microduck/`             | 从 Onshape 导出的 MJCF 模型                                  |
| `src/mjlab_microduck/actuator/friction_dr_bam.py`  | BAM + 摩擦域随机化 + 齿隙编码器反馈                          |
| `train_cli.py` / `train_hook.py` / `hf_jobs.py`    | 训练入口与云端部署                                           |

添加新奖励函数时，在 `mdp.py` 中按任务分组添加。

------

## 八、关键约定与经验

### 8.1 为什么 sim2real 是这个仓库的核心

README 中强调：**每一个约定之所以存在，都是因为违反它会导致策略在查看器中工作但在硬件上失败**。这不是一个“在仿真里能走就行”的项目，而是一条完整的从仿真到真机的控制链路。

### 8.2 奖励设计

`mdp.py` 中所有奖励项都是显式可见且可修改的，而非隐藏在框架内部。奖励设计经验被提炼在 `AGENTS.md`（部分分支为 `CLAUDE.md`）中，作为“distilled playbook”指导新任务开发。

### 8.3 调试技巧

- `uv run --no-sync list-envs | grep MicroDuck` 快速过滤 MicroDuck 任务
- `WANDB_MODE=offline` 环境变量可在无网络环境下训练
- 冒烟测试（64 环境 × 5 迭代）是每次启动长训练前的必做步骤

------

## 九、社区与生态

| 项目                                                         | 说明                                                   |
| :----------------------------------------------------------- | :----------------------------------------------------- |
| [microduck](https://github.com/pollen-robotics/microduck)    | 真机运行时与 SDK，加载 RL 训练产出的 ONNX 策略         |
| [microduck-backflip](https://github.com/Lulzx/microduck-backflip) | 可复现的后空翻 RL 任务、评估管线与安全门               |
| [microduck-lab](https://github.com/jonathanhawkins/microduck-lab) | 在普通 Apple Silicon Mac 上（无 CUDA GPU）训练 RL 策略 |
| [microduck-playground](https://github.com/Vottivott/microduck-playground) | 可复现实验、策略演示和可打印硬件扩展                   |
| [microduck-policies](https://huggingface.co/pollen-robotics/microduck-policies) | Hugging Face Hub 上的官方 ONNX 策略集                  |
| [microduck-simulator](https://huggingface.co/spaces/pollen-robotics/microduck-simulator) | 浏览器中的 RL 沙盒（MuJoCo WASM + onnxruntime-web）    |
| [microduck-jetson](https://github.com/jjjadand/microduck_rl) | Jetson 部署 fork，含部署脚本和训练检查点               |

------

## 十、参考链接

| 资源              | 链接                                                         |
| :---------------- | :----------------------------------------------------------- |
| GitHub 主仓库     | https://github.com/pollen-robotics/microduck_rl              |
| README            | [README.md](https://github.com/pollen-robotics/microduck_rl/blob/main/README.md) |
| 开发约定          | [AGENTS.md](https://github.com/pollen-robotics/microduck_rl/blob/develop/AGENTS.md) |
| Jetson 教程       | https://wiki.seeedstudio.com/cn/ai_robotics_microduck_rl_on_jetson/ |
| 系列课程（14 集） | https://forum.d-robotics.cc/t/topic/35664                    |
| BAM 项目          | https://github.com/Rhoban/bam                                |
| mjlab             | https://github.com/mujocolab/mjlab                           |
| 官方策略          | https://huggingface.co/pollen-robotics/microduck-policies    |