# RL 文档说明

这个目录记录本项目中强化学习部分的当前设计口径，供组内协作和 GitHub 阅读使用。

## 这个目录回答什么问题

- 树莓派、STM32、PC/云端在 RL pipeline 中分别负责什么
- 现场 inference 的输入、输出和闭环流程是什么
- 离线训练、日志采集和模型部署怎么衔接
- 模型输入输出、两阶段 reward 和通信数据各自包含哪些内容
- `STM32` 需要维护哪些内部状态，尤其是 `energy_reserve`

## 阅读顺序

- [RL 总览](./RL-overview.md)
- [模型输入输出与奖励定义](./data-loader.md)
- [通信与日志](./communication-and-logging.md)
- [STM32 接口要求](./stm32-interface-requirements.md)

## 当前统一口径

- inference 输入固定为：
  - 一圈光照传感器的当前光强
  - 当前两个步进电机角度
  - 当前归一化能量预算 `energy_reserve`
- 这里的当前角度定义为 `STM32` 已接受的上一步目标角度
- 当前 light ring 方案固定为 `BH1750 + mux + 16-sensor ring`
- inference 输出只包含下一步两个步进电机的目标角度
- 树莓派负责现场 inference、日志整理和模型加载
- STM32 负责底层采样、执行、状态回传、安全保护，以及根据 `panel - motor - idle` 维护 `energy_reserve`
- PC 或云端负责离线训练，训练完成后导出 `ONNX` 模型并重新部署到树莓派
- `INA219` 原始电压电流读数不进入 inference 输入，也不作为 reward 或训练日志的直接字段
- 与 RL 相关的能量量统一由 `STM32` 先算好，再上传 `panel_power`、`motor_power` 和 `energy_reserve` 这类派生量
- 训练分为两阶段：
  - 第一阶段先学会追 `panel power`
  - 第二阶段再学会判断值不值得转，以及在低 `energy_reserve` 时更保守

