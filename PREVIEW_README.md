# Song Preview Feature

This feature allows the automatic generation of 30-second preview clips for songs in the Carti Catalog.

## Setup

1. Install required dependencies:
   ```bash
   pip install -r requirements_preview.txt
   ```

2. Install FFmpeg (required for audio processing):
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

3. Install Redis (for the Celery task queue):
   - **macOS**: `brew install redis`
   - **Ubuntu/Debian**: `sudo apt-get install redis-server`
   - **Windows**: Follow the installation guide on the [Redis website](https://redis.io/download)

4. Add the preview_url column to your database:
   ```bash
   python manage.py dbshell < catalog/migrations/manual_add_preview_url.sql
   ```

## Usage

1. Start the Redis server:
   ```bash
   redis-server
   ```

2. Start the Celery worker:
   ```bash
   celery -A carti_project worker --loglevel=info
   ```

3. Generate previews for all songs:
   ```bash
   python manage.py generate_previews
   ```

## How It Works

The system works by:
1. Finding songs without previews
2. Extracting download URLs from the song links
3. Downloading the full audio file temporarily
4. Cutting a 30-second segment (starting 30 seconds into the track)
5. Converting to MP3 format
6. Storing in the media/previews directory
7. Updating the song record with the preview URL

## Customization

You can customize the preview generation by editing the `catalog/preview_generator.py` file:

- `PREVIEW_LENGTH`: Change the duration of previews (in milliseconds)
- `START_AT`: Adjust where in the track the preview should start (in milliseconds)
- `extract_download_url()`: Add support for additional file sharing sites

## Troubleshooting

1. **FFmpeg not found**: Ensure FFmpeg is installed and available in your PATH
2. **File downloads failing**: Check logs for specific errors and update the download handlers
3. **Task queue not processing**: Make sure Redis is running and Celery worker is started

## Legal Considerations

Please ensure you have the appropriate rights to create and distribute preview clips of the audio files.