# Rubric Mapping

## Introduction

- Problem statement: explain why always-on solar tracking wastes energy in weak or changing light
- Solution overview: Raspberry Pi plus STM32 architecture with a formal RL pipeline and dual-axis panel motion
- Visual aid: show the tracked PV node in a microgrid-like use case
- High-level requirements: three measurable system goals

## Design

- Whole-system block diagram
- Subsystem descriptions: online inference, embedded control, sensing, actuation, power, display
- Subsystem requirements and verification tables
- Supporting figures: block diagram, sensor front end, power path, protocol flow, mechanical tracker, training and deployment loop
- Tolerance analysis: show angle error or measurement error impact on net power gain

## Cost and Schedule

- Itemized BOM within 1500 RMB
- Weekly/member schedule

## Ethics and Safety

- Battery, rotating mechanism, and electrical safety
- Honest presentation of energy-saving claims
- Honest presentation of what the RL model sees online versus what is only used in training and evaluation
- Reference IEEE Code of Ethics and relevant safety practices
