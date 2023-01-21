import os,sys
import requests as req
from scrapy.selector import Selector
from fake_useragent import UserAgent
import pickledb
from html2text import html2text
import argparse
import pyfiglet
  
result = pyfiglet.figlet_format("Fmail")
ua = UserAgent()
db = pickledb.load('datas.db',True)
headers = {
    'authority': 'tempail.com',
    'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://tempail.com',
    'referer': 'https://tempail.com/en/fake-mail/',
    'user-agent': f'{ua.chrome}',
    'x-requested-with': 'XMLHttpRequest',
}


class Fmail:
    def __init__(self,db) -> None:
        self.db = db
        self.url = "https://tempail.com/en/fake-mail/"
        self.ses=req.session()
        if not self.db.get("sessioncookie"):   
           self.cookie = self.getSessionID()
           self.setdata(self.cookie)

    def setdata(self,cookie):
        self.db.set("sessioncookie",f'PHPSESSID={cookie["PHPSESSID"]}; oturum={cookie["oturum"]};')
        self.db.set("PHPSESSID",cookie["PHPSESSID"])
        self.db.set("oturum",cookie["oturum"])
        self.db.dump()

    def getSessionID(self):
        self.ses.get(self.url,headers=headers)
        data = self.ses.cookies.get_dict()
        if not "oturum" in data.keys():
            print("[help] catched by recaptcha please solve it for us!")
            if os.name=="nt":
                os.system(f"powershell -C Start-Process chrome.exe -ArgumentList @( '-incognito', '{self.url}')")
            elif os.name=="posix":
                os.system(f'open -na "Google Chrome" --args --incognito "{self.url}"') 
            print("[info] restart script after solving recaptcha")
        return data

    def getinfo(self):
        headers.update({"cookie":self.db.get("sessioncookie")})
        res = self.ses.get(self.url,headers=headers)
        selector= Selector(res)
        current_mail = selector.xpath("/html/body/section[1]/div[2]/div/div[2]/div/div/div[1]/input/@value").get()
        mails = selector.xpath('//*[@class="mailler"]/li').getall()
        print("[+] current mail : "+current_mail)
        print("[info]----[current_mails]----")
        for i in mails[1:]:
            if i:
                print(html2text(i)[:-1])
        print("[+]-----[ended]----")

    def createNewSession(self):
        cookie = self.getSessionID()
        self.setdata(cookie)
        headers.update({"cookie":self.db.get("sessioncookie")})
        res = self.ses.get(self.url,headers=headers)
        selector= Selector(res)
        current_mail = selector.xpath("/html/body/section[1]/div[2]/div/div[2]/div/div/div[1]/input/@value").get()
        self.db.set("current_mail",current_mail)
        self.db.dump()

if __name__ == "__main__":
   parser = argparse.ArgumentParser(prog = 'Fmail',
            description="it is a automatiton tool for temp mails.",
            epilog = 'if its catches by recaptcha its opens a chrome tab for you to solve it')
   parser.add_argument('--mail',action='store_true',help="prints your current mail")
   parser.add_argument('--inbox',action='store_true',help="get your mail inbox")
   parser.add_argument('--newmail',action='store_true',help="get you a newmail")
   parser.add_argument('--getcookie',action='store_true',help="prints current cookie")
   args = parser.parse_args()
   if len(sys.argv)<2:
      print(result)
      parser.print_help()
   if args.mail:
      print("[+] current mail : "+db.get("current_mail"))
   if args.getcookie:
      print("[+] current mail : "+db.get("sessioncookie"))
   fmail = Fmail(db)
   if args.inbox:
      fmail.getinfo()
   if args.newmail:
      fmail.createNewSession()
    
    

