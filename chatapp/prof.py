from bs4 import BeautifulSoup
import requests
import pprint
from base64 import b64decode
from tqdm import tqdm
import multiprocessing

class professor:
    def __init__(self):    
        if type(self) is professor:
            raise NotImplementedError("Subclasses must implement this method")
        self.cname = ""
        self.ename = ""        
        self.dept = ""
        self.lab = ""
        self.laburl = ""
        self.research = []
        self.url = ""
        self.imageurl = ""
        self.email = ""
        return
    def print(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.__dict__)

        
    
class NTU_prof(professor):
    def __init__(self, url):
        super().__init__()
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        name_element = soup.find('td', class_='member-data-value-name')
        name = name_element.get_text(strip=True)
        try:
            self.cname = name.split('(')[0][:-1]
            self.ename = name.split('(')[1][:-1]
        except:
            self.cname = name.split('（')[0]
            self.ename = name.split('（')[1][:-1]

        self.dept = "資工系"

        try:
            lab_element = soup.find('td', class_='member-data-value-8').find('a')
            self.lab = lab_element.get_text(strip=True)
            self.laburl = lab_element.get('href')
        except:
            pass       
        
        res_element = soup.find('td', class_='member-data-value-7')
        self.research = res_element.get_text(strip=True).split("、")

        imageurl = soup.find('div', class_='member-pic col-xs-3').find('img').get('src')
        self.imageurl = "https://csie.ntu.edu.tw" + imageurl
        

        email_raw = soup.find('td', class_='member-data-value-email').find('script').get_text(strip=True)
        email_b64 = email_raw.split("atob(\"")[1].split("\"")[0]
        self.email = b64decode(email_b64).decode("UTF-8")

        # super().print()
        # with open("test.txt", "w", encoding="utf-8") as file:
        #     file.write(lab)
            
def worker_func(profs, link):
    try:
        name = link.find('a').get('title').split('(')[1][:-1]
    except:
        name = link.find('a').get('title').split('（')[1][:-1]
    url = "https://csie.ntu.edu.tw" + link.find('a').get('href')
    profs[name] = NTU_prof(url)

def main():
    
    url = "https://csie.ntu.edu.tw/zh_tw/member/Faculty"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all('span', class_="i-member-value member-data-value-name")
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()
    with multiprocessing.Pool(8) as pool:
        pool.map(worker_func, [(shared_dict, link) for link in links])
    for i in shared_dict:
        print(i, shared_dict[i])


if __name__ == '__main__':
    main()