# STM32 Interface Requirements

这份文档面向 `STM32` 侧实现，说明当前 RL pipeline 对下位机提出的接口、状态维护、数据格式和执行逻辑要求。

目标不是描述所有硬件细节，而是把 `STM32 <-> Raspberry Pi` 的边界写清楚，让训练、推理和执行三部分可以稳定对接。

## STM32 在当前系统中的角色

在当前统一架构下：

- `STM32` 负责传感器采样、串口通信、目标角度执行和安全保护
- 树莓派负责加载 `ONNX` 模型并执行在线 inference
- `PC/云端` 负责离线训练

因此，`STM32` 不负责训练，也不负责运行反向传播。  
它在 RL pipeline 中的职责是：

- 周期性采样 `BH1750 + mux + 16-sensor ring`
- 维护当前两轴角度状态
- 读取两个 `INA219` 并在本地计算单标量 `energy_reserve`
- 在本地计算 `panel_power`、`motor_power` 和 `idle_power_model`
- 把模型需要的最小在线状态发给树莓派
- 接收树莓派返回的下一步目标角度
- 在本地执行角度命令并做限位、超时和故障处理
- 将执行结果和附加遥测量回传给树莓派用于日志记录

## 模型输入边界

当前模型在线 inference 的输入固定为：

- `light_ring[16]`
- `current_angle[2]`
- `energy_reserve[1]`

对应含义如下：

| 字段 | 长度 | 含义 |
|---|---:|---|
| `light_ring` | `16` | 一圈 `BH1750` 光照读数，顺序必须固定 |
| `current_angle` | `2` | 当前 `yaw` 和 `pitch` 角度 |
| `energy_reserve` | `1` | 当前归一化剩余能量预算，范围 `[0,1]` |

其中：

- `current_angle` 不是编码器实测角度
- 它定义为 `STM32` 上一轮已经接受并执行的目标角度
- `energy_reserve` 不是传感器直接输出值
- 它由 `STM32` 根据功率和时间积分估算得到

模型不直接读取以下量：

- `panel_voltage`
- `panel_current`
- `motor_voltage`
- `motor_current`
- 任何 `INA219` 原始寄存器值

这些量只属于 `STM32` 内部计算层，不属于模型在线输入层，也不应作为 RL 训练日志的直接字段。

## STM32 必须维护的内部状态

为了满足当前训练和部署边界，`STM32` 至少要维护以下内部变量：

- `current_yaw_deg`
- `current_pitch_deg`
- `energy_reserve`
- `last_seq_rx`
- `last_state_tx_ms`
- `last_target_rx_ms`
- `homing_done`
- `fault_active`

其中最关键的是：

- `current_yaw_deg/current_pitch_deg`
- `energy_reserve`

它们共同构成树莓派模型下轮 inference 的在线状态来源。

## STM32 需要完成的能量计算

`STM32` 读取两个 `INA219` 后，不把原始值发给模型，而是在本地先算：

- `panel_power`
- `motor_power`
- `idle_power_model`
- `delta_energy = (panel_power - motor_power - idle_power_model) * dt`
- `energy_reserve_{t+1} = energy_reserve_t + delta_energy`

然后再把 `energy_reserve` 归一化到 `[0,1]`。

当前要求是：

- `energy_reserve` 必须由 `STM32` 本地维护
- 必须定义 reserve 的更新公式
- 必须定义 reserve 的归一化范围和初始值
- `state_frame` 上传的是 `energy_reserve`，不是 `INA219` 原始值
- `telemetry_frame` 和日志层只上传已经算好的派生量，不上传原始电压电流

推荐更新规则：

`energy_reserve_{t+1} = energy_reserve_t + (panel_power - motor_power - idle_power_model) * dt`

其中：

- `panel_power` 来自太阳能板测试支路
- `motor_power` 来自电机支路
- `idle_power_model` 是系统基础静态功耗模型
- `dt` 是当前控制周期长度

## 树莓派输出给 STM32 的控制语义

树莓派输出给 `STM32` 的模型结果固定为：

- `target_angle[2] = [target_yaw_deg, target_pitch_deg]`

语义是：

- 这是“下一步目标角度”
- 不是“增量角度”
- 不是“转多少步”
- 不是“速度命令”

如果模型希望本轮不移动，则树莓派直接发送：

- `target_angle = current_angle`

因此，`STM32` 端收到命令后必须按“绝对目标角度”解释，而不是按“相对转动量”解释。

## STM32 必须完成的处理逻辑

`STM32` 在接收到树莓派输出后，应按以下顺序处理：

1. 校验串口帧是否完整且校验通过
2. 校验消息类型是否正确
3. 校验 `target_yaw_deg` 和 `target_pitch_deg` 是否为有限数值
4. 校验目标角度是否落在允许机械范围内
5. 如有必要，对单次动作幅度做限幅
6. 将命令转换为步进电机执行目标
7. 如果命令被接受，则更新本地 `current_angle`
8. 将执行结果、故障状态和附加遥测量发送给树莓派

## 推荐的 UART 协议

推荐使用二进制定长/变长混合帧。

### 串口参数

- 波特率：`115200`
- 数据位：`8`
- 校验位：`None`
- 停止位：`1`
- 字节序：`little-endian`

### 推荐帧结构

