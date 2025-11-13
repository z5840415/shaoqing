import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, Select, message, Tag, Space } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { templatesAPI } from '../services/api'

const { TextArea } = Input

export default function Templates() {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      const data = await templatesAPI.list()
      setTemplates(data)
    } catch (error) {
      message.error('加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (values: any) => {
    try {
      await templatesAPI.create(values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      loadTemplates()
    } catch (error) {
      message.error('创建失败')
    }
  }

  const columns = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (val: string) => val === 'douyin' ? '抖音' : val
    },
    {
      title: '场景',
      dataIndex: 'scenario',
      key: 'scenario'
    },
    {
      title: '使用次数',
      dataIndex: 'usage_count',
      key: 'usage_count'
    },
    {
      title: '回复率',
      dataIndex: 'reply_rate',
      key: 'reply_rate',
      render: (val: number) => `${(val * 100).toFixed(2)}%`
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (val: boolean) => (
        <Tag color={val ? 'success' : 'default'}>{val ? '启用' : '禁用'}</Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" type="link">编辑</Button>
          <Button size="small" type="link">预览</Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>话术管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          新建话术
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={templates}
        loading={loading}
        rowKey="id"
      />

      <Modal
        title="新建话术模板"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={700}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item
            name="name"
            label="模板名称"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="如: 首次触达-标准版" />
          </Form.Item>

          <Form.Item
            name="platform"
            label="适用平台"
            initialValue="douyin"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="douyin">抖音</Select.Option>
              <Select.Option value="xiaohongshu">小红书</Select.Option>
              <Select.Option value="bilibili">B站</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="scenario" label="适用场景">
            <Input placeholder="如: 首次触达" />
          </Form.Item>

          <Form.Item
            name="content"
            label="模板内容"
            rules={[{ required: true, message: '请输入模板内容' }]}
            extra="可使用变量: {昵称}, {粉丝数}, {微信号}, {运营姓名} 等"
          >
            <TextArea
              rows={6}
              placeholder="您好{昵称}，我是网易旗下永劫无间生态内容的运营..."
            />
          </Form.Item>

          <Form.Item name="description" label="模板描述">
            <TextArea rows={2} placeholder="描述此模板的用途和特点" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
