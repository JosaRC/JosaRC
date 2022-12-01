import os
import re
import sys
from os import listdir
from pathlib import Path
import selenium
from selenium import webdriver
from time import sleep
from random import uniform
from selenium import NoSuchElementException
from selenium import By
from selenium import Keys
import pandas as pd
import pywhatkit

#from selenium.webdriver.chrome.options import Options


def welcome():
    texto = "Este es el sistema de captura versión alpha 1.0, Bienvenido"
    print("\n" + texto + "\n" + len(texto) * "-" + "\n")


def extract_number(df, driver):
    states_check = 0
    old_state = 0
    fill = None
    id =int(input("¿En cual numero quieres comenzar? "))
    df["numero credito"] = df["numero credito"].apply(lambda x: '{0:0>10}'.format(x))
    numbers = df["numero credito"]
    while id <= len(numbers):
        credito = str(df.loc[id, "numero credito"])
        print(credito)
        print(df.loc[id, ["ESTADO"]])

        if int(df.loc[id, ["ESTADO"]]) != old_state:
            [estado, driver, id] = log_in(driver, df, id, old_state)
            old_state = int(estado)
            states_check += 1

        if int(df.loc[id, ["ESTADO"]]) == old_state:
            fill = check_credict(credito, driver, df, id)
            id += 1
        if id % 300 == 0:
            save_document(fill)

    return [fill, driver]


def time_random(n1, n2):
    random_wait_time = uniform(n1, n2)
    sleep(random_wait_time)


# Toda esta parte está pendiente por las contraseñas
def check_credict(credito, driver, df, id):
    check = False
    while not check:
        try:
            time_random(0.4, 0.6)
            cell = driver.find_element(By.XPATH, '//*[@id="numeroCredito"]')
            for number in credito:
                cell.send_keys(number)
                time_random(0.1, 0.2)

            time_random(0.1, 0.2)
            driver.find_element(By.XPATH, '//*[@id="info"]/div/div/form/fieldset[1]/div/div/span[2]/input').click()
            time_random(0.1, 0.2)

            fill = asignation_credict(driver, df, id)

            driver.implicitly_wait(5)

            cell = driver.find_element(By.XPATH, '//*[@id="numeroCredito"]')
            while len(cell.get_attribute("value")) != 0:
                try:
                    time_random(0.3, 0.4)
                    cell.send_keys(Keys.CONTROL, 'a')
                    time_random(0.3, 0.4)
                    cell.send_keys(Keys.DELETE)
                except selenium.common.exceptions.StaleElementReferenceException:
                    time_random(1.0, 1.2)
                    print("No se pudo encontrar el valor de la celda")
            print("Credito revisado")
            check = True
            return fill
        except TimeoutError:
            time_random(100, 200)
            driver.refresh()


