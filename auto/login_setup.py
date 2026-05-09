"""
One-time login setup (v2 — strict auth check).

Polls until the page shows authenticated UI (the SideNav AccountSwitcher,
which only appears after real login). URL change alone is insufficient
because /home and profile pages render anonymously too.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = Path(__file__).parent / ".chrome-profile"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
TIMEOUT_SEC = 600  # 10 min


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = await ctx.new_page()
        await page.goto("https://x.com/login")
        print("\n  ========================================")
        print("  Chrome opened at x.com/login.")
        print("  Log in COMPLETELY to @YOUR_HANDLE.")
        print("  (Email + password + 2FA if any)")
        print(f"  Auto-detect within {TIMEOUT_SEC}s")
        print("  ========================================\n")

        # Strong auth indicators — these only render when logged in
        AUTH_SELECTOR = (
            '[data-testid="SideNav_AccountSwitcher_Button"], '
            '[data-testid="AppTabBar_Profile_Link"], '
            '[data-testid="SideNav_NewTweet_Button"]'
        )

        elapsed = 0
        while elapsed < TIMEOUT_SEC:
            try:
                el = page.locator(AUTH_SELECTOR).first
                if await el.count() > 0 and await el.is_visible():
                    print(f"  ✓ Authenticated UI detected at: {page.url}")
                    break
            except Exception:
                pass
            await asyncio.sleep(2)
            elapsed += 2
        else:
            print("  ⚠ Timed out waiting for login.")
            await page.screenshot(path=str(Path(__file__).parent / "login_failed.png"))
            await ctx.close()
            return

        # Verify by visiting profile and checking for compose button
        await page.goto("https://x.com/home")
        await page.wait_for_timeout(3000)
        compose_btn = page.locator('[data-testid="SideNav_NewTweet_Button"]').first
        if await compose_btn.count() > 0 and await compose_btn.is_visible():
            print(f"  ✓ Compose button visible — fully authenticated.")
            await page.screenshot(path=str(Path(__file__).parent / "login_verified.png"))
            print(f"  Screenshot: login_verified.png")
            print(f"  ✓ Cookies persisted to {USER_DATA_DIR}\n")
        else:
            print("  ⚠ Compose button not visible — auth may be incomplete.")
            await page.screenshot(path=str(Path(__file__).parent / "login_incomplete.png"))

        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())
