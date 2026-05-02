import os
import sys
import time
import json
import uuid
import subprocess
import threading
import shutil
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 获取项目根目录
BASE_DIR = Path(__file__).parent.absolute()
PADDLE_DETECTION_DIR = BASE_DIR / 'PaddleDetection'
OUTPUT_DIR = PADDLE_DETECTION_DIR / 'output'

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 配置
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
UPLOAD_FOLDER = PADDLE_DETECTION_DIR

# 全局变量
backend_start_time = datetime.now()
active_tasks = 0
logs = []
processing_lock = threading.Lock()

# psutil 首次调用 cpu_percent 需要初始化
_psutil_initialized = False


def log_message(message):
    """添加日志消息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    logs.append(log_entry)
    print(log_entry)
    if len(logs) > 100:  # 保留最近 100 条日志
        logs.pop(0)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_safe_filename(original_filename):
    """
    生成安全的文件名，保留原始扩展名
    解决 secure_filename 对中文文件名处理不当的问题
    """
    ext = ''
    if '.' in original_filename:
        ext = '.' + original_filename.rsplit('.', 1)[1].lower()
    # 使用 UUID 生成唯一文件名，避免中文和冲突
    safe_name = str(uuid.uuid4())[:8] + ext
    return safe_name


def analyze_from_detection_json(json_path):
    """
    基于pipeline导出的JSON检测数据进行分析

    Args:
        json_path: pipeline输出的 _detection.json 文件路径

    Returns:
        dict: 包含统计信息的字典
    """
    log_message(f"从检测数据文件分析：{json_path}")

    with open(str(json_path), 'r', encoding='utf-8') as f:
        data = json.load(f)

    video_info = data.get('video_info', {})
    frames = data.get('frames', [])

    width = video_info.get('width', 0)
    height = video_info.get('height', 0)
    fps = video_info.get('fps', 25)
    total_frames = video_info.get('total_frames', len(frames))
    frame_area = width * height if width > 0 and height > 0 else 1

    if not frames:
        log_message("警告：检测数据为空")
        return _empty_result(total_frames)

    # ===== 逐帧统计 =====
    frame_vehicle_counts = []      # 每帧车辆数
    all_track_ids = set()          # 所有出现过的track_id
    track_positions = {}           # track_id -> [(frame_id, cx, cy), ...]
    track_first_seen = {}          # track_id -> 首次出现帧号
    track_last_seen = {}           # track_id -> 最后出现帧号
    track_areas = {}               # track_id -> [area, ...]
    frame_density_trend = []       # 密度趋势（采样）
    frame_area_ratios = []         # 每帧车辆面积占比

    # 检测JSON格式：新版精简格式用 fid/n/v，旧版用 frame_id/vehicle_count/vehicles
    for frame_data in frames:
        # 兼容新旧格式
        if 'fid' in frame_data:
            fid = frame_data['fid']
            vehicle_count = frame_data['n']
            raw_vehicles = frame_data['v']
        else:
            fid = frame_data['frame_id']
            vehicle_count = frame_data['vehicle_count']
            raw_vehicles = frame_data['vehicles']

        frame_vehicle_counts.append(vehicle_count)

        # 每10帧采样一次用于趋势图
        if fid % 10 == 0:
            frame_density_trend.append(vehicle_count)

        # 累计各车辆信息
        total_vehicle_area = 0
        for v in raw_vehicles:
            # 新格式：v=[track_id, xmin, ymin, xmax, ymax] 数组
            # 旧格式：v={track_id, xmin, ymin, xmax, ymax} 字典
            if isinstance(v, list):
                tid, xmin, ymin, xmax, ymax = v[0], v[1], v[2], v[3], v[4]
            else:
                tid = v['track_id']
                xmin, ymin = v['xmin'], v['ymin']
                xmax, ymax = v['xmax'], v['ymax']

            cx = (xmin + xmax) / 2
            cy = (ymin + ymax) / 2
            area = (xmax - xmin) * (ymax - ymin)

            all_track_ids.add(tid)
            total_vehicle_area += area

            if tid not in track_positions:
                track_positions[tid] = []
            track_positions[tid].append((fid, cx, cy))

            if tid not in track_first_seen:
                track_first_seen[tid] = fid
            track_last_seen[tid] = fid

            if tid not in track_areas:
                track_areas[tid] = []
            track_areas[tid].append(area)

        # 帧面积占比
        if frame_area > 0:
            frame_area_ratios.append(total_vehicle_area / frame_area)
        else:
            frame_area_ratios.append(0)

    # ===== 汇总指标 =====
    total_detections = sum(frame_vehicle_counts)
    unique_vehicle_count = len(all_track_ids)
    avg_detections = total_detections / len(frame_vehicle_counts) if frame_vehicle_counts else 0
    max_concurrent = max(frame_vehicle_counts) if frame_vehicle_counts else 0
    min_concurrent = min(frame_vehicle_counts) if frame_vehicle_counts else 0
    avg_density = avg_detections

    # ===== 车辆停留时长（帧数） =====
    track_durations = {}
    for tid in all_track_ids:
        duration = track_last_seen[tid] - track_first_seen[tid] + 1
        track_durations[tid] = duration

    avg_duration = np.mean(list(track_durations.values())) if track_durations else 0
    max_duration = max(track_durations.values()) if track_durations else 0

    # ===== 帧间位移（像素/帧） =====
    # 区分画面区域：下方车辆更可能是同向行驶，更反映实际路况
    track_avg_speeds = {}
    track_avg_speeds_lower = {}  # 画面下半部分车辆的速度
    track_lower_ids = set()

    for tid, positions in track_positions.items():
        if len(positions) < 2:
            track_avg_speeds[tid] = 0
            continue
        displacements = []
        for i in range(1, len(positions)):
            dx = positions[i][1] - positions[i-1][1]
            dy = positions[i][2] - positions[i-1][2]
            disp = np.sqrt(dx**2 + dy**2)
            frame_diff = positions[i][0] - positions[i-1][0]
            if frame_diff > 0:
                displacements.append(disp / frame_diff)
        track_avg_speeds[tid] = np.mean(displacements) if displacements else 0

        # 判断车辆是否主要出现在画面下半部分（驾驶视角中更接近自车的车辆）
        avg_cy = np.mean([p[2] for p in positions])
        if avg_cy > height / 2:
            track_lower_ids.add(tid)
            track_avg_speeds_lower[tid] = track_avg_speeds[tid]

    all_speeds = list(track_avg_speeds.values())
    avg_speed = np.mean(all_speeds) if all_speeds else 0
    max_speed = max(all_speeds) if all_speeds else 0
    min_speed = min(all_speeds) if all_speeds else 0

    # 像素速度转换为 fps 归一化速度（像素/秒）
    avg_speed_per_sec = avg_speed * fps

    # ===== 静止车辆比例（速度极低的车辆占比） =====
    # 使用良好跟踪（>=3帧）的车辆计算，排除短跟踪噪声
    wt_speed_threshold = 3  # 最少跟踪帧数
    well_tracked_speeds = {tid: s for tid, s in track_avg_speeds.items()
                           if track_durations.get(tid, 0) >= wt_speed_threshold}
    wt_all_speeds = list(well_tracked_speeds.values())

    speed_threshold_low = 0.5  # 像素/帧，低于此视为基本静止
    wt_stationary_count = sum(1 for s in wt_all_speeds if s < speed_threshold_low)
    wt_stationary_ratio = wt_stationary_count / len(wt_all_speeds) if wt_all_speeds else 0
    wt_avg_speed = np.mean(wt_all_speeds) if wt_all_speeds else 0
    wt_fast_ratio = sum(1 for s in wt_all_speeds if s >= 2.0) / len(wt_all_speeds) if wt_all_speeds else 0

    # 全部车辆统计（含短跟踪，仅供参考）
    all_stationary_count = sum(1 for s in all_speeds if s < speed_threshold_low)
    stationary_ratio = all_stationary_count / len(all_speeds) if all_speeds else 0

    # ===== 画面下半部分车辆的速度统计 =====
    # 下方车辆更可能是同向行驶，更反映实际路况
    lower_speeds = list(track_avg_speeds_lower.values())
    lower_vehicle_count = len(track_lower_ids)

    # 良好跟踪的下半屏车辆
    lower_wt_speeds = [s for tid, s in well_tracked_speeds.items() if tid in track_lower_ids]
    lower_wt_avg_speed = np.mean(lower_wt_speeds) if lower_wt_speeds else 0
    lower_wt_stationary = sum(1 for s in lower_wt_speeds if s < speed_threshold_low) if lower_wt_speeds else 0
    lower_wt_stationary_ratio = lower_wt_stationary / len(lower_wt_speeds) if lower_wt_speeds else 0
    lower_wt_fast_ratio = sum(1 for s in lower_wt_speeds if s >= 2.0) / len(lower_wt_speeds) if lower_wt_speeds else 0

    # ===== 车辆面积占比 =====
    avg_area_ratio = np.mean(frame_area_ratios) if frame_area_ratios else 0
    max_area_ratio = max(frame_area_ratios) if frame_area_ratios else 0

    # ===== 位移趋势（按时间分段计算平均位移） =====
    speed_trend = []
    sample_step = max(1, len(frames) // 50)
    for i in range(0, len(frames), sample_step):
        frame_speeds = []
        # 兼容新旧格式
        raw_v = frames[i].get('v', frames[i].get('vehicles', []))
        for v in raw_v:
            if isinstance(v, list):
                tid = v[0]
            else:
                tid = v['track_id']
            if tid in track_avg_speeds:
                frame_speeds.append(track_avg_speeds[tid])
        avg_frame_speed = np.mean(frame_speeds) if frame_speeds else 0
        speed_trend.append(round(avg_frame_speed, 2))

    # ===== 密度趋势（更细粒度：每5帧采样） =====
    density_trend_fine = []
    for frame_data in frames:
        # 兼容新旧格式
        fid = frame_data.get('fid', frame_data.get('frame_id', 0))
        n = frame_data.get('n', frame_data.get('vehicle_count', 0))
        if fid % 5 == 0:
            density_trend_fine.append(n)

    # ===== 路况参考判断（多指标综合） =====
    traffic_status, confidence, judgment_factors = _judge_traffic_status(
        avg_density=avg_density,
        max_concurrent=max_concurrent,
        avg_speed=avg_speed,
        avg_speed_lower=avg_speed,
        avg_speed_per_sec=avg_speed_per_sec,
        stationary_ratio=stationary_ratio,
        lower_stationary_ratio=lower_wt_stationary_ratio if lower_wt_speeds else wt_stationary_ratio,
        lower_vehicle_ratio=lower_vehicle_count / unique_vehicle_count if unique_vehicle_count > 0 else 0,
        avg_area_ratio=avg_area_ratio,
        avg_duration=avg_duration,
        total_frames=total_frames,
        unique_vehicle_count=unique_vehicle_count,
        fps=fps,
        wt_avg_speed=wt_avg_speed,
        wt_stationary_ratio=wt_stationary_ratio,
        wt_fast_ratio=wt_fast_ratio,
        lower_wt_avg_speed=lower_wt_avg_speed,
        lower_wt_stationary_ratio=lower_wt_stationary_ratio,
        lower_wt_fast_ratio=lower_wt_fast_ratio
    )

    # ===== 密度分布统计（基于面积占比而非车辆数） =====
    # 驾驶视角下车辆数区分度差，改用面积占比判断每帧状态
    smooth_frames = sum(1 for r in frame_area_ratios if r < 0.05)
    slow_frames = sum(1 for r in frame_area_ratios if 0.05 <= r < 0.15)
    congested_frames = sum(1 for r in frame_area_ratios if r >= 0.15)

    total_status_frames = len(frame_vehicle_counts)
    if total_status_frames > 0:
        smooth_ratio = smooth_frames / total_status_frames
        slow_ratio = slow_frames / total_status_frames
        congested_ratio = congested_frames / total_status_frames
    else:
        smooth_ratio = slow_ratio = congested_ratio = 0

    log_message(f"分析完成 - 总检测数：{total_detections}, 唯一车辆数：{unique_vehicle_count}, "
                f"路况参考：{traffic_status}（置信度：{confidence}）")

    return {
        'total_frames': total_frames,
        'total_detections': total_detections,
        'unique_vehicle_count': unique_vehicle_count,
        'avg_detections_per_frame': round(avg_density, 2),
        'traffic_status': traffic_status,
        'confidence': confidence,
        'judgment_factors': judgment_factors,
        'vehicle_statistics': {
            'total_vehicles': unique_vehicle_count,
            'max_concurrent': max_concurrent,
            'min_concurrent': min_concurrent,
            'average_density': round(avg_density, 2)
        },
        'speed_statistics': {
            'avg_pixel_speed': round(wt_avg_speed, 2),
            'avg_pixel_speed_per_sec': round(wt_avg_speed * fps, 2),
            'max_pixel_speed': round(max_speed, 2),
            'min_pixel_speed': round(min_speed, 2),
            'stationary_vehicle_ratio': round(wt_stationary_ratio * 100, 2),
            'avg_track_duration_frames': round(avg_duration, 2),
            'max_track_duration_frames': round(max_duration, 2)
        },
        'area_statistics': {
            'avg_vehicle_area_ratio': round(avg_area_ratio * 100, 4),
            'max_vehicle_area_ratio': round(max_area_ratio * 100, 4)
        },
        'class_distribution': {'car': total_detections},
        'density_trend': density_trend_fine[:80] if len(density_trend_fine) > 80 else density_trend_fine,
        'speed_trend': speed_trend[:50] if len(speed_trend) > 50 else speed_trend,
        'traffic_status_distribution': {
            'smooth': round(smooth_ratio * 100, 2),
            'slow': round(slow_ratio * 100, 2),
            'congested': round(congested_ratio * 100, 2)
        },
        'data_source': 'pipeline_detection_json'
    }


def _judge_traffic_status(avg_density, max_concurrent, avg_speed,
                           avg_speed_lower, avg_speed_per_sec,
                           stationary_ratio, lower_stationary_ratio,
                           lower_vehicle_ratio,
                           avg_area_ratio, avg_duration,
                           total_frames, unique_vehicle_count, fps=30,
                           wt_avg_speed=0, wt_stationary_ratio=0,
                           wt_fast_ratio=0, lower_wt_avg_speed=0,
                           lower_wt_stationary_ratio=0,
                           lower_wt_fast_ratio=0):
    """
    多指标综合路况参考判断（驾驶视角优化版）

    核心思路：驾驶视角视频中，车辆密度在畅通和拥堵时差异不大，
    真正的区分指标是：
    1. 车辆面积占比——拥堵时车辆占据画面大部分区域
    2. 近处（画面下半部分）车辆比例——拥堵时周围车辆多
    3. 良好跟踪车辆的速度分布——短跟踪(1-2帧)噪声太大，
       仅使用跟踪>=3帧的车辆统计速度

    返回：(status, confidence, factors)
    """
    factors = {
        'area_ratio': {
            'value': round(avg_area_ratio * 100, 2),
            'label': '车辆面积占比(%)',
            'signal': None
        },
        'nearby_ratio': {
            'value': round(lower_vehicle_ratio * 100, 2),
            'label': '近处车辆占比(%)',
            'signal': None
        },
        'wt_speed': {
            'value': round(wt_avg_speed, 2),
            'label': '稳定跟踪车辆位移(像素/帧)',
            'signal': None
        },
        'wt_stationary': {
            'value': round(wt_stationary_ratio * 100, 2),
            'label': '稳定车辆静止占比(%)',
            'signal': None
        },
        'max_concurrent': {
            'value': max_concurrent,
            'label': '最大同帧车辆数',
            'signal': None
        }
    }

    # ===== 为每个指标判定信号 =====

    # 车辆面积占比信号（最强区分指标）
    # 畅通：车辆远且小，占比<5%；拥堵：车辆近且大，占比>15%
    if avg_area_ratio < 0.05:
        factors['area_ratio']['signal'] = 'smooth'
    elif avg_area_ratio < 0.12:
        factors['area_ratio']['signal'] = 'slow'
    else:
        factors['area_ratio']['signal'] = 'congested'

    # 近处车辆占比信号
    # 畅通：前方基本无车，<5%；拥堵：周围都是车，>10%
    if lower_vehicle_ratio < 0.05:
        factors['nearby_ratio']['signal'] = 'smooth'
    elif lower_vehicle_ratio < 0.10:
        factors['nearby_ratio']['signal'] = 'slow'
    else:
        factors['nearby_ratio']['signal'] = 'congested'

    # 稳定跟踪车辆速度信号（排除短跟踪噪声）
    # 使用跟踪>=3帧的车辆，速度更可靠
    if wt_avg_speed > 4.0:
        factors['wt_speed']['signal'] = 'smooth'
    elif wt_avg_speed > 1.5:
        factors['wt_speed']['signal'] = 'slow'
    else:
        factors['wt_speed']['signal'] = 'congested'

    # 稳定车辆静止占比信号
    if wt_stationary_ratio < 0.15:
        factors['wt_stationary']['signal'] = 'smooth'
    elif wt_stationary_ratio < 0.35:
        factors['wt_stationary']['signal'] = 'slow'
    else:
        factors['wt_stationary']['signal'] = 'congested'

    # 最大同帧数信号（驾驶视角下区分度有限，降低权重）
    if max_concurrent < 5:
        factors['max_concurrent']['signal'] = 'smooth'
    elif max_concurrent < 10:
        factors['max_concurrent']['signal'] = 'slow'
    else:
        factors['max_concurrent']['signal'] = 'congested'

    # ===== 综合投票（加权） =====
    # 面积占比是最可靠的区分指标（驾驶视角核心特征）
    # 速度指标在驾驶视角下不可靠（对向车辆速度高导致误判）
    signal_weights = {
        'area_ratio': 4.0,
        'nearby_ratio': 3.0,
        'wt_speed': 1.0,
        'wt_stationary': 1.0,
        'max_concurrent': 1.0
    }

    # 面积占比极强信号覆盖：当车辆面积占比极高(>15%)时，
    # 无论速度指标如何，都应判断为拥堵
    if avg_area_ratio >= 0.15:
        signal_weights['area_ratio'] = 8.0

    smooth_score = 0
    slow_score = 0
    congested_score = 0

    for key, f in factors.items():
        w = signal_weights[key]
        if f['signal'] == 'smooth':
            smooth_score += w
        elif f['signal'] == 'slow':
            slow_score += w
        elif f['signal'] == 'congested':
            congested_score += w

    # 判断逻辑
    if slow_score > smooth_score and slow_score > congested_score:
        status = '缓行'
    elif smooth_score > congested_score:
        status = '畅通'
    elif congested_score > smooth_score:
        status = '拥堵'
    else:
        status = '缓行'

    # 置信度评估
    total_weight = sum(signal_weights.values())
    dominant_score = max(smooth_score, slow_score, congested_score)
    dominant_ratio = dominant_score / total_weight
    if dominant_ratio >= 0.65:
        confidence = '高'
    elif dominant_ratio >= 0.45:
        confidence = '中'
    else:
        confidence = '低'

    return status, confidence, factors


def _empty_result(total_frames=0):
    """返回空结果"""
    return {
        'total_frames': total_frames,
        'total_detections': 0,
        'unique_vehicle_count': 0,
        'avg_detections_per_frame': 0,
        'traffic_status': '未知',
        'confidence': '低',
        'judgment_factors': {},
        'vehicle_statistics': {
            'total_vehicles': 0,
            'max_concurrent': 0,
            'min_concurrent': 0,
            'average_density': 0
        },
        'speed_statistics': {
            'avg_pixel_speed': 0,
            'avg_pixel_speed_per_sec': 0,
            'max_pixel_speed': 0,
            'min_pixel_speed': 0,
            'stationary_vehicle_ratio': 0,
            'avg_track_duration_frames': 0,
            'max_track_duration_frames': 0
        },
        'area_statistics': {
            'avg_vehicle_area_ratio': 0,
            'max_vehicle_area_ratio': 0
        },
        'class_distribution': {},
        'density_trend': [],
        'speed_trend': [],
        'traffic_status_distribution': {
            'smooth': 0,
            'slow': 0,
            'congested': 0
        },
        'data_source': 'empty'
    }


def analyze_video_results_fallback(video_path):
    """
    后备分析：当JSON检测数据不可用时，从标注视频中提取数据
    仅作为后备方案，精度有限
    """
    log_message(f"使用后备方案分析视频：{video_path}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise Exception(f"无法打开视频：{video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_area = video_width * video_height if video_width > 0 and video_height > 0 else 1

    frame_detections = []
    frame_density = []
    smooth_frames = 0
    slow_frames = 0
    congested_frames = 0

    frame_id = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width = frame.shape[:2]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_orange = np.array([0, 50, 50])
        upper_orange = np.array([30, 255, 255])
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.erode(mask, kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detection_count = sum(1 for c in contours if cv2.contourArea(c) > 100)
        frame_detections.append(detection_count)

        if frame_id % 10 == 0:
            frame_density.append(detection_count)

        if detection_count < 3:
            smooth_frames += 1
        elif detection_count < 8:
            slow_frames += 1
        else:
            congested_frames += 1

        frame_id += 1

        if frame_id % 100 == 0:
            log_message(f"已分析 {frame_id}/{total_frames} 帧")

    cap.release()

    total_detections = sum(frame_detections)
    avg_detections = total_detections / len(frame_detections) if frame_detections else 0
    max_density = max(frame_detections) if frame_detections else 0

    total_status_frames = smooth_frames + slow_frames + congested_frames
    if total_status_frames > 0:
        smooth_ratio = smooth_frames / total_status_frames
        slow_ratio = slow_frames / total_status_frames
        congested_ratio = congested_frames / total_status_frames
    else:
        smooth_ratio = slow_ratio = congested_ratio = 0

    # 简化的路况判断
    if avg_detections < 3:
        traffic_status = '畅通'
    elif avg_detections < 7:
        traffic_status = '缓行'
    else:
        traffic_status = '拥堵'

    log_message(f"后备分析完成 - 总检测数：{total_detections}, 路况参考：{traffic_status}（置信度：低）")

    return {
        'total_frames': total_frames,
        'total_detections': total_detections,
        'unique_vehicle_count': max_density,
        'avg_detections_per_frame': round(avg_detections, 2),
        'traffic_status': traffic_status,
        'confidence': '低',
        'judgment_factors': {},
        'vehicle_statistics': {
            'total_vehicles': max_density,
            'max_concurrent': max_density,
            'min_concurrent': min(frame_detections) if frame_detections else 0,
            'average_density': round(avg_detections, 2)
        },
        'speed_statistics': {
            'avg_pixel_speed': 0,
            'avg_pixel_speed_per_sec': 0,
            'max_pixel_speed': 0,
            'min_pixel_speed': 0,
            'stationary_vehicle_ratio': 0,
            'avg_track_duration_frames': 0,
            'max_track_duration_frames': 0
        },
        'area_statistics': {
            'avg_vehicle_area_ratio': 0,
            'max_vehicle_area_ratio': 0
        },
        'class_distribution': {'car': total_detections},
        'density_trend': frame_density[:50] if len(frame_density) > 50 else frame_density,
        'speed_trend': [],
        'traffic_status_distribution': {
            'smooth': round(smooth_ratio * 100, 2),
            'slow': round(slow_ratio * 100, 2),
            'congested': round(congested_ratio * 100, 2)
        },
        'data_source': 'fallback_video_analysis'
    }


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'success': True, 'status': 'healthy'})


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取后端状态"""
    global _psutil_initialized
    import psutil

    # 首次调用需要初始化 psutil 的 cpu 监控
    if not _psutil_initialized:
        psutil.cpu_percent(interval=None)
        _psutil_initialized = True

    uptime = (datetime.now() - backend_start_time).total_seconds()

    # 系统信息
    try:
        # interval=None 返回自上次调用以来的CPU使用率（非阻塞）
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        cpu_freq = psutil.cpu_freq()

        system_info = {
            'system_cpu_percent': cpu_percent,
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': round(cpu_freq.current, 0) if cpu_freq and cpu_freq.current else 0,
            'system_memory_percent': memory.percent,
            'system_memory_used_gb': round(memory.used / (1024**3), 2),
            'system_memory_total_gb': round(memory.total / (1024**3), 2),
            'num_threads': threading.active_count(),
            'cpu_details': {
                'physical_cores': psutil.cpu_count(logical=False) or 0,
                'logical_cores': psutil.cpu_count(logical=True) or 0
            }
        }
    except Exception as e:
        log_message(f"获取系统信息失败：{str(e)}")
        system_info = None

    return jsonify({
        'success': True,
        'uptime': int(uptime),
        'active_tasks': active_tasks,
        'system': system_info,
        'logs': logs[-20:]
    })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取日志"""
    return jsonify({
        'success': True,
        'logs': logs[-50:]
    })


@app.route('/api/process', methods=['POST'])
def process_video():
    """处理上传的视频"""
    global active_tasks

    if 'video' not in request.files:
        return jsonify({'error': '未找到视频文件'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的视频格式'}), 400

    with processing_lock:
        active_tasks += 1

    try:
        # 保存上传的文件到 PaddleDetection 目录
        # 使用 UUID 生成安全文件名，避免中文文件名问题
        filename = generate_safe_filename(file.filename)
        video_path = UPLOAD_FOLDER / filename
        log_message(f"保存视频文件：{file.filename} -> {filename}")
        file.save(str(video_path))

        # 执行 PaddleDetection 识别脚本
        output_video_name = Path(filename).stem
        output_video_path = OUTPUT_DIR / f"{output_video_name}.mp4"
        detection_json_path = OUTPUT_DIR / f"{output_video_name}_detection.json"

        log_message(f"开始执行识别：{filename}")

        import sys
        python_exe = sys.executable

        # 构建命令 - 直接使用当前 Python 解释器
        cmd = [
            python_exe,
            str(PADDLE_DETECTION_DIR / 'deploy' / 'pipeline' / 'pipeline.py'),
            '--config', str(PADDLE_DETECTION_DIR / 'deploy' / 'pipeline' / 'config' / 'infer_cfg_ppvehicle.yml'),
            '--video_file', str(video_path),
            '--device', 'GPU',
            '--output_dir', str(OUTPUT_DIR)
        ]

        log_message(f"执行命令：python PaddleDetection/deploy/pipeline/pipeline.py --config PaddleDetection/deploy/pipeline/config/infer_cfg_ppvehicle.yml --video_file {filename} --device GPU --output_dir PaddleDetection/output")

        # 执行命令
        try:
            result = subprocess.run(
                cmd,
                cwd=str(PADDLE_DETECTION_DIR),
                capture_output=True,
                text=True,
                timeout=600  # 10 分钟超时
            )

            if result.returncode != 0:
                log_message(f"识别过程出错：{result.stderr}")
                # 即使出错也尝试分析已有的输出
                if not output_video_path.exists() and not detection_json_path.exists():
                    return jsonify({'error': f'识别失败：{result.stderr}'}), 500

            log_message("识别完成")

        except subprocess.TimeoutExpired:
            log_message("识别超时")
            return jsonify({'error': '视频处理超时，请尝试较短的视频'}), 500
        except Exception as e:
            log_message(f"执行命令失败：{str(e)}")
            return jsonify({'error': f'执行失败：{str(e)}'}), 500

        # 检查输出文件
        if not output_video_path.exists():
            possible_files = list(OUTPUT_DIR.glob(f"{output_video_name}*.mp4"))
            if possible_files:
                output_video_path = possible_files[0]
            else:
                log_message("未找到输出视频文件")

        log_message(f"输出视频路径：{output_video_path}")

        # 分析检测结果：优先使用 JSON 检测数据
        log_message("开始分析检测结果")
        if detection_json_path.exists():
            log_message("使用pipeline检测数据(JSON)进行分析")
            analysis_result = analyze_from_detection_json(detection_json_path)
        else:
            # 查找可能的JSON文件
            possible_json = list(OUTPUT_DIR.glob(f"{output_video_name}*_detection.json"))
            if possible_json:
                log_message(f"使用检测数据文件：{possible_json[0]}")
                analysis_result = analyze_from_detection_json(possible_json[0])
            elif output_video_path.exists():
                log_message("未找到JSON检测数据，使用后备方案分析标注视频")
                analysis_result = analyze_video_results_fallback(output_video_path)
            else:
                log_message("无可用的分析数据源")
                analysis_result = _empty_result()

        # 生成视频 URL
        video_url = f"/api/output/{output_video_path.name}" if output_video_path.exists() else ""

        response_data = {
            **analysis_result,
            'annotated_video_url': video_url,
            'video_file_name': output_video_path.name if output_video_path.exists() else ''
        }

        log_message("处理完成，返回结果")
        return jsonify(response_data)

    except Exception as e:
        log_message(f"处理视频时发生错误：{str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理失败：{str(e)}'}), 500

    finally:
        with processing_lock:
            active_tasks -= 1


@app.route('/api/output/<filename>')
def serve_output_video(filename):
    """提供输出视频文件"""
    try:
        return send_from_directory(str(OUTPUT_DIR), filename)
    except Exception as e:
        log_message(f"提供视频文件失败：{str(e)}")
        return jsonify({'error': '文件不存在'}), 404


@app.route('/api/uploaded/<filename>')
def serve_uploaded_video(filename):
    """提供上传的视频文件"""
    try:
        return send_from_directory(str(UPLOAD_FOLDER), filename)
    except Exception as e:
        log_message(f"提供视频文件失败：{str(e)}")
        return jsonify({'error': '文件不存在'}), 404


if __name__ == '__main__':
    log_message("后端服务启动中...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
