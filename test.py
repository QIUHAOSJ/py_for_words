import tkinter as tk
from tkinter import messagebox
import sqlite3
import requests
import json
import pandas as pd
from openpyxl import Workbook
import matplotlib.pyplot as plt

# 创建数据库连接
conn = sqlite3.connect('words.db')
cursor = conn.cursor()

# 创建单词表
def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS words
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       word TEXT,
                       translation TEXT,
                       example TEXT)''')
    conn.commit()

# 插入单词
def insert_word():
    word = entry_word.get()
    translation = entry_translation.get()
    example = text_example.get('1.0', 'end-1c')

    if not word or not translation:
        messagebox.showwarning("警告", "请填写单词和翻译")
        return

    cursor.execute("INSERT INTO words (word, translation, example) VALUES (?, ?, ?)",
                   (word, translation, example))
    conn.commit()
    messagebox.showinfo("成功", "单词添加成功")

# 查询单词
def query_word():
    word = entry_word.get()

    if not word:
        messagebox.showwarning("警告", "请填写单词")
        return

    cursor.execute("SELECT * FROM words WHERE word=?", (word,))
    result = cursor.fetchone()

    if result:
        _, translation, example = result
        entry_translation.delete(0, tk.END)
        entry_translation.insert(tk.END, translation)
        text_example.delete('1.0', tk.END)
        text_example.insert(tk.END, example)
    else:
        messagebox.showwarning("警告", "未找到该单词")

# 删除单词
def delete_word():
    word = entry_word.get()

    if not word:
        messagebox.showwarning("警告", "请填写单词")
        return

    cursor.execute("DELETE FROM words WHERE word=?", (word,))
    conn.commit()
    messagebox.showinfo("成功", "单词删除成功")

# 显示全部单词
def show_all_words():
    cursor.execute("SELECT * FROM words")
    results = cursor.fetchall()

    for row in results:
        word, translation, example = row
        print(f"Word: {word}\nTranslation: {translation}\nExample: {example}\n")

# 导出为 Excel
def export_to_excel():
    cursor.execute("SELECT * FROM words")
    results = cursor.fetchall()

    df = pd.DataFrame(results, columns=["Word", "Translation", "Example"])
    df.to_excel("words.xlsx", index=False)
    messagebox.showinfo("成功", "导出成功")

# 爬取网站内容
def crawl_website():
    url = "http://example.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": "BIDUPSID=E77D173C218741B4316FD79F5650C055; PSTM=1600136675; BD_UPN=12314753; MCITY=-127%3A; BAIDUID=EE2F041E9195FB2FE8425732D124D78A:FG=1; BDUSS=k4N0xCZng0d0YzOG05QkFpMUR0cG40bmRYdTBiMFZ3cGtzenp6dGJ1MWFUNEpsSVFBQUFBJCQAAAAAAAAAAAEAAAC5AlDrYTFzMmQzZmFuNTIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFrCWmVawlplc1; BDUSS_BFESS=k4N0xCZng0d0YzOG05QkFpMUR0cG40bmRYdTBiMFZ3cGtzenp6dGJ1MWFUNEpsSVFBQUFBJCQAAAAAAAAAAAEAAAC5AlDrYTFzMmQzZmFuNTIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFrCWmVawlplc1; H_WISE_SIDS_BFESS=275733_259642_280650_281893_281686_282192_279613_281864_284810_285064_282427_285751_285873_285156_281810_269892_286243_286611_282466_281704_286996_287056_110085_287232_287236_287227_283016_281995_287596_287627_286899_284820_280167_278415_284836_282485_288152; H_PS_PSSID=39839_39934_39933_39943_39939_39998_40039_40051_40033; ab_sr=1.0.1_NDY3YjgxYTA3ZWEyNzM3MWU2ODFmNDZhZWU1MjMwMGE2Mzc4MmU2OGU2Mzc1NGFhMDc2YTJkYThkNGNlZGFhYzYwNWJiYjNiNGJjMjQzZTk3ZDZjMzA3MzBmM2NhNDE2Y2FiMjE0YjhlMjAyMTM0ZTljMTljNTIxYmNjMDY2YmE3ZmVhZDRmYjc3ZjA3MzAxOWI2NjQ3ODAzY2I1ZDljOGZhN2Y4YmJhYTBjODFjOTcxNjEzNGI0MWY1MmQ4YjRhOGRlYWZmNjc3MzdjNGRkYWU5NTU5OTUwMGQ3NjVmZTU=; H_WISE_SIDS=39839_39934_39933_39943_39939_39998_40039_40051_40033; H_PS_645EC=1c7cJxJvdL1b0qkKTJcNRe61vZETqKMzUozQzTcustknuG5jLfu3GXSwNQ8; delPer=0; BD_CK_SAM=1; PSINO=6; BAIDUID_BFESS=EE2F041E9195FB2FE8425732D124D78A:FG=1; BDSVRTM=0; BDORZ=FFFB88E999055A3F8A630C64834BD6D0"
    }

    try:
        response = requests.get(url, headers=headers)
        # 处理网页内容
        # ...

        messagebox.showinfo("成功", "网站爬取成功")
    except requests.exceptions.RequestException:
        messagebox.showerror("错误", "网站爬取失败")

# 爬取翻译
def crawl_translation():
    word = entry_word.get()
    url = f"https://translation-api.example.com/translate?word={word}"

    try:
        response = requests.get(url)
        data = json.loads(response.text)
        translation = data["translation"]
        entry_translation.delete(0, tk.END)
        entry_translation.insert(tk.END, translation)
        messagebox.showinfo("成功", "翻译成功")
    except (requests.exceptions.RequestException, KeyError):
        messagebox.showerror("错误", "翻译失败")

# 重构数据库
def rebuild_database():
    cursor.execute("DROP TABLE IF EXISTS words")
    create_table()
    messagebox.showinfo("成功", "数据库重构成功")

# 数据分析
def data_analysis():
    cursor.execute("SELECT word, translation FROM words")
    results = cursor.fetchall()
    words = [row[0] for row in results]
    translations = [row[1] for row in results]

    # 进行数据分析和可视化
    # ...

# 创建主界面
window = tk.Tk()
window.title("单词管理系统")
window.geometry("400x300")

# 创建控件
label_word = tk.Label(window, text="单词")
label_word.grid(row=0, column=0, sticky=tk.W)

entry_word = tk.Entry(window)
entry_word.grid(row=0, column=1)

label_translation = tk.Label(window, text="翻译")
label_translation.grid(row=1, column=0, sticky=tk.W)

entry_translation = tk.Entry(window)
entry_translation.grid(row=1, column=1)

label_example = tk.Label(window, text="例句")
label_example.grid(row=2, column=0, sticky=tk.W)

text_example = tk.Text(window, width=30, height=5)
text_example.grid(row=2, column=1)

btn_insert = tk.Button(window, text="插入", command=insert_word)
btn_insert.grid(row=3, column=0, pady=10)

btn_query = tk.Button(window, text="查询", command=query_word)
btn_query.grid(row=3, column=1, pady=10)

btn_delete = tk.Button(window, text="删除", command=delete_word)
btn_delete.grid(row=4, column=0, pady=10)

btn_show_all = tk.Button(window, text="显示全部", command=show_all_words)
btn_show_all.grid(row=4, column=1, pady=10)

btn_export = tk.Button(window, text="导出Excel", command=export_to_excel)
btn_export.grid(row=5, column=0, pady=10)

btn_crawl_website = tk.Button(window, text="爬取网站", command=crawl_website)
btn_crawl_website.grid(row=5, column=1, pady=10)

btn_crawl_translation = tk.Button(window, text="爬取翻译", command=crawl_translation)
btn_crawl_translation.grid(row=6, column=0, pady=10)

btn_rebuild_database = tk.Button(window, text="重构数据库", command=rebuild_database)
btn_rebuild_database.grid(row=6, column=1, pady=10)

btn_data_analysis = tk.Button(window, text="数据分析", command=data_analysis)
btn_data_analysis.grid(row=7, column=0, pady=10)

# 创建单词表
create_table()

# 运行主循环
window.mainloop()

# 关闭数据库连接
cursor.close()
conn.close()