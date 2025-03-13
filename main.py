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
    
    # Try multiple selector approaches
    tab_links = soup.select('div.waffle-name-box')
    if not tab_links:
        # Try alternative selectors
        tab_links = soup.select('[id^="sheet-button-"]')
    
    if not tab_links:
        # If still no tabs found, look for tab names in the HTML
        known_tab_names = [
            "Unreleased", "Released", "🏆 Grails", "🥇 Wanted", "⭐ Best Of",
            "✨ Special", "🗑️ Worst Of", "🤖 AI Tracks", "OG Files", "Recent",
            "Stems", "Tracklists", "🔈Remasters", "Misc", "Recently Recorded",
            "Buys", "Fakes", "Interviews", "Album Copies", "Social Media",
            "Fit Pics", "Art"
        ]
        
        # Use existing tabs from database as fallback
        print("No tab elements found in HTML, using existing tabs from database")
        db_tabs = SheetTab.objects.all()
        for tab in db_tabs:
            if tab.sheet_id:
                tabs[tab.sheet_id] = tab.name
            else:
                # Assign a temporary ID
                tabs[f"temp-{tab.id}"] = tab.name
        
        return tabs
    
    print(f"Processing {len(tab_links)} tab elements")
    for tab_link in tab_links:
        tab_name = tab_link.text.strip()
        tab_id = tab_link.get('id', '').replace('sheet-button-', '')
        
        # Skip empty tab names
        if not tab_name:
            continue
            
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
    
    if not sheets and len(soup.find_all('table')) > 0:
        # If we can't find sheet divs but there are tables, use the first table
        print("No sheet divs found, using first table found")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Use the known tab IDs from the database
        db_tabs = SheetTab.objects.all()
        if db_tabs.exists():
            # Use the first sheet tab as fallback
            fallback_tab = db_tabs.first()
            sheet_id = fallback_tab.sheet_id or f"temp-{fallback_tab.id}"
            
            # Process all tables as if they were from this sheet
            all_section_data = []
            
            for table in tables:
                rows = table.select('tr')
                print(f"Processing {len(rows)} rows from table")
                
                current_section = None
                current_subsection = None
                
                for row in rows:
                    cells = row.select('td')
                    if not cells:
                        continue
                        
                    # Get text of first cell (often contains era/section info)
                    first_cell_text = cells[0].get_text(strip=True) if cells else ""
                    
                    # Skip empty rows
                    if not first_cell_text and len(cells) > 1 and not cells[1].get_text(strip=True):
                        continue
                        
                    # Check if this is a section header (typically bold text in first column only)
                    if first_cell_text and len(cells) > 1 and not cells[1].get_text(strip=True):
                        # This might be a section header
                        if cells[0].find('b') or cells[0].find('strong'):
                            current_section = first_cell_text
                            current_subsection = None
                            print(f"Found section header: {current_section}")
                            continue
                            
                        # Or it might be a subsection
                        elif current_section and not first_cell_text.startswith(' '):
                            current_subsection = first_cell_text
                            print(f"Found subsection: {current_subsection}")
                            continue
                    
                    # Regular data row - extract cell values
                    if len(cells) >= 7:  # Need at least era, name, and a few more fields
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
                        row_data['primary_link'] = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""
                        
                        # Only add rows with at least name (era might be None)
                        if row_data.get('name'):
                            all_section_data.append(row_data)
                
            sheet_data[sheet_id] = all_section_data
            return sheet_data
    
    # Standard processing for multiple sheet divs
    print(f"Processing {len(sheets)} sheet divs")
    for sheet in sheets:
        sheet_id = sheet.get('id', '').replace('sheet-', '')
        
        # Skip if this isn't a valid sheet
        if not sheet_id:
            continue
            
        print(f"Processing sheet {sheet_id}")
            
        # Get all rows in this sheet
        rows = sheet.select('tr')
        print(f"Found {len(rows)} rows in sheet {sheet_id}")
        
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
                    print(f"Found section header: {current_section}")
                    continue
                    
                # Or it might be a subsection
                elif current_section and not first_cell_text.startswith(' '):
                    current_subsection = first_cell_text
                    print(f"Found subsection: {current_subsection}")
                    continue
            
            # Regular data row - extract cell values
            if len(cells) >= 7:  # Need at least era, name, and a few more fields
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
                row_data['primary_link'] = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""
                
                # Only add rows with at least name (era might be None)
                if row_data.get('name'):
                    section_data.append(row_data)
        
        sheet_data[sheet_id] = section_data
    
    return sheet_data

