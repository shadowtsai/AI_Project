from urllib.request import urlopen
from bs4 import  BeautifulSoup
import ssl
import re
import json

from urllib.parse import quote
ssl._create_default_https_context = ssl._create_unverified_context


url = "https://www.pixnet.net/blog/articles/category/28/latest" #國內旅遊 "近期熱門"
html = urlopen(url)
bsObj = BeautifulSoup(html, "html.parser")

# =================== 搜刮所有頁面的連結 =======================
navi_list = bsObj.find("div",{"class":"page"}).find_all("a")
url_list = []
print("=========搜刮中，請稍後 =========")

for page_link in navi_list:
    pattern = re.compile(r"^\/blog")
    match = pattern.match(page_link["href"])
    if(match):
        if page_link["href"] not in url_list:
            url_list.append(page_link["href"])


# =================== 處理每一頁部落格網址=======================
article_url_list = []
print("========= 處理網址中，請稍後 =========")

for i, url in enumerate(url_list):
    html = urlopen("https://www.pixnet.net"+url)
    bsObj = BeautifulSoup(html, "html.parser")
    if(i == 0):
        # 取得第一名文章
        blog_url = bsObj.find("div", {"class": "featured"}).a
        article_url_list.append(blog_url["href"])
        # 取得第一頁其他文章
        blog_url = bsObj.find("ol", {"class": "article-list"},"li").findAll("h3")
        for h3str in blog_url:
            article_url_list.append(h3str.a["href"])
    else:
        # 取得其他文章
        blog_url = bsObj.find("ol", {"class": "article-list"},"li").findAll("h3")
        for h3str in blog_url:
            article_url_list.append(h3str.a["href"])

# =================== 處理文章內容輸出成JSON  ===================
result = []
for i, article_url in enumerate(article_url_list):
    print("========= 抓取第{}篇內容中，請稍後 =========".format(i+1))
    article_html = urlopen(article_url)
    article_bsObj = BeautifulSoup(article_html, "html.parser")

    # ================ Title ================
    article_title = article_bsObj.find("title").get_text()
    article_title = article_title.replace(" :: 痞客邦 ::","")

    # ================ Site Category & Custom Category ================
    article_footer_list = article_bsObj.find("div",{"class":"article-footer"}).findAll("li")
    for article_footer in article_footer_list:
        pattern1 = re.compile(r"^全站分類：")
        match1 = pattern1.match(article_footer.get_text())
        pattern2 = re.compile(r"^個人分類：")
        match2 = pattern2.match(article_footer.get_text())
        if (match1):
            site_cate = article_footer.get_text().replace("全站分類：","")
        elif (match2):
            cust_cate = article_footer.get_text().replace("個人分類：", "")

    # ================== Body =================
    article_body = article_bsObj.find("div",{"class":"article-content-inner"})

    result.append({"url":article_url ,
                   "site_category":site_cate,
                   "custom_category":cust_cate,
                   "title":article_title,
                   "body":str(article_body)})

with open('result.json', 'w') as f:
        json.dump(result, f)