# Playboi Carti Catalog

## Art Media Management

### Adding New Artwork

#### Method 1: Manual Entry (Interactive)

For adding a few images at a time:

```
python manage.py manual_art_import --download-images
```

This will prompt you to enter information for each artwork interactively:
- Name
- Era
- Notes
- Media type
- Whether it was used officially
- Source URL for the image

#### Method 2: Bulk Import (JSON)

For adding multiple artworks in one go:

1. Generate a JSON template:
   ```
   python manage.py create_art_json_template --output=art_data.jsonl
   ```

2. Edit the JSON file in any text editor, adding one JSON object per line with:
   - era: Time period (e.g., "Self-Titled", "Die Lit")
   - name: Title of the artwork
   - notes: Additional information
   - media_type: Category (e.g., "Album Cover", "Single Art")
   - was_used: true/false for official usage
   - links: URL to the source image

3. Import the data:
   ```
   python manage.py bulk_art_import art_data.jsonl --download-images
   ```

### How Image Downloading Works

The system will:
1. Parse the provided data
2. For each artwork with a link:
   - Extract direct image URLs from Imgur and other sources
   - Download the images to the `media/art/` directory
   - Store relative paths in the database
3. For artworks without valid image links, a placeholder image is used

### Supported Image Sources

- Google Sheets image URLs (can paste the HTML img tag directly)
- Direct image URLs (.jpg, .png, .gif)
- Imgur links (automatically converted to direct image URLs)
- Other links (will attempt to download directly)

### Example JSON Entry

```json
{
  "era": "Self-Titled",
  "name": "Artwork Title",
  "notes": "Description of the artwork",
  "media_type": "Album Cover",
  "was_used": true,
  "links": "https://imgur.com/6q1dUzi"
}
```

### Google Sheets Image Example

You can also directly copy the image HTML from Google Sheets:

```json
{
  "era": "Aviation Class",
  "name": "TOO FLY KID",
  "notes": "unknown purpose",
  "media_type": "Unknown",
  "was_used": false,
  "links": "<img src=\"https://lh7-rt.googleusercontent.com/sheetsz/AHOq17GxrFDXSC47q-iHi1ZjeqXobQRw70xK7XxjbkebEcU4_HYG3uwyoifi-Lz6fZu-oHblYpI2uJOE-luYJc2jdfmwBgmCzkvsNn_YDY8XhWtU2FsNOxycXscsnQ-BqT10=w330-h334?key=QrLRwW_6ASWi9mCdhUkgTQ\" style=\"width:inherit;height:inherit;object-fit:scale-down;object-position:center center;\">"
}
```

The system will extract the image URL from the HTML tag and download it directly.