def scraper():
    # Set up Chrome options for better compatibility
    chrome_options = Options()
    # Avoid headless mode for now as it might cause issues with loading complex sheets
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    print("Loading Google Sheet...")
    driver = webdriver.Chrome(options=chrome_options) 
    driver.get(GOOGLE_SHEET)
    
    # Need to wait longer for full sheet to load
    wait_time = 20  # Increase wait time for sheet to load
    print(f"Waiting {wait_time} seconds for sheet to fully load...")
    time.sleep(wait_time)
    
    # Check if we see any content
    page_source = driver.page_source
    if "Playboi Carti" not in page_source:
        print("WARNING: Page may not have loaded properly. Waiting 10 more seconds...")
        time.sleep(10)
        page_source = driver.page_source
    
    print("Parsing sheet structure...")
    soup = BeautifulSoup(page_source, "html.parser")
    
    # Debug information
    print(f"Page size: {len(page_source)} bytes")
    print(f"Found {len(soup.find_all('tr'))} table rows")
    print(f"Found {len(soup.find_all('div', class_='waffle-name-box'))} tab name boxes")
    
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
    
    # First, organize rows by sheet_id for better tracking
    song_by_sheet = {}
    for _, row in df.iterrows():
        if pd.isnull(row['sheet_id']):
            continue
            
        sheet_id = row['sheet_id']
        if sheet_id not in song_by_sheet:
            song_by_sheet[sheet_id] = []
            
        song_by_sheet[sheet_id].append(row)
    
    # Process each sheet separately
    total_inserted = 0
    total_updated = 0
    total_metadata_created = 0
    total_metadata_updated = 0
    
    for sheet_id, songs in song_by_sheet.items():
        # Look up the corresponding sheet tab
        sheet_tab = SheetTab.objects.filter(sheet_id=sheet_id).first()
        if not sheet_tab:
            print(f"No sheet tab found for sheet ID: {sheet_id}, skipping {len(songs)} songs")
            continue
            
        print(f"Processing {len(songs)} songs from sheet tab: {sheet_tab.name}")
        
        # Database update stats for this sheet
        inserted = 0
        updated = 0
        metadata_created = 0
        metadata_updated = 0
        
        try:
            # Connect to database
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Process each song in this sheet tab
            for row_index, row in enumerate(songs):
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
                    
                    # IMPORTANT: Definitively associate this song with its sheet tab
                    # since we found it directly in that tab's HTML
                    try:
                        # Get the song
                        song = CartiCatalog.objects.get(id=song_id)
                        
                        # Update or create metadata with high confidence
                        metadata, created = SongMetadata.objects.update_or_create(
                            song=song,
                            defaults={
                                'sheet_tab': sheet_tab,
                                'subsection': row.get('subsection')
                            }
                        )
                        
                        if created:
                            metadata_created += 1
                            print(f"Created metadata for song: {row['name']} in tab: {sheet_tab.name}")
                        else:
                            # Check if tab changed
                            if metadata.sheet_tab != sheet_tab:
                                prev_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
                                print(f"Changed tab for song: {row['name']} from {prev_tab} to {sheet_tab.name}")
                            metadata_updated += 1
                    except Exception as e:
                        print(f"Error updating metadata for song ID {song_id}: {e}")
                    
                except Exception as e:
                    print(f"Error processing row {row['name']}: {e}")
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"Sheet '{sheet_tab.name}' updated: {inserted} inserted, {updated} updated, {metadata_created} metadata created, {metadata_updated} metadata updated")
            
            total_inserted += inserted
            total_updated += updated
            total_metadata_created += metadata_created
            total_metadata_updated += metadata_updated
            
        except Exception as e:
            print(f"Database error processing sheet '{sheet_tab.name}': {e}")
    
    print(f"Total database updates: {total_inserted} inserted, {total_updated} updated")
    print(f"Total metadata updates: {total_metadata_created} created, {total_metadata_updated} updated")

