import time
import syncedlyrics

# Sample songs list (Artist - Title)
SONGS_TO_TEST = [
    "Daft Punk One More Time",
    "Queen Bohemian Rhapsody",
    "Coldplay Viva La Vida",
    "Taylor Swift Anti-Hero",
    "Imagine Dragons Believer",
    "Mr Bruce I am disaster"
]

def fetch_synced_lyrics_with_timing(songs):
    print("=== Synced Lyrics Benchmark & PoC ===\n")
    
    total_start_time = time.perf_counter()
    results = []

    for index, song in enumerate(songs, start=1):
        print(f"[{index}/{len(songs)}] Searching for: '{song}'...")
        
        # 1. Start individual song timer
        song_start_time = time.perf_counter()
        
        # 2. Query syncedlyrics (plain_only=True forces LRC format without timestamps)
        lrc_data = syncedlyrics.search(song, plain_only=True)
        
        # 3. Stop individual song timer
        elapsed_time = time.perf_counter() - song_start_time
        
        success = lrc_data is not None
        
        # Store metadata and results
        results.append({
            "song": song,
            "success": success,
            "time_seconds": round(elapsed_time, 2),
            "lrc_data": lrc_data
        })

        if success:
            # Extract the first line of lyrics to show a snippet
            first_line = lrc_data.strip().split('\n')[0] if lrc_data else ""
            print(f"  ✓ Found in {elapsed_time:.2f}s | Preview: {first_line}")
        else:
            print(f"  ✗ Not found ({elapsed_time:.2f}s)")
            
        print("-" * 50)

    # Calculate total batch time
    total_elapsed_time = time.perf_counter() - total_start_time
    
    # Summary report
    print("\n=== BENCHMARK SUMMARY ===")
    print(f"Total Songs Processed : {len(songs)}")
    print(f"Total Time Taken      : {total_elapsed_time:.2f} seconds")
    print(f"Average Time per Song : {total_elapsed_time / len(songs):.2f} seconds")
    
    return results

if __name__ == "__main__":
    fetch_synced_lyrics_with_timing(SONGS_TO_TEST)