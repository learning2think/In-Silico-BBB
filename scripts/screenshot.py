"""Automated screenshot of the running Streamlit app via Playwright.

Usage:
    streamlit run app.py --server.headless true &
    sleep 5
    python scripts/screenshot.py

Install:
    pip install playwright
    playwright install chromium
"""

from pathlib import Path

from playwright.sync_api import sync_playwright


def capture(
    url: str = "http://localhost:8501",
    output: str = "docs/screenshot.png",
    width: int = 1280,
    height: int = 800,
    wait_ms: int = 4000,
) -> None:
    """Capture a screenshot of the Streamlit app.

    Args:
        url: URL of the running Streamlit instance.
        output: Path where the PNG screenshot will be saved.
        width: Browser viewport width in pixels.
        height: Browser viewport height in pixels.
        wait_ms: Milliseconds to wait for Streamlit to fully render.
    """
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url)
        page.wait_for_timeout(wait_ms)
        page.screenshot(path=output, full_page=False)
        browser.close()
    print(f"Screenshot saved to {output}")


if __name__ == "__main__":
    capture()
