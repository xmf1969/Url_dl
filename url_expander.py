import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

def resolve_url():
    short_url = url_input.get().strip()
    if not short_url:
        messagebox.showwarning("提示", "请输入需要解析的短链接！")
        return
    
    # 自动补全 URL 协议头
    if not short_url.startswith(("http://", "https://")):
        short_url = "https://" + short_url

    # 清空结果框并提示加载
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "正在解析中，请稍候...\n")
    result_text.config(state="disabled")
    btn_resolve.config(state="disabled")

    def worker():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            # 优先使用 HEAD 请求获取响应头，速度更快且省流量
            try:
                response = requests.head(short_url, allow_redirects=True, timeout=8, headers=headers)
            except requests.RequestException:
                # 若服务器不支持 HEAD 请求，退回使用 GET 请求
                response = requests.get(short_url, allow_redirects=True, timeout=8, headers=headers)

            output = []
            if response.history:
                output.append("=== 重定向路径 ===")
                for i, resp in enumerate(response.history, 1):
                    loc = resp.headers.get('Location', '未知')
                    output.append(f"[{i}] {resp.status_code} -> {loc}")
                output.append("\n=== 最终真实链接 ===")
            else:
                output.append("=== 最终真实链接（无跳转） ===")
            
            output.append(response.url)
            result_str = "\n".join(output)

        except Exception as e:
            result_str = f"解析失败：{str(e)}"

        # 切回 UI 线程更新界面
        root.after(0, update_ui, result_str)

    # 开启子线程，避免界面卡死
    threading.Thread(target=worker, daemon=True).start()

def update_ui(result_str):
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, result_str)
    result_text.config(state="disabled")
    btn_resolve.config(state="normal")

def copy_to_clipboard():
    content = result_text.get("1.0", tk.END).strip()
    if content and not content.startswith("正在解析") and not content.startswith("解析失败"):
        # 提取最后一行即最终的真实链接
        final_url = content.splitlines()[-1]
        root.clipboard_clear()
        root.clipboard_append(final_url)
        messagebox.showinfo("成功", "真实链接已复制到剪贴板！")

# ----------------- GUI 布局 -----------------
root = tk.Tk()
root.title("短链接还原解析工具")
root.geometry("560x360")  # 严格的标准尺寸语法
root.resizable(False, False)

# 主容器
frame = ttk.Frame(root, padding=15)
frame.pack(fill=tk.BOTH, expand=True)

# 输入区域
lbl_input = ttk.Label(frame, text="短链接 URL:")
lbl_input.pack(anchor=tk.W, pady=(0, 5))

input_frame = ttk.Frame(frame)
input_frame.pack(fill=tk.X, pady=(0, 10))

url_input = ttk.Entry(input_frame, font=("Segoe UI", 10))
url_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
url_input.focus()
url_input.bind("<Return>", lambda event: resolve_url())

btn_resolve = ttk.Button(input_frame, text="解析", command=resolve_url)
btn_resolve.pack(side=tk.RIGHT)

# 结果显示区域
lbl_output = ttk.Label(frame, text="解析结果:")
lbl_output.pack(anchor=tk.W, pady=(0, 5))

result_text = tk.Text(frame, height=10, font=("Consolas", 10), state="disabled", wrap=tk.WORD)
result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# 底部按钮
btn_copy = ttk.Button(frame, text="复制真实链接", command=copy_to_clipboard)
btn_copy.pack(anchor=tk.E)

root.mainloop()