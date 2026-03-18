<template>
  <div class="home-page" ref="homeRef">
    <header class="home-header">
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
          <a href="https://github.com/sunna-1/PaddlePaddle-with-vueUI" target="_blank" class="nav-link github-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            <span>GitHub</span>
          </a>
        </div>
      </nav>
    </header>

    <main class="home-main">
      <section class="hero" ref="heroRef">
        <div class="hero-content">
          <h1 class="hero-title">交通路况智能分析项目</h1>
          <p class="hero-subtitle">基于深度学习的车载视频智能分析平台</p>
          <router-link to="/analysis" class="hero-cta">
            开始使用
            <ArrowRight theme="outline" size="20" fill="#ffffff" :stroke-width="2" />
          </router-link>
        </div>
        <div class="hero-visual">
          <div class="video-demo-container">
            <video 
              ref="demoVideo"
              class="demo-video"
              autoplay
              muted
              playsinline
              @ended="handleVideoEnded"
              @timeupdate="handleTimeUpdate"
            >
              <source :src="currentVideo" type="video/mp4" />
            </video>
            
            <div class="video-overlay">
              <div class="video-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: videoProgress + '%' }"></div>
                </div>
                <span class="progress-text">{{ Math.floor(videoProgress) }}%</span>
              </div>
              
              <div class="video-indicators">
                <div 
                  v-for="(video, index) in videoList" 
                  :key="index"
                  class="indicator"
                  :class="{ active: currentVideoIndex === index }"
                  @click="switchVideo(index)"
                >
                  <span class="indicator-number">{{ index + 1 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="section section-intro" ref="introRef">
        <div class="section-header">
          <h2 class="section-title">项目迭代历程</h2>
        </div>
        <div class="steps-container">
          <div class="step-card" v-for="(stage, i) in stages" :key="i">
            <div class="step-header">
              <div class="step-icon">
                <component :is="stage.icon" theme="filled" size="28" :fill="stage.color" />
              </div>
              <h3>{{ stage.title }}</h3>
            </div>
            <p class="step-description">{{ stage.desc }}</p>
          </div>
        </div>
      </section>
      
      <section class="section section-dataset" ref="datasetRef">
        <div class="section-header">
          <h2 class="section-title">技术栈与数据集</h2>
        </div>
        <div class="tech-content">
          <div class="tech-section">
            <h3 class="tech-section-title">
              <Code theme="outline" size="20" fill="#3498db" :stroke-width="2" />
              核心技术栈
            </h3>
            <div class="tech-table-wrapper">
              <table class="tech-table">
                <tbody>
                  <tr v-for="(tech, i) in techStack" :key="i">
                    <td><strong>{{ tech.module }}</strong></td>
                    <td>{{ tech.tech }}</td>
                    <td>{{ tech.function }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="tech-section-title">
              <DataFile theme="outline" size="20" fill="#e74c3c" :stroke-width="2" />
              核心数据集
            </h3>
            <div class="tech-table-wrapper">
              <table class="tech-table">
                <tbody>
                  <tr v-for="(dataset, i) in datasets" :key="i">
                    <td><strong>{{ dataset.name }}</strong></td>
                    <td>{{ dataset.scale }}</td>
                    <td>{{ dataset.usage }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="tech-section">
            <h3 class="tech-section-title">
              <LinkOne theme="outline" size="20" fill="#1abc9c" :stroke-width="2" />
              AI工具/框架官方链接
            </h3>
            <div class="links-list">
              <a v-for="(link, i) in officialLinks" :key="i" :href="link.url" target="_blank" class="link-item">
                <component :is="link.icon" theme="outline" size="20" fill="#3498db" :stroke-width="2" />
                <span class="link-name">{{ link.name }}</span>
                <Export theme="outline" size="16" fill="#1abc9c" :stroke-width="2" />
              </a>
            </div>
          </div>
        </div>
      </section>

      <section class="section section-features" ref="featuresRef">
        <div class="section-header">
          <h2 class="section-title">核心功能</h2>
        </div>
        <div class="features-grid">
          <div class="feature-card" v-for="(feature, i) in features" :key="i">
            <div class="feature-icon-large">
              <component 
                :is="feature.icon" 
                theme="filled" 
                size="40" 
                :fill="feature.color"
              />
            </div>
            <h3 class="feature-name">{{ feature.name }}</h3>
            <p class="feature-desc">{{ feature.desc }}</p>
          </div>
        </div>

        <div class="metrics-section">
          <h3 class="section-subtitle">
            <ChartHistogram theme="outline" size="20" fill="#e74c3c" :stroke-width="2" />
            核心识别精度 & 处理速度
          </h3>
          <div class="metrics-table-wrapper">
            <table class="tech-table">
              <tbody>
                <tr v-for="(metric, i) in metrics" :key="i">
                  <td><strong>{{ metric.name }}</strong></td>
                  <td class="metric-value">{{ metric.value }}</td>
                  <td>{{ metric.env }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="highlights-section">
          <h3 class="section-subtitle">
            <CheckOne theme="outline" size="20" fill="#1abc9c" :stroke-width="2" />
            项目特点
          </h3>
          <ul class="highlights-list">
            <li v-for="(highlight, i) in highlights" :key="i">
              <CheckOne theme="filled" size="18" fill="#1abc9c" />
              <span>{{ highlight }}</span>
            </li>
          </ul>
        </div>
      </section>

      <section class="section section-steps" ref="stepsRef">
        <div class="section-header">
          <h2 class="section-title">使用步骤</h2>
        </div>
        <div class="usage-steps">
          <div class="usage-step" v-for="(step, i) in steps" :key="i">
            <div class="step-content">
              <component :is="step.icon" theme="filled" size="24" :fill="step.color" />
              <p class="step-text">{{ step.text }}</p>
            </div>
          </div>
        </div>
        <router-link to="/analysis" class="steps-cta">
          开始使用
          <ArrowRight theme="outline" size="20" fill="#ffffff" :stroke-width="2" />
        </router-link>
      </section>
    </main>

    <footer class="home-footer">
      <div class="footer-content">
        <div class="footer-copyright">
          <span>© 2026 交通路况智能分析项目</span>
        </div>
        <div class="footer-attribution">
          <span>界面组件由</span>
          <a href="https://iconpark.oceanengine.com/" target="_blank" class="iconpark-link">
            IconPark
          </a>
          <span>提供支持</span>
        </div>
        <div class="footer-star">
          <a href="https://github.com/sunna-1/PaddlePaddle-with-vueUI" target="_blank" class="star-link">
            <Like theme="filled" size="16" fill="#e74c3c" />
            <span>喜欢</span>
            <span>的话请给本项目点个</span>
            <Star theme="filled" size="16" fill="#f1c40f" />
            <span>！</span>
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import gsap from 'gsap'
import {
  Car,
  Home,
  Analysis,
  Videocamera,
  Robot,
  ChartLine,
  PlayOne,
  ArrowRight,
  Time,
  Data,
  Code,
  DataFile,
  LinkOne,
  Export,
  Star,
  ChartHistogram,
  CheckOne,
  Play,
  Thunderbolt,
  Like
} from '@icon-park/vue-next'

export default {
  name: 'HomePage',
  components: {
    Car,
    Home,
    Analysis,
    Videocamera,
    Robot,
    ChartLine,
    PlayOne,
    ArrowRight,
    Time,
    Data,
    Code,
    DataFile,
    LinkOne,
    Export,
    Star,
    ChartHistogram,
    CheckOne,
    Play,
    Thunderbolt,
    Like
  },
  setup() {
    const homeRef = ref(null)
    const heroRef = ref(null)
    const introRef = ref(null)
    const datasetRef = ref(null)
    const featuresRef = ref(null)
    const stepsRef = ref(null)
    const demoVideo = ref(null)
    const currentVideoIndex = ref(0)
    const videoProgress = ref(0)
    const videoList = ref([
      '/video-demo/video1.mp4',
      '/video-demo/video2.mp4',
      '/video-demo/video3.mp4'
    ])

    const currentVideo = computed(() => videoList.value[currentVideoIndex.value])

    const handleVideoEnded = () => {
      switchToNextVideo()
    }

    const handleTimeUpdate = () => {
      if (demoVideo.value && demoVideo.value.duration) {
        videoProgress.value = (demoVideo.value.currentTime / demoVideo.value.duration) * 100
      }
    }

    const switchToNextVideo = () => {
      currentVideoIndex.value = (currentVideoIndex.value + 1) % videoList.value.length
      playVideo()
    }

    const switchVideo = (index) => {
      currentVideoIndex.value = index
      videoProgress.value = 0
      playVideo()
    }

    const playVideo = () => {
      if (demoVideo.value) {
        demoVideo.value.load()
        demoVideo.value.play().catch(err => {
          console.log('视频播放失败:', err)
        })
      }
    }

    const stages = [
      {
        title: '第一阶段（算法验证）',
        desc: '基于高德交通路况竞赛数据开展路况识别算法研发，核心解决类别不平衡、指标错误、数据泄漏等算法训练问题，完成ResNet50基础模型的训练优化，验证了拥堵/缓行/畅通三类路况识别的算法可行性',
        icon: 'Time',
        color: '#3498db'
      },
      {
        title: '第二阶段（模型搭建）',
        desc: '扩展数据集至BDD100K自动驾驶数据集，引入YOLOv8n轻量级检测模型，解决版本兼容、显存限制、标注格式不统一等问题，完成车辆检测、目标追踪核心模型的训练与调优，实现单模型的高精度检测',
        icon: 'Code',
        color: '#9b59b6'
      },
      {
        title: '第三阶段（系统集成）',
        desc: '结合数据集训练权重微调与百度飞桨模型，搭建完整的网页端智能分析系统，解决精度太低、目标跟踪丢框等工程化问题，实现视频上传、智能识别、数据统计、可视化展示的全流程功能，达成项目落地应用',
        icon: 'Star',
        color: '#1abc9c'
      }
    ]

    const techStack = [
      { module: '前端', tech: 'Vue 3 + Vite + ECharts', function: '页面交互、数据可视化展示' },
      { module: '后端', tech: 'Python 3.8 + Flask + OpenCV', function: '服务搭建、视频处理、流程调度' },
      { module: 'AI 算法', tech: 'PaddlePaddle 3.0.0/3.3.0 (GPU)、ResNet50、YOLOv8n、PPYOLOE-L + ByteTrack', function: '模型训练、目标检测/跟踪、路况识别' },
      { module: '优化工具', tech: 'AdamW 优化器、Warmup+CosineAnnealing 学习率、混合精度训练', function: '提升模型训练效率与精度' }
    ]

    const datasets = [
      { name: '高德交通路况识别竞赛数据', scale: '1500个视频序列（3类路况）', usage: '初期路况识别算法训练验证' },
      { name: 'BDD100K', scale: '10万张道路图像（3类目标）', usage: '车辆检测/追踪模型训练' },
      { name: 'COCO', scale: '通用目标检测数据集', usage: '模型预训练' }
    ]

    const officialLinks = [
      { name: 'PaddlePaddle飞桨', url: 'https://www.paddlepaddle.org.cn/', icon: 'Thunderbolt' },
      { name: 'Ultralytics YOLOv8', url: 'https://docs.ultralytics.com/', icon: 'Robot' },
      { name: 'PaddleDetection', url: 'https://github.com/PaddlePaddle/PaddleDetection', icon: 'Code' },
      { name: 'ByteTrack', url: 'https://github.com/ifzhang/ByteTrack', icon: 'ChartLine' }
    ]

    const features = [
      { icon: 'Videocamera', name: '多格式视频上传', desc: '支持MP4/AVI/MOV等常见视频格式的上传与解析', color: '#3498db' },
      { icon: 'Robot', name: 'AI 智能识别分析', desc: '集成目标检测与跟踪算法，自动完成道路中车辆的识别与轨迹追踪', color: '#9b59b6' },
      { icon: 'ChartHistogram', name: '多维度车流量统计', desc: '支持车辆总数、唯一ID车辆数、道路平均车辆密度等指标统计', color: '#e74c3c' },
      { icon: 'Star', name: '智能路况判断', desc: '基于检测结果自动判定道路为畅通/缓行/拥堵三类状态', color: '#f59e0b' },
      { icon: 'ChartLine', name: '可视化结果展示', desc: '提供带检测标注的视频回放、车流量/路况统计ECharts图表展示', color: '#1abc9c' },
      { icon: 'Thunderbolt', name: '一键化运行', desc: '配套自动化脚本，实现系统一键启动，降低使用门槛', color: '#e67e22' }
    ]

    const metrics = [
      { name: '车辆检测精度', value: '~90-95%', env: 'GPU 模式' },
      { name: '车辆 ID 跟踪精度', value: '~85-90%', env: 'GPU 模式' },
      { name: '视频处理速度', value: '15-30 FPS', env: 'GPU 模式' }
    ]

    const highlights = [
      '前后端完整集成，实现从视频上传到结果展示的端到端流程',
      '轻量化模型设计，兼顾检测精度与处理速度，适配实际应用场景',
      '现代化界面设计，采用简洁美观的UI风格，提供良好的用户体验',
      '实时系统监控，提供CPU、内存、GPU使用情况等系统资源监控'
    ]

    const steps = [
      { icon: 'Videocamera', text: '进入分析页面，上传车载视频文件', color: '#3498db' },
      { icon: 'Robot', text: '系统自动识别视频中的车辆目标', color: '#9b59b6' },
      { icon: 'ChartHistogram', text: '查看详细的数据分析报告', color: '#e74c3c' },
      { icon: 'PlayOne', text: '预览并下载带标注的结果视频', color: '#1abc9c' }
    ]

    onMounted(() => {
      if (!heroRef.value) return

      playVideo()

      gsap.from(heroRef.value, {
        opacity: 0,
        y: 60,
        duration: 1,
        ease: 'power3.out'
      })
    })

    return {
      homeRef,
      heroRef,
      introRef,
      datasetRef,
      featuresRef,
      stepsRef,
      demoVideo,
      currentVideoIndex,
      videoProgress,
      videoList,
      currentVideo,
      handleVideoEnded,
      handleTimeUpdate,
      switchVideo,
      stages,
      techStack,
      datasets,
      officialLinks,
      features,
      metrics,
      highlights,
      steps
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

.home-page {
  min-height: 100vh;
  background: #ffffff;
  color: #000000;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 40px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #ffffff;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 2px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.github-link {
  color: #000000;
}

.github-link:hover {
  color: #3b82f6;
  background: #f5f5f5;
}

.github-link svg {
  transition: transform 0.3s ease;
}

.github-link:hover svg {
  transform: scale(1.1);
}

.home-main {
  padding-top: 80px;
}

.hero {
  min-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  background: #ffffff;
  position: relative;
  overflow: hidden;
}

.hero-content {
  flex: 1;
  max-width: 600px;
  z-index: 1;
}

.hero-title {
  font-size: clamp(3rem, 6vw, 5rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 24px;
  color: #000000;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.35rem;
  color: #333333;
  margin-bottom: 48px;
  line-height: 1.7;
  font-weight: 500;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 18px 42px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  font-weight: 700;
  text-decoration: none;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  font-size: 1.1rem;
}

.hero-cta:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #3b82f6 0%, #1e5bb8 100%);
}

.hero-visual {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1;
}

.video-demo-container {
  position: relative;
  width: 100%;
  max-width: 500px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  background: #000;
}

.demo-video {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 20px;
}

.video-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 20px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-demo-container:hover .video-overlay {
  opacity: 1;
}

.video-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  border-radius: 2px;
  transition: width 0.1s linear;
}

.progress-text {
  font-size: 0.75rem;
  color: #ffffff;
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}

.video-indicators {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.indicator:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.indicator.active {
  background: #3b82f6;
  border-color: #3b82f6;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
}

.indicator-number {
  font-size: 0.9rem;
  font-weight: 700;
  color: #ffffff;
}

.section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 100px 40px;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #000000;
  letter-spacing: -0.02em;
  margin-bottom: 16px;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
  max-width: 900px;
  margin: 0 auto;
}

.step-card {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.step-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transform: translateY(-4px);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.step-number {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #8e44ad 100%);
  color: white;
  font-weight: 800;
  border-radius: 12px;
  font-size: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.step-icon {
  flex-shrink: 0;
}

.step-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #000000;
  margin: 0;
}

.step-description {
  color: #333333;
  font-size: 1rem;
  line-height: 1.7;
  margin: 0;
}

.tech-content {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.tech-section {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.tech-section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.tech-table-wrapper {
  overflow-x: auto;
}

.tech-table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
}

.tech-table td {
  padding: 16px 20px;
  color: #000000;
  font-size: 0.95rem;
  border-bottom: 1px solid #e0e0e0;
}

.tech-table td:first-child {
  font-weight: 700;
  width: 20%;
}

.tech-table tbody tr:last-child td {
  border-bottom: none;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #f5f5f5;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  text-decoration: none;
  transition: all 0.3s ease;
  color: #000000;
}

.link-item:hover {
  border-color: #3b82f6;
  background: #ffffff;
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.link-name {
  font-weight: 600;
  flex: 1;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.feature-card {
  padding: 40px;
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border-color: #3b82f6;
}

.feature-icon-large {
  margin-bottom: 24px;
}

.feature-name {
  font-size: 1.35rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 16px;
}

.feature-desc {
  color: #333333;
  font-size: 1rem;
  line-height: 1.7;
}

.metrics-section,
.highlights-section {
  margin-top: 48px;
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.section-subtitle {
  font-size: 1.5rem;
  color: #000000;
  margin-bottom: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.metrics-table-wrapper {
  overflow-x: auto;
}

.highlights-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.highlights-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 0;
  color: #000000;
  font-size: 1rem;
  line-height: 1.7;
  border-bottom: 1px solid #e0e0e0;
}

.highlights-list li:last-child {
  border-bottom: none;
}

.highlights-list li span {
  flex: 1;
}

.usage-steps {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.usage-step {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px;
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.usage-step:hover {
  transform: translateX(8px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border-color: #3b82f6;
}

.step-badge {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #8e44ad 100%);
  color: white;
  font-weight: 800;
  border-radius: 12px;
  font-size: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.step-content {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.step-text {
  color: #000000;
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 0;
}

.steps-cta {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  width: fit-content;
  margin: 40px auto 0;
  padding: 18px 42px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  font-weight: 700;
  text-decoration: none;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.steps-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.home-footer {
  background: #ffffff;
  border-top: 2px solid #e0e0e0;
  padding: 32px 40px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.footer-copyright {
  color: #000000;
  font-size: 0.95rem;
  font-weight: 500;
}

.footer-attribution {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #666666;
}

.iconpark-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.iconpark-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

.footer-star {
  margin-top: 8px;
}

.star-link {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666666;
  text-decoration: none;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.star-link:hover {
  color: #3b82f6;
  text-decoration: none;
}

.star-link .icon-park {
  transition: transform 0.3s ease;
}

.star-link:hover .icon-park {
  transform: scale(1.2);
}

@media (max-width: 1024px) {
  .hero {
    flex-direction: column;
    text-align: center;
    padding: 60px 24px;
  }

  .hero-content {
    margin-bottom: 40px;
  }

  .video-demo-container {
    max-width: 100%;
  }

  .section {
    padding: 80px 24px;
  }

  .section-header {
    flex-direction: column;
  }

  .section-title {
    font-size: 1.75rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .nav-bar {
    padding: 12px 20px;
  }

  .nav-logo span {
    display: none;
  }

  .nav-link span {
    display: none;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .hero-cta {
    padding: 14px 32px;
    font-size: 1rem;
  }

  .step-card,
  .usage-step {
    padding: 24px;
  }

  .tech-section {
    padding: 24px;
  }

  .feature-card {
    padding: 24px;
  }
}
</style>