from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from time import sleep
import json
from datetime import datetime
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv('CONNECTION_STRING')
database = os.getenv('DATABASE')
collection_name = os.getenv('COLLECTION')
# Search condition : MIEL https://inal.sifega.anmat.gob.ar/consultadealimentos/
def get_main_link():
    service = Service(executable_path=r"C:\chromedriver-win64\chromedriver.exe")   
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9030")
    driver = webdriver.Chrome(service=service, options=options)

    output = []
    for i in range(1, 2):
        print(f"\n----------- Page {i} -----------\n")
        tbody_list = driver.find_element(By.ID, 'table-result2').find_elements(By.TAG_NAME, 'tbody')
        
        for tbody in tbody_list:
            tr_list = tbody.find_elements(By.TAG_NAME, 'tr')
            for tr in tr_list:
                sub_link = tr.find_element(By.TAG_NAME, 'a').get_attribute('href')
                print(f'Sub Link : {sub_link}')

                rnpa = tr.find_element(By.TAG_NAME, 'a').text
                print(f'RNPA : {rnpa}')
                
                td_list = tr.find_elements(By.TAG_NAME, 'td')
                
                denominación = td_list[1].text
                print(f'Denomination : {denominación}')

                nombreDeFantasía = td_list[2].text
                print(f'Fantasty Name : {nombreDeFantasía}')

                marca = td_list[3].text
                print(f'Brand : {marca}')

                output.append({
                    "link" : sub_link,
                    "rnpa" : rnpa,
                    "denominación" : denominación,
                    "nombreDeFantasía" : nombreDeFantasía,
                    "marca" : marca
                    })
        
        next_button = driver.find_element(By.XPATH, '//*[@id="nextPageLi"]/a')
        driver.execute_script("arguments[0].click();", next_button)
        sleep(5)
    
    print(len(output))
    
    with open('output.json', 'a') as data:
        json.dump(output, data, indent=4)
    
    return output


def extract_sub_link(sub_links):
    final_result = []
    for item_index, item in enumerate(sub_links, start=1):
        print(f"\n-------------- Print {item_index} --------------\n")
        driver = webdriver.Chrome()
        driver.get(item['link'])
        sleep(1)

        while True:
            try:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'frame1')))
                if driver.find_element(By.TAG_NAME, 'body').text == "Acceso denegado" or driver.find_element(By.TAG_NAME, 'body').text == "":
                    rnpa = item['rnpa']
                    denominación = item['denominación']
                    marca = item['marca']
                    nombreDeFantasía = item['nombreDeFantasía']

                    final_result.append({
                        "rnpa": rnpa,
                        "rne": "",
                        "denominación": denominación,
                        "marca": marca,
                        "nombreDeFantasía": nombreDeFantasía,
                        "origenDelProducto": "",
                        "firm": {
                            "razonSocial": "",
                            "cuit": "",
                            "domicilio": ""
                        },
                        "establishment": {
                            "fraccionadoPor": "",
                            "rne": "",
                            "domicilio": ""
                        },
                        "rneInfo": {
                            "propietario": "",
                            "establecimiento": "",
                            "domicilio": "",
                            "localidad": "",
                            "otorgado": "",
                            "vencimiento": ""
                        },
                        "createdAt": "",
                        "updatedAt": "",
                        "__v": "",
                        "matchCount": "",
                        "vencimiento": "",
                        "date" : ""
                    })

                    with open('db_json.json', 'w') as data:
                        json.dump(final_result, data, indent=4)
                    
                    driver.quit()
                    break
                else:
                    form = driver.find_element(By.ID, 'form')
                    rnpa = item['rnpa']
                    if len(form.find_elements(By.TAG_NAME, 'table')[1].find_elements(By.TAG_NAME, 'tr')) > 1:
                        rne = form.find_elements(By.TAG_NAME, 'table')[1].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[0].text
                        print(f'RNE : {rne}')

                        razon_social = form.find_elements(By.TAG_NAME, 'table')[1].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[1].text
                        print(f"Razon Social : {razon_social}")

                        firm_domicilio = form.find_elements(By.TAG_NAME, 'table')[1].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[4].text + ", " + form.find_elements(By.TAG_NAME, 'table')[0].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[1].text
                        print(f'Firm Domicilio : {firm_domicilio}')

                    else:
                        rne = ""
                        razon_social = ""
                        firm_domicilio = form.find_elements(By.TAG_NAME, 'table')[0].find_elements(By.TAG_NAME, 'tr')[1].find_elements(By.TAG_NAME, 'td')[1].text

                    denominación = item['denominación']
                    marca = item['marca']
                    nombreDeFantasía = item['nombreDeFantasía']

                    origenDelProducto = ''

                    cuit = form.find_elements(By.TAG_NAME, 'table')[0].find_elements(By.TAG_NAME, 'tr')[0].find_elements(By.TAG_NAME, 'td')[1].text
                    print(f'CUIT : {cuit}')

                    establishment_fraccionadoPor = ''
                    establishment_rne = ''
                    establishment_domicilio = ''

                    h2_list = form.find_elements(By.TAG_NAME, 'h2')
                    for h2 in h2_list:
                        if 'Fecha de Vencimiento' in h2.text:
                            # vencimiento_date = datetime.strptime(h2.text.split(': ')[-1] + " 00:00:00.000", "%d/%m/%Y %H:%M:%S.%f").isoformat(timespec='milliseconds')
                            vencimiento_date = h2.text.split(': ')[-1]
                            print(f'veniciento date : {vencimiento_date}')
                    
                    rneInfo_propietario = ''
                    rneInfo_establecimiento = ''
                    rneInfo_domicilio = ''
                    rneInfo_localidad = ''
                    rneInfo_otorgado_date = ''
                    rneInfo_veniciento_date = ''

                    createdAt = ''
                    updatedAt = ''
                    __v = ''
                    matchCount = ''

                    final_result.append({
                        "rnpa": rnpa,
                        "rne": rne,
                        "denominación": denominación,
                        "marca": marca,
                        "nombreDeFantasía": nombreDeFantasía,
                        "origenDelProducto": origenDelProducto,
                        "firm": {
                            "razonSocial": razon_social,
                            "cuit": cuit,
                            "domicilio": firm_domicilio
                        },
                        "establishment": {
                            "fraccionadoPor": establishment_fraccionadoPor,
                            "rne": establishment_rne,
                            "domicilio": establishment_domicilio
                        },
                        "rneInfo": {
                            "propietario": rneInfo_propietario,
                            "establecimiento": rneInfo_establecimiento,
                            "domicilio": rneInfo_domicilio,
                            "localidad": rneInfo_localidad,
                            "otorgado": rneInfo_otorgado_date,
                            "vencimiento": rneInfo_veniciento_date
                        },
                        "createdAt": createdAt,
                        "updatedAt": updatedAt,
                        "__v": __v,
                        "matchCount": matchCount,
                        "vencimiento": '',
                        "date" : vencimiento_date
                    })

                    with open('db_json.json', 'w') as data:
                        json.dump(final_result, data, indent=4)
                    
                    driver.quit()
                    break
            except Exception as e:
                print(f"Browser error occured : {e}.\nRefreshing ......")
                driver.refresh()

    print('Generate JSON file for inserting to MongoDB.')
    
    return final_result


