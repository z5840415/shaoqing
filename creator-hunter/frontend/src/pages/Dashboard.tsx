import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Progress } from 'antd'
import {
  UserOutlined,
  MessageOutlined,
  CheckCircleOutlined,
  RiseOutlined
} from '@ant-design/icons'
import { analyticsAPI, targetsAPI } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  const [targetStats, setTargetStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [dashboardData, targetsData] = await Promise.all([
        analyticsAPI.getDashboard(),
        targetsAPI.getStats()
      ])
      setStats(dashboardData)
      setTargetStats(targetsData)
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>仪表板</h2>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日已发送"
              value={stats?.today?.sent || 0}
              prefix={<MessageOutlined />}
              suffix="条"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日回复率"
              value={stats?.today?.reply_rate || 0}
              prefix={<RiseOutlined />}
              suffix="%"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本月已签约"
              value={stats?.this_month?.signed || 0}
              prefix={<CheckCircleOutlined />}
              suffix="人"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总目标数"
              value={targetStats?.total || 0}
              prefix={<UserOutlined />}
              suffix="个"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="本月数据" loading={loading}>
            <p>总发送: <strong>{stats?.this_month?.sent || 0}</strong> 条</p>
            <p>已回复: <strong>{stats?.this_month?.replied || 0}</strong> 条</p>
            <p>回复率: <strong>{stats?.this_month?.reply_rate || 0}%</strong></p>
            <Progress percent={stats?.this_month?.reply_rate || 0} />
            <br />
            <p>已签约: <strong>{stats?.this_month?.signed || 0}</strong> 人</p>
            <p>转化率: <strong>{stats?.this_month?.conversion_rate || 0}%</strong></p>
            <Progress percent={stats?.this_month?.conversion_rate || 0} status="success" />
          </Card>
        </Col>

        <Col span={12}>
          <Card title="目标状态分布" loading={loading}>
            <p>待联系: <strong>{targetStats?.pending || 0}</strong></p>
            <p>已发送: <strong>{targetStats?.sent || 0}</strong></p>
            <p>已回复: <strong>{targetStats?.replied || 0}</strong></p>
            <p>已添加微信: <strong>{targetStats?.added_wechat || 0}</strong></p>
            <p>已签约: <strong>{targetStats?.signed || 0}</strong></p>
            <br />
            <p>整体回复率: <strong>{targetStats?.reply_rate || 0}%</strong></p>
            <p>微信添加率: <strong>{targetStats?.wechat_rate || 0}%</strong></p>
            <p>签约转化率: <strong>{targetStats?.signed_rate || 0}%</strong></p>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
