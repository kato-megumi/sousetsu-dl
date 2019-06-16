#!/usr/bin/python3
from bs4 import BeautifulSoup as bs
import requests
from ebooklib import epub
import sys

if len(sys.argv) < 2:
	print("How to use this program: " +sys.argv[0] +' <link>')
	exit(0)
link = sys.argv[1]

web = "https://ncode.syosetu.com/"
book = epub.EpubBook() 
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
s = requests.get(link,headers = headers).text
soup = bs(s,features="lxml") 


name = soup.find("", {"class": "novel_title"}).text
book.set_identifier(name)
book.set_title(name)
book.set_language('jp')
book.add_author(soup.find("", {"class": "novel_writername"}).text[4:-1])


style = 'body { font-family: Times, Times New Roman, serif; }'
nav_css = epub.EpubItem(uid="style_nav",
                        file_name="style/nav.css",
                        media_type="text/css",
                        content=style)
book.add_item(nav_css)

intro =  epub.EpubHtml(title="Introduction", file_name="Introduction"+'.xhtml',lang='jp')
intro.book=book
intro.set_content(str(soup.find("", {"id": "novel_ex"})).replace("</rb>","").replace("<rb>","").replace("<rp>(</rp>",""))
book.add_item(intro)
spine = ['nav',intro]
t=1
for x in soup.findAll("dd",class_="subtitle"):
	link = web+x.find('a')['href']
	chap_soup= bs(requests.get(link,headers=headers).text,features="lxml")
	title = chap_soup.find("", {"class": "novel_subtitle"}).text
	body = str(chap_soup.find("", {"id": "novel_honbun"}))
	body = body.replace("</rb>","").replace("<rb>","").replace("<rp>(</rp>","")
	c = epub.EpubHtml(title=title, file_name=title+'.xhtml',lang='jp')
	c.book=book
	c.set_content("<h2>"+title+"</h2>"+body)
	book.add_item(c)
	spine.append(c)
	print(t,title)
	t+=1

book.toc = (epub.Link('toc.xhtml', 'toc', 'toc'),
              (
                epub.Section('Content'),
                tuple(spine[1:])
              )
            )
book.spine=spine
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
epub.write_epub(name+'.epub', book)

