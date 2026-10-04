import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

o = Options()
o.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
d = webdriver.Chrome(options=o)
d.get("https://www.wiki-masters.com/pulls")
json.dump(d.get_cookies(), open("cookies.json", "w"))
print(len(d.get_cookies()), "cookies exportés")

#