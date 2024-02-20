import pandas as pd
import os

# Code to analyse
# def list_files(dir):
#     os.chdir(dir)
#     filesList = [f for f in os.listdir() if os.path.isfile(f)]
#     dictFiles = {}
#     count = 1
#     os.chdir("..")

#     for i in filesList:
#         print(f"File = {i} and count = {count}")
#         dictFiles.update({count : i})
#         count+=1
#     return dictFiles

# def menuConvert_xlsx():
#     options = list_files("Bases/")
#     keys = options.keys()

#     print("Select the file by the number you want to convert")
#     for key in keys:
#         print(f"{key} : {options.get(key)}")
#     select = input("Insert the code of the file you want to convert: ")
#     archive = options.get(int(select))
#     print(f"the file is {archive}")
#     return archive

# def convertJsonToPd(file):
#     fileName = file.split(".")[0]
#     value = "Bases/excelConvert/" + fileName + ".xlsx"
#     json_data = getJsonFile("Bases/", file)
#     try:
#         json_data = json_data["metrics_explode"]
#     except:
#         print("n_data")
#     df = pd.json_normalize(json_data)
#     df.to_excel(value, index=False)

# def convertXlsx():
#     iter = "1"

#     while iter == "1":
#         convertJsonToPd(menuConvert_xlsx())
#         iter = input("""
#                      Gostaria de fazer mais uma conversão?
#                         SIM - DIGITE 1 E ENTER
#                         NÃO - APERTE ENTER
#                      """)

