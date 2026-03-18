# 交通路况智能分析项目

基于深度学习的车载视频智能分析平台，集成了目标检测、目标跟踪和路况识别功能。

## 项目简介

本项目是一个完整的交通路况智能分析系统，通过车载视频自动识别车辆、跟踪车辆轨迹，并智能判断道路拥堵状态。系统采用前后端分离架构，前端使用Vue 3构建现代化用户界面，后端使用Python Flask提供API服务，核心算法基于百度飞桨PaddlePaddle深度学习框架。

### 核心功能

- 🎬 **多格式视频上传**：支持MP4、AVI、MOV等常见视频格式
- 🤖 **AI智能识别**：集成目标检测与跟踪算法，自动完成道路中车辆的识别与轨迹追踪
- 📊 **多维度车流量统计**：支持车辆总数、唯一ID车辆数、道路平均车辆密度等指标统计
- 🚦 **智能路况判断**：基于检测结果自动判定道路为畅通/缓行/拥堵三类状态
- 📈 **可视化结果展示**：提供带检测标注的视频回放、车流量/路况统计图表展示
- ⚡ **一键化运行**：配套自动化脚本，实现系统一键启动，降低使用门槛

## 技术栈

### 前端
- **Vue 3**：渐进式JavaScript框架
- **Vite**：新一代前端构建工具
- **ECharts**：数据可视化图表库
- **IconPark**：字节跳动开源的图标库

### 后端
- **Python 3.8**：主要编程语言
- **Flask**：轻量级Web框架
- **OpenCV**：计算机视觉库
- **PaddlePaddle 3.0.0/3.3.0 (GPU)**：百度飞桨深度学习框架

### AI算法
- **ResNet50**：路况识别模型
- **YOLOv8n**：轻量级车辆检测模型
- **PPYOLOE-L + ByteTrack**：高精度目标检测与跟踪
- **AdamW优化器**：模型训练优化
- **Warmup+CosineAnnealing学习率**：学习率调度策略
- **混合精度训练**：提升训练效率

### 部署环境
- **Conda + venv**：环境隔离与依赖管理

## 项目结构

```
pythonProject/
├── frontend/              # 前端项目
│   ├── public/           # 静态资源
│   │   └── video-demo/ # 演示视频
│   ├── src/             # 源代码
│   │   ├── views/       # 页面组件
│   │   ├── App.vue     # 根组件
│   │   ├── main.js     # 入口文件
│   │   └── router.js   # 路由配置
│   └── package.json    # 前端依赖
├── PaddleDetection/     # 飞桨检测框架（子模块）
├── video-demo/         # 测试视频
├── app.py             # 后端主程序
├── config.json        # 配置文件
├── requirements.txt    # Python依赖
├── start.bat         # 一键启动脚本
└── README.md         # 项目说明
```

## 快速开始

### 环境要求

- **Python**：3.8 或更高版本
- **Node.js**：16.x 或更高版本
- **GPU**：NVIDIA GPU（推荐，CPU模式也可运行但速度较慢）
- **CUDA**：11.2 或更高版本（GPU模式需要）
- **操作系统**：Windows 10/11、Linux、macOS

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/sunna-1/PaddlePaddle-with-vueUI.git
cd PaddlePaddle-with-vueUI
```

#### 2. 创建Python虚拟环境

```bash
# 使用Conda创建环境（推荐）
conda create -n traffic python=3.8
conda activate traffic

# 或使用venv
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

#### 3. 安装Python依赖

```bash
pip install -r requirements.txt
```

**注意事项**：
- 如果使用GPU，请安装GPU版本的PaddlePaddle：
  ```bash
  pip install paddlepaddle-gpu
  ```
- 如果使用CPU，请安装CPU版本：
  ```bash
  pip install paddlepaddle
  ```
- 确保CUDA版本与PaddlePaddle版本兼容

#### 4. 安装前端依赖

```bash
cd frontend
npm install
```

#### 5. 配置项目

编辑 `config.json` 文件，根据需要调整配置：

```json
{
  "upload_folder": "PaddleDetection/uploads",
  "output_folder": "PaddleDetection/output",
  "model_path": "PaddleDetection/output_inference/ppyoloe_crn_l_300e_coco/model.pdmodel",
  "max_file_size": 524288000,
  "allowed_extensions": ["mp4", "avi", "mov", "mkv"]
}
```

#### 6. 启动项目

**方式一：使用一键启动脚本（Windows）**

```bash
start.bat
```

**方式二：手动启动**

启动后端：
```bash
python app.py
```

启动前端（新终端）：
```bash
cd frontend
npm run dev
```

#### 7. 访问系统

- 前端地址：http://localhost:3000（或Vite显示的端口）
- 后端API：http://localhost:5000/api

## 使用说明

### 上传视频

1. 访问系统首页，点击"开始分析"
2. 在分析页面点击上传区域或拖拽视频文件
3. 支持的格式：MP4、AVI、MOV、MKV
4. 文件大小限制：500MB

### 查看分析结果

