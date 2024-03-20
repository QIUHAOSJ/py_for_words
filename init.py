import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import ttk
from tkinter import simpledialog
import pandas as pd
import openpyxl
from urllib import parse,request
import requests
import json
import re
import pandas as pd
import matplotlib.pyplot as plt

#头文件


def getWords():
    post_url = "https://fanyi.baidu.com/sug"
    word = simpledialog.askstring("单词翻译", "请输入要翻译的单词:")
    if not word:
        return  # 如果用户没有输入单词，则不进行翻译

    data = {
        'kw': word
    }
    response = requests.post(url=post_url, data=data, headers=headers)
    dir_obj = response.json()
    print(dir_obj)
    try:
        fp = open('./words.json', 'w', encoding='utf-8')
        json.dump(dir_obj, fp=fp, ensure_ascii=False)
        fp.close()
        messagebox.showinfo(title='提示', message='文件写入成功')
    except Exception as e:
        messagebox.showerror(title='错误', message='文件写入失败：' + str(e))
    insert_data(load_data("words.json"))    
def update_table():
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    try:
        # 遍历数据库，获取所有数据
        cursor.execute("SELECT * FROM words")
        rows = cursor.fetchall()

        # 按照首字母排序数据
        sorted_rows = sorted(rows, key=lambda x: x[1][0].lower())

        # 清空原有数据表
        cursor.execute("DELETE FROM words")

        # 重新插入排序后的数据
        for row in sorted_rows:
            cursor.execute("INSERT INTO words (id, english, chinese, count, create_time) VALUES (?, ?, ?, ?, ?)",
                           (row[0], row[1], row[2], row[3], row[4]))

        # 提交更改
        conn.commit()
        
        print("数据库重构成功！")

    except sqlite3.Error as e:
        print(f"操作数据库时出现错误：{e}")

    finally:
        # 关闭连接
        conn.close()
    remove_duplicates()    
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": "BIDUPSID=E77D173C218741B4316FD79F5650C055; PSTM=1600136675; BD_UPN=12314753; MCITY=-127%3A; BAIDUID=EE2F041E9195FB2FE8425732D124D78A:FG=1; BDUSS=k4N0xCZng0d0YzOG05QkFpMUR0cG40bmRYdTBiMFZ3cGtzenp6dGJ1MWFUNEpsSVFBQUFBJCQAAAAAAAAAAAEAAAC5AlDrYTFzMmQzZmFuNTIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFrCWmVawlplc1; BDUSS_BFESS=k4N0xCZng0d0YzOG05QkFpMUR0cG40bmRYdTBiMFZ3cGtzenp6dGJ1MWFUNEpsSVFBQUFBJCQAAAAAAAAAAAEAAAC5AlDrYTFzMmQzZmFuNTIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFrCWmVawlplc1; H_WISE_SIDS_BFESS=275733_259642_280650_281893_281686_282192_279613_281864_284810_285064_282427_285751_285873_285156_281810_269892_286243_286611_282466_281704_286996_287056_110085_287232_287236_287227_283016_281995_287596_287627_286899_284820_280167_278415_284836_282485_288152; H_PS_PSSID=39839_39934_39933_39943_39939_39998_40039_40051_40033; ab_sr=1.0.1_NDY3YjgxYTA3ZWEyNzM3MWU2ODFmNDZhZWU1MjMwMGE2Mzc4MmU2OGU2Mzc1NGFhMDc2YTJkYThkNGNlZGFhYzYwNWJiYjNiNGJjMjQzZTk3ZDZjMzA3MzBmM2NhNDE2Y2FiMjE0YjhlMjAyMTM0ZTljMTljNTIxYmNjMDY2YmE3ZmVhZDRmYjc3ZjA3MzAxOWI2NjQ3ODAzY2I1ZDljOGZhN2Y4YmJhYTBjODFjOTcxNjEzNGI0MWY1MmQ4YjRhOGRlYWZmNjc3MzdjNGRkYWU5NTU5OTUwMGQ3NjVmZTU=; H_WISE_SIDS=39839_39934_39933_39943_39939_39998_40039_40051_40033; H_PS_645EC=1c7cJxJvdL1b0qkKTJcNRe61vZETqKMzUozQzTcustknuG5jLfu3GXSwNQ8; delPer=0; BD_CK_SAM=1; PSINO=6; BAIDUID_BFESS=EE2F041E9195FB2FE8425732D124D78A:FG=1; BDSVRTM=0; BDORZ=FFFB88E999055A3F8A630C64834BD6D0"
    }
