import requests
from bs4 import BeautifulSoup
import pandas as pd
import string
import spacy
import jaro
import re
import warnings

def get_google_sheet(src)->list:
    """
    Returns a 2D array of the contents of the Google Sheet at the given URL

    Args:
        src (str): The URL of the Google Sheet

    Returns:
        grid (list): A 2D array of the contents of the Google Sheet
    """

    raw_html = requests.get(src).text #The size of the Google sheet that can be read is limited (good enough for casual use)
    soup = BeautifulSoup(raw_html, 'html.parser')
    table = soup.find("tbody")
    rows = table.find_all("tr")
    grid = []
    for row in rows:
        cols = row.find_all("td")
        clean_row = []
        for col in cols:
            clean_row.append(col.text)
        grid.append(clean_row)
    return grid

def sheet_to_df(sheet)->list:
    """
    Returns a list of dataframes for each data table in a given 2D array of the contents of a spreadsheet

    Args:
        sheet (list): A 2D array of the contents of the Google Sheet

    Returns:
        dfs (list): A list of dataframes from the Google Sheet
    """

    #A dataframe starts when a header is found
    #A header is a the first instance of a set of contiguous columns in the same row that contain at least some letters
    #A dataframe ends when a blank row is found or an empty column is found

    num = 0 #The number of the dataframe
    headers = [] #Each header is a tuple (num, row, col_start, col_end)
    binding_headers = []
    dfs = [] #Each df is a tuple (num, df)

    #First pass: get all the headers
    for row in range(len(sheet)):

        #if every cell in the row is empty, skip row
        if all([sheet[row][col].strip() == "" for col in range(len(sheet[row]))]):
            headers += binding_headers
            binding_headers = []
            continue

        for col in range(len(sheet[row])):

            #Check if the cell is bounded by a header
            if any([col >= header[2] and col <= header[3] for header in binding_headers]):
                continue

            #Check if the cell is commented out
            if sheet[row][col].strip().startswith("//"):
                continue
            
            if re.search('[a-zA-Z]', sheet[row][col]):
                head_start = col
                head_end = col
                while head_end < len(sheet[row]) and re.search('[a-zA-Z]', sheet[row][head_end]):
                    head_end += 1
                binding_headers.append([num, row, head_start, head_end])
                num += 1   
    headers += binding_headers

    #Second pass: get all the dataframes
    for header in headers:
        df = []
        for row in range(header[1], len(sheet)):
            if all([sheet[row][col].strip() == "" for col in range(header[2], header[3])]):
                break
            df_row = []
            for col in range(header[2], header[3]):
                df_row.append(sheet[row][col])
            df.append(df_row)
        cols = df[0]
        data = df[1:]
        df = pd.DataFrame(data, columns=cols)

        #Cast all the numeric columns to numeric types
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass
        dfs.append(df)
    
    return dfs

def select_df(prompt, dfs)->pd.DataFrame:
    """
    Returns the dataframe that best matches the prompt

    Args:
        prompt (str): The prompt to match
        dfs (list): A list of dataframes from the Google Sheet

    Returns:
        df (pd.DataFrame): The dataframe that best matches the prompt
    """

    if len(dfs) == 0:
        raise ValueError("No dataframes found in the Google Sheet")

    #Simplify the prompt to just the nouns
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(prompt)
    nouns = [token.text for token in doc if (token.pos_ == 'NOUN' or token.pos_ == 'PROPN')]
    nouns = [word.lower() for word in nouns] #lowercase all the words (done after finding the nouns to preserve proper nouns)

    all_columns = [df.columns for df in dfs]

    #Find the similarity between the prompt subject and each df
    similarities = []
    for columns in all_columns:
        #Preprocess the columns
        cleaned_columns = [col.lower().strip().translate(str.maketrans('', '', string.punctuation)).split() for col in columns]
        cleaned_columns = [word for col in cleaned_columns for word in col] #flatten the list

        #Find the similarity
        similarity = 0
        for col in cleaned_columns:
            for word in nouns:
                temp_similarity = jaro.jaro_winkler_metric(col, word)

                #Preserve the number of exact matches without having a bias for larger spreadsheets
                if temp_similarity == 1:
                    similarity += 1
                else:
                    similarity = max(similarity, temp_similarity)

        similarities.append(similarity)
    
    max_similarity = max(similarities)
    
    #Check if the similarity score is ambiguous
    if similarities.count(max_similarity) > 1:
        warnings.warn(
            """
            The prompt is too ambiguous. 
            - Please be more specific about the data table you are referencing by explicitly naming its unique columns.
            - Note that google sheets ai can only handle one dataframe at a time.
            """, 
            UserWarning)

    #Return the df with the highest similarity
    return dfs[similarities.index(max_similarity)]

def google_sheets_ai(url, prompt)->pd.DataFrame:
    """
    Returns the dataframe from a google sheet that best matches the prompt

    Args:
        url (str): The URL of the Google Sheet
        prompt (str): The prompt to match

    Returns:
        df (pd.DataFrame): The dataframe that best matches the prompt
    """

    sheet = get_google_sheet(url)
    dfs = sheet_to_df(sheet)
    df = select_df(prompt, dfs)
    
    return df