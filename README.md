# 🌌 GodHand: AI-Powered Particle Symphony
# 神之手：AI 手势控制粒子系统

> 一个基于 Python、OpenCV 和 MediaPipe 的沉浸式交互粒子模拟器。伸出你的手，掌控星系。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand_Tracking-orange)
![Pygame](https://img.shields.io/badge/Pygame-Rendering-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 📖 简介 (Introduction)

**GodHand** 是一个将计算机视觉与物理引擎结合的互动艺术项目。它利用 Google MediaPipe 实时捕捉手部关键点，并通过 Pygame 渲染数千个高帧率粒子。

你可以通过简单的手势（握拳、张开、双手互动）来控制引力场、斥力场和漩涡，体验如同“奇异博士”般的魔法操控感。

## ✨ 核心功能 (Features)

*   **🖐️ 实时手势追踪**：基于 MediaPipe 的高精度手部识别，支持单手/双手模式。
*   **⚛️ 混合物理引擎**：
    *   **神之手模式**：握拳触发黑洞引力与吸积盘漩涡，张手触发反重力斥力。
    *   **视觉拉伸 (Warp Speed)**：粒子根据速度动态拉伸，产生光速跃迁的视觉冲击。
    *   **双星系统**：双手同时操作时，粒子受双重引力场争夺，并在两手之间产生高能闪电。
*   **🎨 多模式切换**：
    *   `Mode 0`: 自由物理模式。
    *   `Mode 1`: 粒子汇聚成爱心形状。
    *   `Mode 2`: 粒子汇聚成文字 (MAGIC)。

## 🛠️ 安装与运行 (Installation)

1.  **克隆仓库**

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```
    *(主要依赖: opencv-python, mediapipe, pygame)*

3.  **运行魔法**
    ```bash
    python main.py
    ```

## 🎮 操作指南 (Controls)

| 按键/手势 | 功能描述 |
| :--- | :--- |
| **✊ 握拳 (Fist)** | **黑洞模式**：强力吸附粒子并产生高速漩涡。 |
| **✋ 张手 (Open)** | **白洞模式**：释放斥力，将粒子推开。 |
| **双手靠近** | 产生闪电连接，形成复杂的双引力场。 |
| **按键 `0`** | 切换回 **自由物理模式** (默认)。 |
| **按键 `1`** | 切换到 **爱心形状模式**。 |
| **按键 `2`** | 切换到 **文字形状模式**。 |
| **空格键 (Space)** | **大爆炸**：重置并炸散所有粒子。 |

## 📂 项目结构

```text
GodHand/
├── main.py            # 主程序代码
├── requirements.txt   # 依赖库列表
└── README.md          # 项目说明文档