def run_tab_association(respect_scraper=True):
    """Run the existing tab association command"""
    from django.core.management import call_command
    
    print("Running tab association command...")
    if respect_scraper:
        # Only process songs without tab assignments
        call_command('associate_songs_with_tabs', respect_scraper=True)
    else:
        # Process all songs regardless of existing assignments
        call_command('associate_songs_with_tabs', force=True)

def analyze_tab_assignments():
    """Print tab statistics to help diagnose issues"""
    from django.db import models  # Add missing import
    
    print("\n===== TAB ASSIGNMENT ANALYSIS =====")
    
    # Total songs
    total_songs = CartiCatalog.objects.count()
    print(f"Total songs in database: {total_songs}")
    
    # Songs with tab assignments
    songs_with_tabs = CartiCatalog.objects.filter(metadata__sheet_tab__isnull=False).count()
    print(f"Songs with tab assignments: {songs_with_tabs}")
    
    # Songs without tab assignments
    songs_without_tabs = total_songs - songs_with_tabs
    print(f"Songs without tab assignments: {songs_without_tabs}")
    
    # Count by tab
    print("\nSongs by tab:")
    tabs = SheetTab.objects.all().order_by('name')
    for tab in tabs:
        count = SongMetadata.objects.filter(sheet_tab=tab).count()
        print(f"  {tab.name}: {count} songs")
    
    # Get potential Released songs
    potential_released = CartiCatalog.objects.filter(
        models.Q(type__in=["Single", "Album Track"]) |
        models.Q(era__in=["Playboi Carti", "Die Lit", "Whole Lotta Red [V4]"])
    ).exclude(
        metadata__sheet_tab__name="Released"
    ).count()
    
    print(f"\nPotential Released songs in other tabs: {potential_released}")
    
    # Check for songs with emojis in wrong tabs
    emoji_tabs = {
        "🏆": "🏆 Grails",
        "🥇": "🥇 Wanted",
        "⭐": "⭐ Best Of",
        "✨": "✨ Special",
        "🗑️": "🗑️ Worst Of",
        "🤖": "🤖 AI Tracks",
    }
    
    print("\nSongs with emoji markers in wrong tabs:")
    for emoji, expected_tab in emoji_tabs.items():
        misplaced = CartiCatalog.objects.filter(
            name__contains=emoji
        ).exclude(
            metadata__sheet_tab__name=expected_tab
        ).count()
        
        if misplaced > 0:
            print(f"  {emoji} ({expected_tab}): {misplaced} songs in wrong tabs")

if __name__ == "__main__":
    import sys
    
    # Check for command-line args
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        # Ask for confirmation
        print("This script will scrape the Google Sheet and update the database.")
        print("1. Scrape and update with tab data from sheet (RECOMMENDED)")
        print("2. Scrape, update, and force re-assign ALL tabs based on rules")
        print("3. Just scrape and update data (no tab assignment)")
        
        try:
            choice = input("Choose an option (1-3, default is 1): ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "1"  # Default if interrupted
    
    if choice == "2":
        print("Option 2: Will force-reassign ALL tab assignments based on rules.")
        table_setup()
        scraper()
        run_tab_association(respect_scraper=False)
    elif choice == "3":
        print("Option 3: Will only scrape data without reassigning tabs.")
        table_setup()
        scraper()
    else:
        print("Option 1: Will scrape data and only assign tabs for songs without assignments.")
        table_setup()
        scraper()
        run_tab_association(respect_scraper=True)
    
    # Always show tab assignment analysis
    analyze_tab_assignments()