1. 上传视频后，系统自动开始分析
2. 分析完成后，右侧面板显示统计数据：
   - 检测车辆总数
   - 唯一车辆数
   - 平均每帧检测数
   - 交通状态（畅通/缓行/拥堵）
3. 底部显示车型分布和车流密度趋势图表
4. 可以下载带检测标注的输出视频

### 系统监控

顶部状态栏实时显示：
- 后端服务状态（运行中/未启动）
- CPU使用率和核心数
- 内存使用情况
- 系统运行时间
- 活跃任务数

## 部署注意事项

### 1. 依赖版本兼容性

- **PaddlePaddle版本**：确保CUDA版本与PaddlePaddle版本匹配
  - PaddlePaddle 3.0.0：CUDA 11.2+
  - PaddlePaddle 3.3.0：CUDA 11.8+
- **Python版本**：建议使用Python 3.8-3.10
- **Node.js版本**：建议使用16.x或18.x

### 2. GPU环境配置

如果使用GPU，请确保：
- 已安装NVIDIA驱动
- 已安装CUDA Toolkit
- 已安装cuDNN
- 环境变量正确配置：
  ```bash
  export CUDA_HOME=/usr/local/cuda
  export PATH=$CUDA_HOME/bin:$PATH
  export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
  ```

### 3. 端口占用

- 后端默认端口：5000
- 前端默认端口：3000（Vite自动选择可用端口）
- 如果端口被占用，请修改 `app.py` 和 `vite.config.js` 中的端口配置

### 4. 文件路径问题

- Windows路径使用反斜杠 `\` 或双反斜杠 `\\`
- Linux/macOS路径使用正斜杠 `/`
- 确保所有路径使用绝对路径或正确的相对路径

### 5. 视频编码问题

- 支持的视频编码：H.264、H.265
- 如果视频无法播放，请使用FFmpeg转换：
  ```bash
  ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4
  ```

### 6. 内存和显存要求

- **系统内存**：建议16GB或更高
- **GPU显存**：建议8GB或更高
- 如果显存不足，可以：
  - 减小输入视频分辨率
  - 使用更小的模型（如YOLOv8n）
  - 降低batch size

### 7. 性能优化

- **GPU加速**：使用GPU模式可获得10-20倍速度提升
- **多线程处理**：在 `config.json` 中配置线程数
- **视频预处理**：提前将视频转换为统一格式和分辨率

### 8. 安全注意事项

- 不要在生产环境中使用Flask内置服务器
- 建议使用Nginx或Apache作为反向代理
- 配置HTTPS加密传输
- 设置文件上传大小限制
- 添加用户认证机制

## 常见问题

### Q1: 后端启动失败，提示"ModuleNotFoundError"

**A**: 确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

### Q2: 前端无法连接后端

**A**: 检查：
- 后端是否正常运行
- 端口是否正确
- 浏览器控制台是否有CORS错误
- 检查 `vite.config.js` 中的代理配置

### Q3: 视频处理速度很慢

**A**: 
- 检查是否使用GPU模式
- 降低视频分辨率
- 使用更小的模型
- 增加GPU显存

### Q4: 检测精度不理想

**A**:
- 确保使用正确的模型权重
- 调整检测阈值
- 使用更高分辨率的视频
- 训练模型适配特定场景

### Q5: 内存溢出

**A**:
- 减小视频分辨率
- 减少并发处理数量
- 增加系统内存
- 使用视频分片处理

## 项目特点

- ✅ **前后端完整集成**：实现从视频上传到结果展示的端到端流程
- ✅ **解决部署问题**：解决依赖缺失、环境冲突、视频编码等部署问题，系统可稳定正常运行
- ✅ **轻量化模型设计**：兼顾检测精度与处理速度，适配实际应用场景
- ✅ **一键化启动**：配套自动化处理脚本与一键启动程序，提升系统易用性
- ✅ **现代化界面**：采用简洁现代的UI设计，响应式布局，良好的用户体验
- ✅ **实时监控**：提供系统资源使用情况实时监控
- ✅ **多格式支持**：支持多种视频格式和编码

## 性能指标

### 检测精度（GPU模式）
- 车辆检测精度：~90-95%
- 车辆ID跟踪精度：~85-90%

### 处理速度（GPU模式）
- 视频处理速度：15-30 FPS
- 平均处理时间：约10-30秒/分钟视频

## 数据集

- **高德交通路况识别竞赛数据**：1500个视频序列（3类路况）
- **BDD100K**：10万张道路图像（3类目标）
- **COCO**：通用目标检测数据集

## 致谢

- **PaddlePaddle飞桨**：百度开源的深度学习平台
- **Ultralytics YOLOv8**：先进的目标检测算法
- **PaddleDetection**：飞桨目标检测开发套件
- **ByteTrack**：高性能多目标跟踪算法
- **IconPark**：字节跳动开源的图标库

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues：https://github.com/sunna-1/PaddlePaddle-with-vueUI/issues
- 邮箱：[待填写]

## 更新日志

### v1.0.0 (2026-03-18)
- 初始版本发布
- 实现视频上传、检测、跟踪功能
- 完成前后端集成
- 添加系统监控功能
- 实现数据可视化展示
- 优化用户界面和交互体验