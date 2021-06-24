from tkinter import *
import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
list_urls = []

def wind():
    global town
    global categ
    window = Tk()
    window.title("Парсер GoogleMaps Енот")

    window.geometry('400x250')  # размеры окна

    lbl = Label(window, text="Укажите город")
    lbl2 = Label(window, text="Укажите категорию")
    lbl.grid(column=0, row=0)
    lbl2.grid(column=0, row=1)

    town = Entry(window, width=10)
    town.grid(column=1, row=0)

    categ = Entry(window, width=10)
    categ.grid(column=1, row=1)



    btn = Button(window, text="Go!", command=cliked)
    btn.grid(column=3, row=1)

    btn_go = Button(window, text="Отмена!", command=exit_go)
    btn_go.grid(column=4, row=1)

    window.mainloop()

def cliked():
    run_browser(town.get(), categ.get())
def exit_go():
    browser.quit()
    exit()

def run_browser(town, categories):
    """
    Функция для сбора всех ссылок по запросу категории и города
    :param town: город для поиска берёт из файла
    :param categories: категория поиска берёт из файла
    :return: список ссылок
    """
    global browser
    opts = Options()
    opts.headless = True
    assert opts.headless
    browser = webdriver.Firefox(options=opts)
    # browser = webdriver.Firefox()

    base_url = 'https://www.google.com/maps/search/' + town + '+' + categories + '/@55.802957,49.0908432,13z/data=!3m1!4b1?hl=ru-RU'
    browser.get(base_url)
    time.sleep(7)

    while True:
        # скроллим вниз в окне организаций до конца
        try:
            html = browser.find_element_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')
            for i in range(5):
                html.send_keys(Keys.END)
                time.sleep(3)
        except Exception as e:
            print('1', e)
        try:
            elems = browser.find_elements_by_xpath("//a[@href]")
            for elem in elems:
                list_urls.append(elem.get_attribute("href"))
                print(f'Найдено организаций {len(list_urls)} ')
        except Exception as e:
            print('2', e)
        time.sleep(3)
        try:
            button_next = browser.find_element_by_xpath('//*[@id="ppdPk-Ej1Yeb-LgbsSe-tJiF1e"]')
            button_next.click()
            time.sleep(3)
        except Exception as e:
            print('3', e)
            browser.close()
            browser.quit()
            get_html_site(list_urls, town)
        # browser.close()
        # browser.quit()
        # get_html_site(list_urls, town)


def save_in_csv(town, out_data):
    """
    Функция для записи списка в файл CSV
    :param out_data: принимает список имя организации, телефон, сайт
    :return:
    """
    with open(f"{town}.csv", mode="a", encoding='utf-8') as csv_file:
        file_writer = csv.writer(csv_file, delimiter=";")
        file_writer.writerow(out_data)

def get_html_site(list_urls, town):
    for row_url in list_urls:
        if 'http' in row_url:
            try:
                opts = Options()
                opts.headless = True
                assert opts.headless
                driver = webdriver.Firefox(options=opts)
                # driver = webdriver.Firefox()
                driver.get(row_url)
                time.sleep(9)
            except Exception as e:
                print(e)
                continue
            try:
                main_info = driver.find_element_by_xpath(
                    '/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[9]').text  # ищем элементы на страницы

                main_info_dubler = driver.find_element_by_xpath(
                    '/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[7]').text
                name_org = driver.find_element_by_xpath(
                    '/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]/h1/span[1]').text

                row_phone = re.findall(r"(\+7|8).*?(\d{3}).*?(\d{3}).*?(\d{2}).*?(\d{2})", main_info)
                row_phone2 = re.findall(r"(\+7|8).*?(\d{3}).*?(\d{3}).*?(\d{2}).*?(\d{2})", main_info_dubler)
                row_phone = re.findall(r'[0-9]\s\(\d{0,4}\)\s\d{0,4}\-\d{0,3}\-\d{0,3}', main_info)
                any_row_phone = re.findall(r'\+\d+.+', main_info)
                if row_phone:
                    phone = ''.join(list(row_phone[0]))  # блок для поиска телефона
                elif row_phone:
                    phone = ''.join(list(row_phone2[0]))
                else:
                    phone = ''.join(any_row_phone)
                    if not phone:
                        phone = 'Не указан тел.'

                row_site = re.findall(r'.+\.[a-zA-Z]{2,4}', main_info)
                row_site2 = re.findall(r'.+\.[a-zA-Z]{2,4}', main_info_dubler)
                if row_site:
                    site = ''.join(row_site)  # блок для поиска сайта
                elif not row_site:
                    site = ''.join(row_site2)
                else:
                    site = 'Не указан сайт'

                print('------------------------------------------------')  # дебаг инфо
                print(f'Название " {name_org} "' + '\n')
                print(main_info)
                print(main_info_dubler)
                print('tel', phone)
                print('site  ', site)
                print('------------------------------------------------')
                print('')

                out_list = [name_org, phone, site]
                save_in_csv(town, out_list)  # формируем список и передаем в ф-цию записи CSV

                driver.quit()

            except Exception as e:
                print('007', e)
                driver.close()
                driver.quit()
                continue
        else:
            continue


def main():
    wind()


if __name__ == '__main__':
    main()
