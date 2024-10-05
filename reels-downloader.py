import sys
import csv
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import yt_dlp  # Importing yt-dlp library

# Input arguments for channel name and URL
chanel = sys.argv[1]
url = sys.argv[2]

# Start Playwright
with sync_playwright() as p:
    # Launch Chromium browser
    browser = p.chromium.launch(headless=False)  # Not headless
    page = browser.new_page()

    # Open the Facebook URL
    page.goto(url)
    
    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")  # Wait until the network is idle

    # Close the login pop-up if it exists
    try:
        close_button = page.locator("//div[@aria-label='Close']")
        close_button.wait_for(state="visible")  # Wait for the close button to be visible
        close_button.click()
    except:
        print("No pop-up found.")
    
    # Scroll to the bottom multiple times
    scroll_steps = 100  # Adjust as needed
    for _ in range(scroll_steps):
        # Scroll down
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Wait for new content to load
        page.wait_for_load_state("networkidle")  # Wait until the network is idle

        # Check if new content has loaded
        current_reels_count = len(page.query_selector_all('a[href*="/reel/"]'))

        # Wait for some time to ensure new content is loaded
        page.wait_for_timeout(2000)  # Adjust this timeout as needed

        # After waiting, check the count of reels again
        new_reels_count = len(page.query_selector_all('a[href*="/reel/"]'))

        # If the count hasn't changed, break the loop
        if new_reels_count == current_reels_count:
            print("Reached the bottom of the page or no new content loaded.")
            break

    # Extract all anchor (a) elements that contain "/reel/" in the href attribute
    a_elements = page.query_selector_all('a[href*="/reel/"]')

    # Create a channel output directory (Cross-platform path handling)
    output_dir = Path(f"output/{chanel}")
    output_dir.mkdir(parents=True, exist_ok=True)  # Cross-platform mkdir
    
    # Write the extracted URLs to a CSV file
    csv_file = output_dir / f"{chanel}.csv"
    with open(csv_file, "w") as f:
        writer = csv.writer(f)
        for element in a_elements:
            href = element.get_attribute('href')
            if href:
                writer.writerow([href.split('/?s=')[0]])  # Write URL to CSV

    # Close the browser
    browser.close()

# Bulk download reels with yt-dlp (Using yt-dlp library directly)
ydl_opts = {
    'format': 'best',
    'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([str(csv_file)])
