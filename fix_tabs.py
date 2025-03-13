import os
import django
import argparse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carti_project.settings")
django.setup()

from django.db import models
from catalog.models import CartiCatalog, SheetTab, SongMetadata

def fix_misc_and_art_tabs():
    """Fix Misc tab assignments and clear the Art tab"""
    print("Fixing Misc tab assignments and clearing Art tab...")
    
    misc_tab = SheetTab.objects.get(name="Misc")
    art_tab = SheetTab.objects.get(name="Art")
    unreleased_tab = SheetTab.objects.get(name="Unreleased")
    released_tab = SheetTab.objects.get(name="Released")
    
    # Types that should be in Misc tab
    misc_types = ["Music Video", "Studio Footage", "Documentary", "Promo", "Visualizer"]
    
    # Keywords that indicate Misc content
    misc_keywords = ["Music Video", "Video", "Studio", "Documentary", "Promo", "Visualizer", 
                    "Behind The Scenes", "BTS", "Interview", "Footage"]
    
    # Move all Art tab items to Unreleased
    art_items = SongMetadata.objects.filter(sheet_tab=art_tab)
    moved_from_art = 0
    
    for metadata in art_items:
        metadata.sheet_tab = unreleased_tab
        metadata.save()
        moved_from_art += 1
        print(f"[ART] Moved '{metadata.song.name}' from Art to Unreleased")
    
    print(f"Moved {moved_from_art} items from Art tab to Unreleased")
    
    # Find items that should be in Misc based on type or keywords
    misc_items_count = 0
    
    # By type
    for song in CartiCatalog.objects.filter(type__in=misc_types).exclude(notes__icontains="Streaming").exclude(name__contains="CARNIVAL"):
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        if metadata.sheet_tab != misc_tab:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = misc_tab
            metadata.save()
            print(f"[MISC] Moved '{song.name}' from '{old_tab}' to 'Misc' (Type: {song.type})")
            misc_items_count += 1
    
    # By keywords in name
    for keyword in misc_keywords:
        for song in CartiCatalog.objects.filter(name__icontains=keyword).exclude(notes__icontains="Streaming").exclude(name__contains="CARNIVAL"):
                
            metadata, created = SongMetadata.objects.get_or_create(song=song)
            if metadata.sheet_tab != misc_tab:
                old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
                metadata.sheet_tab = misc_tab
                metadata.save()
                print(f"[MISC] Moved '{song.name}' from '{old_tab}' to 'Misc' (Keyword: {keyword})")
                misc_items_count += 1
    
    # Special check for "TOO FLY KID"
    try:
        too_fly_kid = CartiCatalog.objects.get(name="TOO FLY KID")
        
        # Skip if it has Streaming category
        if too_fly_kid.notes and "Streaming" in too_fly_kid.notes:
            print(f"[MISC-SKIP] Keeping 'TOO FLY KID' in 'Released' (has Streaming category)")
        else:
            metadata, created = SongMetadata.objects.get_or_create(song=too_fly_kid)
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = misc_tab
            metadata.save()
            print(f"[MISC] Moved 'TOO FLY KID' from '{old_tab}' to 'Misc' (Special case)")
            misc_items_count += 1
    except CartiCatalog.DoesNotExist:
        print("Note: 'TOO FLY KID' not found in database")
    
    print(f"Moved {misc_items_count} items to Misc tab")