| 字段 | 类型 | 字节数 | 说明 |
|---|---|---:|---|
| `sof` | `uint16` | `2` | 固定帧头，推荐 `0xAA55` |
| `version` | `uint8` | `1` | 协议版本，当前固定 `1` |
| `msg_type` | `uint8` | `1` | 消息类型 |
| `payload_len` | `uint16` | `2` | payload 字节长度 |
| `seq` | `uint16` | `2` | 帧序号 |
| `payload` | `bytes` | `N` | 负载 |
| `crc16` | `uint16` | `2` | 对前面字段做 CRC16 |

### 消息类型

| `msg_type` | 方向 | 用途 |
|---:|---|---|
| `0x01` | `STM32 -> Pi` | 在线状态上传 `state_frame` |
| `0x02` | `Pi -> STM32` | 目标角度命令 `target_frame` |
| `0x03` | `STM32 -> Pi` | 遥测与执行结果 `telemetry_frame` |
| `0x04` | `STM32 -> Pi` | 错误或故障状态 `fault_frame` |

## STM32 -> Pi 的在线状态格式

这一帧直接构成树莓派模型的在线输入。

### `state_frame` payload

推荐字段顺序如下：

| 顺序 | 字段 | 类型 | 说明 |
|---:|---|---|---|
| `1` | `timestamp_ms` | `uint32` | 本地毫秒时间戳 |
| `2` | `light_ring[16]` | `float32 x 16` | `BH1750` 光强值 |
| `3` | `current_yaw_deg` | `float32` | 当前 accepted yaw target |
| `4` | `current_pitch_deg` | `float32` | 当前 accepted pitch target |
| `5` | `energy_reserve` | `float32` | 当前归一化剩余能量预算 |

总 payload 大小：

- `4 + 16*4 + 4 + 4 + 4 = 80 bytes`

要求说明：

- `light_ring[16]` 的顺序必须固定
- `yaw`、`pitch` 顺序必须固定
- 角度单位统一用 `deg`
- `energy_reserve` 范围固定为 `[0,1]`

## Pi -> STM32 的目标角度格式

### `target_frame` payload

推荐字段顺序如下：

| 顺序 | 字段 | 类型 | 说明 |
|---:|---|---|---|
| `1` | `timestamp_ms` | `uint32` | 树莓派生成该动作时的时间戳 |
| `2` | `target_yaw_deg` | `float32` | 下一步目标 yaw 角度 |
| `3` | `target_pitch_deg` | `float32` | 下一步目标 pitch 角度 |

总 payload 大小：

- `4 + 4 + 4 = 12 bytes`

## STM32 -> Pi 的执行结果与日志支持格式

虽然这些量不进入模型在线输入，但树莓派需要它们做日志、reward 和调试。

### `telemetry_frame` payload

推荐字段顺序如下：

| 顺序 | 字段 | 类型 | 说明 |
|---:|---|---|---|
| `1` | `timestamp_ms` | `uint32` | 本地毫秒时间戳 |
| `2` | `accepted_yaw_deg` | `float32` | `STM32` 最终接受并执行的 yaw |
| `3` | `accepted_pitch_deg` | `float32` | `STM32` 最终接受并执行的 pitch |
| `4` | `panel_power` | `float32` | `STM32` 计算后的太阳能板功率 |
| `5` | `motor_power` | `float32` | `STM32` 计算后的电机功率 |
| `6` | `idle_power_model` | `float32` | `STM32` 使用的静态功耗模型值 |
| `7` | `energy_reserve` | `float32` | 当前归一化剩余能量预算 |
| `8` | `status_flags` | `uint16` | 系统状态位 |
| `9` | `error_code` | `uint16` | 错误码 |

当前 RL 口径下，原始电压电流不作为训练日志字段保存。  
RL 相关日志只保留 `STM32` 已经算好的 `panel_power`、`motor_power`、`idle_power_model` 和 `energy_reserve`。

## 推荐的在线闭环时序

当前建议的控制周期是 `10 Hz`，即每 `100 ms` 一轮。

每一轮建议流程如下：

1. `STM32` 完成一轮 `BH1750 + mux` 采样
2. `STM32` 读取当前 accepted target 作为 `current_angle`
3. `STM32` 根据 `panel - motor - idle` 更新 `energy_reserve`
4. `STM32` 打包并发送 `state_frame`
5. 树莓派执行 `ONNX Runtime` inference
6. 树莓派返回 `target_frame`
7. `STM32` 校验并执行
8. `STM32` 发送 `telemetry_frame`

## STM32 实现时的固定约束

- 不要把 `current_angle` 改成增量或步数语义
- 不要把树莓派输出解释为速度指令
- 不要把 `INA219` 原始量直接混进模型输入帧
- 不要改变 `light_ring[16]` 的排列顺序
- 不要在未完成 homing 的情况下开始正常 RL 闭环

## 当前推荐结论

当前这版系统中，`STM32` 侧最重要的接口要求可以压缩成五句话：

1. 发送给树莓派的在线输入是 `light_ring[16] + current_angle[2] + energy_reserve[1]`
2. 树莓派返回给 `STM32` 的只有绝对目标角度 `target_angle[2]`
3. `current_angle` 由 `STM32` 本地维护，定义为上一轮已接受目标角度
4. `energy_reserve` 由 `STM32` 根据 `panel - motor - idle` 计算并归一化
5. 所有安全检查、限位处理、超时处理和最终执行都由 `STM32` 负责
