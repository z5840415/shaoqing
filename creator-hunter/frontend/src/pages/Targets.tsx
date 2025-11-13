import { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Upload,
  message,
  Space,
  Tag
} from 'antd'
import { PlusOutlined, UploadOutlined } from '@ant-design/icons'
import { targetsAPI } from '../services/api'

const { TextArea } = Input

export default function Targets() {
  const [targets, setTargets] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [importModalVisible, setImportModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadTargets()
  }, [])

  const loadTargets = async () => {
    setLoading(true)
    try {
      const data = await targetsAPI.list()
      setTargets(data)
    } catch (error) {
      message.error('加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (values: any) => {
    try {
      await targetsAPI.create(values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      loadTargets()
    } catch (error) {
      message.error('创建失败')
    }
  }

  const handleImport = async (file: File) => {
    try {
      const result: any = await targetsAPI.importExcel(file)
      message.success(
        `导入完成！成功: ${result.success_count}, 失败: ${result.failed_count}, 跳过: ${result.skipped_count}`
      )
      setImportModalVisible(false)
      loadTargets()
    } catch (error) {
      message.error('导入失败')
    }
    return false
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '昵称',
      dataIndex: 'nickname',
      key: 'nickname'
    },
    {
      title: '抖音ID',
      dataIndex: 'platform_id',
      key: 'platform_id'
    },
    {
      title: '粉丝数',
      dataIndex: 'followers_count',
      key: 'followers_count',
      render: (val: number) => val.toLocaleString()
    },
    {
      title: '平均播放量',
      dataIndex: 'avg_views',
      key: 'avg_views',
      render: (val: number) => val.toLocaleString()
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap: any = {
          pending: 'default',
          sent: 'blue',
          replied: 'green',
          added_wechat: 'cyan',
          signed: 'success'
        }
        const textMap: any = {
          pending: '待联系',
          sent: '已发送',
          replied: '已回复',
          added_wechat: '已添加微信',
          signed: '已签约'
        }
        return <Tag color={colorMap[status]}>{textMap[status] || status}</Tag>
      }
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority'
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" type="link">编辑</Button>
          <Button size="small" type="link">发送私信</Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>目标管理</h2>
        <Space>
          <Button icon={<UploadOutlined />} onClick={() => setImportModalVisible(true)}>
            批量导入
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
            添加目标
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={targets}
        loading={loading}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />

      <Modal
        title="添加目标创作者"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item
            name="nickname"
            label="抖音昵称"
            rules={[{ required: true, message: '请输入昵称' }]}
          >
            <Input placeholder="请输入昵称" />
          </Form.Item>

          <Form.Item
            name="platform_id"
            label="抖音ID"
            rules={[{ required: true, message: '请输入抖音ID' }]}
          >
            <Input placeholder="请输入抖音ID" />
          </Form.Item>

          <Form.Item
            name="profile_url"
            label="主页链接"
            rules={[{ required: true, message: '请输入主页链接' }]}
          >
            <Input placeholder="https://www.douyin.com/user/..." />
          </Form.Item>

          <Form.Item name="followers_count" label="粉丝数">
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item name="avg_views" label="平均播放量">
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item name="tags" label="内容标签">
            <Input placeholder="如: AI视频, Sora" />
          </Form.Item>

          <Form.Item name="notes" label="备注">
            <TextArea rows={3} placeholder="备注信息" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="批量导入目标"
        open={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        footer={null}
      >
        <Upload.Dragger
          name="file"
          accept=".xlsx,.xls,.csv"
          beforeUpload={handleImport}
          maxCount={1}
        >
          <p className="ant-upload-drag-icon">
            <UploadOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 Excel (.xlsx, .xls) 或 CSV 文件
          </p>
        </Upload.Dragger>
        <div style={{ marginTop: 16 }}>
          <Button type="link" href="/templates/import_template.xlsx" download>
            下载导入模板
          </Button>
        </div>
      </Modal>
    </div>
  )
}
