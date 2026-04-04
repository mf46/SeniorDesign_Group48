# 模型输入输出与奖励定义

这份文档说明当前 RL 模型在训练和推理时分别使用哪些量，以及 reward 的基本设计思路。

## 模型输入输出

### inference 输入

模型在现场 inference 时接收三类输入：

- 一圈光照传感器的当前光强 `light_ring = [R1..Rn]`
- 当前两个步进电机角度 `current_angle = [theta1, theta2]`
- 当前归一化能量预算 `energy_reserve`

这里的 `current_angle` 定义为上一轮 inference 输出、并被 `STM32` 接受执行的目标角度。当前版本中，它不是来自独立角度传感器。

这里的输入是当前时刻的在线状态，不包含 `INA219` 原始电压电流读数。  
和能量相关的在线输入只有一个由 `STM32` 计算好的标量：`energy_reserve`。

### inference 输出

模型输出为下一步两个步进电机的目标角度：

- `target_angle = [target_theta1, target_theta2]`

树莓派输出这个目标角度后，由 `STM32` 负责执行、限位检查和状态回传。

如果模型判断当前不需要移动，则直接输出：

- `target_angle = current_angle`

## 训练样本定义

离线训练时，基础样本形式仍然统一为：

- `(state, action, reward, next_state, done)`

其中：

- `state` 和 `next_state` 的推理输入结构一致，包含光照环、当前角度和 `energy_reserve`
- `action` 是模型给出的下一步目标角度
- `reward` 根据训练日志中的附加信息计算
- `done` 表示当前回合是否结束

当前统一输入维度为：

- `obs.shape = (19,)`
- 顺序固定为 `light_ring[16] + current_angle[2] + energy_reserve[1]`

## reward 设计思路

当前 reward 采用两阶段训练设计。目标不是一开始就同时学会“追光”和“省电”，而是先学会找到高发电位置，再学会判断值不值得移动。

### reward 使用的附加信息

以下量不进入 inference 输入，但会保留在训练日志中，用于 reward 计算、离线评估和安全约束：

- `panel_power`
- `motor_power`
- `idle_energy` 或等效静态功耗模型
- 安全错误码或状态标志

当前统一要求是：

- reward 不直接读取 `INA219` 原始值
- 树莓派 RL 日志也不保存 `INA219` 原始电压电流
- 与 RL 相关的能量字段由 `STM32` 先算好，再上传给树莓派

### 第一阶段：纯追 `panel power`

第一阶段的目标是先让模型学会把面板转到发电功率更高的位置。

这一阶段的 reward 只关注：

1. 当前时刻的太阳能板输出功率 `panel power`
2. 相邻时刻之间的发电增量 `panel power delta`
3. 安全违规或故障状态对应的 `fault penalty`

这一阶段暂时不强调：

- 电机功耗
- 动作幅度
- hold 奖励

第一阶段训练完成后，保存一个纯追光 checkpoint，并由人工评估其效果是否满意。

### 第二阶段：在第一阶段基础上引入功耗

第二阶段不是重新训练一个新模型，而是从第一阶段 checkpoint 继续微调。

这一阶段在追 `panel power` 的基础上，再引入：

1. 基于短时间窗的净收益差
2. 生存相关的 `energy_reserve`
3. hold 奖励
4. 安全违规惩罚

第二阶段的目标是让模型学会：

- 是否值得移动
- 如果值得移动，转到哪里性价比更高
- 如果不值得移动，直接输出 `target_angle = current_angle`
- 在低 `energy_reserve` 时更保守，在高 `energy_reserve` 时可以更积极

当前第二阶段 reward 的核心判据是：

- 在一个短时间窗内，执行动作方案和保持不动方案相比，谁的净收益更高

其中净收益按以下思路计算：

- `net_gain = panel_energy - motor_energy - idle_energy`

当前推荐的第二阶段判据可以写成：

- `delta_net_gain_H = net_gain(move, H) - net_gain(hold, H)`

其中：

- `H` 是一个短时间窗
- `move` 表示执行本步动作后的方案
- `hold` 表示保持 `current_angle` 不动的方案

这样做的原因是：

- 模型学到的不是“转了以后赚了多少”
- 而是“和不转相比，这一下到底值不值”

当前模型不直接读取 `INA219` 原始值，而是只读取 `STM32` 计算好的 `energy_reserve`。  
reward 也只使用 `STM32` 已经算好的 `panel_power`、`motor_power` 和 `energy_reserve`，而不是让树莓派再从原始电压电流重算。

### `energy_reserve` 的意义

`energy_reserve` 是当前系统能量预算的单标量抽象。

它由 `STM32` 在本地根据下式维护：

- `energy_reserve_{t+1} = energy_reserve_t + (panel_power - motor_power - idle_power_model) * dt`

然后再归一化到 `[0,1]`。

这意味着：

- 模型在线时不需要读一堆原始功率测量
- 但仍然可以基于当前能量预算做“更激进”或“更保守”的决策
- reward 和日志也可以围绕已经算好的派生量保持统一

### 阶段切换方式

当前阶段切换方式固定为：

1. 先完成第一阶段训练
2. 保存第一阶段 checkpoint
3. 由人工评估该 checkpoint 的追光效果
4. 只有在确认满意后，才切换到第二阶段继续训练

## 设计边界

当前文档明确区分两件事：

- inference 输入只使用光照环、当前角度和单标量 `energy_reserve`
- 训练与评估阶段允许使用更多附加量来定义 reward 和分析策略表现

这样做的好处是：

- 现场推理输入简单，接口清晰
- reward 仍然可以结合能量和安全信息
- 模型输入定义不会因为训练评估字段增加而频繁变化
