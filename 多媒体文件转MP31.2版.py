import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from threading import Thread
import subprocess
import re


class MP4toMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("多媒体文件转MP3工具")
        self.root.geometry("500x300")

        # 创建界面组件
        self.create_widgets()

        # 初始化文件路径
        self.input_file = ""
        self.output_folder = os.path.expanduser("~")
        self.total_duration = 0
        self.audio_quality = 2

        # 右下角添加作者信息
        self.author_label = tk.Label(self.root, text="我是小猫")
        self.author_label.place(relx=0.95, rely=0.95, anchor=tk.SE)

        # 左下角添加微信号信息
        self.wechat_label = tk.Label(self.root, text="微信号hcyaaa197")
        self.wechat_label.place(relx=0.05, rely=0.95, anchor=tk.SW)

    def create_widgets(self):
        # 文件选择区域
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)

        self.btn_select = tk.Button(
            file_frame,
            text="选择多媒体文件",
            command=self.select_file,
            bg="green"
        )
        self.btn_select.pack(side=tk.LEFT, padx=5)

        self.file_label = tk.Label(file_frame, text="未选择文件")
        self.file_label.pack(side=tk.LEFT, padx=5)

        # 输出目录选择
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=5)

        self.btn_output = tk.Button(
            output_frame,
            text="选择输出目录",
            command=self.select_output_folder
        )
        self.btn_output.pack(side=tk.LEFT, padx=5)

        self.output_label = tk.Label(output_frame, text="输出到：桌面")
        self.output_label.pack(side=tk.LEFT, padx=5)

        # 转换按钮
        self.btn_convert = tk.Button(
            self.root,
            text="开始转换",
            command=self.start_conversion_thread,
            state=tk.DISABLED
        )
        self.btn_convert.pack(pady=10)

        # 音频质量选择
        quality_frame = tk.Frame(self.root)
        quality_frame.pack(pady=5)

        quality_label = tk.Label(quality_frame, text="选择音频质量 (0 - 9, 0为最高质量):")
        quality_label.pack(side=tk.LEFT, padx=5)

        self.quality_var = tk.StringVar()
        self.quality_var.set("2")

        quality_options = [str(i) for i in range(10)]
        self.quality_combobox = ttk.Combobox(quality_frame, textvariable=self.quality_var, values=quality_options)
        self.quality_combobox.pack(side=tk.LEFT, padx=5)

        # 进度条
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        # 进度标签
        self.status_label = tk.Label(self.root, text="准备就绪")
        self.status_label.pack()

    def select_file(self):
        filetypes = (
            ("MP4文件", "*.mp4"),
            ("WAV文件", "*.wav"),
            ("AAC文件", "*.aac"),
            ("MOV文件", "*.mov"),
            ("所有文件", "*.*")
        )
        self.input_file = filedialog.askopenfilename(
            title="选择多媒体文件",
            filetypes=filetypes
        )
        if self.input_file:
            self.file_label.config(text=os.path.basename(self.input_file))
            self.btn_convert.config(state=tk.NORMAL)
        else:
            self.file_label.config(text="未选择文件")
            self.btn_convert.config(state=tk.DISABLED)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=f"输出到：{folder}")

    def start_conversion_thread(self):
        if not self.input_file:
            messagebox.showerror("错误", "请先选择多媒体文件！")
            return

        try:
            self.audio_quality = int(self.quality_var.get())
            if self.audio_quality < 0 or self.audio_quality > 9:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "请输入 0 - 9 之间的有效数字作为音频质量。")
            return

        self.btn_convert.config(state=tk.DISABLED)
        self.status_label.config(text="转换中...")
        self.progress_bar['value'] = 0

        self.get_total_duration()

        thread = Thread(target=self.convert_to_mp3)
        thread.start()

    def get_total_duration(self):
        try:
            command = ['ffmpeg', '-i', self.input_file]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
            output, _ = process.communicate()
            duration_match = re.search(r'Duration: (\d+):(\d+):(\d+.\d+)', output)
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = float(duration_match.group(3))
                self.total_duration = hours * 3600 + minutes * 60 + seconds
        except Exception as e:
            print(f"获取视频时长失败: {e}")

    def convert_to_mp3(self):
        try:
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(self.output_folder, f"{base_name}.mp3")

            command = [
                'ffmpeg',
                '-i', self.input_file,
                '-vn',
                '-acodec', 'libmp3lame',
                '-q:a', str(self.audio_quality),
                output_file
            ]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8'
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    time_match = re.search(r'time=(\d+):(\d+):(\d+.\d+)', output)
                    if time_match and self.total_duration > 0:
                        hours = int(time_match.group(1))
                        minutes = int(time_match.group(2))
                        seconds = float(time_match.group(3))
                        elapsed_time = hours * 3600 + minutes * 60 + seconds
                        progress = (elapsed_time / self.total_duration) * 100
                        self.root.after(0, self.update_progress, progress)

            self.root.after(0, self.conversion_complete)

        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def update_progress(self, progress):
        self.progress_bar['value'] = progress
        self.status_label.config(text=f"转换中... {progress:.2f}%")

    def conversion_complete(self):
        self.btn_convert.config(state=tk.NORMAL)
        self.status_label.config(text="转换完成！")
        self.progress_bar['value'] = 100
        messagebox.showinfo("完成", "文件转换成功！")

    def show_error(self, message):
        self.btn_convert.config(state=tk.NORMAL)
        self.status_label.config(text="转换失败")
        self.progress_bar['value'] = 0
        messagebox.showerror("错误", f"转换过程中发生错误：\n{message}")


if __name__ == "__main__":
    try:
        subprocess.run(['ffmpeg', '-version'], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        messagebox.showerror("依赖缺失", "未找到FFmpeg，请先安装FFmpeg并添加到系统路径")
        exit()

    root = tk.Tk()
    app = MP4toMP3Converter(root)
    root.mainloop()