def fix_streaming_songs():
    """Move all songs with Streaming category to Released tab"""
    print("Fixing Streaming songs...")
    
    released_tab = SheetTab.objects.get(name="Released")
    misc_tab = SheetTab.objects.get(name="Misc")
    
    # Types that should be in Misc tab
    misc_types = ["Music Video", "Studio Footage", "Documentary", "Promo", "Visualizer"]
    
    # Keywords that indicate Misc content
    misc_keywords = ["Music Video", "Video", "Studio", "Documentary", "Promo", "Visualizer", 
                    "Behind The Scenes", "BTS", "Interview", "Footage"]
    
    updated_streaming = 0
    special_cases = 0
    
    # Special case for CARNIVAL song - check and handle it specifically
    target_carnival = "¥$ - CARNIVAL [Music Video Version](feat. Playboi Carti & Rich The Kid)"
    
    try:
        carnival_songs = CartiCatalog.objects.filter(name__contains="CARNIVAL", type="Feature")
        for carnival_song in carnival_songs:
            # Handle the specific song we've been having issues with
            if target_carnival in carnival_song.name:
                metadata, created = SongMetadata.objects.get_or_create(song=carnival_song)
                if metadata.sheet_tab != released_tab:
                    old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
                    metadata.sheet_tab = released_tab
                    metadata.save()
                    print(f"[SPECIAL-CARNIVAL] Moved '{carnival_song.name}' to Released tab (Feature type)")
                    updated_streaming += 1
    except Exception as e:
        print(f"Note: Error handling CARNIVAL song: {e}")
    
    # Track media songs that have streaming category
    streaming_media_songs = []
    
    # First, identify streaming songs that are also multimedia/video content
    for song in CartiCatalog.objects.filter(notes__icontains="Streaming"):
        is_multimedia = False
        
        # Skip the CARNIVAL song as we've handled it specially
        if "CARNIVAL" in song.name:
            continue
        
        # Check if it's a multimedia type
        if song.type in misc_types:
            is_multimedia = True
        
        # Check if it has a multimedia keyword in the name
        if not is_multimedia:
            for keyword in misc_keywords:
                if keyword.lower() in song.name.lower():
                    is_multimedia = True
                    break
        
        if is_multimedia:
            streaming_media_songs.append(song.id)
            print(f"[SPECIAL] '{song.name}' is both Streaming and multimedia content")
            special_cases += 1
    
    # Handle normal streaming songs (not multimedia)
    for song in CartiCatalog.objects.filter(
        notes__icontains="Streaming"
    ).exclude(
        id__in=streaming_media_songs  # Skip the special cases for now
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="CARNIVAL"  # Skip the special CARNIVAL case
    ):
        try:
            metadata = SongMetadata.objects.get(song=song)
            current_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            
            # Update to Released tab
            metadata.sheet_tab = released_tab
            metadata.save()
            
            print(f"[STREAMING] Moved '{song.name}' from '{current_tab}' to 'Released' (Category: Streaming)")
            updated_streaming += 1
        except SongMetadata.DoesNotExist:
            # Create new metadata
            metadata = SongMetadata.objects.create(song=song, sheet_tab=released_tab)
            print(f"[STREAMING] Created new metadata for '{song.name}' in 'Released' (Category: Streaming)")
            updated_streaming += 1
    
    print(f"Updated {updated_streaming} songs to Released tab based on Streaming category")
    
    # Let the user know about special cases
    if special_cases > 0:
        print(f"Note: Found {special_cases} songs that are both streaming and multimedia content")
        print("These songs will be placed in the Released tab due to Streaming category")
        
        # Handle special cases - multimedia streaming songs go to Released
        for song_id in streaming_media_songs:
            song = CartiCatalog.objects.get(id=song_id)
            metadata, created = SongMetadata.objects.get_or_create(song=song)
            
            if metadata.sheet_tab != released_tab:
                old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
                metadata.sheet_tab = released_tab
                metadata.save()
                print(f"[STREAMING-MEDIA] Moved '{song.name}' from '{old_tab}' to 'Released' (Special case)")
                updated_streaming += 1

