# Microduck 项目资料

## 一、项目概述

**Microduck** 是由 Pollen Robotics（Hugging Face 旗下位于波尔多的机器人团队）开发的一款开源双足鸭形机器人。它是一个面向 AI 开发者和创客的可编程物理 AI 实验平台，核心定位是“行动导向的 AI 平台”——不只是执行固定动作的玩具，而是一个可以让你自行训练神经网络策略、然后部署到真机运行的实验平台。

Microduck 高约 25 cm，重约 800 g，由运行在 Rockchip RK3566 芯片上的多个守护进程驱动，包含一个 50 Hz 控制回路，通过神经网络策略驱动 15 个舵机、无线电和摄像头。其运行策略由相邻仓库 **microduck_rl** 训练，使用 MuJoCo 和 PPO，涵盖 sim2real 配方以及导出 ONNX 供本仓库加载。

Microduck 于 2026 年 8 月 27 日正式开放预购，售价 399 美元（不含税和运费），预售 24 小时内销售额超过 260 万美元。它是 Pollen Robotics 继 Reachy Mini 之后的第二款消费级机器人。

**主要功能：**

- **行走**：使用游戏手柄即可驱动
- **滑行**：装上轮子，按住方向键上，即可加载另一套“大脑”
- **拾取物品**：鸭嘴触地，一键抓取
- **跌倒恢复**：被推倒后能自行站起

此外，它还能坐下、踢球、按指令向前滚动，并用自己独特的声音“嘎嘎”叫。

------

## 二、硬件规格

| 项目   | 规格                                                       |
| :----- | :--------------------------------------------------------- |
| 高度   | 约 25 cm                                                   |
| 重量   | 约 800 g                                                   |
| 处理器 | Rockchip RK3566（Arm 架构，集成 AI 加速器）                |
| 内存   | 1 GB RAM                                                   |
| 存储   | 32 GB Flash                                                |
| 电机   | 15 个伺服电机（分布于双腿、颈部与头部）                    |
| 传感器 | 广角摄像头、小型激光雷达、2 个 IMU（惯性测量单元）、麦克风 |
| 执行器 | 铰接式鸭喙（同时是小型夹爪，可夹取约 800 g 物体）          |
| 连接   | Wi-Fi、蓝牙、NFC 标签识别                                  |
| 音频   | 扬声器                                                     |
| 配色   | 四种配色可选                                               |

Microduck 采用瑞芯微 RK3566 处理器运行 50 Hz 控制回路，驱动电机同时管控摄像头与无线电模块。尽管仅配备 1 GB 内存和 32 GB 存储空间，仅内存成本就占据了总价的 10% 至 15%。机器人由中国制造。

------

## 三、软件架构

### 3.1 总体设计

Microduck 的软件系统由 **7 个守护进程** 组成，运行在同一块板子上，通过 Unix 套接字通信。其中一个进程驱动机器人，另外三个进程的存在使得第一个进程即使崩溃也不会导致板子无法访问，其余进程是传输和传感器相关进程，不拥有任何资源。

架构采用 **JSON-RPC 2.0** 协议，每行一个对象。每个服务对应一个 Unix 套接字。

### 3.2 核心守护进程

| 守护进程     | 职责                                                         |
| :----------- | :----------------------------------------------------------- |
| **robotd**   | 唯一直接接触机器人的进程，负责 50 Hz 控制回路、安全层、15 个舵机 + IMU 的串口总线 |
| **configd**  | 网络配置、设备命名、游戏手柄配对（`net.*`、`pad.*`、`system.*`） |
| **updaterd** | 更新系统：验证、交换、健康门控                               |
| **btd**      | 蓝牙守护进程                                                 |
| **padd**     | 游戏手柄守护进程                                             |
| **mediad**   | 媒体服务                                                     |
| **robotctl** | 机器人控制命令行工具                                         |

