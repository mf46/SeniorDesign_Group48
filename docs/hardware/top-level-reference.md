# Top-Level Hardware Reference

This note captures the durable design intent currently sketched in [`TopLevel.txt`](/home/fangminghao/SeniorDesign_Group48/TopLevel.txt). Treat this page as the `docs/` version of that top-level source so later hardware and design-document updates do not depend on an orphan text diagram.

## Original Source Intent

The original top-level sketch establishes the following system chain:

1. A small solar panel under test feeds an `INA219`-instrumented measurement path and then a dummy load to ground.
2. An external `5V` logic supply powers the Raspberry Pi, the `STM32`, and the OLED-side logic.
3. The Raspberry Pi exchanges data with the `STM32` over `UART`.
4. The `STM32` drives two `A4988` stages, each connected to a `NEMA17` stepper motor.
5. A second `INA219` monitors the externally powered motor branch.
6. An `I2C` splitter or mux fans the sensor bus out to the light-sensing subsystem.
7. The light-sensing plan is a `BH1750` ring, with `16` sensors as the intended final direction-sensing layout.
8. A `60W 12V 5A` adapter, fed from `220V` mains, powers the motor branch.
9. Model training happens on a PC or cloud node, while the Raspberry Pi handles deployed inference.

## Explicit Hardware Details Preserved From TopLevel.txt

### Panel-under-test note

- The top-level sketch names the panel as a `6V 100mA 80x55 mm` polycrystalline solar panel.
- Keep this as the current placeholder panel assumption unless the purchased panel changes.
- If the exact purchased panel differs, update this page, the BOM note, and the design document together.

### Panel measurement path

- The panel is treated as a source under test, not as the system power rail.
- `INA219_1` sits on the panel branch.
- The panel output is terminated into a dummy load, described in the sketch as `resistor/MOS`.
- This path exists specifically so generated panel power can be measured independently from controller power consumption.

### Logic-side control path

- The Raspberry Pi sits above the `STM32` in the control stack.
- `UART` is the intended Pi-to-STM32 runtime link.
- The OLED is part of the local STM32-side interface path.
- The logic-side supply is a dedicated external `5V` branch rather than panel-derived power.

### Motor and actuation path

- The STM32 outputs control signals to two `A4988` driver stages.
- Two `NEMA17` motors implement the dual-axis motion subsystem.
- `INA219_2` monitors the motor-power branch so actuation energy can be compared with panel output.

### Light-sensing path

- The sketch explicitly calls out an `I2C` branching module between the STM32-side logic and the light sensors.
- The intended final sensing geometry is a `BH1750` ring with `16` sensors.
- In the more precise architecture notes, interpret the "I2C splitter" wording as the bus-expansion stage that makes the repeated-address `BH1750` ring practical, likely via an `I2C` mux.

### External power path

- The motor branch is powered from a `60W 12V 5A` adapter.
- That adapter is fed from `220V` mains.
- The top-level power story is therefore:
  - mains `220V AC` -> external `12V` adapter -> motor branch
  - separate external `5V` supply -> Raspberry Pi and STM32 logic branch

## Normalized Interpretation Used Elsewhere In Docs

Use this normalized wording when updating other notes or `design_document.tex`:

- "The project uses separate external `12V` and `5V` supplies."
- "The solar panel is a measured source under test and does not power the controller."
- "The `STM32` is the lower-level real-time controller; the Raspberry Pi is the online inference and logging node."
- "A `BH1750 + I2C mux + 16-sensor ring` provides directional sensing."
- "Two `INA219` channels instrument the panel path and the motor branch for net-energy accounting."

## Follow-On Update Rules

- Update this note first if the top-level wiring concept changes.
- Then propagate the change into:
  - [`system-architecture.md`](/home/fangminghao/SeniorDesign_Group48/docs/hardware/system-architecture.md)
  - [`interfaces-and-protocols.md`](/home/fangminghao/SeniorDesign_Group48/docs/hardware/interfaces-and-protocols.md)
  - [`bom-and-budget.md`](/home/fangminghao/SeniorDesign_Group48/docs/hardware/bom-and-budget.md)
  - [`figure-plan.md`](/home/fangminghao/SeniorDesign_Group48/docs/design-doc/figure-plan.md)