#获取url
def get_url(word):
    base_url = "http://www.baidu.com/s?wd="
    new_word = parse.quote(word)
    url = base_url+new_word
    return url

#获取html
def get_html(url,headers):
    #创建请求对象
    req = request.Request(url=url,headers=headers)
    #发送请求，获取响应对象
    res = request.urlopen(req)
    #获取html
    html = res.read().decode('utf-8')
    return html

#保存数据
def save_data(filename,html):
    with open(filename,'w',encoding="utf-8") as f:
        f.write(html)

#将数据导出为Excel
def export_to_excel():
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 从数据库中读取数据
    df = pd.read_sql_query("SELECT * from words", conn)

    # 将数据导出为Excel文件
    df.to_excel("words.xlsx", index=False)

    # 关闭连接
    conn.close()

    messagebox.showinfo("成功", "导出成功")

#建立数据库
def create_table():
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    try:
        # 创建数据表
        cursor.execute('''CREATE TABLE IF NOT EXISTS words
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       english TEXT,
                       chinese TEXT,
                       count INTEGER,
                       create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        # 提交更改
        conn.commit()

    except sqlite3.Error as e:
        print(f"操作数据库时出现错误：{e}")

    finally:
        # 关闭连接
        conn.close()
#查询单词
def search_word(english):
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    cursor.execute("SELECT english, chinese, count FROM words WHERE english=?", (english,))
    for row in cursor.fetchall():
        print(row)
    try:
        # 查询英文单词对应的中文翻译
        cursor.execute("SELECT english, chinese FROM words WHERE english=?", (english,))
        result = cursor.fetchone()

        if result is not None:
            messagebox.showinfo("查询结果", f"{result[0]} 的中文翻译为：{result[1]}")
            chinese_translation = result[1]
            count = result[2] + 1
            # 更新查询次数
            cursor.execute("UPDATE words SET count=? WHERE english=?", (count, english))

            messagebox.showinfo("查询结果", f"{english} 的中文翻译为：{chinese_translation}")
        else:
            messagebox.showinfo("查询结果", f"未找到英文单词：{english}")
            getWords(english)
    except sqlite3.Error as e:
        messagebox.showerror("错误", f"操作数据库时出现错误：{e}")

    finally:
        # 关闭连接
        conn.close()
#删除单词
def delete_word(english):
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    try:
        # 删除指定的英文单词对应的数据
        cursor.execute("DELETE FROM words WHERE english=?", (english,))
        if cursor.rowcount == 0:
            messagebox.showinfo("删除结果", f"未找到英文单词：{english}")
        else:
            messagebox.showinfo("删除结果", f"已删除英文单词：{english}")

        # 提交更改
        conn.commit()

    except sqlite3.Error as e:
        messagebox.showerror("错误", f"操作数据库时出现错误：{e}")

    finally:
        # 关闭连接
        conn.close()
#添加单词
def insert_word(english, chinese):
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    try:
        # 查询是否存在相同的英文单词
        cursor.execute("SELECT english, chinese FROM words WHERE english=?", (english,))
        result = cursor.fetchone()
        cursor.execute("SELECT english, chinese, count FROM words WHERE english=?", (english,))
        result = cursor.fetchone()

        if result is not None:
            saved_chinese = result[1]
            saved_count = result[2]
            if saved_chinese != chinese:
                # 更新中文内容并加上分号
                chinese += ";" + saved_chinese

                # 更新数据库中的数据
                cursor.execute("UPDATE words SET chinese=?, count=? WHERE english=?", (chinese, saved_count + 1, english))
                messagebox.showinfo("插入结果", f"已更新 {english} 的中文翻译为：{chinese}")
            else:
                messagebox.showinfo("插入结果", f"{english} 的中文翻译已存在，无需更新")
        else:
            # 插入新数据
            cursor.execute("INSERT INTO words (english, chinese, count) VALUES (?, ?, 1)", (english, chinese))
            messagebox.showinfo("插入结果", f"已插入新数据：{english}: {chinese}")

        # 提交更改
        conn.commit()

        # 刷新最近添加的单词列表
        show_recent_words_on_main()

    except sqlite3.Error as e:
        messagebox.showerror("错误", f"操作数据库时出现错误：{e}")

    finally:
        # 关闭连接
        conn.close()
#显示所有单词

#创建菜单

def create_menu():
    # 设置导航栏字体样式
    font = ("Arial", 10, "bold")
    
    menu_frame = tk.Frame(window)
    menu_frame.pack(side="top", fill="x")
    
    # 创建一个弹窗用于显示其他功能按钮的内容
    def show_popup():
        popup = tk.Toplevel(window)
        popup.title("其他功能")
        popup.geometry("200x200")
        
        options = [
            ("查询", search_window),
            ("删除", delete_window),
            ("插入", insert_window),
            ("显示全部", show_all_words),
            ("导出excel", export_to_excel1),
            ("爬取网站", crawl_website),
            ("爬取翻译", getWords),
            ("重构数据库", update_table),
            ("数据库修改记录", export_to_excel),
            ("数据分析", analyze_initial_counts)
        ]
        
        for i, (text, command) in enumerate(options):
            button = tk.Button(popup, text=text, command=command, bg="#fff", fg="#000", 
                               font=font, padx=5, pady=3, bd=0, activebackground="#eee", 
                               activeforeground="#000")
            button.pack(side="top", fill="x")
            
    # 创建一个功能按钮，点击后显示其他功能按钮的内容
    menu_button = tk.Button(menu_frame, text="更多功能", command=show_popup, bg="#fff", fg="#000", 
                           font=font, padx=5, pady=3, bd=0, activebackground="#eee", 
                           activeforeground="#000")
    menu_button.pack(side="top", fill="x")

#查询单词
def search_window():
    # 创建新窗口
    search_win = tk.Toplevel(window)

    # 设置窗口标题
    search_win.title("查询单词")

    # 创建标签和输入框
    label = tk.Label(search_win, text="请输入要查询的英文单词：")
    label.pack()

    word_entry = tk.Entry(search_win)
    word_entry.pack()

    # 创建确认按钮
    confirm_button = tk.Button(search_win, text="确认", command=lambda: search_word(word_entry.get()))
    confirm_button.pack()
#删除单词
def delete_window():
    # 创建新窗口
    delete_win = tk.Toplevel(window)

    # 设置窗口标题
    delete_win.title("删除单词")

    # 创建标签和输入框
    label = tk.Label(delete_win, text="请输入要删除的英文单词：")
    label.pack()

    word_entry = tk.Entry(delete_win)
    word_entry.pack()

    # 创建确认按钮
    confirm_button = tk.Button(delete_win, text="确认", command=lambda: delete_word(word_entry.get()))
    confirm_button.pack()
#显示最近添加的单词
def show_recent_words_on_main():
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    try:
        # 查询最近添加的5行数据
        cursor.execute("SELECT english, chinese, count FROM words ORDER BY create_time DESC LIMIT 10")
        results = cursor.fetchall()
        if len(results) > 0:
            # 创建标签框架
            recent_frame = tk.LabelFrame(window, text="最近添加的单词", width=500, height=400)
            recent_frame.place(x=10, y=40)

            # 创建表格
            table = ttk.Treeview(recent_frame, columns=("english", "chinese", "count"), show="headings")
            table.column("english", width=100, anchor="center")
            table.column("chinese", width=200, anchor="center")
            table.column("count", width=50, anchor="center")
            table.heading("english", text="英文单词")
            table.heading("chinese", text="中文翻译")
            table.heading("count", text="查询次数")

            for result in results:
                table.insert("", "end", values=result)

            table.pack()

        else:
            messagebox.showinfo("查询结果", "数据库中没有最近添加的单词")

    except sqlite3.Error as e:
        messagebox.showerror("错误", f"操作数据库时出现错误：{e}")
    finally:
        # 关闭连接
        conn.close()
#主界面插入单词
def insert_window():
    # 创建新窗口
    insert_win = tk.Toplevel(window)

    # 设置窗口标题
    insert_win.title("插入单词")

    # 创建标签和输入框
    english_label = tk.Label(insert_win, text="请输入插入的英文单词：")
    english_label.pack()

    english_entry = tk.Entry(insert_win)
    english_entry.pack()

    chinese_label = tk.Label(insert_win, text="请输入对应的中文翻译：")
    chinese_label.pack()

    chinese_entry = tk.Entry(insert_win)
    chinese_entry.pack()

    # 创建确认按钮
    confirm_button = tk.Button(insert_win, text="确认", command=lambda: insert_word(english_entry.get(), chinese_entry.get()))
    confirm_button.pack()
#回车确定
def on_enter(event):
    insert_word(english_entry.get(), chinese_entry.get())
    english_entry.delete(0, 'end')
    chinese_entry.delete(0, 'end')

def show_all_words():
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    try:
        # 查询所有的词条数据
        cursor.execute("SELECT english, chinese, count FROM words")
        results = cursor.fetchall()
        if len(results) > 0:
            # 对结果按照单词长度排序
            results_sorted = sorted(results, key=lambda x: (len(x[0]), x[0]))
            message = "所有词条：\n"
            message += "+----------+------------------+----------+\n"
            message += "| 英文单词 | 中文翻译         | 查询次数 |\n"
            message += "+----------+------------------+----------+\n"
            for result in results_sorted:
                message += f"| {result[0]:<8} | {result[1]:<16} | {result[2]:<8} |\n"
            message += "+----------+------------------+----------+\n"

            # 创建一个新的窗口
            top = tk.Toplevel()
            top.title("查询结果")

            # 创建滚动条
            scroll_bar = tk.Scrollbar(top)
            scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

            # 创建文本框
            text_box = tk.Text(top, yscrollcommand=scroll_bar.set)
            text_box.pack()

            # 向文本框中插入查询结果
            text_box.insert(tk.END, message)

            # 配置滚动条与文本框的关联
            scroll_bar.config(command=text_box.yview)

            # 设置窗口大小和位置
            top.geometry("400x300")
            top.mainloop()
        else:
            messagebox.showinfo("查询结果", "数据库中没有词条数据")
    except sqlite3.Error as e:
        messagebox.showerror("错误", f"操作数据库时出现错误：{e}")
    finally:
        # 关闭连接
        conn.close()
def crawl_website():
    # 创建新窗口
    crawl_win = tk.Toplevel(window)
    crawl_win.title("输入URL")
    
    label = tk.Label(crawl_win, text="请输入要爬取的URL：")
    label.pack()

    url_entry = tk.Entry(crawl_win)
    url_entry.pack()

    def confirm_crawl():
        url=get_url(url_entry.get())
        html = get_html(url, headers)  # 根据用户输入的url爬取网站内容
        save_data('result.html', html)  # 保存网站内容到文件

        messagebox.showinfo("爬取结果", "网站内容已爬取并保存到result.html文件")

    confirm_button = tk.Button(crawl_win, text="确认", command=confirm_crawl)
    confirm_button.pack()

def get_html(url, headers):
    req = request.Request(url=url, headers=headers)
    res = request.urlopen(req)
    html = res.read().decode('utf-8')
    return html

def save_data(filename, html):
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(html)
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dict_list = []
    for item in data['data']:  # 访问'data'键对应的值，即列表
        word = item['k']
        translation = item['v']
        dictionary = {'k': word, 'v': translation}
        dict_list.append(dictionary)

    return dict_list

def remove_duplicates():
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    try:
        # 查询数据库中的重复元素
        cursor.execute("SELECT english, COUNT(*) FROM words GROUP BY english HAVING COUNT(*) > 1")
        duplicated_rows = cursor.fetchall()

        # 删除重复元素
        for row in duplicated_rows:
            word = row[0]
            cursor.execute("DELETE FROM words WHERE english=?", (word,))

        # 提交更改
        conn.commit()
        
        print("删除重复元素成功！")

    except sqlite3.Error as e:
        print(f"操作数据库时出现错误：{e}")

    finally:
        # 关闭连接
        conn.close()
def export_to_excel1():
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 从数据库中读取数据
    df = pd.read_sql_query("SELECT * from words", conn)

    # 将数据导出为Excel文件
    df.to_excel("wordss.xlsx", index=False)

    # 关闭连接
    conn.close()

    # 打开Excel文件
    wb = openpyxl.load_workbook('wordss.xlsx')
    # 保存并关闭Excel文件
    wb.save('wordss.xlsx')
    wb.close()
#建立数据库
def insert_data(data):
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    # 查询数据库中已存在的所有英文单词
    cursor.execute("SELECT english FROM words")
    existing_words = [row[0] for row in cursor.fetchall()]

    # 遍历单词列表，逐个插入到数据库中
    for word in data:
        english = word.get("k")  # 获取英文单词
        chinese = word.get("v")  # 获取中文翻译
        
        # 使用正则表达式匹配中文字符，并将结果作为翻译插入到数据库中
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        chinese_match = chinese_pattern.search(chinese)
        
        if chinese_match:
            chinese_trans = chinese_match.group()
            # 删除翻译中的大写英文字母
            chinese_trans = re.sub('[A-Z]', '', chinese_trans)
            
            # 判断单词中是否含有大写字母
            if not re.search('[A-Z]', english) and english not in existing_words:
                count = 0  # 初始出现次数为 0
                
                # 将该单词插入到数据库中
                cursor.execute("INSERT INTO words (english, chinese, count) VALUES (?, ?, ?)",
                               (english, chinese_trans, count))

    # 提交更改
    conn.commit()
    show_recent_words_on_main()
    
    # 关闭连接
    conn.close()
def analyze_initial_counts():
    # 连接到数据库
    conn = sqlite3.connect('database.db')

    # 从数据库中读取数据
    df = pd.read_sql_query("SELECT * from words", conn)

    # 关闭连接
    conn.close()

    # 统计单词首字母的出现次数
    initial_counts = df['english'].str[0].str.upper().value_counts().sort_index()

    # 绘制折线图
    plt.plot(initial_counts.index, initial_counts.values, marker='o')
    plt.title('单词首字母出现次数统计')
    plt.xlabel('首字母')
    plt.ylabel('出现次数')
    plt.show()



# 创建主窗口    
window = tk.Tk()

# 设置窗口标题
window.title("单词管理系统")

# 设置窗口大小
window.geometry("500x400")

# 创建数据表
create_table()

# 创建菜单
create_menu()

# 显示最近添加的单词
show_recent_words_on_main()

# 创建标签和输入框
english_label = tk.Label(window, text="请输入要插入的英文单词：")
english_label.place(x=10, y=300)
english_entry = tk.Entry(window)
english_entry.place(x=150, y=300)
english_entry.bind('<Return>', on_enter)
chinese_label = tk.Label(window, text="请输入对应的中文翻译：")
chinese_label.place(x=10, y=330)
chinese_entry = tk.Entry(window)
chinese_entry.place(x=150, y=330)
chinese_entry.bind('<Return>', on_enter)

# 运行主窗口
window.mainloop()