robotd 是唯一能命令电机的进程，客户端发送意图（“以这个速度前进”、“看向那里”、“站起来”），由 robotd 内部的安全层决定哪些实际可执行。configd、updaterd 和 btd 三个守护进程具有独立性，即使 robotd 死亡也能存活。

### 3.3 控制回路

- 15 个舵机和 IMU 板共享一条串口总线
- 50 Hz 控制回路拥有该总线
- 安全层持续进行钳制（clamping）操作
- `robotctl monitor` 可查看客户端请求与实际应用之间的差异，以及限制原因

------

## 四、入门指南

### 4.1 获取机器人

在 Pollen Robotics 官网购买：https://pollen-robotics.com/microduck

### 4.2 快速上手

**首次运行：**

bash

```
robotctl version
```



查看每个守护进程运行版本与安装版本的对比，以及不一致时的警告。

**健康检查：**

bash

```
robotctl health
```



硬件和软件一体化报告。当机器人不健康或不可达时返回非零退出码，可用于脚本门控。`--json` 参数可生成支持包。

**监控循环：**

bash

```
robotctl monitor
```



查看客户端请求与实际应用之间的差异，以及差异原因。可显示每个关节的测量值与指令值对比、IMU 投影重力、跌倒判定和实际循环速率。

### 4.3 配置机器人

bash

```
sudo robotctl configure
```



通过 configd 设置机器人。

### 4.4 游戏手柄配对

游戏手柄配对**每个手柄只需一次**。配对模式的进入方式、配对流程以及配对失败时的处理方法详见文档。

------

## 五、开发资源

### 5.1 核心文档

