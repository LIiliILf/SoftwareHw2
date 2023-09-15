import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import os
from tkinter import Tk, Label, StringVar, ttk, Button, Entry, Text
import tkinter as tk

baseurl = "https://www.luogu.com.cn/problem/P"
savePath = "F:\problems\\"
blogurl = "https://www.luogu.com.cn/blog/_post/"
listurl = "https://www.luogu.com.cn/problem/list"
solutionurl = "https://www.luogu.com.cn/problem/solution/P"
minn = 1000    #开始题号
maxn = 1010    # 结束题号


# 模拟用户访问浏览器
def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.1.4031 SLBChan/103",
        "cookie": "__client_id=af4215a6f73e4641a2ae5ed49f35ef0b93b0709b; login_referer=https%3A%2F%2Fwww.luogu.com.cn%2Fauth%2Flogin; _uid=664601; C3VK=a66952"
    }
    response = requests.get(url=url, headers=headers)
    return response.text


# 获取洛谷题库信息
def get_baseHTML(url):
    basehtml = get_html(url)
    return basehtml


# 将题目信息转化为md格式
def get_base_md(html):
    bs = BeautifulSoup(html, "html.parser")
    core = bs.select("article")[0]
    md = str(core)
    md = re.sub("<h1>", "# ", md)
    md = re.sub("<h2>", "## ", md)
    md = re.sub("<h3>", "#### ", md)
    md = re.sub("</?[a-zA-Z]+[^<>]*>", "", md)
    return md


# 获取题解信息
def get_solutionHTML(url):
    solutionhtml = get_html(url)
    key = get_postfix(solutionhtml)
    new_url = solutionurl + key
    new_solutionhtml = get_html(new_url)
    return new_solutionhtml


def get_postfix(text):
    pattern = r"%22id%22%3A(\d+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None


# 将题解网页转化为md格式
def get_solutionMD(html):
    core = BeautifulSoup(html, "html.parser")
    md = str(core)
    md = re.sub("<h1>", "# ", md)
    md = re.sub("<h2>", "## ", md)
    md = re.sub("<h3>", "#### ", md)
    md = re.sub("</p>", "<br>", md)
    return md


# 生成文件夹
def born_file(name):
    if not os.path.exists(name):
        os.mkdir(name)


# 获取题目关键词
def slice(t_list, key_list):
    if t_list[0] == "[":
        key_list.append(t_list[1:5] + t_list[10:13])
        key_list.append(t_list[5:9])


# 获取标题列表
def get_titles(url, t_list):
    thtml = get_html(url)
    soup = BeautifulSoup(thtml, "html.parser")
    all_titles = soup.findAll("li")
    for title in all_titles:
        name = title.find("a")
        t_list.append(name.string)


def dif_level(dif):
    if dif == "1":
        d = "入门"
    elif dif == "2":
        d = "普及-"
    elif dif == "3":
        d = "普及&提高-"
    elif dif == "4":
        d = "普及+&提高"
    elif dif == "5":
        d = "提高+&省选-"
    elif dif == "6":
        d = "省选&NOI-"
    else:
        d = "NOI&NOI+&CTSC"
    return d


def get_dif(url):
    thtml = get_html(url)
    text = urllib.parse.unquote(thtml)
    pattern = r'"difficulty":(\d)'
    numbers = re.findall(pattern, text)
    return numbers


# 存储md文件
def saveData(data, filename):
    file = open(filename, "w", encoding="utf-8")
    for d in data:
        file.writelines(d)
    file.close()


def on_select(event):
    selected_item = event.widget.get()
    print(f"Selected item: {selected_item}")


def crawl():
    global minn, maxn
    minn = int(min_entry.get())
    maxn = int(max_entry.get())
    print("爬取到P{}".format(maxn))
    t_list = []
    get_titles(listurl, t_list)
    dif_list = get_dif(listurl)

    for i in range(minn, maxn + 1):
        print("正在爬取P{}...".format(i), end="")
        text_output.insert(tk.END, "正在爬取P" + str(i) + "\n")
        key_list = []
        slice(t_list[i - 1000], key_list)
        dif = dif_level(dif_list[i - 1000])
        phtml = get_baseHTML(baseurl + str(i))
        shtml = get_solutionHTML(solutionurl + str(i))
        if phtml == "error":
            print("爬取失败，可能是不存在该题或无权查看")
        else:
            problem = get_base_md(phtml)
            solution = get_solutionMD(shtml)

            # Extract the problem title
            title = t_list[i - 1000]

            # Create folder for this problem
            folder_name = "{}-{}".format(i, title)
            folder_path = os.path.join(savePath, folder_name)
            born_file(folder_path)

            # Save problem content
            problem_filename = "{}.md".format(folder_name)
            problem_path = os.path.join(folder_path, problem_filename)
            saveData(problem, problem_path)

            # Save solution content
            solution_filename = "{}-题解.md".format(folder_name)
            solution_path = os.path.join(folder_path, solution_filename)
            saveData(solution, solution_path)

            print("保存成功!")
            text_output.insert(tk.END, "保存成功!" + "\n")


# ...


# Create the main window
root = tk.Tk()
root.title("Luogu Crawler")

# Label and Entry for Min Problem Number
min_label = tk.Label(root, text="Min Problem Number:")
min_label.pack()
min_entry = tk.Entry(root)
min_entry.pack()

# Label and Entry for Max Problem Number
max_label = tk.Label(root, text="Max Problem Number:")
max_label.pack()
max_entry = tk.Entry(root)
max_entry.pack()

# Difficulty Selection
difficulty_label = tk.Label(root, text="Select Difficulty:")
difficulty_label.pack()

difficulty_var = tk.StringVar()
difficulty_combo = ttk.Combobox(root, textvariable=difficulty_var,
                                values=["入门", "普及-", "普及&提高-", "普及+&提高", "提高+&省选-", "省选&NOI-",
                                        "NOI&NOI+&CTSC"])
difficulty_combo.pack()

# Text Output Widget
text_output = Text(root, wrap=tk.WORD, width=50, height=20)
text_output.pack()

# Start Button
start_button = tk.Button(root, text="Start Crawling", command=crawl)
start_button.pack()

root.mainloop()
