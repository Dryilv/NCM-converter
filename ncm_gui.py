import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from ncm_converter import NCMConverter

class NCMConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NCM Converter")

        # 设置样式
        style = ttk.Style()
        style.theme_use('default')  # 可以改为 'clam', 'alt', 'default', 'classic' 等
        style.configure('Treeview', rowheight=25)  # 设置行高
        style.configure('TButton', font=('Helvetica', 12), padding=6)
        style.configure('TFrame', padding=10)

        # 使用Frame增强布局
        self.frame = ttk.Frame(root, padding=(10, 10))
        self.frame.grid(row=0, column=0, sticky='nsew')

        # 使根窗口自适应大小变化
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # 设置表格
        self.tree = ttk.Treeview(self.frame, columns=('File Name', 'File Path', 'File Size'), show='headings')
        self.tree.heading('File Name', text='文件名')
        self.tree.heading('File Path', text='文件路径')
        self.tree.heading('File Size', text='文件大小')
        self.tree.column('File Name', width=150, anchor='w')
        self.tree.column('File Path', width=300, anchor='w')
        self.tree.column('File Size', width=100, anchor='e')
        self.tree.grid(row=0, column=0, columnspan=3, sticky='nsew')

        # 添加滚动条
        scroll = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        scroll.grid(row=0, column=3, sticky='ns')
        self.tree.configure(yscrollcommand=scroll.set)

        # 按钮
        self.select_files_button = ttk.Button(self.frame, text="选择文件", command=self.select_files)
        self.select_files_button.grid(row=1, column=0, pady=10, sticky='ew')

        self.select_output_button = ttk.Button(self.frame, text="选择存储位置", command=self.select_output)
        self.select_output_button.grid(row=1, column=1, pady=10, sticky='ew')

        self.convert_button = ttk.Button(self.frame, text="开始转换", command=self.convert_files)
        self.convert_button.grid(row=1, column=2, pady=10, sticky='ew')

        # 列与行配置
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.files = []
        self.output_path = None
        self.converter = NCMConverter()

    def select_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("NCM Files", "*.ncm")])
        self.files = list(paths)
        self.tree.delete(*self.tree.get_children())  # 清空列表
        for path in paths:
            file_name = os.path.basename(path)
            file_size = f"{os.path.getsize(path) / 1024:.2f} KB"
            self.tree.insert('', 'end', values=(file_name, path, file_size))
    
    def select_output(self):
        self.output_path = filedialog.askdirectory()
        if self.output_path:
            self.select_output_button.config(text=f"已选择存储位置: {self.output_path}")
        else:
            self.select_output_button.config(text="选择存储位置")

    def convert_files(self):
        if not self.files:
            messagebox.showwarning("警告", "请先选择一个或多个 .ncm 文件")
            return
        if not self.output_path:
            messagebox.showwarning("警告", "请先选择存储位置")
            return
        
        try:
            for file_path in self.files:
                self.converter.dump(file_path, self.output_path)  # 注意更新dump方法接受输出目录
            messagebox.showinfo("成功", f"所有文件已转换完毕并保存至: {self.output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"文件转换失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")  # 可以根据需要调整窗口大小
    app = NCMConverterGUI(root)
    root.mainloop()
