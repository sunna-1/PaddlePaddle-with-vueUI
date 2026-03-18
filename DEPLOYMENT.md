# 部署指南

本文档提供详细的部署步骤和注意事项，帮助您快速部署交通路况智能分析项目。

## 目录

- [系统要求](#系统要求)
- [环境准备](#环境准备)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [启动项目](#启动项目)
- [常见问题](#常见问题)
- [性能优化](#性能优化)
- [安全配置](#安全配置)

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4核心 | 8核心或更高 |
| 内存 | 8GB | 16GB或更高 |
| GPU | 无（CPU模式） | NVIDIA GPU（GTX 1060或更高） |
| 显存 | - | 8GB或更高 |
| 存储 | 20GB | 50GB或更高 |

### 软件要求

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.8-3.10 | 推荐Python 3.8 |
| Node.js | 16.x+ | 推荐Node.js 18.x |
| CUDA | 11.2+ | GPU模式需要 |
| cuDNN | 8.0+ | GPU模式需要 |
| 操作系统 | Windows 10/11, Linux, macOS | 推荐Windows 10/11 |

## 环境准备

### 1. 安装Python

#### Windows
```bash
# 下载Python 3.8安装包
# https://www.python.org/downloads/

# 安装时勾选"Add Python to PATH"
```

#### Linux
```bash
sudo apt-get update
sudo apt-get install python3.8 python3-pip
```

#### macOS
```bash
brew install python@3.8
```

### 2. 安装Node.js

#### Windows
```bash
# 下载Node.js安装包
# https://nodejs.org/

# 或使用nvm（推荐）
nvm install 18
nvm use 18
```

#### Linux/macOS
```bash
# 使用nvm安装
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

### 3. 安装CUDA（GPU模式）

#### Windows
```bash
# 下载CUDA Toolkit
# https://developer.nvidia.com/cuda-downloads

# 下载cuDNN
# https://developer.nvidia.com/cudnn

# 解压cuDNN到CUDA安装目录
```

#### Linux
```bash
# 安装CUDA Toolkit
wget https://developer.download.nvidia.com/compute/cuda/11.2.2/local_installers/cuda_11.2.2_460.82.00_linux.run
sudo sh cuda_11.2.2_460.82.00_linux.run

# 安装cuDNN
tar -xzvf cudnn-11.2-linux-x64-v8.1.1.34.tgz
sudo cp cuda/include/cudnn*.h /usr/local/cuda/include
sudo cp -P cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

### 4. 安装Git

```bash
# Windows：下载Git安装包
# https://git-scm.com/downloads

# Linux
sudo apt-get install git

# macOS
brew install git
```

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/sunna-1/PaddlePaddle-with-vueUI.git
cd PaddlePaddle-with-vueUI
```

### 2. 创建Python虚拟环境

#### 使用Conda（推荐）

```bash
# 创建环境
conda create -n traffic python=3.8 -y

# 激活环境
conda activate traffic

# 验证Python版本
python --version
```

#### 使用venv

```bash
# 创建虚拟环境
python -m venv venv

# Windows激活
venv\Scripts\activate

# Linux/macOS激活
source venv/bin/activate
```

### 3. 安装Python依赖

```bash
# 安装基础依赖
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

#### GPU模式

```bash
# 安装GPU版本的PaddlePaddle
pip install paddlepaddle-gpu==3.0.0 -i https://mirror.baidu.com/pypi/simple

# 验证GPU是否可用
python -c "import paddle; print(paddle.device.cuda.device_count())"
```

#### CPU模式

```bash
# 安装CPU版本的PaddlePaddle
pip install paddlepaddle==3.0.0 -i https://mirror.baidu.com/pypi/simple
```

### 4. 安装前端依赖

```bash
cd frontend

# 安装依赖
npm install

# 或使用yarn（更快）
yarn install
```

### 5. 验证安装

```bash
# 验证Python依赖
python -c "import flask, cv2, numpy, paddle; print('All dependencies installed successfully')"

# 验证前端依赖
cd frontend
npm list
```

## 配置说明

### 1. 编辑config.json

```json
{
  "upload_folder": "PaddleDetection/uploads",
  "output_folder": "PaddleDetection/output",
  "model_path": "PaddleDetection/output_inference/ppyoloe_crn_l_300e_coco/model.pdmodel",
  "max_file_size": 524288000,
  "allowed_extensions": ["mp4", "avi", "mov", "mkv"],
  "max_threads": 4,
  "gpu_memory_fraction": 0.8
}
```

### 2. 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| upload_folder | 上传文件存储目录 | PaddleDetection/uploads |
| output_folder | 输出文件存储目录 | PaddleDetection/output |
| model_path | 模型文件路径 | PaddleDetection/output_inference/... |
| max_file_size | 最大文件大小（字节） | 524288000 (500MB) |
| allowed_extensions | 允许的文件扩展名 | ["mp4", "avi", "mov", "mkv"] |
| max_threads | 最大线程数 | 4 |
| gpu_memory_fraction | GPU显存使用比例 | 0.8 |

### 3. 环境变量配置

#### Windows

```bash
# 设置CUDA环境变量
set CUDA_HOME=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2
set PATH=%CUDA_HOME%\bin;%PATH%
set LD_LIBRARY_PATH=%CUDA_HOME%\lib64;%LD_LIBRARY_PATH%
```

#### Linux/macOS

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# 使配置生效
source ~/.bashrc
```

## 启动项目

### 方式一：使用一键启动脚本（Windows）

```bash
# 双击运行
start.bat

# 或在命令行中运行
start.bat
```

### 方式二：手动启动

#### 启动后端

```bash
# 激活Python环境
conda activate traffic

# 启动后端服务
python app.py
```

后端将在 http://localhost:5000 启动

#### 启动前端（新终端）

```bash
# 进入前端目录
cd frontend

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动（或Vite显示的端口）

### 访问系统

打开浏览器访问：http://localhost:3000

## 常见问题

### Q1: ModuleNotFoundError: No module named 'xxx'

**原因**：依赖未安装或虚拟环境未激活

**解决方案**：
```bash
# 激活虚拟环境
conda activate traffic

# 重新安装依赖
pip install -r requirements.txt
```

### Q2: CUDA out of memory

**原因**：GPU显存不足

**解决方案**：
```bash
# 1. 减小batch size
# 2. 降低视频分辨率
# 3. 减少并发处理数量
# 4. 调整gpu_memory_fraction参数
```

### Q3: 前端无法连接后端

**原因**：CORS错误或端口被占用

**解决方案**：
```bash
# 1. 检查后端是否正常运行
# 2. 检查端口是否被占用
netstat -ano | findstr :5000

# 3. 检查vite.config.js中的代理配置
# 4. 查看浏览器控制台错误信息
```

### Q4: 视频无法播放

**原因**：视频编码不支持

**解决方案**：
```bash
# 使用FFmpeg转换视频格式
ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4

# 或安装额外的编解码器
pip install opencv-python-headless
```

### Q5: 检测精度低

**原因**：模型权重不匹配或阈值设置不当

**解决方案**：
```bash
# 1. 确认使用正确的模型权重
# 2. 调整检测阈值
# 3. 使用更高分辨率的视频
# 4. 训练模型适配特定场景
```

### Q6: 处理速度慢

**原因**：使用CPU模式或配置不当

**解决方案**：
```bash
# 1. 使用GPU模式
pip install paddlepaddle-gpu

# 2. 增加线程数
# 3. 降低视频分辨率
# 4. 使用更小的模型
```

## 性能优化

### 1. GPU优化

```bash
# 使用混合精度训练
export FLAGS_fraction_of_gpu_memory_to_use=0.8

# 启用TensorRT加速
export FLAGS_use_tensorrt=True

# 使用多GPU
export CUDA_VISIBLE_DEVICES=0,1
```

### 2. 视频预处理

```bash
# 统一视频格式
ffmpeg -i input.mp4 -c:v libx264 -preset fast -crf 23 output.mp4

# 调整分辨率
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

# 降低帧率
ffmpeg -i input.mp4 -r 15 output.mp4
```

### 3. 并发处理

```json
{
  "max_threads": 8,
  "batch_size": 4,
  "concurrent_requests": 2
}
```

### 4. 缓存优化

```bash
# 启用模型缓存
export FLAGS_enable_mkldnn=true

# 使用内存缓存
export FLAGS_fraction_of_gpu_memory_to_use=0.9
```

## 安全配置

### 1. 文件上传限制

```python
# 在app.py中配置
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
```

### 2. 用户认证

```python
# 添加JWT认证
from flask_jwt_extended import JWTManager

jwt = JWTManager(app)

# 添加登录接口
@app.route('/login', methods=['POST'])
def login():
    # 验证用户
    pass
```

### 3. HTTPS配置

```nginx
# Nginx配置示例
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. 防火墙配置

```bash
# Windows防火墙
netsh advfirewall firewall add rule name="TrafficAnalysis" dir=in action=allow protocol=TCP localport=5000

# Linux防火墙
sudo ufw allow 5000/tcp
```

## 监控和日志

### 1. 系统监控

访问系统监控页面查看：
- CPU使用率
- 内存使用情况
- GPU使用情况
- 任务队列状态

### 2. 日志查看

```bash
# 查看后端日志
tail -f logs/app.log

# 查看前端日志
cd frontend
npm run dev
```

### 3. 性能分析

```bash
# 使用Python性能分析器
python -m cProfile -s time app.py

# 使用GPU性能分析
nvidia-smi -l 1
```

## 备份和恢复

### 1. 数据备份

```bash
# 备份上传文件
tar -czf backup_$(date +%Y%m%d).tar.gz PaddleDetection/uploads

# 备份输出文件
tar -czf output_$(date +%Y%m%d).tar.gz PaddleDetection/output
```

### 2. 配置备份

```bash
# 备份配置文件
cp config.json config_backup_$(date +%Y%m%d).json
```

### 3. 恢复数据

```bash
# 恢复上传文件
tar -xzf backup_20260318.tar.gz

# 恢复配置
cp config_backup_20260318.json config.json
```

## 升级指南

### 1. 备份当前版本

```bash
# 备份数据和配置
./backup.sh

# 创建备份分支
git checkout -b backup
```

### 2. 拉取最新代码

```bash
# 切换到主分支
git checkout main

# 拉取最新代码
git pull origin main
```

### 3. 更新依赖

```bash
# 更新Python依赖
pip install -r requirements.txt --upgrade

# 更新前端依赖
cd frontend
npm update
```

### 4. 测试升级

```bash
# 测试后端
python app.py

# 测试前端
npm run dev
```

## 技术支持

如有问题，请通过以下方式获取帮助：

- GitHub Issues：https://github.com/sunna-1/PaddlePaddle-with-vueUI/issues
- 文档：https://github.com/sunna-1/PaddlePaddle-with-vueUI/wiki
- 社区论坛：[待填写]

## 附录

### A. 端口说明

| 服务 | 默认端口 | 说明 |
|------|----------|------|
| 后端API | 5000 | Flask服务端口 |
| 前端开发服务器 | 3000 | Vite开发服务器 |
| 生产环境前端 | 80/443 | Nginx/Apache端口 |

### B. 目录权限

```bash
# 确保目录有写权限
chmod -R 755 PaddleDetection/uploads
chmod -R 755 PaddleDetection/output

# Windows
icacls "PaddleDetection\uploads" /grant Everyone:F
icacls "PaddleDetection\output" /grant Everyone:F
```

### C. 环境变量清单

```bash
# CUDA相关
CUDA_HOME=/usr/local/cuda
PATH=$CUDA_HOME/bin:$PATH
LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Python相关
PYTHONPATH=/path/to/project:$PYTHONPATH

# 应用相关
FLASK_ENV=production
FLASK_DEBUG=False
```

---

**最后更新**：2026-03-18
**文档版本**：v1.0.0