def asignation_credict(driver, df, id):
    direction = None
    complete = False
    while not complete:

        try:

            driver.implicitly_wait(5)
            valor_status = driver.find_element(By.CLASS_NAME, "system_title").text
            print("No hay monto y es estatus es {}".format(valor_status))

            if valor_status == "Servicio no Disponible, intente más tarde":
                df.loc[id, ["id estatus"]] = 8
                time_random(300, 350)

            if valor_status == "NO EXISTE EL CREDITO EN SALDOS":
                df.loc[id, ["id estatus"]] = 20

            elif valor_status == "FALTA ACTUALIZARSE":
                df.loc[id, ["id estatus"]] = 8

            elif valor_status == "CAMBIO NUMERO CREDITO":
                df.loc[id, ["id estatus"]] = 3

            elif valor_status == "CARTERA VENCIDA":
                df.loc[id, ["id estatus"]] = 5

            elif valor_status == "NO GENERA VALE DE ECOTECNOLOGIAS":
                df.loc[id, ["id estatus"]] = 10

            elif valor_status == "RETENIDO":
                df.loc[id, ["id estatus"]] = 12

            elif valor_status == "Solicitud de Credito de Paquete":
                df.loc[id, ["id estatus"]] = 10

            elif valor_status == "Se ha terminado el saldo para ecotecnologias":
                df.loc[id, ["id estatus"]] = 14

            elif valor_status == "Cobertura no autorizada para el canje de esta constancia.":
                df.loc[id, ["id estatus"]] = 6

            elif valor_status == "Vale de Ecotecnologias en solicitud de pago":
                df.loc[id, ["id estatus"]] = 14

            elif valor_status == "CREDITO VENCIDO O CON OMISOS":
                df.loc[id, ["id estatus"]] = 5

            elif valor_status == "CREDITO NO ACTIVO":
                df.loc[id, ["id estatus"]] = 12

            elif valor_status == "Para Linea III y IV no se genera Vale de Ecotecnologias":
                df.loc[id, ["id estatus"]] = 10

            elif valor_status == "Solo Individuales o Titulares":
                df.loc[id, ["id estatus"]] = 10

            complete = True
            return df

        except selenium.common.exceptions.NoSuchElementException:
            valor_status = "Disponible"
            if valor_status == "Disponible":
                df.loc[id, ["id estatus"]] = 6
                try:
                    direction = driver.find_element(By.XPATH, '//*[@id="info"]/div/div/form/fieldset[2]/div/div[5]/span')

                except selenium.common.exceptions.NoSuchElementException:
                    direction = driver.find_element(By.XPATH, '//*[@id="info"]/div/div/form/fieldset[2]/div/div[4]/span')

            monto = direction.text
            monto_final = re.findall("[$] (\d{0,6}[,]?\d+?[.]?\d+)", monto)
            df.loc[id, ["monto ecotec"]] = monto_final

            print("Hay monto y es {} y el estatus es {}".format(monto_final, valor_status))
            complete = True
            return df
        except TimeoutError:
            driver.set_page_load_timeout(10)




def find_user_path():
    return "{}/".format(Path.home())


def search_documentation(path_document):
    list_documentation = listdir(path_document)
    return list_documentation


def send_message(necs, disponibles, estado):
    text = "el reporte de captura de {} es: {}  NO EXISTE EL CREDITO EN SALDOS y {} DISPONIBLES".format(estado, necs,
                                                                                                        disponibles)
    try:
        pywhatkit.sendwhatmsg_instantly("+524499992228", text, tab_close=True)

        print("Mensaje enviado")

        pywhatkit.sendwhatmsg_instantly("+524494610426", text, tab_close=True)

        print("Mensaje enviado")

    except:
        print("NO SIRVIO")