def fix_released_tabs():
    """Fix Released tab assignments based on song types"""
    print("Fixing Released tab assignments...")
    
    released_tab = SheetTab.objects.get(name="Released")
    unreleased_tab = SheetTab.objects.get(name="Unreleased")
    misc_tab = SheetTab.objects.get(name="Misc")
    
    # Types that should be in Released tab
    released_types = ["Single", "Feature", "Album Track", "Lost"]
    
    # Types that should be in Unreleased tab
    unreleased_types = ["Remix", "Unknown", "OG", "Throwaway", "High Bitrate Rip", 
                        "Demo", "Alt Mix", "OG File", "Ref Track"]
                        
    # Types that should be in Misc tab
    misc_types = ["Music Video", "Studio Footage", "Documentary", "Promo", "Visualizer"]
    
    updated_released = 0
    updated_unreleased = 0
    
    # Fix RELEASED - move appropriate songs to Released tab
    for song in CartiCatalog.objects.filter(
        # Any regular types
        models.Q(type__in=released_types) |
        # Special case: "Lost" songs in "THC: The High Chronicals" era
        models.Q(type="Lost", era="THC: The High Chronicals") |
        # Special case: "Mixtape" songs in "Young Mi$fit" era
        models.Q(type="Mixtape", era="Young Mi$fit")
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        # Skip songs with media types (Music Video etc.) unless they have Streaming category
        models.Q(type__in=misc_types) & ~models.Q(notes__icontains="Streaming")
    ).exclude(
        # Skip CARNIVAL as it's handled specially
        name__contains="CARNIVAL"
    ):
        # Get the song's current tab
        try:
            metadata = SongMetadata.objects.get(song=song)
            current_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            
            # Update to Released tab
            metadata.sheet_tab = released_tab
            metadata.save()
            
            print(f"[RELEASED] Moved '{song.name}' from '{current_tab}' to 'Released' (Type: {song.type})")
            updated_released += 1
        except SongMetadata.DoesNotExist:
            # Create new metadata
            metadata = SongMetadata.objects.create(song=song, sheet_tab=released_tab)
            print(f"[RELEASED] Created new metadata for '{song.name}' in 'Released' (Type: {song.type})")
            updated_released += 1
    
    # Fix UNRELEASED - move appropriate songs to Unreleased tab if they're in Released
    for song in CartiCatalog.objects.filter(
        type__in=unreleased_types,
        metadata__sheet_tab=released_tab
    ).exclude(notes__icontains="Streaming"):  # Don't move Streaming songs back to Unreleased
        metadata = SongMetadata.objects.get(song=song)
        
        # Update to Unreleased tab
        metadata.sheet_tab = unreleased_tab
        metadata.save()
        
        print(f"[UNRELEASED] Moved '{song.name}' from 'Released' to 'Unreleased' (Type: {song.type})")
        updated_unreleased += 1
    
    print(f"Updated {updated_released} songs to Released tab based on type")
    print(f"Updated {updated_unreleased} songs to Unreleased tab")

def fix_emoji_tabs():
    """Fix emoji-based tab assignments"""
    print("Fixing emoji-based tab assignments...")
    
    # Define emoji to tab mapping
    emoji_tabs = {
        "🏆": SheetTab.objects.get(name="🏆 Grails"),
        "🥇": SheetTab.objects.get(name="🥇 Wanted"),
        "⭐": SheetTab.objects.get(name="⭐ Best Of"),
        "✨": SheetTab.objects.get(name="✨ Special"),
        "🗑️": SheetTab.objects.get(name="🗑️ Worst Of"),
        "🗑": SheetTab.objects.get(name="🗑️ Worst Of"),
        "🤖": SheetTab.objects.get(name="🤖 AI Tracks")
    }
    
    updated_count = 0
    
    # Process each emoji
    for emoji, tab in emoji_tabs.items():
        # Find songs with this emoji
        emoji_songs = CartiCatalog.objects.filter(name__contains=emoji)
        
        for song in emoji_songs:
            # Get current tab - we won't remove from Released tab
            try:
                metadata = SongMetadata.objects.get(song=song)
                if metadata.sheet_tab != tab:
                    # Only log this as we want to potentially DUPLICATE these songs
                    # rather than move them - especially if in Released
                    print(f"[EMOJI] '{song.name}' has emoji {emoji} but is in '{metadata.sheet_tab.name}' tab")
                    updated_count += 1
            except SongMetadata.DoesNotExist:
                # Create new metadata
                metadata = SongMetadata.objects.create(song=song, sheet_tab=tab)
                print(f"[EMOJI] Created new metadata for '{song.name}' in '{tab.name}'")
                updated_count += 1
    
    print(f"Found {updated_count} songs with emoji inconsistencies")

