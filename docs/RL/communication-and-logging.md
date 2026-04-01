# 通信与日志

这份文档说明 `STM32`、树莓派和 `PC/云端` 之间在当前 RL pipeline 中交换哪些数据。

## 一句话原则

训练时可见的量多于 inference 时可见的量。

也就是说，现场推理只用最小输入集合，但日志会额外保留 reward、评估和安全相关信息。

## STM32 -> Raspberry Pi

`STM32` 发给树莓派的推理输入包应至少包含：

- 时间戳
- 一圈光照传感器读数 `light_ring = [R1..Rn]`
- 当前两个步进电机角度 `current_angle = [theta1, theta2]`

这部分数据构成模型 inference 的直接输入。

## Raspberry Pi -> STM32

树莓派发给 `STM32` 的控制输出包应至少包含：

- 下一步两个步进电机目标角度 `target_angle = [target_theta1, target_theta2]`

收到目标角度后，`STM32` 负责完成：

- 本地执行
- 限位与越界检查
- 超时处理
- 执行结果回传

## 训练日志

为了支持离线训练和策略评估，树莓派保存的日志应同时包含：

- `state`
- `action`
- `reward`
- `next_state`
- `done`

此外，日志中还应保留以下附加字段：

- 电压
- 电流
- 功耗估计
- 剩余电量估计
- 安全状态或错误码

这些附加字段不进入 inference 输入，但用于：

- reward 计算
- 训练后分析
- 安全性回溯

## 模型更新链路

当前模型更新链路如下：

1. 树莓派在现场采集日志。
2. 日志同步到 `PC` 或云端。
3. 在 `PyTorch` 中完成离线训练。
4. 导出 `ONNX` 模型。
5. 将模型重新部署到树莓派。
6. 树莓派使用 `ONNX Runtime` 执行新模型的现场 inference。
