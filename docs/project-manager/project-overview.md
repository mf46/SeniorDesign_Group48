# Project Overview

## Problem

Small-scale photovoltaic systems lose efficiency when fixed panels are not aligned with the sun. A naive active tracker can also waste more energy moving motors than it gains in extra generation, especially under clouds or weak light.

## Solution

The team is building an intelligent solar tracking controller that decides when tracking is worth the energy cost. The system combines:

- An `STM32F407ZGT6` for real-time sensing, execution, telemetry, and safety
- A Raspberry Pi for online inference, logging, and model loading
- `PC/云端` offline training for policy updates
- Light sensing and power sensing for decision making and reward analysis
- Motor actuation for a dual-axis tracking mechanism
- OLED feedback for user-visible status

## Core Idea

The main objective is net energy gain, not just positional tracking. In the current RL pipeline, the online model reads the current light-ring intensity and the current two-axis angle, then predicts the next target angles for the two axes. The lower-level execution and safety checks remain on the `STM32`.

## Success Criteria

- One-button autonomous start with no external computer required after launch
- Accurate tracking under normal lighting conditions
- Avoidance of negative net energy gain in low-light or rapidly changing conditions
- A stable online pipeline from `STM32` state upload to Raspberry Pi inference to target-angle command return
- Live OLED display of key metrics such as voltage, current, and operating state

## Constraints

- Fixed microcontroller choice: `STM32F407ZGT6`
- Budget ceiling: `1500 RMB`
- One-semester build timeline
- Must remain feasible as a hardware-heavy senior design project