def reconcile_tabs():
    """Do a full reconciliation of tabs based on priority rules"""
    print("Reconciling all tab assignments...")
    
    # Get all tabs
    released_tab = SheetTab.objects.get(name="Released")
    unreleased_tab = SheetTab.objects.get(name="Unreleased")
    
    # Define emoji to tab mapping
    emoji_tabs = {
        "🏆": SheetTab.objects.get(name="🏆 Grails"),
        "🥇": SheetTab.objects.get(name="🥇 Wanted"),
        "⭐": SheetTab.objects.get(name="⭐ Best Of"),
        "✨": SheetTab.objects.get(name="✨ Special"),
        "🗑️": SheetTab.objects.get(name="🗑️ Worst Of"),
        "🗑": SheetTab.objects.get(name="🗑️ Worst Of"),
        "🤖": SheetTab.objects.get(name="🤖 AI Tracks")
    }
    
    # Types that should be in Released tab
    released_types = ["Single", "Feature", "Album Track", "Lost"]
    
    # Types that should be in Unreleased tab
    unreleased_types = ["Remix", "Unknown", "OG", "Throwaway", "High Bitrate Rip", 
                        "Demo", "Alt Mix", "OG File", "Ref Track"]
                        
    # Special keywords to tab mapping
    keyword_tabs = {
        "OG Files": SheetTab.objects.get(name="OG Files"),
        "Stems": SheetTab.objects.get(name="Stems"),
        "Fakes": SheetTab.objects.get(name="Fakes"),
        "Art": SheetTab.objects.get(name="Art"),
        "Social Media": SheetTab.objects.get(name="Social Media"),
        "Tracklists": SheetTab.objects.get(name="Tracklists"),
        "Buys": SheetTab.objects.get(name="Buys")
    }
    
    updated_count = 0
    
    # Process all songs
    for song in CartiCatalog.objects.all():
        # Determine correct tab
        correct_tab = None
        reason = ""
        
        # PRIORITY 1: Songs with proper types should go to Released
        if song.type in released_types:
            correct_tab = released_tab
            reason = f"Type '{song.type}' belongs in Released"
        
        # Special cases for specific eras
        elif song.type == "Lost" and song.era == "THC: The High Chronicals":
            correct_tab = released_tab
            reason = "Lost songs in THC era go to Released"
        elif song.type == "Mixtape" and song.era == "Young Mi$fit":
            correct_tab = released_tab
            reason = "Mixtape songs in Young Mi$fit era go to Released"
        
        # PRIORITY 1.5: Songs with Streaming category should go to Released
        elif song.notes and "Streaming" in song.notes:
            correct_tab = released_tab
            reason = "Song has Streaming category"
            
            # Apply this correction immediately if needed
            try:
                metadata = SongMetadata.objects.get(song=song)
                if metadata.sheet_tab != released_tab:
                    old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
                    metadata.sheet_tab = released_tab
                    metadata.save()
                    print(f"[FIX] Moved '{song.name}' from '{old_tab}' to 'Released' (Streaming category)")
                    updated_count += 1
            except SongMetadata.DoesNotExist:
                # Create new metadata
                metadata = SongMetadata.objects.create(song=song, sheet_tab=released_tab)
                print(f"[FIX] Created metadata for '{song.name}' in 'Released' (Streaming category)")
                updated_count += 1
            
        # PRIORITY 2: Songs with unreleased types should NOT be in Released
        # UNLESS they have the Streaming category
        elif song.type in unreleased_types and not (song.notes and "Streaming" in song.notes):
            # Check if currently in Released
            try:
                metadata = SongMetadata.objects.get(song=song)
                if metadata.sheet_tab == released_tab:
                    # This is wrong, should move to Unreleased
                    metadata.sheet_tab = unreleased_tab
                    metadata.save()
                    print(f"[FIX] Moved '{song.name}' from Released to Unreleased (Type: {song.type})")
                    updated_count += 1
            except SongMetadata.DoesNotExist:
                pass
                
        # PRIORITY 3: Emoji-based categorization
        # These should be in BOTH the emoji tab AND potentially Released
        for emoji, tab in emoji_tabs.items():
            if emoji in song.name:
                # This song should be in this tab
                try:
                    metadata = SongMetadata.objects.get(song=song)
                    current_tab = metadata.sheet_tab
                    
                    # Special case: if it's in Released and should be, leave it there
                    if current_tab == released_tab and (
                        song.type in released_types or 
                        (song.notes and "Streaming" in song.notes)
                    ):
                        # This is correct - it should be in Released due to type or Streaming
                        # Potentially duplicate to emoji tab later
                        pass
                    elif current_tab != tab:
                        # This is in the wrong tab
                        metadata.sheet_tab = tab
                        metadata.save()
                        print(f"[FIX] Moved '{song.name}' from '{current_tab.name}' to '{tab.name}' (Emoji: {emoji})")
                        updated_count += 1
                except SongMetadata.DoesNotExist:
                    # Create new with emoji tab
                    metadata = SongMetadata.objects.create(song=song, sheet_tab=tab)
                    print(f"[FIX] Created metadata for '{song.name}' in '{tab.name}' (Emoji: {emoji})")
                    updated_count += 1
                break  # Only use the first emoji found
    
    print(f"Updated {updated_count} song tab assignments")

