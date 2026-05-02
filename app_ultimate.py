import os
import sys
import time
import json
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

BASE_DIR = Path(__file__).parent.absolute()
PADDLE_DETECTION_DIR = BASE_DIR / 'PaddleDetection'
OUTPUT_DIR = PADDLE_DETECTION_DIR / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
UPLOAD_FOLDER = PADDLE_DETECTION_DIR

backend_start_time = datetime.now()
active_tasks = 0
logs = []
processing_lock = threading.Lock()


class HybridTrafficAnalyzer:
    """混合路况分析器：HSV车辆计数(PaddleDetection输出) + 帧差法运动分析(原始视频)"""
    
    def __init__(self):
        self.fps = 25
    
    def count_vehicles_hsv(self, output_video_path):
        """从PaddleDetection输出视频中，用HSV检测橙色框来计数车辆"""
        cap = cv2.VideoCapture(str(output_video_path))
        if not cap.isOpened():
            return None
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_detections = []
        frame_density = []
        smooth_frames = 0
        slow_frames = 0
        congested_frames = 0
        vehicle_class_count = {}
        frame_id = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
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
            if detection_count > 0:
                vehicle_class_count['car'] = vehicle_class_count.get('car', 0) + detection_count
            if detection_count < 5:
                smooth_frames += 1
            elif detection_count < 12:
                slow_frames += 1
            else:
                congested_frames += 1
            frame_id += 1
        cap.release()
        if not frame_detections:
            return None
        total_detections = sum(frame_detections)
        avg_density = total_detections / len(frame_detections)
        max_density = max(frame_detections)
        total_status = smooth_frames + slow_frames + congested_frames
        if total_status > 0:
            smooth_ratio = smooth_frames / total_status
            slow_ratio = slow_frames / total_status
            congested_ratio = congested_frames / total_status
        else:
            smooth_ratio = slow_ratio = congested_ratio = 0
        return {
            'avg_density': round(avg_density, 2),
            'max_density': max_density,
            'total_detections': total_detections,
            'total_frames': total_frames,
            'frame_density': frame_density[:50],
            'smooth_frames': smooth_frames,
            'slow_frames': slow_frames,
            'congested_frames': congested_frames,
            'smooth_ratio': round(smooth_ratio * 100, 2),
            'slow_ratio': round(slow_ratio * 100, 2),
            'congested_ratio': round(congested_ratio * 100, 2),
            'vehicle_class_count': vehicle_class_count or {'car': total_detections}
        }
    
    def analyze_motion(self, original_video_path):
        """从原始视频中，用帧差法分析运动强度"""
        cap = cv2.VideoCapture(str(original_video_path))
        if not cap.isOpened():
            return None
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 25
        frame_id = 0
        motion_data = []
        prev_gray = None
        while frame_id < 300:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            if prev_gray is not None:
                frame_delta = cv2.absdiff(prev_gray, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                motion_intensity = np.sum(thresh) / 255
                motion_data.append(motion_intensity)
            prev_gray = gray
            frame_id += 1
        cap.release()
        if not motion_data:
            return None
        mid_point = len(motion_data) // 2
        first_half = motion_data[:mid_point]
        second_half = motion_data[mid_point:]
        avg_motion = np.mean(motion_data)
        first_half_motion = np.mean(first_half) if first_half else 0
        second_half_motion = np.mean(second_half) if second_half else 0
        motion_change = second_half_motion - first_half_motion
        motion_ratio = second_half_motion / first_half_motion if first_half_motion > 0 else 0
        return {
            'avg_motion': round(avg_motion, 2),
            'first_half_motion': round(first_half_motion, 2),
            'second_half_motion': round(second_half_motion, 2),
            'motion_change': round(motion_change, 2),
            'motion_ratio': round(motion_ratio, 3),
            'analyzed_frames': frame_id
        }
    
    def judge_traffic(self, hsv_result, motion_result):
        """综合HSV车辆计数和运动分析，判断路况"""
        if hsv_result is None and motion_result is None:
            return '畅通', 0.0
        
        avg_density = hsv_result['avg_density'] if hsv_result else -1
        has_hsv = hsv_result is not None
        
        avg_motion = motion_result['avg_motion'] if motion_result else 0
        motion_change = motion_result['motion_change'] if motion_result else 0
        motion_ratio = motion_result['motion_ratio'] if motion_result else 1.0
        second_half_motion = motion_result['second_half_motion'] if motion_result else 0
        has_motion = motion_result is not None
        
        congested_ratio_val = 0
        if hsv_result:
            total_f = hsv_result['smooth_frames'] + hsv_result['slow_frames'] + hsv_result['congested_frames']
            if total_f > 0:
                congested_ratio_val = hsv_result['congested_frames'] / total_f
        
        condition = '畅通'
        confidence = 0.0
        
        if has_hsv and has_motion:
            if congested_ratio_val > 0.8 and avg_density >= 12:
                condition = '拥堵'
                confidence = 0.95
            elif avg_density >= 8 and motion_ratio < 0.5:
                condition = '拥堵'
                confidence = 0.90
            elif avg_density >= 12 and second_half_motion < 15000:
                condition = '拥堵'
                confidence = 0.85
            elif avg_density >= 15 and avg_motion < 25000:
                condition = '拥堵'
                confidence = 0.85
            elif avg_density >= 12 and avg_motion < 40000:
                condition = '缓行'
                confidence = 0.75
            elif 5 <= avg_density < 12 and motion_ratio < 0.5:
                condition = '缓行'
                confidence = 0.80
            elif 5 <= avg_density < 12 and avg_motion < 20000:
                condition = '缓行'
                confidence = 0.70
            elif 5 <= avg_density < 12 and avg_motion >= 20000:
                condition = '畅通'
                confidence = 0.75
            elif avg_density < 5:
                condition = '畅通'
                confidence = 0.85
            else:
                condition = '缓行'
                confidence = 0.60
        
        elif has_motion and not has_hsv:
            if motion_ratio < 0.3:
                condition = '拥堵'
                confidence = 0.85
            elif motion_ratio < 0.5 and motion_change < -20000:
                condition = '拥堵'
                confidence = 0.80
            elif avg_motion < 10000 and abs(motion_change) < 5000:
                condition = '畅通'
                confidence = 0.80
            elif 10000 <= avg_motion < 30000 and abs(motion_change) < 10000:
                condition = '缓行'
                confidence = 0.70
            elif avg_motion > 30000 and motion_change < -30000:
                condition = '拥堵'
                confidence = 0.85
            elif 10000 <= avg_motion < 30000 and motion_change > 0:
                condition = '缓行'
                confidence = 0.70
            elif avg_motion < 15000:
                condition = '畅通'
                confidence = 0.60
            else:
                condition = '缓行'
                confidence = 0.55
        
        elif has_hsv and not has_motion:
            if avg_density < 5:
                condition = '畅通'
                confidence = 0.60
            elif avg_density < 12:
                condition = '缓行'
                confidence = 0.55
            else:
                condition = '拥堵'
                confidence = 0.60
        
        return condition, confidence


def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    logs.append(log_entry)
    print(log_entry)
    if len(logs) > 100:
        logs.pop(0)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def analyze_video_results(original_video_path, output_video_path):
    """分析视频：HSV计数(输出视频) + 运动分析(原始视频) + 综合判断"""
    log_message(f"开始分析视频 - 原始：{original_video_path}, 输出：{output_video_path}")
    
    analyzer = HybridTrafficAnalyzer()
    
    hsv_result = None
    motion_result = None
    
    if output_video_path and Path(output_video_path).exists():
        hsv_result = analyzer.count_vehicles_hsv(output_video_path)
        log_message(f"HSV分析完成 - 平均密度：{hsv_result['avg_density'] if hsv_result else 'N/A'}")
    
    if original_video_path and Path(original_video_path).exists():
        motion_result = analyzer.analyze_motion(original_video_path)
        log_message(f"运动分析完成 - 平均运动：{motion_result['avg_motion'] if motion_result else 'N/A'}")
    
    traffic_status, confidence = analyzer.judge_traffic(hsv_result, motion_result)
    
    # 构建兼容前端的返回数据
    if hsv_result:
        avg_density = hsv_result['avg_density']
        max_density = hsv_result['max_density']
        total_detections = hsv_result['total_detections']
        total_frames = hsv_result['total_frames']
        smooth_frames = hsv_result['smooth_frames']
        slow_frames = hsv_result['slow_frames']
        congested_frames = hsv_result['congested_frames']
        frame_density = hsv_result['frame_density']
        vehicle_class_count = hsv_result['vehicle_class_count']
        smooth_ratio = hsv_result['smooth_ratio']
        slow_ratio = hsv_result['slow_ratio']
        congested_ratio = hsv_result['congested_ratio']
    else:
        avg_density = 0
        max_density = 0
        total_detections = 0
        total_frames = 0
        smooth_frames = slow_frames = congested_frames = 0
        frame_density = []
        vehicle_class_count = {'car': 0}
        smooth_ratio = slow_ratio = congested_ratio = 0
    
    unique_vehicle_count = max_density if max_density > 0 else 1
    
    log_message(f"分析完成 - 路况：{traffic_status}, 置信度：{confidence}")
    
    return {
        'total_frames': total_frames,
        'total_detections': total_detections,
        'unique_vehicle_count': unique_vehicle_count,
        'avg_detections_per_frame': round(avg_density, 2),
        'traffic_status': traffic_status,
        'confidence': round(confidence, 2),
        'vehicle_statistics': {
            'total_vehicles': unique_vehicle_count,
            'max_concurrent': max_density,
            'average_density': round(avg_density, 2)
        },
        'class_distribution': vehicle_class_count,
        'density_trend': frame_density,
        'traffic_status_distribution': {
            'smooth': smooth_ratio,
            'slow': slow_ratio,
            'congested': congested_ratio
        }
    }


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'success': True, 'status': 'healthy'})


