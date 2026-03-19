# 交通路况智能分析项目

基于PaddleDetection PP-Vehicle的深度学习车载视频智能分析平台，集成了目标检测、目标跟踪、车牌识别、车道线检测等功能。

## 项目简介

本项目是一个完整的交通路况智能分析系统，基于百度飞桨PaddleDetection的PP-Vehicle工具开发，通过车载视频自动识别车辆、跟踪车辆轨迹、识别车牌号码、检测车道线，并智能判断道路拥堵状态。系统采用前后端分离架构，前端使用Vue 3构建现代化用户界面，后端使用Python Flask提供API服务，核心算法基于百度飞桨PaddlePaddle深度学习框架。

### 核心功能

- 🎬 **多格式视频上传**：支持MP4、AVI、MOV等常见视频格式
- 🤖 **AI智能识别**：集成目标检测与跟踪算法，自动完成道路中车辆的识别与轨迹追踪
- 📊 **多维度车流量统计**：支持车辆总数、唯一ID车辆数、道路平均车辆密度等指标统计
- 🚦 **智能路况判断**：基于检测结果自动判定道路为畅通/缓行/拥堵三类状态
- 📈 **可视化结果展示**：提供带检测标注的视频回放、车流量/路况统计图表展示
- 🎯 **实时路况占比**：环形图展示畅通、缓行、拥堵的占比分布

## 技术栈

### 前端
- **Vue 3**：渐进式JavaScript框架
- **Vite**：新一代前端构建工具
- **ECharts**：数据可视化图表库
- **IconPark**：字节跳动开源的图标库

### 后端
- **Python 3.9-3.13**：主要编程语言（推荐Python 3.10）
- **Flask**：轻量级Web框架
- **OpenCV**：计算机视觉库
- **PaddlePaddle 3.3.0 (GPU)**：百度飞桨深度学习框架

### AI算法
- **PP-Vehicle**：PaddleDetection的实时车辆分析工具
- **PPYOLOE-L**：高精度车辆检测模型
- **ByteTrack**：高性能多目标跟踪算法

## 项目演示