def check_status():
    """Check current tab assignments"""
    print("\n===== CURRENT TAB ASSIGNMENTS =====")
    
    # Count by tab
    tabs = SheetTab.objects.all().order_by('name')
    for tab in tabs:
        count = SongMetadata.objects.filter(sheet_tab=tab).count()
        print(f"  {tab.name}: {count} songs")
    
    # Check for songs without tab assignments
    total_songs = CartiCatalog.objects.count()
    songs_with_tabs = SongMetadata.objects.filter(sheet_tab__isnull=False).count()
    unassigned = total_songs - songs_with_tabs
    
    print(f"\nTotal songs: {total_songs}")
    print(f"Assigned songs: {songs_with_tabs}")
    print(f"Unassigned songs: {unassigned}")
    
    # Check for type inconsistencies
    released_tab = SheetTab.objects.get(name="Released")
    unreleased_tab = SheetTab.objects.get(name="Unreleased")
    
    # Types that should be in Released tab
    released_types = ["Single", "Feature", "Album Track", "Lost"]
    
    # Types that should be in Unreleased tab
    unreleased_types = ["Remix", "Unknown", "OG", "Throwaway", "High Bitrate Rip", 
                        "Demo", "Alt Mix", "OG File", "Ref Track"]
    
    # Check for Released songs with Unreleased types
    wrong_released = CartiCatalog.objects.filter(
        type__in=unreleased_types,
        metadata__sheet_tab=released_tab
    ).count()
    
    # Check for Unreleased songs with Released types
    wrong_unreleased = CartiCatalog.objects.filter(
        type__in=released_types
    ).exclude(
        metadata__sheet_tab=released_tab
    ).count()
    
    print(f"\nIncorrect type assignments:")
    print(f"  Songs with Unreleased types in Released tab: {wrong_released}")
    print(f"  Songs with Released types not in Released tab: {wrong_unreleased}")
    
    # Check for emoji inconsistencies
    print("\nEmoji inconsistencies:")
    
    emoji_tabs = {
        "🏆": "🏆 Grails",
        "🥇": "🥇 Wanted",
        "⭐": "⭐ Best Of",
        "✨": "✨ Special",
        "🗑️": "🗑️ Worst Of", 
        "🗑": "🗑️ Worst Of",
        "🤖": "🤖 AI Tracks"
    }
    
    for emoji, tab_name in emoji_tabs.items():
        # Count songs with this emoji not in the right tab
        wrong_emoji = CartiCatalog.objects.filter(
            name__contains=emoji
        ).exclude(
            metadata__sheet_tab__name=tab_name
        ).count()
        
        if wrong_emoji > 0:
            print(f"  {emoji} ({tab_name}): {wrong_emoji} songs in wrong tabs")

