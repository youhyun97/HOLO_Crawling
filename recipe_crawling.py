import urllib.request
from bs4 import BeautifulSoup as bs
import re
import json, csv

def toJson(recipe_dict):
    with open('recipe_for_one.json', 'w', encoding='utf-8') as file :
        json.dump(recipe_dict, file, ensure_ascii=False, indent='\t')


def toCSV(recipe_list):
    with open('ingredients_for_one.csv', 'w', encoding='utf-8', newline='') as file :
        csvfile = csv.writer(file)
        for row in recipe_list:
            csvfile.writerow(row)

# 'by 만개의 레시피'로 작성된 레시피 주소 크롤링(page 1~165)
# /recipe/xxxxxxx
def url_func(m):
    url_list = []
    num = 1

    while num <= m:
        url = "https://www.10000recipe.com/profile/recipe.html?uid=gdubu33&page="
        req = urllib.request.Request(url + str(num)) # page 수 붙이기
        code = urllib.request.urlopen(url + str(num)).read()
        soup = bs(code, "html.parser")

        try:
            res = soup.find(class_='cont_list st3')
            for i in res.find_all('a'):
                url_tmp = i.get('href')
                url_list.append(url_tmp)
        except(AttributeError):
            pass
        num = num + 1

    return url_list

############################################################
num_id=0
food_dicts = []
ingre_set = set() # 재료 목록들을 담기 위한 set
url_lists = url_func(165)
for url_str in url_lists:
    url = "https://www.10000recipe.com"
    if (url_str == '/recipe/6892286') or (url_str == '/recipe/6874949') or (url_str == '/recipe/6864347') or (url_str == '/recipe/6863293') or (url_str == '/recipe/6842650'):
        continue
    url = url + url_str
    print(url)
    req = urllib.request.Request(url)
    code = urllib.request.urlopen(url).read()
    soup = bs(code, "html.parser")

    # 변수목록
    # menu_name : 메뉴 이름
    # menu_img : 메뉴 이미지
    # menu_summary : 메뉴 설명
    # menu_info_1 : n인분
    # menu_info_2 : 요리 시간
    # menu_info_3 : 난이도
    # ingredient_name : 재료 이름
    # ingredient_count : 계랑 숫자
    # ingredient_unit : 계량 단위
    # ingredient_main : 조미료 판단
    # recipe_step_txt : 레시피 순서 txt
    # recipe_step_img : 레시피 순서 img

    info_dict = {}
    ingre_list = []
    ingre_dict = {}
    recipe_list = []
    recipe_dict = {}
    food_dict = {}

    # menu_name
    res = soup.find('div', 'view2_summary')
    res = res.find('h3')
    menu_name = res.get_text()

    # menu_img
    res = soup.find('div', 'centeredcrop')
    res = res.find('img')
    menu_img = res.get('src')

    # menu_summary
    res = soup.find('div', 'view2_summary_in')
    if res:
        menu_summary = res.get_text().replace('\n','').strip()
    else:
        menu_summary = ''
    # menu_info
    res = soup.find('span', 'view2_summary_info1') # menu_info_1
    if res:
        menu_info_1 = res.get_text()
    else:
        menu_info_1 = ''
    
    # 1인분만
    if '1' not in menu_info_1:
        continue

    res = soup.find('span', 'view2_summary_info2') # menu_info_2
    if res:
        menu_info_2 = res.get_text()
    else:
        menu_info_2 = ''
    res = soup.find('span', 'view2_summary_info3') # menu_info_3
    if res:
        menu_info_3 = res.get_text()
    else:
        menu_info_3 = ''

    # info dict
    info_dict = {"info1":menu_info_1,
                "info2":menu_info_2,
                "info3":menu_info_3}

    # ingredient
    res = soup.find('div','ready_ingre3')
    try :
        for n in res.find_all('ul'):
            for tmp in n.find_all('li'):
                ingredient_name_1 = tmp.get_text().replace('\n','').replace(' ','')                
                #tmp1 = ingredient_name
                count = tmp.find('span')
                ingredient_tmp = count.get_text().replace(' ','')
                # ingredient_tmp 글자 수 세기
                length = len(ingredient_tmp)
                # ingredient_name 에서 위에서 센 글자 수 만큼 substring
                ingredient_name = ingredient_name_1[:-length]
                ingredient_unit = ingredient_tmp.replace('/','').replace('+','').replace('.','')
                # tmp2 = ingredient_unit
                # tmp1 = tmp1.replace('/','').replace('+','').replace('.','') 
                # ingredient_name = re.sub(tmp2,'',tmp1) # ingredient_name
                ingredient_unit = ''.join([i for i in ingredient_unit if not i.isdigit()]) # ingredient_unit
                ingredient_count = re.sub(ingredient_unit, '', ingredient_tmp) # ingredient_count
                str1 = re.findall('[0-9]\+[0-9]*\/+[0-9]*$',ingredient_count) # \$는 문자 '$'를 의미
                str2 = re.findall('[0-9]*\/+[0-9]*$',ingredient_count)
                if str1 or str2:
                    ingredient_count = str(eval(ingredient_count))
                # ingre_list
                ingre_dict = {"ingre_name":ingredient_name,
                                "ingre_count":ingredient_count,
                                "ingre_unit":ingredient_unit,}
                ingre_list.append(ingre_dict)

                # set에 업데이트
                ingre_set.add(ingredient_name)
    except(AttributeError):
        pass

    # recipe
    res = soup.find('div','view_step')
    for n in res.find_all('div','view_step_cont'):
        recipe_step_txt = n.get_text().replace('\n',' ')
        tmp = n.find('img')
        if tmp:
            recipe_step_img = tmp.get('src')
        else:
            recipe_step_img = ''

        # recipe_list
        recipe_dict = {"txt":recipe_step_txt,
                        "img":recipe_step_img,}
        recipe_list.append(recipe_dict)

    # 재료 형식에 맞지 않게 올라온 글들 skip
    if not ingre_list:
        continue

    num_id = num_id + 1
    print(num_id)
    food_dict = {"id":num_id,
                "name":menu_name,
                "img":menu_img,
                "summary":menu_summary,
                "info":info_dict,
                "ingre":ingre_list,
                "recipe":recipe_list}

    food_dicts.append(food_dict)

# json 생성
toJson(food_dicts)

# ingredients list csv 생성
ingre_list_csv=[]
for i in ingre_set:
    tmp_l = []
    tmp_l.append(i)
    ingre_list_csv.append(tmp_l)
toCSV(ingre_list_csv)
