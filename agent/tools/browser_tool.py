"""Browser tool: fetch URL text via Playwright (headless chromium)."""
import asyncio
from playwright.async_api import async_playwright

async def _fetch(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=30000)
        text = await page.inner_text("body")
        await browser.close()
        return text[:8000]

def fetch_page(url: str) -> str:
    """Synchronous wrapper around async fetch."""
    try:
        return asyncio.run(_fetch(url))
    except Exception as e:
        return f"[browser_tool error] {e}"
