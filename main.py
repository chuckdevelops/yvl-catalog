from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
import psycopg2
import re
import os
import django

# Set Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carti_project.settings")
django.setup()

from catalog.models import SheetTab, SongMetadata, CartiCatalog

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

def get_sheet_tabs(soup):
    """Extract all sheet tabs from the HTML"""
    tabs = {}
    tab_links = soup.select('div.waffle-name-box')
    for tab_link in tab_links:
        tab_name = tab_link.text.strip()
        tab_id = tab_link.get('id', '').replace('sheet-button-', '')
        tabs[tab_id] = tab_name
        
        # Create or update sheet tab in database
        SheetTab.objects.update_or_create(
            name=tab_name,
            defaults={'sheet_id': tab_id}
        )
    
    return tabs

def parse_sheet_structure(soup):
    """Parse the entire sheet structure to identify sections, subsections, and songs"""
    sheet_data = {}
    
    # Find all sheets/tabs
    sheets = soup.select('div[id^="sheet-"]')
    
    for sheet in sheets:
        sheet_id = sheet.get('id', '').replace('sheet-', '')
        
        # Skip if this isn't a valid sheet
        if not sheet_id:
            continue
            
        # Get all rows in this sheet
        rows = sheet.select('tr')
        
        current_section = None
        current_subsection = None
        section_data = []
        
        for row in rows:
            # Check if this is a header row (section or subsection)
            if 'frozen-row' in row.get('class', []):
                continue  # Skip column headers
                
            cells = row.select('td')
            if not cells:
                continue
                
            # Get text of first cell (often contains era/section info)
            first_cell_text = cells[0].get_text(strip=True) if cells else ""
            
            # Check if this is a section header (typically bold text in first column only)
            if first_cell_text and len(cells) > 1 and not cells[1].get_text(strip=True):
                # This might be a section header
                if cells[0].find('b') or cells[0].find('strong'):
                    current_section = first_cell_text
                    current_subsection = None
                    continue
                    
                # Or it might be a subsection
                elif current_section and not first_cell_text.startswith(' '):
                    current_subsection = first_cell_text
                    continue
            
            # Regular data row - extract cell values
            row_data = {}
            if len(cells) >= 11:  # Ensure we have enough cells for standard fields
                row_data = {
                    'era': current_section,
                    'name': cells[1].get_text(strip=True) if len(cells) > 1 else "",
                    'notes': cells[2].get_text(strip=True) if len(cells) > 2 else "",
                    'track_length': cells[3].get_text(strip=True) if len(cells) > 3 else "",
                    'leak_date': cells[4].get_text(strip=True) if len(cells) > 4 else "",
                    'file_date': cells[5].get_text(strip=True) if len(cells) > 5 else "",
                    'type': cells[6].get_text(strip=True) if len(cells) > 6 else "",
                    'available_length': cells[7].get_text(strip=True) if len(cells) > 7 else "",
                    'quality': cells[8].get_text(strip=True) if len(cells) > 8 else "",
                    'links': cells[9].get_text(strip=True) if len(cells) > 9 else "",
                    'subsection': current_subsection,
                    'sheet_id': sheet_id
                }
                
                # Get link if available
                link_tag = cells[9].find("a") if len(cells) > 9 else None
                row_data['primary_link'] = link_tag["href"] if link_tag else ""
                
                # Only add rows with at least era and name
                if row_data.get('era') and row_data.get('name'):
                    section_data.append(row_data)
        
        sheet_data[sheet_id] = section_data
    
    return sheet_data

def scraper():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options) 
    driver.get(GOOGLE_SHEET)
    print("Loading Google Sheet...")
    
    # Need to wait longer for full sheet to load
    time.sleep(15)
    
    print("Parsing sheet structure...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    
    # Extract sheet tabs
    tabs = get_sheet_tabs(soup)
    print(f"Found {len(tabs)} sheet tabs")
    
    # Parse full sheet structure
    sheet_data = parse_sheet_structure(soup)
    
    # Flatten sheet data for database import
    all_rows = []
    for sheet_id, rows in sheet_data.items():
        for row in rows:
            all_rows.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_rows)
    
    # Save to CSV
    df.to_csv("sheetsdata.csv", index=False)
    print(f"Data saved: {len(df)} rows to CSV")
    
    # Database update stats
    inserted = 0
    updated = 0
    metadata_created = 0
    metadata_updated = 0

    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Insert each row, update if it already exists
        for _, row in df.iterrows():
            # Skip rows without an era or name
            if pd.isnull(row['era']) or pd.isnull(row['name']):
                continue
                
            # Extract values for database insertion
            values = [
                row['era'], row['name'], row['notes'], row['track_length'],
                row['leak_date'], row['file_date'], row['type'],
                row['available_length'], row['quality'], row['links'],
                row['primary_link']
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
                    RETURNING id
                """, values)
                
                # Get the ID of the inserted/updated row
                song_id = cur.fetchone()[0]
                
                if cur.statusmessage.startswith("INSERT"):
                    inserted += 1
                else:
                    updated += 1
                
                # Update song metadata with sheet tab and subsection
                try:
                    # Get the sheet tab
                    sheet_tab = None
                    if 'sheet_id' in row and not pd.isnull(row['sheet_id']):
                        sheet_tab = SheetTab.objects.filter(sheet_id=row['sheet_id']).first()
                    
                    if sheet_tab:
                        # Get the song
                        song = CartiCatalog.objects.get(id=song_id)
                        
                        # Update or create metadata
                        metadata, created = SongMetadata.objects.update_or_create(
                            song=song,
                            defaults={
                                'sheet_tab': sheet_tab,
                                'subsection': row.get('subsection')
                            }
                        )
                        
                        if created:
                            metadata_created += 1
                        else:
                            metadata_updated += 1
                except Exception as e:
                    print(f"Error updating metadata for song ID {song_id}: {e}")
                
            except Exception as e:
                print(f"Error processing row {row['name']}: {e}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Database updated: {inserted} rows inserted, {updated} rows updated")
        print(f"Metadata updated: {metadata_created} created, {metadata_updated} updated")
        
    except Exception as e:
        print(f"Database error: {e}")

def run_tab_association():
    """Run the existing tab association command"""
    from django.core.management import call_command
    
    print("Running tab association command...")
    call_command('associate_songs_with_tabs')

if __name__ == "__main__":
    table_setup()
    scraper()
    run_tab_association()