| 文档                                                         | 内容                                                         |
| :----------------------------------------------------------- | :----------------------------------------------------------- |
| [Cheat sheet](https://github.com/pollen-robotics/microduck/blob/main/docs/robot/cheatsheet.md) | 所有 `robotctl` 命令：驱动、配置、语音、合唱、特雷门琴、Wi-Fi、更新、日志 |
| [duckctl.md](https://github.com/pollen-robotics/microduck/blob/main/docs/robot/duckctl.md) | 通过蓝牙从笔记本控制机器人，无需网络和 SSH                   |
| [architecture.md](https://github.com/pollen-robotics/microduck/blob/main/docs/design/architecture.md) | 整个系统架构：守护进程、总线、更新如何到达机器人             |
| [install-dev.md](https://github.com/pollen-robotics/microduck/blob/main/docs/robot/install-dev.md) | 从空白板子搭建开发环境                                       |
| [simulation.md](https://github.com/pollen-robotics/microduck/blob/main/docs/robot/simulation.md) | MuJoCo 仿真环境使用指南                                      |

### 5.2 开发板安装

开发板安装流程：

1. **刷写板子**：使用 [Armbian imager](https://www.armbian.com/radxa-zero-3/)，选择 Radxa Zero 3 + Armbian 26.2.1 Minimal
2. **准备**：板子 IP 地址、SSH 密钥访问、GitHub token、本仓库克隆
3. **安装**：

bash

```
export DUCK_TOKEN=github_pat_replace_with_your_token
./scripts/provision-board.sh --pause-btd-on-pair --name <name> radxa@192.168.1.42
```



该命令发送开发密钥、启动配置、等待重启、流式输出日志，最终运行 `robotctl health`

开发板信任团队开发密钥，因此可以安装团队构建的任何内容；客户机器人则特意拒绝这些构建。

### 5.3 duckctl（蓝牙控制）

`duckctl` 用于从笔记本电脑通过蓝牙 LE 与机器人通信，无需网络和 SSH，是手机 App 的替代方案。

bash

```
# 扫描机器人
duckctl scan

# 获取 IP 地址
duckctl ip

# SSH 连接
duckctl ssh

# Wi-Fi 状态
duckctl wifi status
```



------

## 六、策略与强化学习

### 6.1 microduck_rl 仓库

策略训练在 **microduck_rl** 仓库中进行，使用 **MuJoCo** 物理引擎和 **PPO** 算法，包含 sim2real 配方和导出 ONNX 的完整流程。

### 6.2 已发布策略

Pollen 于 2026 年 8 月 31 日将 9 个已发布的 ONNX 策略发布到 Hugging Face Hub 的 `microduck-policies` 仓库，采用 Apache-2.0 许可证，可独立于守护进程直接拉取。

| 策略            | 说明                                 |
| :-------------- | :----------------------------------- |
| Drive (rollers) | 四轮被动滑行的速度跟踪，最高速度更高 |
| Stand / Walk    | 站立与行走                           |
| Grasp           | 抓取                                 |
| Standup         | 跌倒恢复                             |
| Kick            | 踢球                                 |
| Sit             | 坐下                                 |
| ...             | 共 9 个官方策略                      |

### 6.3 策略接口

所有可热插拔的 Microduck 策略共享相同的接口：

- **61 维 actor 观测**：48 个本体感知值 + 13 维命令块
  - twist: 3 维（速度指令）
  - head_pose: 4 维（头部姿态）
  - body_pose: 6 维（身体姿态）

### 6.4 策略清单（Manifest）

`policy-manifest.md` 是 `manifest.json` 旁边 `microduck .onnx` 文件的契约，定义了所有字段。在 `microduck_rl` 中运行 `uv run publish` 可从检查点或 ONNX 文件写入符合规范的单一策略仓库。

`robotctl policy load <slot> <repo>` 和 `robotctl policy add <name> <repo>` 读取该清单。

### 6.5 自定义策略开发

参见 Seeed Studio Wiki 上的教程：

- [训练和运行官方 Microduck 动作](https://wiki.seeedstudio.com/)（西班牙语/葡萄牙语/日语）
- [创建自定义 Microduck 动作](https://wiki.seeedstudio.com/)

关键工作流：理解策略契约 → 选择最接近的模板 → 复制模板 → 设计动作时间线。

------

## 七、仿真与测试

### 7.1 MuJoCo 仿真

Microduck 提供完整的 MuJoCo 仿真环境，由真实的守护进程驱动——相同的 robotd、相同的策略、相同的 50 Hz 循环、相同的 robotctl、相同的控制台，仅身体不同。

**运行方式：**

bash

```
robotd --sim host:port
```



使用 `duck_control::sim::RemoteIo` 替代舵机总线：每个 tick，关节位置、速度和 IMU 数据通过 TCP 套接字从 MuJoCo 进程传入，策略的目标值传出。

**仿真内容：**

- 控制回路、策略、安全、跌倒检测、运动学、里程计、整个 IPC 接口——都是机器人运行的代码，未经修改
- `tofd --sim` 从同一模拟器获取 8×8 深度帧
- `mediad --sim-camera` 获取渲染的头部摄像头图像
- configd 和 updaterd 也运行，使仿真鸭子拥有序列号、名称和 Hugging Face 账户

**MuJoCo 端**位于 microduck_rl 的 `duck-body` 中：一个进程、一个窗口、一个场景中 N 个鸭子身体，使用策略训练时相同的 BAM 执行器模型。

**局限性：** 仿真无法告知驱动层面的问题——Dynamixel 总线、BLE 无线电、摄像头 ISP、NPU 和硬件编码器均未建模，这些方面的 bug 只能在真机上发现。

### 7.2 浏览器仿真

**Microduck Sandbox**（Hugging Face Spaces）：在浏览器中完全运行的真实训练 RL 策略。MuJoCo 编译为 WebAssembly 步进物理，onnxruntime-web 以 50 Hz 运行策略网络。

**相关项目：**

- [microduck-playground](https://github.com/Vottivott/microduck-playground)：可复现的 RL 实验、策略演示和可打印硬件扩展
- [microduck-lab](https://github.com/jonathanhawkins/microduck-lab)：在普通 Apple Silicon Mac 上（无 CUDA GPU）训练 RL 策略并在浏览器中实时观看

### 7.3 up vs boot

`scripts/duck-sim` 提供两种模式：

|                  | `up`                             | `boot N`                             |
| :--------------- | :------------------------------- | :----------------------------------- |
| 守护进程运行方式 | 普通进程（用户级，各有 pidfile） | systemd-nspawn 容器中的 systemd 服务 |
| 需求             | 仅需仓库和 microduck_rl          | sudo、一次性 Debian rootfs 构建      |
| 启动时间         | 秒级                             | 首次约 1 分钟，之后秒级              |

------

## 八、社区与生态

### 8.1 相关项目

| 项目                                                         | 说明                                                         |
| :----------------------------------------------------------- | :----------------------------------------------------------- |
| [microduck_rl](https://github.com/pollen-robotics/microduck_rl) | 策略训练仓库：MuJoCo、PPO、domain randomisation、ONNX 导出   |
| [microduck-policies](https://huggingface.co/pollen-robotics/microduck-policies) | Hugging Face Hub 上的 9 个已发布 ONNX 策略                   |
| [microduck-simulator](https://huggingface.co/spaces/pollen-robotics/microduck-simulator) | 浏览器中的 RL 沙盒                                           |
| [awesome-microduck](https://github.com/joeynyc/awesome-microduck) | 精选列表：软件、模拟器、策略、代理工具和报道                 |
| [microduck-mcp](https://glama.ai/)                           | MCP 服务器，让 AI 代理（Claude、ChatGPT、Cursor 等）驱动 Microduck |
| [microduck-cli](https://pypi.org/)                           | 统一 CLI 工具，任何代理和人类使用相同的动词                  |
| [microduck-tracking](https://github.com/AlexBodner/microduck-tracking) | 多目标跟踪，基于 roboflow/trackers                           |

### 8.2 社区资源

- **Seeed Studio Wiki**：提供西班牙语、葡萄牙语、日语等多语言教程，涵盖 Jetson 上的 RL 训练和自定义动作开发
- **EMQX 教程**：Microduck × Device Agent，为机器小鸭增加云端大脑
- **百度百科**：Microduck 词条

### 8.3 定价与销售

- 售价：399 美元（不含税和运费）， introductory price
- 预售 24 小时销售额：超过 260 万美元
- 预计发货时间：2026 年圣诞节

------

## 九、更新与维护

### 9.1 更新系统

每次更新都经过验证、健康门控且可回滚。

bash

```
# 应用更新
sudo robotctl update apply --ref <branch>

# 更新 daemon
sudo robotctl update apply --ref main daemon

# 暂存更新
sudo robotctl update apply --staging daemon
```



`robotctl update apply` 如果请求的版本板子已有，会报告 `already_current` 并安装任何内容——但它不再是惰性的。

### 9.2 策略清单发布流程

向官方策略集添加策略只需四步，无需发布守护进程：

1. 将 `.onnx` 上传到 `pollen-robotics/microduck-policies`
2. 添加 manifest 条目
3. 打标签：`hf repos tag create pollen-robotics/microduck-policies v4`
4. 机器人自动拉取

官方策略集中的一个策略可到达每一台机器人。

------

## 十、参考链接

| 资源          | 链接                                                         |
| :------------ | :----------------------------------------------------------- |
| GitHub 主仓库 | https://github.com/pollen-robotics/microduck                 |
| 策略训练仓库  | https://github.com/pollen-robotics/microduck_rl              |
| 产品页面      | https://pollen-robotics.com/microduck                        |
| 官方策略      | https://huggingface.co/pollen-robotics/microduck-policies    |
| 浏览器沙盒    | https://huggingface.co/spaces/pollen-robotics/microduck-simulator |
| Cheat Sheet   | [docs/robot/cheatsheet.md](https://github.com/pollen-robotics/microduck/blob/main/docs/robot/cheatsheet.md) |
| 架构文档      | [docs/design/architecture.md](https://github.com/pollen-robotics/microduck/blob/main/docs/design/architecture.md) |
| 贡献指南      | [CONTRIBUTING.md](https://github.com/pollen-robotics/microduck/blob/main/CONTRIBUTING.md) |