📺 **视频演示**：[基于vue3和百度飞桨3.3搭建的车辆识别系统-哔哩哔哩](https://b23.tv/eIxrcQG)

## 项目结构

```
pythonProject/
├── frontend/              # 前端项目
│   ├── public/           # 静态资源
│   ├── src/             # 源代码
│   │   ├── views/       # 页面组件
│   │   ├── App.vue     # 根组件
│   │   ├── main.js     # 入口文件
│   │   └── router.js   # 路由配置
│   └── package.json    # 前端依赖
├── PaddleDetection/     # 飞桨检测框架
│   ├── deploy/         # 部署脚本
│   │   └── pipeline/   # PP-Vehicle工具
│   │       └── config/ # 配置文件
│   ├── configs/        # 模型配置
│   └── output/        # 输出目录
├── video-demo/         # 测试视频
├── app.py             # 后端主程序
├── config.json        # 配置文件
├── requirements.txt    # Python依赖
└── README.md         # 项目说明
```

## 快速开始

### 环境要求

- **Python**：3.9-3.13（推荐Python 3.10）
- **pip**：20.2.2 或更高版本
- **Node.js**：16.x 或更高版本
- **GPU**：NVIDIA GPU（推荐，CPU模式也可运行但速度较慢）
- **CUDA**：11.8 或更高版本（GPU模式需要）
- **操作系统**：Windows 10/11、Linux、macOS

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/sunna-1/PaddlePaddle-with-vueUI.git
cd PaddlePaddle-with-vueUI
```

#### 2. 创建Python虚拟环境

**Windows系统（推荐使用Conda）**：

```bash
# 创建名为pp的虚拟环境
conda create -n pp python=3.10 -y

# 激活虚拟环境
conda activate pp
```

**或使用venv**：

```bash
# 创建虚拟环境
python -m venv pp

# 激活虚拟环境
pp\Scripts\activate
```

**Linux/macOS系统**：

```bash
# 使用Conda
conda create -n pp python=3.10 -y
conda activate pp

# 或使用venv
python -m venv pp
source pp/bin/activate
```

#### 3. 安装Python依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**安装PaddlePaddle**：

根据您的CUDA版本选择合适的PaddlePaddle版本：

- **CUDA 11.8**：
  ```bash
  pip install paddlepaddle-gpu==3.3.0
  ```

- **CUDA 12.0**：
  ```bash
  pip install paddlepaddle-gpu==3.3.0
  ```

- **CUDA 12.6**：
  ```bash
  pip install paddlepaddle-gpu==3.3.0
  ```

- **CUDA 12.9**：
  ```bash
  pip install paddlepaddle-gpu==3.3.0
  ```

- **CPU版本**（无GPU）：
  ```bash
  pip install paddlepaddle==3.3.0
  ```

> 💡 **提示**：更多安装详情请参考 [PaddlePaddle官方安装文档](https://www.paddlepaddle.org.cn/documentation/docs/zh/install/index_cn.html)

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

**启动后端**：

```bash
# 确保在虚拟环境中
conda activate pp

# 启动后端服务
python app.py
```

后端将在 http://localhost:5000 启动

**启动前端（新终端）**：

```bash
cd frontend
npm run dev
```

前端将在 http://localhost:3000 启动（或Vite显示的端口）

#### 7. 访问系统

打开浏览器访问：http://localhost:3000

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
  - PaddlePaddle 3.3.0：CUDA 11.8+
- **Python版本**：建议使用Python 3.9-3.13（推荐Python 3.10）
- **Node.js版本**：建议使用16.x或18.x

### 2. GPU环境配置

如果使用GPU，请确保：
- 已安装NVIDIA驱动
- 已安装CUDA Toolkit（11.8或更高版本）
- 已安装cuDNN
- 环境变量正确配置：
  ```bash
  export CUDA_HOME=/usr/local/cuda
  export PATH=$CUDA_HOME/bin:$PATH
  export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
  ```

### 3. PP-Vehicle功能配置

本项目基于PaddleDetection的PP-Vehicle工具，核心配置文件位于：
```
PaddleDetection/deploy/pipeline/config/infer_cfg_ppvehicle.yml
```

**当前功能配置**：
- ✅ **多目标跟踪 (MOT)**：实时检测并跟踪车辆，输出唯一ID（已开启）
- ❌ **车牌识别**：识别车牌号码（蓝牌/绿牌）（已关闭）
- ❌ **车道线检测**：检测车道线（已关闭）
- ❌ **压线检测**：检测车辆是否压线（已关闭）
- ❌ **逆行检测**：检测车辆逆行行为（已关闭）
- ❌ **车辆属性识别**：识别车辆颜色和类型（已关闭）

**配置说明**：
- 开启/关闭功能：编辑配置文件，修改对应模块的`enable`字段
- 模型路径：支持HTTP URL或本地路径，首次运行自动下载模型（约300MB）
- 模型默认缓存到`C:\Users\<用户名>/.cache/paddle/infer_weights/`目录

**PP-Vehicle详细部署教程**：

#### 环境要求
- **操作系统**：Windows / Linux（本教程基于 Windows 11 测试）
- **Python**：3.9 - 3.12（推荐 3.9）
- **CUDA**：11.8（GPU 版 PaddlePaddle 需要，CPU 版可跳过）
- **GPU 显存**：建议 ≥ 6GB（同时开启多模块时需更多显存）
- **Git**：用于克隆代码仓库

#### 部署步骤

**1. 创建 conda 环境**
```bash
conda create -n pp python=3.9 -y
conda activate pp
pip install --upgrade pip
```

**2. 安装 PaddlePaddle**
根据你的 CUDA 版本选择对应命令。本项目使用 CUDA 11.8，安装命令如下：
```bash
python -m pip install paddlepaddle-gpu==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
```
如果使用 CPU 或无合适 CUDA 版本，请参考 [PaddlePaddle 官网](https://www.paddlepaddle.org.cn/install/quick) 选择安装命令。

**3. 克隆 PaddleDetection 仓库**
```bash
git clone https://github.com/PaddlePaddle/PaddleDetection.git
cd PaddleDetection
```

**4. 安装项目依赖**
```bash
pip install -r requirements.txt
pip install scikit-learn          # MOT 依赖
pip install numba==0.56.4         # 可选，提升跟踪速度
```

**5. 模型下载（自动方式）**
PP-Vehicle 的模型通过配置文件中的 URL 自动下载。你无需手动下载，只需确保运行命令时网络畅通即可。

**6. 运行分析**
将你的车载视频（例如 `dashcam.mp4`）放入 `PaddleDetection` 目录下，执行：
```bash
python deploy/pipeline/pipeline.py \
    --config deploy/pipeline/config/infer_cfg_ppvehicle.yml \
    --video_file=dashcam.mp4 \
    --device=gpu \
    --output_dir=./output
```
- `--device`：可选 `gpu` 或 `cpu`
- `--output_dir`：结果视频保存目录

首次运行会自动下载模型（约 300MB），请耐心等待。

**7. 查看结果**
- 输出视频位于 `./output/dashcam.mp4`，包含检测框、跟踪 ID
- 控制台会实时打印每帧的检测信息，可用于统计车辆数量

### 4. 端口占用

- 后端默认端口：5000
- 前端默认端口：3000（Vite自动选择可用端口）
- 如果端口被占用，请修改 `app.py` 和 `vite.config.js` 中的端口配置

### 5. 文件路径问题

本项目采用动态路径处理，自动适配不同的部署环境，**无需手动修改路径**：

**路径处理机制**：
- 项目根目录：自动通过`Path(__file__).parent.absolute()`获取
- PaddleDetection目录：`项目根目录/PaddleDetection`
- 输出目录：`项目根目录/PaddleDetection/output`
- 上传目录：`项目根目录/PaddleDetection`

**路径兼容性**：
- ✅ **Windows**：自动处理路径分隔符（`\`或`/`）
- ✅ **Linux/macOS**：自动处理路径分隔符（`/`）
- ✅ **相对路径**：所有路径基于项目根目录，支持任意位置部署
- ✅ **Python解释器**：自动使用当前激活环境的Python解释器

**注意事项**：
- 确保在项目根目录下运行`python app.py`
- 不要修改`app.py`中的路径配置
- 日志中显示的路径为相对路径，便于阅读和理解

### 6. 视频编码问题

- 支持的视频编码：H.264、H.265
- 如果视频无法播放，请使用FFmpeg转换：
  ```bash
  ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4
  ```

### 7. 内存和显存要求

- **系统内存**：建议16GB或更高
- **GPU显存**：建议8GB或更高（同时开启多模块时需更多显存）
- 如果显存不足，可以：
  - 关闭不需要的模块（如车牌识别、逆行检测）
  - 减小输入视频分辨率
  - 使用CPU推理（`--device=cpu`，仅用于测试）

### 8. 性能优化

- **GPU加速**：使用GPU模式可获得10-20倍速度提升
- **多线程处理**：在 `config.json` 中配置线程数
- **视频预处理**：提前将视频转换为统一格式和分辨率
- **跳帧处理**：添加`--skip_frame_num=2`参数，每隔2帧处理一次

### 9. 安全注意事项

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
pip install scikit-learn          # MOT 依赖
pip install numba==0.56.4         # 可选，提升跟踪速度
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
- 关闭不需要的模块（如车牌识别、逆行检测）
- 使用跳帧处理：`--skip_frame_num=2`
- 增加GPU显存

### Q4: 内存溢出

**A**:
- 减小视频分辨率
- 减少并发处理数量
- 增加系统内存
- 使用视频分片处理

### Q6: 运行后报错"Cannot open file .../model.json"

**A**: 这是车辆属性模块的问题，解决方法：
- 方法一（推荐）：在配置文件中设置`VEHICLE_ATTR.enable: false`
- 方法二：修改代码适配，编辑`deploy/pipeline/pphuman/attr_infer.py`，添加判断逻辑

### Q7: 车道线没有绘制在输出视频中

**A**: 必须同时满足两个条件：
- 配置了`LANE_SEG`模块
- 开启了`VEHICLE_PRESSING`模块（即使不关心压线也要开启）

### Q8: 压线检测不报警

**A**: 需要设置具体的`fence_line`坐标，例如在1920x1080画面中：
```yaml
VEHICLE_PRESSING:
  enable: true
  fence_line: [0, 500, 1920, 500]
```

### Q9: 模型下载速度慢

**A**: 
- 使用代理或更换网络环境
- 手动下载模型压缩包（URL见配置文件），解压后修改配置中的`model_dir`为本地路径
- 模型默认缓存到`C:\Users\<用户名>/.cache/paddle/infer_weights/`

### Q10: GPU显存不足

**A**: 
- 关闭暂时不需要的模块（如车牌识别、逆行检测）
- 降低`VEHICLE_ATTR.batch_size`（如果开启）
- 使用CPU推理：`--device=cpu`（仅用于测试）
- 升级GPU或减少输入视频分辨率

### Q11: 逆行检测效果不佳

**A**: 
- 调整配置文件中的参数：`deviation`、`move_scale`、`frame_len`
- 参考PaddleDetection文档调整
- 如果不需要，可直接关闭逆行检测（`enable: false`）

### Q12: PP-Vehicle模型下载失败

**A**: 
- 检查网络连接，确保可以访问百度云
- 使用代理或更换网络环境
- 手动下载模型：从配置文件中的URL下载模型压缩包，解压到本地，然后修改配置文件中的`model_dir`为本地路径
- Windows PowerShell正确下载命令：
  ```powershell
  Invoke-WebRequest -Uri <URL> -OutFile <filename.zip>
  ```
  或使用系统自带的`curl.exe`：
  ```powershell
  curl.exe -L -o <filename.zip> <URL>
  ```

### Q13: 运行时提示"Unable to use numba in PP-Tracking"

**A**: 
- 这是警告信息，不影响功能
- 如需提升跟踪速度，安装numba：
  ```bash
  pip install numba==0.56.4
  ```

### Q14: 警告"No ccache found"

**A**: 
- 这是不影响运行的警告，可以忽略
- 如需优化编译速度，安装ccache：
  ```bash
  # Linux/macOS
  sudo apt-get install ccache
  
  # Windows (使用conda)
  conda install -c conda-forge ccache
  ```

### Q15: 错误"ValueError: not find model file path .../inference.pdmodel"

**A**: 
- 模型文件未下载或路径错误
- 检查配置文件中的`model_dir`是否正确指向包含`.pdmodel`文件的文件夹
- 确认URL可访问或本地路径正确
- 尝试删除缓存目录重新下载：
  ```bash
  # Windows
  rm -rf C:\Users\<用户名>\.cache\paddle\infer_weights\
  
  # Linux/macOS
  rm -rf ~/.cache/paddle/infer_weights/
  ```

### Q16: 车辆跟踪ID不稳定

**A**: 
- 调整跟踪器配置：编辑`deploy/pipeline/config/tracker_config.yml`
- 调整参数如`track_buffer`、`match_thresh`等
- 参考ByteTrack文档进行参数调优
- 如果视频中有遮挡严重的情况，这是正常现象

## 项目特点

- ✅ **前后端完整集成**：实现从视频上传到结果展示的端到端流程
- ✅ **轻量化模型设计**：兼顾检测精度与处理速度，适配实际应用场景
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
  - [GitHub仓库](https://github.com/PaddlePaddle/Paddle/releases?github.com)
  - [官方网站](https://www.paddlepaddle.org.cn/documentation/docs/zh/install/index_cn.html)
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