@app.route('/api/status', methods=['GET'])
def get_status():
    import psutil
    uptime = (datetime.now() - backend_start_time).total_seconds()
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        cpu_freq = psutil.cpu_freq()
        system_info = {
            'system_cpu_percent': cpu_percent,
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': round(cpu_freq.current, 0) if cpu_freq else 0,
            'system_memory_percent': memory.percent,
            'system_memory_used_gb': round(memory.used / (1024**3), 2),
            'system_memory_total_gb': round(memory.total / (1024**3), 2),
            'num_threads': threading.active_count(),
            'cpu_details': {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True)
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
    return jsonify({'success': True, 'logs': logs[-50:]})


@app.route('/api/process', methods=['POST'])
def process_video():
    """处理上传的视频 - PaddleDetection识别 + 混合路况分析"""
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
        filename = secure_filename(file.filename)
        if not filename or filename == '.':
            filename = 'upload.mp4'
        video_path = UPLOAD_FOLDER / filename
        log_message(f"保存视频文件：{filename}")
        file.save(str(video_path))
        
        output_video_name = Path(filename).stem
        output_video_path = OUTPUT_DIR / f"{output_video_name}.mp4"
        
        log_message(f"开始执行PaddleDetection识别：{filename}")
        
        import sys
        python_exe = sys.executable
        
        cmd = [
            python_exe,
            str(PADDLE_DETECTION_DIR / 'deploy' / 'pipeline' / 'pipeline.py'),
            '--config', str(PADDLE_DETECTION_DIR / 'deploy' / 'pipeline' / 'config' / 'infer_cfg_ppvehicle.yml'),
            '--video_file', str(video_path),
            '--device', 'GPU',
            '--output_dir', str(OUTPUT_DIR)
        ]
        
        log_message(f"执行命令：python PaddleDetection/deploy/pipeline/pipeline.py --video_file {filename} --device GPU")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(PADDLE_DETECTION_DIR),
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                log_message(f"识别过程出错：{result.stderr}")
                if not output_video_path.exists():
                    return jsonify({'error': f'识别失败：{result.stderr}'}), 500
            
            log_message("PaddleDetection识别完成")
            
        except subprocess.TimeoutExpired:
            log_message("识别超时")
            return jsonify({'error': '视频处理超时，请尝试较短的视频'}), 500
        except Exception as e:
            log_message(f"执行命令失败：{str(e)}")
            return jsonify({'error': f'执行失败：{str(e)}'}), 500
        
        if not output_video_path.exists():
            possible_files = list(OUTPUT_DIR.glob(f"{output_video_name}*"))
            if possible_files:
                output_video_path = possible_files[0]
            else:
                log_message("未找到输出视频，使用原始视频进行分析")
                output_video_path = video_path
        
        log_message(f"输出视频路径：{output_video_path}")
        
        # 关键改动：同时传入原始视频和输出视频路径
        log_message("开始混合路况分析（HSV计数+运动分析）")
        analysis_result = analyze_video_results(str(video_path), str(output_video_path))
        
        video_url = f"/api/output/{output_video_path.name}"
        
        response_data = {
            **analysis_result,
            'annotated_video_url': video_url,
            'video_file_name': output_video_path.name
        }
        
        log_message(f"处理完成 - 路况：{analysis_result['traffic_status']}")
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
    try:
        return send_from_directory(str(OUTPUT_DIR), filename)
    except Exception as e:
        log_message(f"提供视频文件失败：{str(e)}")
        return jsonify({'error': '文件不存在'}), 404


@app.route('/api/uploaded/<filename>')
def serve_uploaded_video(filename):
    try:
        return send_from_directory(str(UPLOAD_FOLDER), filename)
    except Exception as e:
        log_message(f"提供视频文件失败：{str(e)}")
        return jsonify({'error': '文件不存在'}), 404


if __name__ == '__main__':
    log_message("混合路况分析后端服务启动中...（PaddleDetection识别 + HSV计数 + 运动分析）")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
