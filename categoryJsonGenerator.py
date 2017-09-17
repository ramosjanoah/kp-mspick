import pandas as pd
import json

category = pd.read_csv("data/categories.csv")

df_id = category[['id', 'name']]
df_id_dict = {}
df_name_dict = {}
for index, row in df_id.iterrows():
    df_id_dict[row['id']] = row['name']
    df_name_dict[row['name']] = row['id']
    
with open("WebApp/data/category_id.json", 'w') as outfile:
    json.dump(df_id_dict, outfile)
    
with open("WebApp/data/category_name.json", 'w') as outfile:
    json.dump(df_name_dict, outfile)