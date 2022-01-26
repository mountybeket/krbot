import config
import telebot
from telebot import types
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import date
from selenium.webdriver.common.action_chains import ActionChains
import urllib.request
from telebot.types import InputMediaPhoto, InputMediaVideo
import os

bot = telebot.TeleBot(config.token) #должно быть в начале. Вызывает токен

cred = credentials.Certificate("C:/Users/Nurdaulet/Desktop/codes/nurlan_bot/1komn/key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://nurlan-komn-default-rtdb.firebaseio.com/' })


today = date.today()
d2 = today.strftime("%B %d, %Y")
today_day = d2[8] + d2[9] #ТУТ ДОБАВИТЬ d2[9] +

options = webdriver.ChromeOptions()

options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

def begin():
    page = 1

    while True:
        url = "https://krisha.kz/arenda/kvartiry/nur-sultan/?das[_sys.hasphoto]=1&das[live.rooms]=1&das[rent.period]=2&das[who]=1&page=" + str(page)
        driver = webdriver.Chrome(
            executable_path='C:/Users/Nurdaulet/Desktop/codes/nurlan_bot/1komn/chromedriver.exe',
            options = options

        )
        driver.get(url=url)
        html = BS(driver.page_source, 'html.parser')
        items = html.select(".a-list > .a-card")
        #tag = html.div




        if(len(items)):

            for el in items:
                title = el.select('.card-stats > div')
                p = title[1].text
                space = p.replace(" ","")
                day = space[1] + space[2]#ТУТ ДОБАВИТЬ + space[2]
                if day == today_day:
                        data_id = el.get('data-id')
                        check = db.reference("id/"+str(data_id)+"/id").get()
                        if check == data_id:
                            print("Этот есть")
                        else:

                            db.reference("id/"+str(data_id)).update({"id": data_id})
                            db.reference("id/"+str(data_id)).update({"day": day})
                            print(data_id)
                            driver.get(url="https://krisha.kz/a/show/" + str(data_id))
                            page = BS(driver.page_source, 'html.parser')
                            time.sleep(2)

                            phone_button = driver.find_element(By.CLASS_NAME, "show-phones").click()
                            time.sleep(2)

                            phone = driver.find_element(By.XPATH, "/html/body/main/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/div[3]/div/div/div[1]/p")

                            ph_num = phone.text
                            print(phone.text)
                            db.reference("id/"+str(data_id)).update({"phone": phone.text})

                            driver.refresh()





                            name = page.select('.offer__advert-title > h1')
                            name = name[0].text
                            print(name)
                            db.reference("id/"+str(data_id)).update({"name": name})


                            txt_2 = page.select('.a-text')
                            text_2 = txt_2[0].text
                            print(text_2)
                            db.reference("id/"+str(data_id)).update({"text_2": text_2})


                            price = page.select('.offer__sidebar-header > div')
                            ps = price[0].text
                            price_space = ps.replace(" ","")
                            print(price_space)
                            db.reference("id/"+str(data_id)).update({"price": price_space})

                            files = []

                            imgs_small = driver.find_elements(By.CLASS_NAME, "gallery__small-item")
                            num_img = 1
                            for img_small in imgs_small:
                                hover = ActionChains(driver).move_to_element(img_small)
                                hover.perform()
                                time.sleep(1)

                                download_img = driver.find_element(By.XPATH, "/html/body/main/div[2]/div/div[2]/div[2]/div[2]/div/a/picture/img").get_attribute('src')
                                picture = str(data_id) + "_" + str(num_img) + ".jpg"
                                urllib.request.urlretrieve(download_img, picture)
                                files.append(picture)
                                #тут надо закидывать фото в массив files[]
                                time.sleep(2)
                                num_img += 1

                            media= []
                            for file in files:
                                 media.append(InputMediaPhoto (open(file, "rb"), caption = name + price_space + '\n' + ph_num + '\n\n' + text_2  if file == str(data_id) + "_1.jpg" else ''))
                            print(repr(media))

                            #bot.send_message("-1001763006059", name + price_space + '\n' + phone.text + '\n\n' + text_2)
                            bot.send_media_group("-1001757168435", media = media)
                            time.sleep(5)
                            #for file in files:
                                #os.close(file)
                                #os.remove(file)
                            #удалять фотографии с папки





            page += 1
        else:
            begin()


begin()










bot.polling(none_stop=True, interval = 2) #в конце. Бесконечно.
while 1:
    try:
        bot.polling(none_stop=True)
        print(cycle)
        time.sleep(3)
    except Exception as e:
        print(e)
        pass
