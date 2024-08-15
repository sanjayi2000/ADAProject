import os 
from dotenv import load_dotenv
from groq import Groq
from firecrawl import FirecrawlApp
import json
import pandas as pd
from datetime import datetime

def scrapedata(url):
    load_dotenv()
    app=FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
    scrapeddata=app.scrape_url(url)
    if 'markdown' in scrapeddata:
        return scrapeddata['markdown']
    else:
        raise KeyError("Mardown Not Found")
    
def savedata(rawdata,timestamp,output_folder = 'output'):
    os.makedirs(output_folder,exist_ok=True)
    
    rawpath = os.path.join(output_folder, f'rawData_{timestamp}.md')
    with open(rawpath, 'w',encoding='utf-8') as f:
        f.write(rawdata)
    print(f"Raw Data saved to {rawpath}")
def formatdata(data):
    load_dotenv()
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    fields = ['Festival','Year']
        
    systemprompt = f"""
    
    You are an intelligent text extraction and conversion assistant. Your task is to extract structured information from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text,with no additional commentary, explanations, or extraneous information. Please process the following text and provide the output in pure JSON format with no words before or after the JSON:
    
    """
    
    userprompt = f'Extract the following information from the provided text:\nPage content:\n\n{data}\n\nInformation to extract: {fields}'
    response = client.chat.completions.create(
        model = "llama3-70b-8192",
        response_format = {"type":"json_object"},
        messages = [
            {
                "role" : "system",
                "content" : systemprompt
            },
            
            {
                "role" : "user",
                "content" : userprompt
            }
        ]
    )
    
    if response and response.choices:
        formatteddata = response.choices[0].message.content.strip()
        print(f"Formatted data received from API: {formatteddata}")
        
        try:
            parsed_json = json.loads(formatteddata)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            print(f"Formatted data that caused the error: {formatteddata}")
            raise ValueError("The formatted data could not be decoded into JSON.")
        
        return parsed_json
    else:
        raise ValueError("The OpenAI API response did not contain the expected choices data.")
    
# This function is for saving the formatted data

def save_formatted_data(formatted_data, timestamp, output_folder='output'):
       
    os.makedirs(output_folder, exist_ok=True)
    
    output_path = os.path.join(output_folder, f'sorted_data_{timestamp}.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=4)
    print(f"Formatted data saved to {output_path}")

    if isinstance(formatted_data, dict) and len(formatted_data) == 1:
        key = next(iter(formatted_data))
        formatted_data = formatted_data[key]

    if isinstance(formatted_data, dict):
        formatted_data = [formatted_data]

    df = pd.DataFrame(formatted_data)

    excel_output_path = os.path.join(output_folder, f'sorted_data_{timestamp}.xlsx')
    df.to_excel(excel_output_path, index=False)
    print(f"Formatted data saved to Excel at {excel_output_path}")

if __name__ == "__main__":
        # Scrape a single URL
        url = 'https://www.imdb.com/list/ls543587091?ref_=hm_edcft_india_mid_year_popular_movies_2024_geo_1_i'
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            raw_data = scrapedata(url)
            
            savedata(raw_data, timestamp)
 
            formatted_data = formatdata(raw_data)
            
            save_formatted_data(formatted_data, timestamp)
            
        except Exception as e:
            print(f"An error occurred: {e}")