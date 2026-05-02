<template>
  <div class="page">
    <header class="header">
      <nav class="nav">
        <router-link to="/" class="nav-logo">
          <Car theme="outline" size="24" fill="#000" :stroke-width="2" />
          <span>交通路况智能分析</span>
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link" exact-active-class="active">
            <Home theme="outline" size="20" fill="#000" :stroke-width="2" />
            <span>项目介绍</span>
          </router-link>
          <router-link to="/analysis" class="nav-link" exact-active-class="active">
            <Analysis theme="outline" size="20" fill="#000" :stroke-width="2" />
            <span>开始分析</span>
          </router-link>
        </div>
      </nav>
    </header>

    <main class="main">
      <!-- 顶部状态栏 -->
      <div class="status-bar">
        <div class="status-block" :class="{ offline: !backendStatus.online }">
          <div class="status-head">
            <span class="dot" :class="{ on: backendStatus.online }"></span>
            <span>后端: {{ backendStatus.online ? '运行中' : '未启动' }}</span>
          </div>
          <div class="status-detail" v-if="backendStatus.online">
            <span>{{ formatUptime(backendStatus.uptime) }}</span>
            <span>任务: {{ backendStatus.activeTasks }}</span>
          </div>
          <div class="status-warn" v-else>python app.py</div>
        </div>
        <div class="status-block hw" v-if="backendStatus.system">
          <div class="hw-row">
            <div class="hw-item">
              <div class="hw-label">CPU</div>
              <div class="hw-val">{{ backendStatus.system.system_cpu_percent || 0 }}%</div>
              <div class="hw-sub">{{ backendStatus.system.cpu_count || 0 }} 核心</div>
              <div class="hw-bar"><div class="hw-fill" :style="{ width: (backendStatus.system.system_cpu_percent || 0) + '%' }"></div></div>
            </div>
            <div class="hw-item">
              <div class="hw-label">内存</div>
              <div class="hw-val">{{ backendStatus.system.system_memory_percent || 0 }}%</div>
              <div class="hw-sub">{{ backendStatus.system.system_memory_used_gb || 0 }} / {{ backendStatus.system.system_memory_total_gb || 0 }} GB</div>
              <div class="hw-bar"><div class="hw-fill" :style="{ width: (backendStatus.system.system_memory_percent || 0) + '%' }"></div></div>
            </div>
          </div>
        </div>
        <div class="status-block info" v-if="backendStatus.system">
          <div class="info-grid">
            <div class="info-row"><span class="info-k">CPU频率</span><span class="info-v">{{ backendStatus.system.cpu_freq || 0 }} MHz</span></div>
            <div class="info-row"><span class="info-k">物理核心</span><span class="info-v">{{ backendStatus.system.cpu_details?.physical_cores || '-' }}</span></div>
            <div class="info-row"><span class="info-k">逻辑核心</span><span class="info-v">{{ backendStatus.system.cpu_details?.logical_cores || '-' }}</span></div>
            <div class="info-row"><span class="info-k">线程数</span><span class="info-v">{{ backendStatus.system.num_threads || 0 }}</span></div>
          </div>
        </div>
      </div>

      <!-- 终端 -->
      <div class="terminal">
        <div class="term-head">
          <span>终端日志</span>
          <button class="btn-sm" @click="clearLogs">清空</button>
        </div>
        <div class="term-body" ref="terminalContent">
          <div v-for="(log, i) in logs" :key="i" class="log-line">{{ log }}</div>
          <div v-if="logs.length === 0" class="log-empty">等待日志...</div>
        </div>
      </div>

      <!-- 主内容 -->
      <div class="content-grid">
        <!-- 左列：上传 + 视频 -->
        <div class="col-left">
          <div class="card">
            <h2>视频上传</h2>
            <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
              <input type="file" ref="fileInput" @change="handleFileSelect" accept="video/*" class="file-input" id="video-upload" />
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
              <button @click="processVideo" class="btn btn-go" :disabled="processing">
                {{ processing ? '处理中...' : '开始分析' }}
              </button>
            </div>
            <div v-if="videoPreview" class="video-box">
              <h3>原始视频预览</h3>
              <video ref="videoPlayer" :src="videoPreview" controls class="video-player"></video>
            </div>
            <div v-if="processing" class="processing-box">
              <div class="spinner"></div>
              <p>正在分析视频，请稍候...</p>
              <p class="hint">首次加载模型可能需要一些时间</p>
            </div>
          </div>

          <div v-if="annotatedVideoUrl" class="card">
            <h2>输出视频预览</h2>
            <div v-if="videoLoading" class="video-loading">
              <div class="spinner"></div>
              <span>视频加载中...</span>
            </div>
            <div v-if="videoError" class="video-error">
              <div class="err-icon">!</div>
              <h3>视频加载失败</h3>
              <p>{{ videoErrorMessage }}</p>
              <div class="err-actions">
                <button @click="retryLoadVideo" class="btn btn-primary">重新加载</button>
                <a :href="annotatedVideoUrl" download="traffic_analysis_output.mp4" class="btn btn-secondary">下载视频</a>
              </div>
            </div>
            <video v-show="!videoLoading && !videoError" ref="annotatedVideoPlayer" :src="annotatedVideoUrl"
              controls class="video-player annotated" preload="metadata"
              @error="handleVideoError" @canplay="handleVideoReady" @loadedmetadata="handleVideoMetadata"></video>
            <div v-if="!videoError" class="video-actions">
              <a :href="annotatedVideoUrl" download="traffic_analysis_output.mp4" class="btn btn-secondary">下载视频</a>
              <span class="video-path">{{ outputFileName }}</span>
            </div>
          </div>
        </div>

        <!-- 右列：数据面板 -->
        <div class="col-right">
          <!-- 顶部概览卡片 -->
          <div class="overview-grid">
            <div class="overview-card">
              <div class="ov-label">检测车辆总数</div>
              <div class="ov-value">{{ hasData ? analysisResult.total_detections : '--' }}</div>
            </div>
            <div class="overview-card">
              <div class="ov-label">唯一车辆数</div>
              <div class="ov-value">{{ hasData ? analysisResult.unique_vehicle_count : '--' }}</div>
            </div>
            <div class="overview-card">
              <div class="ov-label">平均每帧车辆</div>
              <div class="ov-value">{{ hasData ? analysisResult.avg_detections_per_frame : '--' }}</div>
            </div>
            <div class="overview-card status" :class="statusTheme">
              <div class="ov-label">路况参考判断</div>
              <div class="ov-value">{{ hasData ? analysisResult.traffic_status : '--' }}</div>
              <div class="ov-badge" v-if="hasData">
                <span class="badge" :class="'badge-' + badgeConf">置信度：{{ confidenceLabel }}</span>
              </div>
            </div>
          </div>

          <!-- 详细指标 2x2 网格 -->
          <div class="detail-grid">
            <div class="detail-card">
              <div class="detail-title">车辆密度</div>
              <div class="detail-rows">
                <div class="detail-row"><span>最大同帧车辆数</span><span>{{ sv(analysisResult?.vehicle_statistics?.max_concurrent) }}</span></div>
                <div class="detail-row"><span>最小同帧车辆数</span><span>{{ sv(analysisResult?.vehicle_statistics?.min_concurrent) }}</span></div>
                <div class="detail-row"><span>平均车辆密度</span><span>{{ sv(analysisResult?.vehicle_statistics?.average_density) }}</span></div>
              </div>
            </div>
            <div class="detail-card">
              <div class="detail-title">车辆位移</div>
              <div class="detail-rows">
                <div class="detail-row"><span>平均帧间位移</span><span>{{ sv(analysisResult?.speed_statistics?.avg_pixel_speed, ' px/帧') }}</span></div>
                <div class="detail-row"><span>最大帧间位移</span><span>{{ sv(analysisResult?.speed_statistics?.max_pixel_speed, ' px/帧') }}</span></div>
                <div class="detail-row"><span>静止车辆占比</span><span>{{ sv(analysisResult?.speed_statistics?.stationary_vehicle_ratio, '%') }}</span></div>
              </div>
            </div>
            <div class="detail-card">
              <div class="detail-title">跟踪时长</div>
              <div class="detail-rows">
                <div class="detail-row"><span>平均跟踪帧数</span><span>{{ sv(analysisResult?.speed_statistics?.avg_track_duration_frames, ' 帧') }}</span></div>
                <div class="detail-row"><span>最长跟踪帧数</span><span>{{ sv(analysisResult?.speed_statistics?.max_track_duration_frames, ' 帧') }}</span></div>
              </div>
            </div>
            <div class="detail-card">
              <div class="detail-title">车辆面积</div>
              <div class="detail-rows">
                <div class="detail-row"><span>平均面积占比</span><span>{{ sv(analysisResult?.area_statistics?.avg_vehicle_area_ratio, '%') }}</span></div>
                <div class="detail-row"><span>最大面积占比</span><span>{{ sv(analysisResult?.area_statistics?.max_vehicle_area_ratio, '%') }}</span></div>
              </div>
            </div>
          </div>

          <!-- 判断因素 -->
          <div class="card factors-card" :class="{ 'card-empty': !hasData }">
            <h2>判断因素分析</h2>
            <p class="factors-note" v-if="hasData">基于视觉分析的多指标综合判断（无速度/GPS数据支撑）</p>
            <p class="factors-note" v-else>上传视频后显示判断因素</p>
            <div class="factors-grid" v-if="hasData && hasJudgmentFactors">
              <div v-for="(factor, key) in analysisResult.judgment_factors" :key="key"
                class="factor-item" :class="'factor-' + factor.signal">
                <div class="factor-head">
                  <span class="factor-name">{{ factor.label }}</span>
                  <span class="factor-signal" :class="'sig-' + factor.signal">{{ signalLabel(factor.signal) }}</span>
                </div>
                <div class="factor-val">{{ factor.value }}</div>
              </div>
            </div>
            <div class="factors-empty" v-else>
              <div v-for="i in 5" :key="i" class="factor-skeleton"></div>
            </div>
          </div>

          <!-- 出行建议 -->
          <div class="card suggest-card" :class="statusTheme" v-if="hasData">
            <h2>出行建议</h2>
            <div class="suggest-body" :class="statusTheme">
              <p>{{ travelSuggestion }}</p>
            </div>
            <p v-if="analysisResult.confidence === '低'" class="suggest-warn">
              注意：当前判断置信度较低，建议结合其他信息综合判断路况。
            </p>
          </div>

          <!-- 图表区 -->
          <div class="charts-row">
            <div class="card chart-card" :class="{ 'card-empty': !hasData }">
              <h2>车流密度趋势</h2>
              <div ref="trendChart" class="chart-box"></div>
            </div>
            <div class="card chart-card" :class="{ 'card-empty': !hasData }">
              <h2>车辆位移趋势</h2>
              <div ref="speedTrendChart" class="chart-box"></div>
            </div>
          </div>

          <div class="card chart-card" :class="{ 'card-empty': !hasData }">
            <h2>路况占比</h2>
            <div ref="statusChart" class="chart-box"></div>
          </div>

          <!-- 数据来源 -->
          <div class="data-source" v-if="hasData">
            数据来源：{{ dataSourceLabel }}
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
import { Car, Home, Analysis } from '@icon-park/vue-next'

