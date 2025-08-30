import asyncio
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Navigate to the local XML file
        page.goto("file:///app/jettheme-v2.xml")
        # Wait for any potential scripts to load, although it's a static file
        page.wait_for_load_state('networkidle')
        # Give it a second for any final rendering
        page.wait_for_timeout(1000)
        # Take a screenshot
        page.screenshot(path="jules-scratch/verification/bootstrap-update.png")
        browser.close()

if __name__ == "__main__":
    run()
