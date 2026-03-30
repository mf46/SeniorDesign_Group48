# Project Overview

## Problem

Small-scale photovoltaic systems lose efficiency when fixed panels are not aligned with the sun. A naive active tracker can also waste more energy moving motors than it gains in extra generation, especially under clouds or weak light.

## Solution

The team is building an intelligent solar tracking controller that decides when tracking is worth the energy cost. The system combines:

- A Raspberry Pi for higher-level optimization
- An STM32F407ZGT6 for real-time control
- Light sensing and power sensing for decision making
- Motor actuation for a dual-axis tracking mechanism
- OLED feedback for user-visible status

## Core Idea

The main objective is net energy gain, not just positional tracking. The controller should compare expected generation gain against motor energy cost and choose whether to move, how far to move, and when to wait.

## Success Criteria

- One-button autonomous start with no external computer required after launch
- Accurate tracking under normal lighting conditions
- Avoidance of negative net energy gain in low-light or rapidly changing conditions
- Live OLED display of key metrics such as voltage, current, and operating state

## Constraints

- Fixed microcontroller choice: STM32F407ZGT6
- Budget ceiling: 1500 RMB
- One-semester build timeline
- Must remain feasible as a hardware-heavy senior design project