const API_BASE = '/api'

export default {
  name: 'AnalysisPage',
  components: { Car, Home, Analysis },
  setup() {
    const fileInput = ref(null)
    const videoPlayer = ref(null)
    const annotatedVideoPlayer = ref(null)
    const trendChart = ref(null)
    const speedTrendChart = ref(null)
    const statusChart = ref(null)

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
    const backendStatus = ref({ online: false, uptime: 0, activeTasks: 0, system: null })
    const logs = ref([])
    const terminalContent = ref(null)

    let trendChartInstance = null
    let speedTrendChartInstance = null
    let statusChartInstance = null

    const hasData = computed(() => !!analysisResult.value)

    const sv = (val, suffix = '') => {
      if (val === undefined || val === null || val === 0) return '--'
      return val + suffix
    }

    const confidenceLabel = computed(() => {
      const c = analysisResult.value?.confidence
      if (c === '高') return '高'
      if (c === '中') return '中'
      if (c === '低') return '低'
      return '--'
    })

    const badgeConf = computed(() => {
      const c = analysisResult.value?.confidence
      if (c === '高') return 'high'
      if (c === '中') return 'mid'
      return 'low'
    })

    const hasJudgmentFactors = computed(() => {
      const factors = analysisResult.value?.judgment_factors
      return factors && Object.keys(factors).length > 0
    })

    const dataSourceLabel = computed(() => {
      const src = analysisResult.value?.data_source
      if (src === 'pipeline_detection_json') return 'Pipeline检测数据(JSON)'
      if (src === 'fallback_video_analysis') return '标注视频后备分析'
      return '未知'
    })

    const statusTheme = computed(() => {
      const s = analysisResult.value?.traffic_status || ''
      return {
        'theme-smooth': s === '畅通',
        'theme-slow': s === '缓行',
        'theme-congested': s === '拥堵'
      }
    })

    const travelSuggestion = computed(() => {
      const s = analysisResult.value?.traffic_status || ''
      if (s === '畅通') return '道路畅通，适合出行。建议保持安全车速，愉快出行。'
      if (s === '缓行') return '前方道路缓行，建议提前规划路线或绕道行驶，注意保持车距。'
      if (s === '拥堵') return '严重拥堵，建议绕行或推迟出行时间。如已在路上，请保持耐心。'
      return '请上传视频进行分析，获取出行建议。'
    })

    const signalLabel = (signal) => {
      if (signal === 'smooth') return '畅通'
      if (signal === 'slow') return '缓行'
      if (signal === 'congested') return '拥堵'
      return '未知'
    }

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
      videoLoading.value = false
      videoError.value = true
      const code = event?.target?.error?.code
      const msgs = { 1: '加载被中止', 2: '网络错误', 3: '视频格式不支持', 4: '视频源不存在' }
      videoErrorMessage.value = msgs[code] || '视频加载失败'
    }

    const handleVideoReady = () => { videoLoading.value = false; videoError.value = false }
    const handleVideoMetadata = () => {}

    const retryLoadVideo = () => {
      if (!annotatedVideoPlayer.value) return
      videoError.value = false; videoLoading.value = true
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
          timeout: 600000
        })
        const data = response.data
        analysisResult.value = {
          total_frames: data.total_frames,
          total_detections: data.total_detections,
          unique_vehicle_count: data.unique_vehicle_count,
          avg_detections_per_frame: data.avg_detections_per_frame,
          traffic_status: data.traffic_status,
          confidence: data.confidence,
          judgment_factors: data.judgment_factors,
          vehicle_statistics: data.vehicle_statistics,
          speed_statistics: data.speed_statistics,
          area_statistics: data.area_statistics,
          class_distribution: data.class_distribution,
          density_trend: data.density_trend,
          speed_trend: data.speed_trend,
          traffic_status_distribution: data.traffic_status_distribution,
          data_source: data.data_source
        }
        const videoUrl = data.annotated_video_url
        if (videoUrl) {
          videoLoading.value = true; videoError.value = false
          annotatedVideoUrl.value = videoUrl
          outputFileName.value = videoUrl.split('/').pop()
        }
        renderCharts()
      } catch (error) {
        alert('处理视频失败: ' + (error.response?.data?.error || error.message))
      } finally {
        processing.value = false
      }
    }

    const renderCharts = () => {
      if (!analysisResult.value) return
      setTimeout(() => {
        // 密度趋势
        if (trendChart.value && analysisResult.value.density_trend?.length > 0) {
          const rect = trendChart.value.getBoundingClientRect()
          if (rect.width > 0 && rect.height > 0) {
            if (trendChartInstance) trendChartInstance.dispose()
            trendChartInstance = echarts.init(trendChart.value)
            const d = analysisResult.value.density_trend
            trendChartInstance.setOption({
              backgroundColor: 'transparent',
              tooltip: { trigger: 'axis' },
              grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
              xAxis: { type: 'category', boundaryGap: false, data: d.map((_, i) => i + 1), axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { color: '#888' } },
              yAxis: { type: 'value', name: '车辆数', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f0f0f0' } }, axisLabel: { color: '#888' } },
              series: [{ name: '车流密度', type: 'line', smooth: true, data: d, lineStyle: { color: '#3b82f6', width: 2.5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(59,130,246,0.25)' }, { offset: 1, color: 'rgba(59,130,246,0.02)' }]) }, itemStyle: { color: '#3b82f6' } }]
            })
          }
        }
        // 速度趋势
        if (speedTrendChart.value && analysisResult.value.speed_trend?.length > 0) {
          const rect = speedTrendChart.value.getBoundingClientRect()
          if (rect.width > 0 && rect.height > 0) {
            if (speedTrendChartInstance) speedTrendChartInstance.dispose()
            speedTrendChartInstance = echarts.init(speedTrendChart.value)
            const d = analysisResult.value.speed_trend
            speedTrendChartInstance.setOption({
              backgroundColor: 'transparent',
              tooltip: { trigger: 'axis', formatter: '{b}帧: {c} px/帧' },
              grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
              xAxis: { type: 'category', boundaryGap: false, data: d.map((_, i) => i + 1), axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { color: '#888' } },
              yAxis: { type: 'value', name: '位移(px/帧)', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f0f0f0' } }, axisLabel: { color: '#888' } },
              series: [{ name: '平均位移', type: 'line', smooth: true, data: d, lineStyle: { color: '#7c3aed', width: 2.5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(124,58,237,0.25)' }, { offset: 1, color: 'rgba(124,58,237,0.02)' }]) }, itemStyle: { color: '#7c3aed' } }]
            })
          }
        }
        // 路况占比
        if (statusChart.value && analysisResult.value.traffic_status_distribution) {
          const rect = statusChart.value.getBoundingClientRect()
          if (rect.width > 0 && rect.height > 0) {
            if (statusChartInstance) statusChartInstance.dispose()
            statusChartInstance = echarts.init(statusChart.value)
            const sd = analysisResult.value.traffic_status_distribution
            statusChartInstance.setOption({
              backgroundColor: 'transparent',
              tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
              series: [{
                name: '路况占比', type: 'pie', radius: ['40%', '70%'],
                itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
                label: { show: true, formatter: '{b}: {c}%' },
                data: [
                  { value: sd.smooth, name: '畅通', itemStyle: { color: '#10b981' } },
                  { value: sd.slow, name: '缓行', itemStyle: { color: '#f59e0b' } },
                  { value: sd.congested, name: '拥堵', itemStyle: { color: '#ef4444' } }
                ]
              }]
            })
          }
        }
      }, 100)
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024, s = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + s[i]
    }

    const formatUptime = (s) => {
      if (!s) return '0秒'
      const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = Math.floor(s % 60)
      if (h > 0) return `${h}小时${m}分`
      if (m > 0) return `${m}分${sec}秒`
      return `${sec}秒`
    }

    const updateBackendStatus = async () => {
      try {
        const r = await axios.get(`${API_BASE}/status`, { timeout: 3000 })
        if (r.data.success) {
          backendStatus.value = { online: true, uptime: r.data.uptime, activeTasks: r.data.active_tasks, system: r.data.system }
          if (r.data.logs?.length > 0) logs.value = r.data.logs
        }
      } catch { backendStatus.value.online = false; backendStatus.value.system = null }
    }

    const fetchLogs = async () => {
      try {
        const r = await axios.get(`${API_BASE}/logs`)
        if (r.data.success) { logs.value = r.data.logs; nextTick(() => { if (terminalContent.value) terminalContent.value.scrollTop = terminalContent.value.scrollHeight }) }
      } catch {}
    }

    const clearLogs = () => { logs.value = [] }

    const statusInterval = setInterval(() => { updateBackendStatus(); if (processing.value) fetchLogs() }, 2000)

    onMounted(() => { axios.get(`${API_BASE}/health`).catch(() => {}); updateBackendStatus() })
    onUnmounted(() => { clearInterval(statusInterval); if (trendChartInstance) trendChartInstance.dispose(); if (speedTrendChartInstance) speedTrendChartInstance.dispose(); if (statusChartInstance) statusChartInstance.dispose() })

    return {
      fileInput, videoPlayer, annotatedVideoPlayer, trendChart, speedTrendChart, statusChart,
      uploadedFile, fileSize, videoPreview, processing, analysisResult,
      annotatedVideoUrl, outputFileName, videoLoading, videoError, backendStatus, logs, terminalContent,
      hasData, sv, confidenceLabel, badgeConf, hasJudgmentFactors, dataSourceLabel, statusTheme,
      travelSuggestion, signalLabel,
      handleFileSelect, handleDrop, handleVideoError, handleVideoReady, retryLoadVideo, processVideo,
      formatFileSize, formatUptime, clearLogs
    }
  }
}
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }

.page {
  min-height: 100vh;
  background: #f8f9fb;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #1a1a2e;
}

/* 导航 */
.header {
  position: sticky; top: 0; z-index: 50;
  background: #fff; border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.nav { display: flex; justify-content: space-between; align-items: center; padding: 14px 32px; max-width: 1600px; margin: 0 auto; }
.nav-logo { display: flex; align-items: center; gap: 10px; font-size: 1.15rem; font-weight: 700; color: #1a1a2e; text-decoration: none; }
.nav-links { display: flex; gap: 6px; }
.nav-link { display: flex; align-items: center; gap: 6px; color: #555; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 10px; transition: all .2s; }
.nav-link:hover { background: #f0f1f5; color: #1a1a2e; }
.nav-link.active { background: #eef2ff; color: #3b82f6; }

/* 主体 */
.main { max-width: 1600px; margin: 0 auto; padding: 20px 24px 60px; }

/* 状态栏 */
.status-bar { display: grid; grid-template-columns: 1fr 2fr 1fr; gap: 12px; margin-bottom: 12px; }
.status-block { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px 18px; }
.status-block.offline { border-color: #fca5a5; background: #fef2f2; }
.status-head { display: flex; align-items: center; gap: 8px; font-size: .9rem; font-weight: 600; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; }
.dot.on { background: #10b981; }
.status-detail { display: flex; gap: 16px; font-size: .82rem; color: #666; margin-top: 6px; }
.status-warn { font-size: .82rem; color: #ef4444; margin-top: 4px; }
.hw-row { display: flex; gap: 24px; }
.hw-item { flex: 1; }
.hw-label { font-size: .78rem; color: #888; }
.hw-val { font-size: 1.2rem; font-weight: 700; color: #3b82f6; }
.hw-sub { font-size: .75rem; color: #999; }
.hw-bar { height: 5px; background: #e5e7eb; border-radius: 3px; margin-top: 6px; overflow: hidden; }
.hw-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #10b981); border-radius: 3px; transition: width .5s; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 16px; }
.info-row { display: flex; justify-content: space-between; font-size: .82rem; }
.info-k { color: #888; }
.info-v { color: #1a1a2e; font-weight: 500; }

/* 终端 */
.terminal { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 16px; overflow: hidden; }
.term-head { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #f8f9fb; border-bottom: 1px solid #e5e7eb; font-size: .88rem; font-weight: 600; }
.btn-sm { background: transparent; border: 1px solid #d1d5db; color: #555; padding: 4px 12px; border-radius: 6px; font-size: .78rem; cursor: pointer; transition: all .2s; }
.btn-sm:hover { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.term-body { max-height: 100px; overflow-y: auto; padding: 10px 16px; font-family: 'Consolas', 'Courier New', monospace; font-size: .78rem; background: #fafbfc; }
.log-line { color: #333; line-height: 1.5; padding: 1px 0; }
.log-empty { color: #aaa; font-style: italic; }

/* 内容区 */
.content-grid { display: grid; grid-template-columns: 380px 1fr; gap: 20px; align-items: start; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 16px; }

/* 卡片 */
.card { background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 24px; }
.card h2 { font-size: 1.1rem; font-weight: 700; color: #1a1a2e; margin-bottom: 16px; }

/* 上传 */
.upload-area { position: relative; border: 2px dashed #d1d5db; border-radius: 12px; padding: 36px; text-align: center; cursor: pointer; transition: all .2s; }
.upload-area:hover { border-color: #3b82f6; background: #f8faff; }
.file-input { position: absolute; width: 100%; height: 100%; top: 0; left: 0; opacity: 0; cursor: pointer; }
.upload-label { cursor: pointer; }
.upload-text { font-size: 1rem; color: #333; margin-bottom: 6px; font-weight: 500; }
.upload-hint { font-size: .85rem; color: #999; }
.file-info { margin-top: 16px; padding: 14px; background: #f8f9fb; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; }
.file-details { display: flex; flex-direction: column; gap: 2px; }
.file-name { font-weight: 600; font-size: .9rem; }
.file-size { font-size: .8rem; color: #888; }
.video-box { margin-top: 16px; }
.video-box h3 { font-size: .95rem; font-weight: 600; margin-bottom: 10px; }
.video-player { width: 100%; border-radius: 10px; max-height: 360px; background: #000; }
.processing-box { text-align: center; padding: 30px; color: #888; }
.spinner { width: 40px; height: 40px; border: 3px solid #e5e7eb; border-top-color: #3b82f6; border-radius: 50%; animation: spin .8s linear infinite; margin: 0 auto 12px; }
@keyframes spin { to { transform: rotate(360deg); } }
.hint { font-size: .82rem; color: #aaa; margin-top: 6px; }
.annotated { border: 1px solid #e5e7eb; }
.video-loading { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 30px; background: #f8f9fb; border-radius: 10px; }
.video-error { text-align: center; padding: 24px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px; }
.err-icon { font-size: 2.5rem; color: #ef4444; font-weight: bold; margin-bottom: 8px; }
.video-error h3 { font-size: 1.1rem; color: #ef4444; margin-bottom: 6px; }
.video-error p { color: #666; margin-bottom: 12px; }
.err-actions { display: flex; gap: 10px; justify-content: center; }
.video-actions { margin-top: 12px; display: flex; align-items: center; gap: 12px; }
.video-path { font-size: .78rem; color: #999; }

/* 按钮 */
.btn { padding: 10px 20px; border: none; border-radius: 10px; font-size: .9rem; cursor: pointer; font-weight: 600; transition: all .2s; }
.btn-primary { background: #3b82f6; color: #fff; }
.btn-primary:hover { background: #2563eb; }
.btn-secondary { background: #fff; color: #555; border: 1px solid #d1d5db; }
.btn-secondary:hover { border-color: #3b82f6; color: #3b82f6; }
.btn-go { background: linear-gradient(135deg, #10b981, #059669); color: #fff; }
.btn-go:hover { box-shadow: 0 4px 12px rgba(16,185,129,.35); }
.btn:disabled { opacity: .5; cursor: not-allowed; }

/* ===== 右侧数据面板 ===== */

/* 概览卡片 */
.overview-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.overview-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px 16px; text-align: center; transition: all .2s; }
.overview-card:hover { border-color: #3b82f6; box-shadow: 0 2px 8px rgba(59,130,246,.1); }
.ov-label { font-size: .78rem; color: #888; margin-bottom: 6px; }
.ov-value { font-size: 1.6rem; font-weight: 800; color: #1a1a2e; }
.overview-card.status.theme-smooth { border-color: #10b981; background: #f0fdf4; }
.overview-card.status.theme-smooth .ov-value { color: #10b981; }
.overview-card.status.theme-slow { border-color: #f59e0b; background: #fffbeb; }
.overview-card.status.theme-slow .ov-value { color: #f59e0b; }
.overview-card.status.theme-congested { border-color: #ef4444; background: #fef2f2; }
.overview-card.status.theme-congested .ov-value { color: #ef4444; }
.ov-badge { margin-top: 6px; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: .72rem; font-weight: 600; }
.badge-high { background: #d1fae5; color: #059669; }
.badge-mid { background: #fef3c7; color: #d97706; }
.badge-low { background: #fecaca; color: #dc2626; }

/* 详细指标 */
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.detail-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; }
.detail-title { font-size: .88rem; font-weight: 700; color: #3b82f6; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 2px solid #eef2ff; }
.detail-rows { display: flex; flex-direction: column; gap: 2px; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #f3f4f6; }
.detail-row:last-child { border-bottom: none; }
.detail-row span:first-child { font-size: .84rem; color: #666; }
.detail-row span:last-child { font-size: .9rem; font-weight: 600; color: #1a1a2e; }

/* 判断因素 */
.factors-card { transition: all .2s; }
.factors-note { font-size: .82rem; color: #aaa; margin-bottom: 14px; font-style: italic; }
.factors-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
.factor-item { padding: 14px; border-radius: 10px; border: 1px solid #e5e7eb; transition: all .2s; }
.factor-item.factor-smooth { border-color: #10b981; background: #f0fdf4; }
.factor-item.factor-slow { border-color: #f59e0b; background: #fffbeb; }
.factor-item.factor-congested { border-color: #ef4444; background: #fef2f2; }
.factor-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.factor-name { font-size: .8rem; color: #666; font-weight: 500; }
.factor-signal { padding: 2px 7px; border-radius: 6px; font-size: .7rem; font-weight: 600; }
.sig-smooth { background: #d1fae5; color: #059669; }
.sig-slow { background: #fef3c7; color: #d97706; }
.sig-congested { background: #fecaca; color: #dc2626; }
.factor-val { font-size: 1.35rem; font-weight: 800; color: #1a1a2e; }
.factors-empty { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
.factor-skeleton { height: 68px; border-radius: 10px; background: #f3f4f6; }

/* 出行建议 */
.suggest-card { border-left: 4px solid #3b82f6; }
.suggest-card.theme-smooth { border-color: #10b981; }
.suggest-card.theme-slow { border-color: #f59e0b; }
.suggest-card.theme-congested { border-color: #ef4444; }
.suggest-body { padding: 16px; border-radius: 10px; background: #f8f9fb; }
.suggest-body p { font-size: .95rem; line-height: 1.7; color: #1a1a2e; }
.suggest-body.theme-smooth { background: #ecfdf5; }
.suggest-body.theme-smooth p { color: #059669; }
.suggest-body.theme-slow { background: #fffbeb; }
.suggest-body.theme-slow p { color: #d97706; }
.suggest-body.theme-congested { background: #fef2f2; }
.suggest-body.theme-congested p { color: #dc2626; }
.suggest-warn { margin-top: 10px; font-size: .82rem; color: #999; font-style: italic; }

/* 图表 */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.chart-card { padding: 20px; }
.chart-box { width: 100%; height: 220px; }
.card-empty .chart-box { background: #f9fafb; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.card-empty .chart-box::after { content: '--'; color: #ccc; font-size: 1.2rem; font-weight: 600; }

/* 数据来源 */
.data-source { text-align: center; font-size: .78rem; color: #aaa; padding: 8px 0; font-style: italic; }

/* 响应式 */
@media (max-width: 1200px) {
  .content-grid { grid-template-columns: 1fr; }
  .status-bar { grid-template-columns: 1fr; }
  .detail-grid { grid-template-columns: 1fr; }
  .overview-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .nav { padding: 10px 16px; }
  .main { padding: 12px; }
  .overview-grid { grid-template-columns: 1fr 1fr; }
  .factors-grid, .factors-empty { grid-template-columns: 1fr; }
}
</style>