def clean_unknown_era_entries(auto_confirm=False):
    """Remove entries that are just formatting dividers from Google Sheets with unknown era
    
    Args:
        auto_confirm: If True, skips confirmation prompt and deletes entries automatically
    """
    print("Cleaning up unknown era entries...")
    
    # Find songs with null or "Unknown" era
    unknown_era_songs = CartiCatalog.objects.filter(
        models.Q(era__isnull=True) | 
        models.Q(era__exact="") | 
        models.Q(era__iexact="Unknown")
    )
    
    print(f"Found {unknown_era_songs.count()} songs with unknown era")
    
    # Track which ones to delete
    to_delete = []
    
    # Check each song
    for song in unknown_era_songs:
        delete_entry = False
        
        # Check for formatting patterns like "DONDA [V3]" or "16*29 [V2]" without other data
        if song.name and (
            ("[V" in song.name) or 
            (song.name.startswith("16*29")) or
            ("DONDA" in song.name) or
            ("Total Full" in song.name) or
            ("<td class=" in song.name) or
            ("dir=\"ltr\"" in song.name) or
            ("span style=" in song.name) or
            (song.name.startswith("<"))
        ):
            delete_entry = True
        
        # Check for empty name with unknown era
        if not song.name or song.name.strip() == "":
            delete_entry = True
            
        # Add to deletion list
        if delete_entry:
            to_delete.append(song.id)
            print(f"Marking for deletion: ID:{song.id} - '{song.name}'")
    
    # Delete or confirm deletion
    if to_delete:
        print(f"\nFound {len(to_delete)} entries to delete.")
        
        if auto_confirm:
            # Auto-confirm and delete without prompting
            CartiCatalog.objects.filter(id__in=to_delete).delete()
            print(f"Deleted {len(to_delete)} entries automatically.")
        else:
            # Ask for confirmation
            try:
                confirm = input(f"Delete these {len(to_delete)} entries? (y/n): ")
                
                if confirm.lower() == 'y':
                    # Delete the entries
                    CartiCatalog.objects.filter(id__in=to_delete).delete()
                    print(f"Deleted {len(to_delete)} entries.")
                else:
                    print("Deletion cancelled.")
            except (EOFError, KeyboardInterrupt):
                # Handle EOF or interrupt
                print("\nInteractive confirmation not available. Use --auto-confirm option.")
    else:
        print("No entries found to delete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix tab assignments in the database')
    parser.add_argument('--released', action='store_true', help='Fix Released/Unreleased tab assignments based on types')
    parser.add_argument('--streaming', action='store_true', help='Move all songs with Streaming category to Released tab')
    parser.add_argument('--emoji', action='store_true', help='Fix emoji-based tab assignments')
    parser.add_argument('--reconcile', action='store_true', help='Reconcile all tab assignments based on priority rules')
    parser.add_argument('--misc', action='store_true', help='Fix Misc tab assignments and clear Art tab')
    parser.add_argument('--check', action='store_true', help='Check current tab assignments')
    parser.add_argument('--clean-unknown', action='store_true', help='Clean up unknown era entries that are formatting dividers')
    parser.add_argument('--auto-confirm', action='store_true', help='Auto-confirm deletion of entries without prompting')
    parser.add_argument('--fix-all', action='store_true', help='Run all fixes in the recommended order')
    args = parser.parse_args()
    
    if args.fix_all:
        # Run all fixes in order of priority
        clean_unknown_era_entries(auto_confirm=True) # First clean up unknown era entries
        fix_misc_and_art_tabs()     # Then handle Misc tab assignments
        fix_streaming_songs()       # Then handle streaming songs (highest priority)
        fix_released_tabs()         # Finally handle other Released tab assignments
        check_status()
    elif args.released:
        fix_released_tabs()
    elif args.streaming:
        fix_streaming_songs()
    elif args.emoji:
        fix_emoji_tabs()
    elif args.reconcile:
        reconcile_tabs()
    elif args.misc:
        fix_misc_and_art_tabs()
    elif args.check:
        check_status()
    elif args.clean_unknown:
        clean_unknown_era_entries(auto_confirm=args.auto_confirm)
    else:
        # Default: just check status
        check_status()
        print("\nUse --released, --misc, --emoji, --reconcile, --clean-unknown, or --fix-all to fix tab assignments")