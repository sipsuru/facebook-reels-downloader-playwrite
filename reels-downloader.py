import sys
import csv
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

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
        # Here you can track the number of reels before scrolling
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

# Bulk download reels with yt-dlp (Cross-platform subprocess call)
yt_dlp_cmd = ["yt-dlp", "-f", "best", "-a", str(csv_file), "--output", str(output_dir / "%(id)s.%(ext)s")]

# Execute yt-dlp and handle cross-platform compatibility
process = subprocess.Popen(yt_dlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
for line in iter(lambda: process.stdout.readline(), ''):
    print(line.strip())

process.wait()


# import sys
# import csv
# import subprocess
# import os
# from pathlib import Path
# from playwright.sync_api import sync_playwright
# from time import sleep

# # Input arguments for channel name and URL
# chanel = sys.argv[1]
# url = sys.argv[2]

# # Start Playwright
# with sync_playwright() as p:
#     # Launch Chromium browser
#     browser = p.chromium.launch(headless=False)  # Not headless
#     page = browser.new_page()

#     # Open the Facebook URL
#     page.goto(url)
    
#     # Wait for the page to load
#     sleep(5)
    
#     # Close the login pop-up if it exists
#     try:
#         page.locator("//div[@aria-label='Close']").click()
#     except:
#         print("No pop-up found.")
    
#     # Scroll to the bottom multiple times
#     scroll_steps = 100  # Adjust as needed
#     scroll_interval = 4  # Adjust as needed
    
#     for _ in range(scroll_steps):
#         # Scroll down
#         page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
#         # Wait for new content to load
#         sleep(scroll_interval)
        
#         # Check if you reached the bottom
#         prev_scroll_position = page.evaluate("window.pageYOffset")
#         curr_scroll_position = page.evaluate("window.pageYOffset")
        
#         if prev_scroll_position == curr_scroll_position:
#             print("Reached the bottom of the page.")
#             break
    
#     # Extract all anchor (a) elements that contain "/reel/" in the href attribute
#     a_elements = page.query_selector_all('a')
    
#     # Create a channel output directory (Cross-platform path handling)
#     output_dir = Path(f"output/{chanel}")
#     output_dir.mkdir(parents=True, exist_ok=True)  # Cross-platform mkdir
    
#     # Write the extracted URLs to a CSV file
#     csv_file = output_dir / f"{chanel}.csv"
#     with open(csv_file, "w") as f:
#         writer = csv.writer(f)
#         for element in a_elements:
#             href = element.get_attribute('href')
#             if href and '/reel/' in href:
#                 writer.writerow([href.split('/?s=')[0]])  # Write URL to CSV
    
#     f.close()
    
#     # Close the browser
#     browser.close()

# # Bulk download reels with yt-dlp (Cross-platform subprocess call)
# yt_dlp_cmd = ["yt-dlp", "-f", "best", "-a", str(csv_file), "--output", str(output_dir / "%(id)s.%(ext)s")]

# # Execute yt-dlp and handle cross-platform compatibility
# process = subprocess.Popen(yt_dlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
# for line in iter(lambda: process.stdout.readline(), ''):
#     print(line.strip())

# process.wait()
