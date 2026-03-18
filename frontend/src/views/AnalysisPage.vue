<template>
  <div class="analysis-page">
    <header class="app-header-bar">
      <nav class="nav-bar">
        <router-link to="/" class="nav-logo">
          <Car theme="outline" size="24" fill="#000000" :stroke-width="2" />
          <span>交通路况智能分析</span>
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link" exact-active-class="active">
            <Home theme="outline" size="20" fill="#000000" :stroke-width="2" />
            <span>项目介绍</span>
          </router-link>
          <router-link to="/analysis" class="nav-link" exact-active-class="active">
            <Analysis theme="outline" size="20" fill="#000000" :stroke-width="2" />
            <span>开始分析</span>
          </router-link>
        </div>
      </nav>
    </header>

    <main class="main-content">
      <!-- 顶部状态栏：系统监控 -->
      <div class="status-bar">
        <!-- 左侧：后端状态 -->
        <div class="status-section backend-section" :class="{ offline: !backendStatus.online }">
          <div class="status-header">
            <span class="status-dot" :class="{ online: backendStatus.online }"></span>
            <span>后端服务: {{ backendStatus.online ? '运行中' : '未启动' }}</span>
          </div>
          <div class="status-details" v-if="backendStatus.online">
            <span>运行时间: {{ formatUptime(backendStatus.uptime) }}</span>
            <span>任务数: {{ backendStatus.activeTasks }}</span>
          </div>
          <div class="status-warning" v-else>
            请运行: python app.py
          </div>
        </div>

        <!-- 中间：硬件监控仪表盘 -->
        <div class="status-section hardware-section" v-if="backendStatus.system">
          <div class="hardware-grid">
            <div class="hardware-item">
              <div class="hardware-label">CPU</div>
              <div class="hardware-value">
                <span class="value">{{ backendStatus.system.system_cpu_percent || 0 }}%</span>
                <span class="sub">{{ backendStatus.system.cpu_count || 0 }} 核心</span>
              </div>
              <div class="hardware-bar">
                <div class="bar-fill" :style="{ width: (backendStatus.system.system_cpu_percent || 0) + '%' }"></div>
              </div>
            </div>
            <div class="hardware-item">
              <div class="hardware-label">内存</div>
              <div class="hardware-value">
                <span class="value">{{ backendStatus.system.system_memory_percent || 0 }}%</span>
                <span class="sub">{{ backendStatus.system.system_memory_used_gb || 0 }} / {{ backendStatus.system.system_memory_total_gb || 0 }} GB</span>
              </div>
              <div class="hardware-bar">
                <div class="bar-fill" :style="{ width: (backendStatus.system.system_memory_percent || 0) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：硬件详情 -->
        <div class="status-section info-section" v-if="backendStatus.system">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">CPU频率</span>
              <span class="info-value">{{ backendStatus.system.cpu_freq || 0 }} MHz</span>
            </div>
            <div class="info-item">
              <span class="info-label">物理核心</span>
              <span class="info-value">{{ backendStatus.system.cpu_details?.physical_cores || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">逻辑核心</span>
              <span class="info-value">{{ backendStatus.system.cpu_details?.logical_cores || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">进程线程</span>
              <span class="info-value">{{ backendStatus.system.num_threads || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 终端日志 -->
      <div class="terminal-panel">
        <div class="terminal-header">
          <span>终端日志</span>
          <button class="btn-clear" @click="clearLogs">清空</button>
        </div>
        <div class="terminal-content" ref="terminalContent">
          <div v-for="(log, index) in logs" :key="index" class="log-line">
            {{ log }}
          </div>
          <div v-if="logs.length === 0" class="log-empty">等待日志...</div>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="content-grid">
        <!-- 左侧面板 -->
        <div class="left-panel">
          <div class="card">
            <h2>视频上传</h2>
            <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
              <input
                type="file"
                ref="fileInput"
                @change="handleFileSelect"
                accept="video/*"
                class="file-input"
                id="video-upload"
              />
              <label for="video-upload" class="upload-label">
                <p class="upload-text">点击选择视频文件或拖拽到此处</p>
                <p class="upload-hint">支持 MP4, AVI, MOV 格式</p>
              </label>
            </div>

            <div v-if="uploadedFile" class="file-info">
              <div class="file-details">
                <span class="file-name">{{ uploadedFile }}</span>
                <span class="file-size">{{ formatFileSize(fileSize) }}</span>
              </div>
              <button
                @click="processVideo"
                class="btn btn-success"
                :disabled="processing"
              >
                {{ processing ? '处理中...' : '开始分析' }}
              </button>
            </div>

            <!-- 原始视频预览 -->
            <div v-if="videoPreview" class="video-preview-container">
              <h3>原始视频预览</h3>
              <video ref="videoPlayer" :src="videoPreview" controls class="video-player"></video>
            </div>

            <!-- 处理进度 -->
            <div v-if="processing" class="processing-status">
              <div class="spinner"></div>
              <p>正在分析视频，请稍候...</p>
              <p class="progress-hint">首次加载模型可能需要一些时间</p>
            </div>
          </div>

          <!-- 输出视频预览 -->
          <div v-if="annotatedVideoUrl" class="card">
            <h2>输出视频预览</h2>
            <div v-if="videoLoading" class="video-loading">
              <div class="loading-spinner"></div>
              <span>视频加载中...</span>
            </div>
            <div v-if="videoError" class="video-error-container">
              <div class="error-icon">⚠️</div>
              <h3>视频加载失败</h3>
              <p class="error-message">{{ videoErrorMessage }}</p>
              <div class="error-suggestions">
                <p><strong>可能的原因：</strong></p>
                <ul>
                  <li>视频格式不支持（当前支持：MP4, WebM, Ogg）</li>
                  <li>视频编码格式不兼容</li>
                  <li>视频文件损坏或未完全生成</li>
                </ul>
                <p><strong>建议操作：</strong></p>
                <ol>
                  <li>点击"重新加载"按钮重试</li>
                  <li>尝试下载视频到本地播放</li>
                  <li>检查后端日志确认视频处理是否完成</li>
                </ol>
              </div>
              <div class="error-actions">
                <button @click="retryLoadVideo" class="btn btn-primary">
                  🔄 重新加载
                </button>
                <a
                  :href="annotatedVideoUrl"
                  download="traffic_analysis_output.mp4"
                  class="btn btn-secondary"
                >
                  ⬇️ 下载视频
                </a>
              </div>
            </div>
            <video
              v-show="!videoLoading && !videoError"
              ref="annotatedVideoPlayer"
              :src="annotatedVideoUrl"
              controls
              class="video-player annotated-video"
              preload="metadata"
              @error="handleVideoError"
              @canplay="handleVideoReady"
              @loadedmetadata="handleVideoMetadata"
            ></video>
            <div v-if="!videoError" class="video-actions">
              <a
                :href="annotatedVideoUrl"
                download="traffic_analysis_output.mp4"
                class="btn btn-secondary"
              >
                下载视频
              </a>
              <span class="video-path">文件：{{ outputFileName }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧面板 -->
        <div class="right-panel">
          <div v-if="analysisResult" class="analysis-content">
            <!-- 统计卡片 -->
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon">V</div>
                <div class="stat-content">
                  <h3>检测车辆总数</h3>
                  <p class="stat-value">{{ analysisResult.total_detections }}</p>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">I</div>
                <div class="stat-content">
                  <h3>唯一车辆数</h3>
                  <p class="stat-value">{{ uniqueVehicleCount }}</p>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">A</div>
                <div class="stat-content">
                  <h3>平均每帧</h3>
                  <p class="stat-value">{{ analysisResult.avg_detections_per_frame }}</p>
                </div>
              </div>
              <div class="stat-card status-card">
                <div class="stat-icon">S</div>
                <div class="stat-content">
                  <h3>交通状态</h3>
                  <p class="stat-value status-value">{{ analysisResult.traffic_status }}</p>
                </div>
              </div>
            </div>

            <!-- 出行建议 -->
            <div class="card suggestion-card">
              <h2>出行建议</h2>
              <div class="suggestion-content" :class="trafficStatusClass">
                <p>{{ travelSuggestion }}</p>
              </div>
            </div>

            <!-- 车型分布图表 -->
            <div class="card chart-card">
              <h2>车型分布统计</h2>
              <div ref="classChart" class="chart-container"></div>
            </div>

            <!-- 密度趋势 -->
            <div class="card chart-card">
              <h2>车流密度趋势</h2>
              <div ref="trendChart" class="chart-container"></div>
            </div>
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">[ ]</div>
            <p>暂无分析数据</p>
            <p class="empty-hint">请先上传视频进行分析</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import gsap from 'gsap'
import {
  Car,
  Home,
  Analysis
} from '@icon-park/vue-next'

const API_BASE = '/api'  // 使用 Vite 代理到后端

export default {
  name: 'AnalysisPage',
  components: {
    Car,
    Home,
    Analysis
  },
  setup() {
    const fileInput = ref(null)
    const videoPlayer = ref(null)
    const annotatedVideoPlayer = ref(null)
    const classChart = ref(null)
    const trendChart = ref(null)

    const uploadedFile = ref(null)
    const fileSize = ref(0)
    const videoPreview = ref(null)
    const processing = ref(false)
    const analysisResult = ref(null)
    const annotatedVideoUrl = ref('')
    const outputFileName = ref('')
    const videoLoading = ref(false)
    const videoError = ref(false)
    const videoErrorMessage = ref('')
    const videoErrorCode = ref(null)
    const backendStatus = ref({
      online: false,
      uptime: 0,
      activeTasks: 0,
      system: null
    })
    const logs = ref([])
    const terminalContent = ref(null)

    let classChartInstance = null
    let trendChartInstance = null

    const hasResult = computed(() => analysisResult.value !== null)

    const uniqueVehicleCount = computed(() => {
      return analysisResult.value?.unique_vehicle_count || 0
    })

    // 出行建议
    const travelSuggestion = computed(() => {
      const status = analysisResult.value?.traffic_status || ''
      if (status === '畅通') {
        return '道路畅通，适合出行。建议保持安全车速，愉快出行。'
      } else if (status === '缓行') {
        return '前方道路缓行，建议提前规划路线或绕道行驶，注意保持车距。'
      } else if (status === '拥堵') {
        return '严重拥堵，建议绕行或推迟出行时间。如已在路上，请保持耐心。'
      }
      return '请上传视频进行分析，获取出行建议。'
    })

    const trafficStatusClass = computed(() => {
      const status = analysisResult.value?.traffic_status || ''
      return {
        'suggestion-smooth': status === '畅通',
        'suggestion-slow': status === '缓行',
        'suggestion-congested': status === '拥堵'
      }
    })

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        uploadedFile.value = file.name
        fileSize.value = file.size
        videoPreview.value = URL.createObjectURL(file)
        annotatedVideoUrl.value = ''
        outputFileName.value = ''
        analysisResult.value = null
      }
    }

    const handleDrop = (event) => {
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('video/')) {
        uploadedFile.value = file.name
        fileSize.value = file.size
        videoPreview.value = URL.createObjectURL(file)
        annotatedVideoUrl.value = ''
        outputFileName.value = ''
        analysisResult.value = null
      }
    }

    const handleVideoError = (event) => {
      console.error('视频加载失败:', event)
      videoLoading.value = false
      videoError.value = true
          
      // 获取详细错误信息
      const videoElement = event?.target
      const errorCode = videoElement?.error?.code
      const errorMessage = videoElement?.error?.message || '未知错误'
          
      videoErrorCode.value = errorCode
          
      // 根据错误代码提供详细的错误信息
      switch (errorCode) {
        case 1: // MEDIA_ERR_ABORTED
          videoErrorMessage.value = '视频加载被用户中止'
          break
        case 2: // MEDIA_ERR_NETWORK
          videoErrorMessage.value = '网络错误导致视频加载失败'
          break
        case 3: // MEDIA_ERR_DECODE
          videoErrorMessage.value = '视频解码错误：该视频格式或编码不受浏览器支持'
          break
        case 4: // MEDIA_ERR_SRC_NOT_SUPPORTED
          videoErrorMessage.value = '视频源不支持或文件不存在'
          break
        default:
          videoErrorMessage.value = `视频加载失败：${errorMessage}`
      }
          
      console.error('视频错误详情:', {
        code: errorCode,
        message: errorMessage,
        src: videoElement?.currentSrc
      })
    }

    const handleVideoReady = () => {
      console.log('视频加载成功')
      videoLoading.value = false
      videoError.value = false
      videoErrorMessage.value = ''
    }
    
    const handleVideoMetadata = () => {
      console.log('视频元数据加载成功:', {
        duration: annotatedVideoPlayer.value?.duration,
        width: annotatedVideoPlayer.value?.videoWidth,
        height: annotatedVideoPlayer.value?.videoHeight
      })
    }

    const retryLoadVideo = () => {
      if (!annotatedVideoPlayer.value) return
      videoError.value = false
      videoLoading.value = true
      annotatedVideoPlayer.value.load()
    }

    const processVideo = async () => {
      if (!uploadedFile.value) return
      processing.value = true

      try {
        const formData = new FormData()
        formData.append('video', fileInput.value.files[0])

        const response = await axios.post(`${API_BASE}/process`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 600000  // 10分钟超时
        })

        const data = response.data

        analysisResult.value = {
          total_frames: data.total_frames,
          total_detections: data.total_detections,
          unique_vehicle_count: data.unique_vehicle_count,
          avg_detections_per_frame: data.avg_detections_per_frame,
          traffic_status: data.traffic_status,
          vehicle_statistics: data.vehicle_statistics,
          class_distribution: data.class_distribution,
          density_trend: data.density_trend,
        }

        // 视频 URL 处理 - 简化版本
        const videoUrl = data.annotated_video_url
        if (videoUrl) {
          videoLoading.value = true
          videoError.value = false
          videoErrorMessage.value = '' // 清空错误信息
          annotatedVideoUrl.value = videoUrl
          outputFileName.value = videoUrl.split('/').pop()
          
          console.log('📹 使用视频 URL:', annotatedVideoUrl.value)
          
          // 验证 URL 是否可访问（不强制要求成功）
          try {
            const testResponse = await fetch(videoUrl, { method: 'HEAD' })
            if (testResponse.ok) {
              console.log('✅ 视频 URL 验证成功')
              console.log('Content-Type:', testResponse.headers.get('Content-Type'))
              
              // 检查 Content-Type 是否是视频
              const contentType = testResponse.headers.get('Content-Type')
              if (!contentType || !contentType.includes('video')) {
                console.warn('⚠️  响应类型不是视频:', contentType)
              }
            } else {
              console.warn('⚠️  视频 URL 返回状态码:', testResponse.status)
            }
          } catch (fetchError) {
            console.warn('⚠️  视频 URL 验证失败，但会继续尝试加载:', fetchError.message)
          }
        }

        renderCharts()

      } catch (error) {
        console.error('处理视频失败:', error)
        alert('处理视频失败: ' + (error.response?.data?.error || error.message))
      } finally {
        processing.value = false
      }
    }

    const renderCharts = () => {
      if (!analysisResult.value) return

      setTimeout(() => {
        if (classChart.value) {
          const classChartRect = classChart.value.getBoundingClientRect()
          if (classChartRect.width > 0 && classChartRect.height > 0) {
            if (classChartInstance) classChartInstance.dispose()

            classChartInstance = echarts.init(classChart.value)
            const classData = Object.entries(analysisResult.value.class_distribution).map(([name, value]) => ({
              value,
              name: getVehicleName(name) || name
            }))

            classChartInstance.setOption({
              backgroundColor: 'transparent',
              tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
              series: [{
                name: '车型分布',
                type: 'pie',
                radius: ['40%', '70%'],
                itemStyle: { borderRadius: 10, borderColor: '#0a0a0f', borderWidth: 2 },
                label: { show: true, formatter: '{b}: {d}%' },
                data: classData,
                color: ['#ff6b35', '#00d4aa', '#7c3aed', '#f59e0b', '#06b6d4', '#ec4899']
              }]
            })
          }
        }

        if (trendChart.value && analysisResult.value.density_trend?.length > 0) {
          const trendChartRect = trendChart.value.getBoundingClientRect()
          if (trendChartRect.width > 0 && trendChartRect.height > 0) {
            if (trendChartInstance) trendChartInstance.dispose()

            trendChartInstance = echarts.init(trendChart.value)
            const trendData = analysisResult.value.density_trend

            trendChartInstance.setOption({
              backgroundColor: 'transparent',
              tooltip: { trigger: 'axis' },
              grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
              xAxis: {
                type: 'category',
                boundaryGap: false,
                data: trendData.map((_, i) => `帧${(i * 30 + 1)}`),
                axisLine: { lineStyle: { color: '#444' } },
                axisLabel: { color: '#a0a0b0' }
              },
              yAxis: {
                type: 'value',
                name: '车辆数',
                axisLine: { show: false },
                splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
                axisLabel: { color: '#a0a0b0' }
              },
              series: [{
                name: '车流密度',
                type: 'line',
                smooth: true,
                data: trendData,
                lineStyle: { color: '#ff6b35', width: 3 },
                areaStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(255,107,53,0.4)' },
                    { offset: 1, color: 'rgba(255,107,53,0.05)' }
                  ])
                },
                itemStyle: { color: '#ff6b35' }
              }]
            })
          }
        }
      }, 100)
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const getVehicleName = (type) => {
      const names = { 'car': '汽车', 'truck': '卡车', 'bus': '公交车', 'motorcycle': '摩托车', 'bicycle': '自行车' }
      return names[type] || type
    }

    const formatUptime = (seconds) => {
      if (!seconds) return '0秒'
      const h = Math.floor(seconds / 3600)
      const m = Math.floor((seconds % 3600) / 60)
      const s = Math.floor(seconds % 60)
      if (h > 0) return `${h}小时${m}分`
      if (m > 0) return `${m}分${s}秒`
      return `${s}秒`
    }

    const updateBackendStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE}/status`, { timeout: 3000 })
        if (response.data.success) {
          backendStatus.value = {
            online: true,
            uptime: response.data.uptime,
            activeTasks: response.data.active_tasks,
            system: response.data.system
          }
          if (response.data.logs?.length > 0) {
            logs.value = response.data.logs
          }
        }
      } catch (error) {
        backendStatus.value.online = false
        backendStatus.value.system = null
      }
    }

    const fetchLogs = async () => {
      try {
        const response = await axios.get(`${API_BASE}/logs`)
        if (response.data.success) {
          logs.value = response.data.logs
          nextTick(() => {
            if (terminalContent.value) {
              terminalContent.value.scrollTop = terminalContent.value.scrollHeight
            }
          })
        }
      } catch (error) {}
    }

    const clearLogs = () => { logs.value = [] }

    const statusInterval = setInterval(() => {
      updateBackendStatus()
      if (processing.value) { fetchLogs() }
    }, 2000)

    onMounted(() => {
      axios.get(`${API_BASE}/health`).catch(() => {})
      updateBackendStatus()
    })

    watch(analysisResult, (val) => {
      if (val) {
        nextTick(() => {
          const stats = document.querySelectorAll('.stat-card')
          if (stats.length) {
            gsap.from(stats, { opacity: 0, y: 30, stagger: 0.1, duration: 0.6, ease: 'power2.out' })
          }
        })
      }
    })

    onUnmounted(() => {
      clearInterval(statusInterval)
      if (classChartInstance) classChartInstance.dispose()
      if (trendChartInstance) trendChartInstance.dispose()
    })

    return {
      fileInput, videoPlayer, annotatedVideoPlayer, classChart, trendChart,
      uploadedFile, fileSize, videoPreview, processing, analysisResult,
      annotatedVideoUrl, outputFileName, videoLoading, videoError, backendStatus, logs, terminalContent,
      uniqueVehicleCount, travelSuggestion, trafficStatusClass,
      handleFileSelect, handleDrop, handleVideoError, handleVideoReady, retryLoadVideo, processVideo,
      formatFileSize, getVehicleName, formatUptime, clearLogs
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.analysis-page {
  min-height: 100vh;
  background: #ffffff;
  color: #000000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-header-bar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: #ffffff;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 2px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 40px;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.25rem;
  font-weight: 700;
  color: #000000;
  text-decoration: none;
  letter-spacing: -0.02em;
  transition: transform 0.3s ease;
}

.nav-logo:hover {
  transform: translateX(4px);
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #000000;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 10px 20px;
  border-radius: 20px;
  background: transparent;
}

.nav-link:hover {
  color: #000000;
  background: #f5f5f5;
}

.nav-link.active {
  color: #000000;
  background: #f5f5f5;
  font-weight: 600;
}

.main-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 40px 24px;
  padding-top: 80px;
}

/* 状态栏 */
.status-bar {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.status-section {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.status-section.offline {
  border-color: #e74c3c;
  background: #fff5f5;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e74c3c;
}

.status-dot.online {
  background: #10b981;
}

.status-details {
  display: flex;
  gap: 16px;
  font-size: 0.9rem;
  color: #333333;
}

.status-warning {
  color: #e74c3c;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 硬件监控 */
.hardware-grid {
  display: flex;
  gap: 24px;
}

.hardware-item {
  flex: 1;
}

.hardware-label {
  font-size: 0.85rem;
  color: #666666;
  margin-bottom: 4px;
}

.hardware-value {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.hardware-value .value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #3b82f6;
}

.hardware-value .sub {
  font-size: 0.8rem;
  color: #666666;
}

.hardware-bar {
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  margin-top: 8px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  border-radius: 3px;
  transition: width 0.5s;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.info-label {
  color: #666666;
}

.info-value {
  color: #000000;
  font-weight: 500;
}

/* 终端 */
.terminal-panel {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
}

.terminal-header span {
  font-size: 0.95rem;
  color: #000000;
  font-weight: 600;
}

.btn-clear {
  background: transparent;
  border: 2px solid #e0e0e0;
  color: #000000;
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-clear:hover {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #ffffff;
}

.terminal-content {
  max-height: 120px;
  overflow-y: auto;
  padding: 12px 20px;
  font-family: 'Consolas', monospace;
  font-size: 0.8rem;
  background: #fafafa;
}

.log-line {
  color: #000000;
  line-height: 1.6;
  padding: 2px 0;
}

.log-empty {
  color: #666666;
  font-style: italic;
}

/* 内容区 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 24px;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.card h2 {
  font-size: 1.5rem;
  color: #000000;
  margin-bottom: 24px;
  font-weight: 700;
}

/* 出行建议 */
.suggestion-card {
  border-left: 4px solid #3b82f6;
}

.suggestion-card.suggestion-smooth {
  border-color: #10b981;
}

.suggestion-card.suggestion-slow {
  border-color: #f59e0b;
}

.suggestion-card.suggestion-congested {
  border-color: #e74c3c;
}

.suggestion-content {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 12px;
}

.suggestion-content p {
  font-size: 1rem;
  line-height: 1.7;
  color: #000000;
  margin: 0;
}

.suggestion-smooth .suggestion-content {
  background: #ecfdf5;
}

.suggestion-smooth .suggestion-content p {
  color: #10b981;
}

.suggestion-slow .suggestion-content {
  background: #fffbeb;
}

.suggestion-slow .suggestion-content p {
  color: #f59e0b;
}

.suggestion-congested .suggestion-content {
  background: #fef2f2;
}

.suggestion-congested .suggestion-content p {
  color: #e74c3c;
}

/* 上传 */
.upload-area {
  position: relative;
  border: 2px dashed #e0e0e0;
  border-radius: 20px;
  padding: 48px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: #f5f5f5;
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-label {
  cursor: pointer;
}

.upload-text {
  font-size: 1.1rem;
  color: #000000;
  margin-bottom: 8px;
  font-weight: 500;
}

.upload-hint {
  font-size: 0.9rem;
  color: #666666;
}

.file-info {
  margin-top: 24px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  color: #000000;
  font-weight: 600;
}

.file-size {
  font-size: 0.85rem;
  color: #666666;
}

.video-preview-container {
  margin-top: 24px;
}

.video-preview-container h3 {
  font-size: 1.1rem;
  color: #000000;
  margin-bottom: 16px;
  font-weight: 600;
}

.video-player {
  width: 100%;
  border-radius: 16px;
  max-height: 400px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
.video-error-container {
  text-align: center;
  padding: 32px 24px;
  background: #fef2f2;
  border: 2px solid #e74c3c;
  border-radius: 16px;
  margin: 16px 0;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.video-error-container h3 {
  font-size: 1.3rem;
  color: #e74c3c;
  margin-bottom: 12px;
}

.error-message {
  font-size: 1rem;
  color: #000000;
  margin: 16px 0;
  line-height: 1.6;
}

.error-suggestions {
  text-align: left;
  background: #ffffff;
  padding: 16px;
  border-radius: 12px;
  margin: 16px 0;
  border: 2px solid #e0e0e0;
}

.error-suggestions p {
  margin: 8px 0;
  color: #000000;
}

.error-suggestions ul,
.error-suggestions ol {
  margin: 8px 0 8px 20px;
  color: #333333;
}

.error-suggestions li {
  margin: 4px 0;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 16px;
}

.video-loading {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e0e0e0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.video-error {
  color: #e74c3c;
  text-align: center;
  padding: 16px;
  background: #fef2f2;
  border-radius: 8px;
  margin-top: 12px;
  border: 2px solid #e74c3c;
}

.processing-status {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e0e0e0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.progress-hint {
  font-size: 0.85rem;
  color: #666666;
  margin-top: 8px;
}

.annotated-video {
  border: 2px solid #e0e0e0;
}

.video-actions {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.video-path {
  font-size: 0.8rem;
  color: #666666;
}

.video-loading {
  position: relative;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: #f5f5f5;
  border-radius: 16px;
  border: 2px solid #e0e0e0;
  padding: 40px;
}

.video-loading .loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e0e0e0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.video-loading span {
  font-size: 0.95rem;
  color: #666666;
}

.video-error {
  margin-top: 12px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 2px solid #e74c3c;
  border-radius: 8px;
  color: #e74c3c;
  font-size: 0.85rem;
}

/* 统计 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border-color: #3b82f6;
}

.stat-icon {
  font-size: 2rem;
  color: #3b82f6;
  font-weight: bold;
}

.stat-content h3 {
  font-size: 0.85rem;
  color: #666666;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #3b82f6;
}

.status-card .stat-value {
  color: #10b981;
}

.chart-card {
  padding: 32px;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  color: #666666;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 1.1rem;
  color: #333333;
}

.empty-hint {
  font-size: 0.9rem;
  color: #666666;
}

/* 按钮 */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: #ffffff;
  color: #000000;
  border: 2px solid #e0e0e0;
}

.btn-secondary:hover {
  background: #f5f5f5;
  border-color: #3b82f6;
  color: #3b82f6;
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .status-bar {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .nav-bar {
    padding: 12px 20px;
  }

  .main-content {
    padding: 24px 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