def count_number(fill):
    aguascalientes = fill[(fill["ESTADO"] == 1)]
    NECS_aguascalientes = len(aguascalientes[(aguascalientes["id estatus"] == 20) | (aguascalientes["id estatus"] == 8)])
    Diposnibles_aguascalientes = len(aguascalientes[aguascalientes["id estatus"] == 6])
    send_message(NECS_aguascalientes, Diposnibles_aguascalientes, "Aguascalientes")

    mexico = fill[(fill["ESTADO"] == 15)]
    NECS_mexico = len(mexico[(mexico["id estatus"] == 20) | (mexico["id estatus"] == 8)])
    Diposnibles_mexico = len(mexico[mexico["id estatus"] == 6])
    send_message(NECS_mexico, Diposnibles_mexico, "México")

    guanajuato = fill[(fill["ESTADO"] == 11)]
    NECS_guanajuato = len(guanajuato[(guanajuato["id estatus"] == 20) | (guanajuato["id estatus"] == 8)])
    Diposnibles_guanajuato = len(guanajuato[guanajuato["id estatus"] == 6])
    send_message(NECS_guanajuato, Diposnibles_guanajuato, "Guanajuato")

    jalisco = fill[(fill["ESTADO"] == 14)]
    NECS_jalisco = len(jalisco[(jalisco["id estatus"] == 20) | (jalisco["id estatus"] == 8)])
    Diposnibles_jalisco = len(jalisco[jalisco["id estatus"] == 6])
    send_message(NECS_jalisco, Diposnibles_jalisco, "Jalisco")

    puebla = fill[(fill["ESTADO"] == 21)]
    NECS_puebla = len(puebla[(puebla["id estatus"] == 20) | (puebla["id estatus"] == 8)])
    Diposnibles_puebla = len(puebla[puebla["id estatus"] == 6])
    send_message(NECS_puebla, Diposnibles_puebla, "Puebla")

    queretaro = fill[(fill["ESTADO"] == 22)]
    NECS_queretaro = len(queretaro[(queretaro["id estatus"] == 20) | (queretaro["id estatus"] == 8)])
    Diposnibles_queretaro = len(queretaro[queretaro["id estatus"] == 6])
    send_message(NECS_queretaro, Diposnibles_queretaro, "Queretaro")

    quintana_roo = fill[(fill["ESTADO"] == 23)]
    NECS_quintana_roo = len(quintana_roo[(quintana_roo["id estatus"] == 20) | (quintana_roo["id estatus"] == 8)])
    Diposnibles_quintana_roo = len(quintana_roo[quintana_roo["id estatus"] == 6])
    send_message(NECS_quintana_roo, Diposnibles_quintana_roo, "Quintana Roo")

    san_luis = fill[(fill["ESTADO"] == 24)]
    NECS_san_luis = len(san_luis[(san_luis["id estatus"] == 20) | (san_luis["id estatus"] == 8)])
    Diposnibles_san_luis = len(san_luis[san_luis["id estatus"] == 6])
    send_message(NECS_san_luis, Diposnibles_san_luis, "San Luis")

    zacatecas = fill[(fill["ESTADO"] == 32)]
    NECS_zacatecas = len(zacatecas[(zacatecas["id estatus"] == 20) | (zacatecas["id estatus"] == 8)])
    Diposnibles_zacatecas = len(zacatecas[zacatecas["id estatus"] == 6])
    send_message(NECS_zacatecas, Diposnibles_zacatecas, "Zacatecas")


def complete_number(fill):
    fill["nss"] = fill["nss"].apply(lambda x: '{0:0>11}'.format(x))
    fill["numero credito"] = fill["numero credito"].apply(lambda x: '{0:0>10}'.format(x))


def usuarios(actual_state):
    user_path = find_user_path()
    path_document = (user_path + "\\Captura\\Users\\")
    list_documentation = search_documentation(path_document)
    USERS = pd.read_excel(path_document + list_documentation[0], index_col="Estado")

    user = USERS.loc[actual_state, ["User"]]
    password = USERS.loc[actual_state, ["Password"]]

    return [user, password]


def looking_new_state(df, id):
    current_position = id
    current_state = int(df.loc[current_position, ["ESTADO"]])
    numbers_advance = 0
    while current_state == int(df.loc[id, ["ESTADO"]]):
        numbers_advance += 1
    current_state = int(df.loc[id+numbers_advance, ["ESTADO"]])
    print("Andamos aquí")
    return [current_state, numbers_advance]


def asignation_user(driver, df, id, old_state):
    user = None
    password = None
    current_state = int(df.loc[id, ["ESTADO"]])

    if current_state == old_state:
        [user, password] = usuarios(current_state)

    elif current_state != old_state:
        if id != 0:
            driver.implicitly_wait(5)
            driver.close()
            driver = open_browse()
            driver.implicitly_wait(10)

        driver.implicitly_wait(5)
        [user, password] = usuarios(current_state)
    return [driver, user, password, current_state, id]


