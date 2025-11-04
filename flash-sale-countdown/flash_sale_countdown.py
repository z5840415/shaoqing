#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闪购倒计时桌面应用
功能：
- 时间表管理（添加、编辑、删除）
- 实时倒计时
- 提前1分钟红色闪烁提醒（持续10秒）
- 窗口置顶
- 全屏/窗口切换
- 自动保存数据
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class FlashSaleCountdown:
    """闪购倒计时应用主类"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⚡ 闪购倒计时提醒工具")
        self.root.geometry("800x600")

        # 数据文件路径
        self.data_file = "flash_sales.json"

        # 时间表数据
        self.sales_times: List[Dict] = []

        # 已闪烁过的秒杀（避免重复闪烁）
        self.flashed_sales = set()

        # 闪烁状态
        self.is_flashing = False
        self.flash_start_time = None
        self.current_flash_item = None

        # 全屏状态
        self.is_fullscreen = False

        # 加载数据
        self.load_data()

        # 设置窗口置顶
        self.root.attributes('-topmost', True)

        # 创建界面
        self.create_widgets()

        # 绑定快捷键
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())

        # 启动倒计时更新
        self.update_countdown()

        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """创建界面组件"""

        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="⚡ 闪购倒计时提醒工具 ⚡",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        # 倒计时显示区域
        countdown_frame = ttk.LabelFrame(main_frame, text="⏱️ 倒计时", padding="20")
        countdown_frame.pack(fill=tk.X, padx=10, pady=10)

        self.countdown_label = ttk.Label(
            countdown_frame,
            text="距离下一个秒杀还有：计算中...",
            font=("Arial", 16, "bold"),
            foreground="blue"
        )
        self.countdown_label.pack()

        # 时间表显示区域
        table_frame = ttk.LabelFrame(main_frame, text="📊 秒杀时间表", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建表格
        columns = ("时间", "状态")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        # 设置列标题
        self.tree.heading("时间", text="秒杀时间")
        self.tree.heading("状态", text="状态")

        # 设置列宽
        self.tree.column("时间", width=200, anchor="center")
        self.tree.column("状态", width=150, anchor="center")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 配置行标签样式
        self.tree.tag_configure('normal', background='white')
        self.tree.tag_configure('flash', background='red', foreground='white')
        self.tree.tag_configure('passed', foreground='gray')

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # 添加时间按钮
        add_btn = ttk.Button(
            button_frame,
            text="➕ 添加时间",
            command=self.add_time
        )
        add_btn.pack(side=tk.LEFT, padx=5)

        # 删除时间按钮
        delete_btn = ttk.Button(
            button_frame,
            text="❌ 删除选中",
            command=self.delete_time
        )
        delete_btn.pack(side=tk.LEFT, padx=5)

        # 编辑时间按钮
        edit_btn = ttk.Button(
            button_frame,
            text="✏️ 编辑选中",
            command=self.edit_time
        )
        edit_btn.pack(side=tk.LEFT, padx=5)

        # 全屏按钮
        fullscreen_btn = ttk.Button(
            button_frame,
            text="🖥️ 全屏 (F11)",
            command=self.toggle_fullscreen
        )
        fullscreen_btn.pack(side=tk.RIGHT, padx=5)

        # 置顶按钮
        self.topmost_var = tk.BooleanVar(value=True)
        topmost_check = ttk.Checkbutton(
            button_frame,
            text="📌 窗口置顶",
            variable=self.topmost_var,
            command=self.toggle_topmost
        )
        topmost_check.pack(side=tk.RIGHT, padx=5)

        # 刷新时间表
        self.refresh_table()

    def load_data(self):
        """加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sales_times = data.get('sales_times', [])
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.sales_times = []
        else:
            # 初始化默认时间表（从图片中的时间）
            self.sales_times = [
                {"time": "12:20"},
                {"time": "12:40"},
                {"time": "13:00"},
                {"time": "13:20"},
                {"time": "13:40"},
                {"time": "14:00"},
                {"time": "14:20"},
                {"time": "14:40"},
                {"time": "15:00"},
                {"time": "15:20"},
                {"time": "15:40"}
            ]
            self.save_data()

    def save_data(self):
        """保存数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({'sales_times': self.sales_times}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def refresh_table(self):
        """刷新时间表显示"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 排序时间
        self.sales_times.sort(key=lambda x: x['time'])

        # 获取当前时间
        now = datetime.now()

        # 添加数据到表格
        for sale in self.sales_times:
            time_str = sale['time']
            sale_time = self.parse_time(time_str)

            if sale_time:
                if sale_time < now:
                    status = "已过期"
                    tag = 'passed'
                else:
                    time_diff = (sale_time - now).total_seconds()
                    if time_diff <= 60:  # 1分钟内
                        status = "⚡ 即将开始"
                        tag = 'flash'
                    else:
                        minutes = int(time_diff // 60)
                        status = f"还有 {minutes} 分钟"
                        tag = 'normal'

                self.tree.insert('', tk.END, values=(time_str, status), tags=(tag,))

    def parse_time(self, time_str: str) -> Optional[datetime]:
        """解析时间字符串，返回今天的该时刻"""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            today = datetime.now().date()
            return datetime.combine(today, time_obj)
        except ValueError:
            return None

    def get_next_sale(self) -> Optional[Dict]:
        """获取下一个秒杀时间"""
        now = datetime.now()

        upcoming_sales = []
        for sale in self.sales_times:
            sale_time = self.parse_time(sale['time'])
            if sale_time and sale_time > now:
                upcoming_sales.append({
                    'time_str': sale['time'],
                    'datetime': sale_time,
                    'seconds_until': (sale_time - now).total_seconds()
                })

        if upcoming_sales:
            # 返回最近的一个
            upcoming_sales.sort(key=lambda x: x['seconds_until'])
            return upcoming_sales[0]

        return None

    def update_countdown(self):
        """更新倒计时显示"""
        next_sale = self.get_next_sale()

        if next_sale:
            seconds = int(next_sale['seconds_until'])
            minutes = seconds // 60
            secs = seconds % 60

            self.countdown_label.config(
                text=f"距离下一个秒杀还有：{minutes}分{secs}秒",
                foreground="blue"
            )

            # 检查是否需要开始闪烁
            # 提前1分钟（60秒）开始闪烁
            if 50 <= seconds <= 60 and next_sale['time_str'] not in self.flashed_sales:
                if not self.is_flashing:
                    self.start_flash(next_sale['time_str'])

            # 检查是否需要停止闪烁
            if self.is_flashing and self.flash_start_time:
                flash_duration = (datetime.now() - self.flash_start_time).total_seconds()
                if flash_duration >= 10:  # 闪烁10秒
                    self.stop_flash()
        else:
            self.countdown_label.config(
                text="今天已无秒杀活动",
                foreground="gray"
            )

            # 停止闪烁
            if self.is_flashing:
                self.stop_flash()

        # 刷新表格（更新状态）
        self.refresh_table()

        # 每秒更新一次
        self.root.after(1000, self.update_countdown)

    def start_flash(self, time_str: str):
        """开始闪烁"""
        self.is_flashing = True
        self.flash_start_time = datetime.now()
        self.current_flash_item = time_str
        self.flashed_sales.add(time_str)
        self.flash_toggle = False
        self.do_flash()

    def do_flash(self):
        """执行闪烁动画"""
        if not self.is_flashing:
            return

        # 切换闪烁状态
        self.flash_toggle = not self.flash_toggle

        # 更新表格中的对应行
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if values[0] == self.current_flash_item:
                if self.flash_toggle:
                    self.tree.item(item, tags=('flash',))
                else:
                    self.tree.item(item, tags=('normal',))

        # 更新倒计时标签颜色
        if self.flash_toggle:
            self.countdown_label.config(foreground="red", font=("Arial", 16, "bold"))
        else:
            self.countdown_label.config(foreground="blue", font=("Arial", 16, "bold"))

        # 每0.5秒切换一次（每秒闪烁1次）
        self.root.after(500, self.do_flash)

    def stop_flash(self):
        """停止闪烁"""
        self.is_flashing = False
        self.flash_start_time = None
        self.current_flash_item = None
        self.countdown_label.config(foreground="blue")
        self.refresh_table()

    def add_time(self):
        """添加新时间"""
        dialog = TimeInputDialog(self.root, "添加秒杀时间", "")
        if dialog.result:
            # 验证时间格式
            if self.parse_time(dialog.result):
                self.sales_times.append({"time": dialog.result})
                self.save_data()
                self.refresh_table()
            else:
                messagebox.showerror("错误", "时间格式不正确！请使用 HH:MM 格式（如 14:30）")

    def delete_time(self):
        """删除选中的时间"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的时间！")
            return

        for item in selected:
            values = self.tree.item(item, 'values')
            time_str = values[0]

            # 从数据中删除
            self.sales_times = [s for s in self.sales_times if s['time'] != time_str]

        self.save_data()
        self.refresh_table()

    def edit_time(self):
        """编辑选中的时间"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的时间！")
            return

        if len(selected) > 1:
            messagebox.showwarning("警告", "一次只能编辑一个时间！")
            return

        item = selected[0]
        values = self.tree.item(item, 'values')
        old_time = values[0]

        dialog = TimeInputDialog(self.root, "编辑秒杀时间", old_time)
        if dialog.result:
            # 验证时间格式
            if self.parse_time(dialog.result):
                # 更新数据
                for sale in self.sales_times:
                    if sale['time'] == old_time:
                        sale['time'] = dialog.result
                        break

                self.save_data()
                self.refresh_table()
            else:
                messagebox.showerror("错误", "时间格式不正确！请使用 HH:MM 格式（如 14:30）")

    def toggle_topmost(self):
        """切换窗口置顶状态"""
        self.root.attributes('-topmost', self.topmost_var.get())

    def toggle_fullscreen(self, event=None):
        """切换全屏状态"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        return "break"

    def exit_fullscreen(self):
        """退出全屏"""
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)

    def on_closing(self):
        """窗口关闭时的处理"""
        self.save_data()
        self.root.destroy()


class TimeInputDialog:
    """时间输入对话框"""

    def __init__(self, parent, title, default_value=""):
        self.result = None

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (150 // 2)
        self.dialog.geometry(f"300x150+{x}+{y}")

        # 输入框
        label = ttk.Label(self.dialog, text="请输入时间（格式：HH:MM）：")
        label.pack(pady=20)

        self.entry = ttk.Entry(self.dialog, width=20, font=("Arial", 14))
        self.entry.pack(pady=10)
        self.entry.insert(0, default_value)
        self.entry.focus()

        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ok_btn = ttk.Button(button_frame, text="确定", command=self.ok)
        ok_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # 绑定回车键
        self.entry.bind('<Return>', lambda e: self.ok())

        # 等待对话框关闭
        self.dialog.wait_window()

    def ok(self):
        """确定按钮"""
        self.result = self.entry.get().strip()
        self.dialog.destroy()

    def cancel(self):
        """取消按钮"""
        self.result = None
        self.dialog.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = FlashSaleCountdown(root)
    root.mainloop()


if __name__ == "__main__":
    main()
