from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import psycopg2

DB_CONFIG = {
    "host":"localhost",
    "dbname": "postgres",
    "user": "postgres",
    "password": "MySQL32$98512",
    "port": 5432

}

GOOGLE_SHEET = "https://docs.google.com/spreadsheets/u/0/d/1rAU0sktd1GKpqo_AAWBtkXy10Px3BB_dnK9yJoN0umw/htmlview?pli=1#"

def table_setup():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS carti_catalog (
            id SERIAL PRIMARY KEY,
            era TEXT,
            name TEXT,
            notes TEXT,
            track_length TEXT,
            leak_date TEXT,
            file_date TEXT,
            type TEXT,
            available_length TEXT,
            quality TEXT,
            links TEXT,
            primary_link TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(era, name)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

def scraper():

    driver = webdriver.Chrome() 
    driver.get(GOOGLE_SHEET)
    time.sleep(10)  
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit() 

    rows = soup.find_all("tr")

    parsed_data = []
    for row in rows:
        row_data = [td.get_text(" ", strip=True) for td in row.find_all("td")]
        if row_data:
            try:
                link_tag = row.find("a")
                link = link_tag["href"] if link_tag else ""
            except:
                link = ""

            row_data.append(link)
            parsed_data.append(row_data)

    df = pd.DataFrame(parsed_data)


    column_names = [
        "Era", "Name", "Notes", "Track_Length", "Leak_Date", "File_Date", 
        "Type", "Available_Length", "Quality", "Links", "Primary_Link"
    ]

    # Add generic column names
    while len(column_names) < df.shape[1]:
        column_names.append(f"Extra_{len(column_names) - 10}")

    df.columns = column_names

    # Drop NaN rows
    df = df.dropna(how='all')

    df.to_csv("sheetsdata.csv", index=False)
    print(f"data saved: {len(df)} rows")

    inserted = 0
    updated = 0

    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Insert each row, update if it already exists
        for _, row in df.iterrows():
            # Skip rows without an era or name
            if pd.isnull(row['Era']) or pd.isnull(row['Name']):
                continue
                
            # Extract values for database insertion
            values = [
                row['Era'], row['Name'], row['Notes'], row['Track_Length'],
                row['Leak_Date'], row['File_Date'], row['Type'],
                row['Available_Length'], row['Quality'], row['Links'],
                row['Primary_Link']
            ]
            
            # Insert or update the row
            try:
                cur.execute("""
                    INSERT INTO carti_catalog 
                    (era, name, notes, track_length, leak_date, file_date, 
                     type, available_length, quality, links, primary_link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (era, name) DO UPDATE SET
                    notes = EXCLUDED.notes,
                    track_length = EXCLUDED.track_length,
                    leak_date = EXCLUDED.leak_date,
                    file_date = EXCLUDED.file_date,
                    type = EXCLUDED.type,
                    available_length = EXCLUDED.available_length,
                    quality = EXCLUDED.quality,
                    links = EXCLUDED.links,
                    primary_link = EXCLUDED.primary_link
                """, values)
                
                if cur.statusmessage.startswith("INSERT"):
                    inserted += 1
                else:
                    updated += 1
            except Exception as e:
                print(f"Error inserting row {row['Name']}: {e}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Database updated: {inserted} rows inserted, {updated} rows updated")
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    table_setup()

    scraper()