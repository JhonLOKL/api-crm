import gspread
from oauth2client.service_account import ServiceAccountCredentials
from decouple import config
import pandas as pd
from src.utils.credentials import credentials
import ast

def bedroomDummies():
    try:

        json_credenciales = credentials()
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(json_credenciales, scope)
        gc = gspread.authorize(credenciales)
        
        spreadsheet = gc.open_by_url(config('HOTELS_URL'))
        bedrooms_looker_sheet = spreadsheet.worksheet('bedrooms_looker')
        bedrooms_looker_sheet.clear()
        
        bedrooms_df_sheet = spreadsheet.worksheet('bedrooms_df')

        data = bedrooms_df_sheet.get_all_values()
        bedrooms_df = pd.DataFrame(data[1:], columns=data[0])

       
        bedrooms_df['id'] = bedrooms_df['title_hotel'] + '-' + bedrooms_df['title_room']
        bedrooms_df = bedrooms_df.drop_duplicates(subset=['id'], keep='last')
        bedrooms_df = bedrooms_df.drop('id', axis=1)
        
        bedrooms_df['features_room'] = bedrooms_df['features_room'].apply(ast.literal_eval)
        df_services_dummies = pd.get_dummies(bedrooms_df['features_room'].apply(pd.Series).stack()).groupby(level=0).sum()
        bedrooms_df = pd.concat([bedrooms_df, df_services_dummies], axis=1)
        bedrooms_df = bedrooms_df.drop('features_room', axis=1)
        
        new_data = [bedrooms_df.columns.values.tolist()] + bedrooms_df.values.tolist()
        bedrooms_looker_sheet.update(new_data)

        return ("The bedrooms were dummies successfully!"), 201

    except gspread.exceptions.GSpreadException as e:
        return (f"Google Sheets error: {e}"), 400
    except KeyError as e:
        return (f"Key error: {e}"), 400
    except ValueError as e:
        return (f"Value error: {e}"), 400
    except Exception as e:
        return (f"Unexpected error: {e}"), 400
