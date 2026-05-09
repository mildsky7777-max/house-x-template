"""
X (Twitter) auto-publishing via Playwright.

Uses a persistent Chrome user data directory to inherit the user's logged-in X session.
No API key needed. Free.

Multi-paragraph paste uses execCommand insertText (workaround for X's ProseMirror bug
where direct typing of \\n\\n loses paragraphs).
"""
import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright, Page

USER_DATA_DIR = Path.home() / "x" / "grow" / "auto" / ".chrome-profile"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)


async def _open_browser(playwright, headless: bool = False):
    """Launch a persistent browser context (inherits X session cookies)."""
    return await playwright.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )


async def _paste_into_compose(page: Page, text: str):
    """
    Set the ProseMirror compose textbox to `text`, preserving multi-paragraph
    structure.

    X's compose uses ProseMirror with React state. execCommand("insertText")
    with embedded \\n only commits the LAST paragraph (known bug). The
    reliable approach is to type line-by-line and press Enter between
    paragraphs — this mimics a human typist and triggers the right input
    events so all paragraphs persist.
    """
    box = page.locator('div[data-testid="tweetTextarea_0"]').first
    await box.wait_for(state="visible", timeout=10000)
    await box.click()
    # Clear any existing content
    await page.keyboard.press("Meta+A")
    await page.keyboard.press("Backspace")
    await page.wait_for_timeout(150)

    # Type line by line. Empty lines become double Enter (paragraph break).
    # Splitting on a single \n preserves layout for both:
    #   "line1\n\nline2"  -> ["line1", "", "line2"]
    #   "line1\nline2"    -> ["line1", "line2"]
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line:
            # Use insertText for non-Latin / multi-byte safety (Korean, 漢字, ⸻)
            await page.evaluate(
                "(t) => document.execCommand('insertText', false, t)",
                line,
            )
        if i < len(lines) - 1:
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(40)
    await page.wait_for_timeout(600)


async def _click_post_button(page: Page, is_reply: bool = False) -> None:
    """Click Post or Reply button. Waits for it to be enabled first."""
    # In reply: button text is "Reply"; in compose modal: "Post"
    selector = '[data-testid="tweetButton"], [data-testid="tweetButtonInline"]'
    buttons = page.locator(selector)
    # Find an enabled one
    count = await buttons.count()
    for i in range(count):
        btn = buttons.nth(i)
        if await btn.is_visible() and await btn.is_enabled():
            await btn.click()
            return
    raise RuntimeError("No enabled tweet/reply button found")


async def _extract_tweet_url(page: Page, timeout_ms: int = 10000) -> str | None:
    """After publish, X navigates back. Try to grab the new tweet URL from the toast or profile."""
    # Easiest: click "View" on the toast notification
    try:
        await page.wait_for_selector('text=/Your post was sent/i', timeout=3000)
    except Exception:
        pass
    # Fall back: navigate to profile and grab top tweet
    return None  # caller can verify via profile if needed


async def publish_single(text: str, media_path: str | None = None) -> dict:
    """Publish a standalone tweet. Returns {'ok': bool, 'url': str|None, 'error': str|None}."""
    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()
        try:
            await page.goto("https://x.com/compose/post", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            # Optional media upload
            if media_path:
                file_input = page.locator('input[type="file"][accept*="video"], input[type="file"][accept*="image"]').first
                await file_input.set_input_files(media_path)
                # Wait for media processing
                await page.wait_for_timeout(5000)
            await _paste_into_compose(page, text)
            await _click_post_button(page)
            await page.wait_for_timeout(3000)
            return {"ok": True, "url": None, "error": None}
        except Exception as e:
            return {"ok": False, "url": None, "error": str(e)}
        finally:
            await ctx.close()


async def publish_reply(text: str, target_url: str) -> dict:
    """Reply to a specific tweet by URL."""
    async with async_playwright() as p:
        ctx = await _open_browser(p)
        page = await ctx.new_page()
        try:
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500)
            # Click "Post your reply" inline reply box
            reply_input = page.locator('[data-testid="tweetTextarea_0"]').first
            await reply_input.click()
            await page.wait_for_timeout(500)
            await _paste_into_compose(page, text)
            await _click_post_button(page, is_reply=True)
            await page.wait_for_timeout(3000)
            return {"ok": True, "url": None, "error": None}
        except Exception as e:
            return {"ok": False, "url": None, "error": str(e)}
        finally:
            await ctx.close()


async def publish_quote(text: str, target_url: str, media_path: str | None = None) -> dict:
    """Quote tweet: append target_url to text, X auto-embeds the quote card."""
    body = f"{text.rstrip()}\n\n{target_url}"
    return await publish_single(body, media_path=media_path)


# Sync wrappers for use from Flask
def sync_publish(draft: dict) -> dict:
    """Dispatch on draft.type: single | reply | quote."""
    t = draft.get("type", "single")
    text = draft["text"]
    media = draft.get("media_path")
    target = draft.get("target_url")

    if t == "single":
        return asyncio.run(publish_single(text, media_path=media))
    if t == "reply":
        if not target:
            return {"ok": False, "url": None, "error": "reply requires target_url"}
        return asyncio.run(publish_reply(text, target))
    if t == "quote":
        if not target:
            return {"ok": False, "url": None, "error": "quote requires target_url"}
        return asyncio.run(publish_quote(text, target, media_path=media))
    return {"ok": False, "url": None, "error": f"unknown type: {t}"}


if __name__ == "__main__":
    # Smoke test: open browser, navigate to x.com, take screenshot
    async def smoke():
        async with async_playwright() as p:
            ctx = await _open_browser(p, headless=False)
            page = await ctx.new_page()
            await page.goto("https://x.com/home")
            await page.wait_for_timeout(3000)
            await page.screenshot(path="smoke.png")
            print("Screenshot saved: smoke.png")
            print(f"URL: {page.url}")
            await ctx.close()
    asyncio.run(smoke())
