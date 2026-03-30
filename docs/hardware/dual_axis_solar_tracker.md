# Dual-Axis Solar Tracker System (STM32-Based)

## Overview

This document describes the complete hardware architecture of a dual-axis solar tracking system.

The system is divided into three main subsystems:

1. Light Sensing (LDR)
2. Energy System (Solar + Battery)
3. Motor Control (PWM + Driver)

---

# 1. Light Sensor (LDR) Subsystem

## Components

- LDR (Photoresistor) ×4
- Resistor: 10kΩ
- Capacitor: 0.01µF (optional)

## Circuit (Voltage Divider)

3.3V
  |
 [LDR]
  |
  +-----> STM32 ADC
  |
 [10kΩ]
  |
 GND

## STM32 Connection

| Sensor | STM32 Pin |
|--------|-----------|
| LDR1 | PA0 |
| LDR2 | PA1 |
| LDR3 | PA2 |
| LDR4 | PA3 |

## Function

error_x = left - right  
error_y = up - down  

---

# 2. Energy System (Solar + Battery)

## Recommended Hardware

- Solar Panel: 5V–6V small panel
- INA219 Current Sensor ×2
- Buck Converter: LM2596 or TPS5430
- Charging Module: TP4056
- Battery: 18650 Li-ion
- Boost Converter: MT3608 (3.7V → 5V)

---

## 2.1 Solar Measurement Path

Solar + → INA219_1 VIN+ → VIN- → Buck Converter  
Solar - → GND  

---

## 2.2 Voltage Regulation

Solar → Buck Converter → Stable 5V  

---

## 2.3 Charging Path (Safe Design)

Buck Output (5V) → TP4056 → Battery  

⚠️ Never connect solar panel directly to battery.

---

## 2.4 Load Measurement Path

Battery + → INA219_2 → Boost Converter → System  
Battery - → GND  

---

## 2.5 I2C Connection (INA219)

STM32 PB7 (SDA) → INA219_1, INA219_2  
STM32 PB6 (SCL) → INA219_1, INA219_2  

Addresses:  
- INA219_1: 0x40  
- INA219_2: 0x41  

---

# 3. Motor Control Subsystem

## Components

- Motor Driver: TB6612FNG  
- DC Geared Motors ×2  

---

## 3.1 Control Signals

- PWM → Speed  
- IN1 / IN2 → Direction  

---

## 3.2 STM32 Connection

Motor A (Yaw):  
PWMA → PA8  
AIN1 → PB0  
AIN2 → PB1  

Motor B (Pitch):  
PWMB → PA9  
BIN1 → PB10  
BIN2 → PB11  

---

## 3.3 Power Connection

Battery / 5V → TB6612 VM  
STM32 3.3V → TB6612 VCC  
GND → Common Ground  

⚠️ Motor is NOT powered by STM32.

---

## 3.4 Direction Logic

| IN1 | IN2 | Result |
|-----|-----|--------|
| 1 | 0 | Forward |
| 0 | 1 | Reverse |
| 0 | 0 | Stop |
| 1 | 1 | Brake |

---

# 4. Full System Architecture

Solar Panel → INA219 → Buck → Charger → Battery → INA219 → Boost → STM32 + Motor Driver → Motors

---

# 5. Safety Rules

❌ Solar → Battery (direct)  
❌ STM32 → Motor  

✅ Use charging module  
✅ Use voltage regulation  
✅ Common ground  

---

# 6. Core Logic

Net Energy = Solar Power - System Consumption

---

# End