def log_in(driver, df, id, old_state):
    [driver, user, password, current_state, id] = asignation_user(driver, df, id, old_state)
    id_new = None
    complete = False
    while not complete:
        try:
            introduce_user(driver, user, password)

            while driver.find_element(By.XPATH, '//*[@id="login_wrapperMsg"]/ul/li/strong'):
                time_random(1, 2)
                driver.close()
                driver = open_browse()
                opcion = None
                while opcion != "S" and opcion != "N":
                    opcion = input("¿Quieres seguir intentando o ir a otro estado? [S/N]: ")
                    if opcion == "S":
                        user = input('Escribe el usuario en lugar de {}: .'.format(user))
                        password = input('La contraseña de {}: '.format(user))
                        introduce_user(driver, user, password)
                    elif opcion == "N":
                        [old_state, numbers_advance] = looking_new_state(df, id)
                        id += numbers_advance
                        [driver, user, password, current_state, id] = asignation_user(driver, df, id, old_state)
                        introduce_user(driver, user, password)
            complete = True

        except NoSuchElementException:
            driver.implicitly_wait(1)
            if driver.find_element(By.XPATH, '//*[@id="numeroCredito"]'):
                #'//*[@id="numeroCredito"]'
                break
    return [current_state, driver, id]


def introduce_user(driver, user, password):
    driver.implicitly_wait(3)
    add_user_button = driver.find_element(By.XPATH, '//*[@id="login_wrapper"]/form/fieldset/div[1]/span/input')
    add_user_button.send_keys(user)
    add_password_button = driver.find_element(By.XPATH, '//*[@id="login_wrapper"]/form/fieldset/div[2]/span/input')
    add_password_button.send_keys(password)
    time_random(1.0, 1.5)
    driver.find_element(By.XPATH, '//*[@id="login_wrapper"]/form/fieldset/div[3]/div/span').click()


def registro():
    login = ['GreenHouse01', 'Josa1234',]
    contrasena = ['Rtxs23451H', 'Gpicom31416llas']
    user = None
    intentos = 0
    while 3 != intentos:
        user = input("Introduce el usuario: ")
        if user in login:
            position = login.index(user)
            password = input('Introduce la contraseña: ')
            if password == contrasena[position]:
                os.system("cls")
                break
            else:
                print('Contraseña incorrecta')
                intentos += 1

        elif user not in login:
            print('usuario no valido')
            intentos += 1
        os.system("cls")

        if intentos == 3:
            sys.exit()


def open_browse():

    welcome()
    print("Inicializando...")
    driver = webdriver.Chrome()
    ready= False
    while not ready:
        try:
            driver.implicitly_wait(10)
            print("Abriendo el navegador...")

            url = "http://proveedoreco.infonavit.org.mx/proveedoresEcoWeb/"  # Link de la pagina
            driver.get(url)
            print("Cargando sitio...")
            ready = True
            return driver
        except Exception:
            time_random(10, 15)
            driver.close()





def save_document(fill):
    user_path = find_user_path()
    path_save = user_path + "\\Captura\\save_captur\\"
    fill["remember token"].fillna("null", inplace=True)
    try:
        fill["cobertura"].fillna("#N/D", inplace=True)
    except KeyError:
        print("Exitooo!")
    complete_number(fill)
    fill.to_excel(path_save + "CALLCENTER.xlsx")


def main():
    registro()

    repeticion = int(input('¿Cuantas veces quieres capturar? '))
    for vuelta in range(repeticion):
        driver = open_browse()
        time_random(1.0, 1.5)
        user_path = find_user_path()  # buscamos el usuario que utiliza la computadora
        print(user_path)
        path_document = user_path + "Captura\\Data base\\"  # asignamos donde se localizan la documentación
        list_documentation = search_documentation(path_document)
        df = pd.read_excel(path_document + list_documentation[0])
        [fill, driver] = extract_number(df, driver)
        save_document(fill)
        count_number(fill)
        driver.close()


if __name__ == "__main__":
    main()
