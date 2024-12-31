import ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import threading
import time
import traceback
import os

# 设置日志记录配置
logging.basicConfig(filename='audio_extraction.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def extract_audio(video_path, audio_path, update_time_callback):
    """
    使用 FFmpeg 提取视频中的音频，并支持多种音频格式

    Args:
        video_path (str): 视频文件路径
        audio_path (str): 保存音频的路径
        update_time_callback (function): 用于更新提取时间的回调函数
    """
    try:
        # 记录开始时间
        start_time = time.time()

        logging.info(f"视频路径: {video_path}")
        logging.info(f"音频保存路径: {audio_path}")

        # 确保保存路径有扩展名
        if not audio_path.endswith(('.mp3', '.aac', '.wav')):
            raise ValueError(f"保存路径 {audio_path} 必须以 .mp3, .aac 或 .wav 结尾")

        # 检查视频文件是否存在
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件 {video_path} 不存在")

        logging.info(f"检查通过: 视频文件存在")

        # 生成 FFmpeg 命令
        input_stream = ffmpeg.input(video_path)

        if audio_path.endswith('.mp3'):
            # MP3格式
            output_stream = ffmpeg.output(input_stream, audio_path, acodec='libmp3lame', vn=None, threads=4, b='192k')
        elif audio_path.endswith('.wav'):
            # WAV格式
            output_stream = ffmpeg.output(input_stream, audio_path, acodec='pcm_s16le', vn=None, threads=4)
        else:
            # 默认使用 AAC 格式
            output_stream = ffmpeg.output(input_stream, audio_path, acodec='aac', vn=None, threads=4, b='192k')

        # 打印 FFmpeg 命令到日志
        ffmpeg_command = ffmpeg.compile(output_stream)
        logging.debug(f"FFmpeg 命令: {ffmpeg_command}")

        # 开始提取音频
        process = ffmpeg.run_async(output_stream)

        logging.info(f"音频提取已启动，开始提取...")

        # 每秒更新一次时间
        elapsed_time = 0
        while process.poll() is None:  # 当进程未结束时，每秒更新一次时间
            elapsed_time = time.time() - start_time
            update_time_callback(f"提取时间：{int(elapsed_time)} 秒")
            time.sleep(1)

        # 提取完成
        elapsed_time = time.time() - start_time
        update_time_callback(f"提取时间：{int(elapsed_time)} 秒")  # 提取完成后更新总时间
        logging.info(f"音频提取成功，总共花费 {elapsed_time:.2f} 秒")
        messagebox.showinfo("完成", f"音频提取成功！\n保存路径：{audio_path}\n提取时间：{int(elapsed_time)} 秒")
    except FileNotFoundError as fnf_error:
        logging.error(f"文件不存在: {fnf_error}")
        messagebox.showerror("错误", f"文件不存在，请检查路径: {fnf_error}")
    except ValueError as ve:
        logging.error(f"路径格式错误: {ve}")
        messagebox.showerror("错误", f"路径格式错误: {ve}")
    except Exception as e:
        logging.error(f"提取失败: {e}")
        logging.error(f"错误堆栈: {traceback.format_exc()}")
        messagebox.showerror("错误", f"提取失败：{e}")


def browse_video():
    """打开文件选择框，选择视频文件"""
    video_file = filedialog.askopenfilename(title="选择视频文件", filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")))
    if video_file:
        video_entry.delete(0, tk.END)
        video_entry.insert(0, video_file)
        logging.info(f"选择了视频文件: {video_file}")


def browse_audio():
    """打开文件选择框，选择保存的音频文件路径"""
    audio_file = filedialog.asksaveasfilename(defaultextension=".aac", title="保存音频文件", filetypes=(
        ("AAC files", "*.aac"), ("MP3 files", "*.mp3"), ("WAV files", "*.wav")))

    if audio_file:
        audio_entry.delete(0, tk.END)
        audio_entry.insert(0, audio_file)
        logging.info(f"选择了音频保存路径: {audio_file}")


def start_extraction():
    """开始提取音频"""
    video_path = video_entry.get()
    audio_path = audio_entry.get()

    if not video_path or not audio_path:
        logging.error("请选择视频文件和音频保存路径")
        messagebox.showerror("错误", "请选择视频文件和音频保存路径")
        return

    # 启动线程处理提取操作，避免阻塞主界面
    extraction_thread = threading.Thread(target=extract_audio, args=(video_path, audio_path, update_time))
    extraction_thread.start()


def update_time(text):
    """更新GUI中的提取时间"""
    time_label.config(text=text)


# 创建 GUI 窗口
root = tk.Tk()
root.title("视频音频提取器")
root.geometry("500x300")

# 视频文件选择框
video_label = tk.Label(root, text="选择视频文件:")
video_label.pack(pady=5)
video_entry = tk.Entry(root, width=50)
video_entry.pack(pady=5)
browse_video_button = tk.Button(root, text="浏览", command=browse_video)
browse_video_button.pack(pady=5)

# 音频保存路径选择框
audio_label = tk.Label(root, text="保存音频文件路径:")
audio_label.pack(pady=5)
audio_entry = tk.Entry(root, width=50)
audio_entry.pack(pady=5)
browse_audio_button = tk.Button(root, text="浏览", command=browse_audio)
browse_audio_button.pack(pady=5)

# 提取按钮
extract_button = tk.Button(root, text="开始提取音频", command=start_extraction)
extract_button.pack(pady=20)

# 显示提取时间的标签
time_label = tk.Label(root, text="提取时间：")
time_label.pack(pady=5)

root.mainloop()