def process_json(json_data):
    for item in json_data:
        if "-" in item["date"]:
            item["date"] = item["date"].replace("-", "/")

    for item in json_data:
        if "-" in item["rnpa"]:
            item["rnpa"] = item["rnpa"].replace("-", "")

    return json_data


def delete_data_database():
    confirm = input("Do you want to delete all the data on your database?(Y/N) : ")
    if confirm == "Y":
        client = MongoClient(connection_string)
        db = client[database]
        collection = db[collection_name]

        delete_result = collection.delete_many({})
        print(f"Number of documents deleted: {delete_result.deleted_count}")
    else:
        pass


def read_data_database():
    client = MongoClient(connection_string)
    db = client[database]
    collection = db[collection_name]

    documents = collection.find()
    for doc in documents:
        print(doc)


def get_database_collection_database():
    client = MongoClient(connection_string)
    db = client[database]
    collection = db[collection_name]
    
    document_count = collection.count_documents({})

    print(f"Database : {client.list_database_names()}")
    print(f"Collection : {db.list_collection_names()}")
    print(f"Total number of documents in the collection : {document_count}")


def insert_data_mongodb(json_data):
    for item in json_data:
        if item["date"] == "":
            item['vencimiento'] = datetime.now()
        else:
            item['vencimiento'] = datetime.strptime(item['date'], '%d/%m/%Y')
        item['rneInfo']['vencimiento'] = item['vencimiento']
        item['rneInfo']['otorgado'] = item['vencimiento']
        item['createdAt'] = datetime.now()
        item['updatedAt'] = datetime.now()
        item['matchCount'] = 0
        del item['date']

    client = MongoClient(connection_string)
    db = client[database]
    collection = db[collection_name]

    insert_data = collection.insert_many(json_data)
    # print(f"Inserted document ID : {insert_data.inserted_ids}")
    print(f"Total number of inserted document : {len(insert_data.inserted_ids)}")
    print(f"Total number of documents in the collection : {collection.count_documents({})}")


if __name__ == "__main__":
    output = get_main_link()
    json_data = extract_sub_link(output)

    # read_data_database()
    # get_database_collection_database()

    process_json_data = process_json(json_data)
    delete_data_database()
    insert_data_mongodb(process_json_data)