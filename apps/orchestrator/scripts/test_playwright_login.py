"""
Playwright 테스트 — ID/PW 로그인 후 Ambassador 페이지 캡처

로그인 흐름:
  gologin.php → 이메일/PW 입력 → submit → 메인 리다이렉트
  → /myambassador?device=mobile 이동 → 캡처
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path(__file__).parent.parent.parent.parent / "screenshots"

LOGIN_URL = "https://www.stylekorean.com/manage-account/gologin.php"
EMAIL = "stoneidev@gmail.com"
PASSWORD = "Dsji0201!@"
TARGET_URL = "https://www.stylekorean.com/myambassador?device=mobile"


async def main():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        context = await browser.new_context(viewport={"width": 430, "height": 932})
        page = await context.new_page()

        # Step 1: 로그인 페이지
        print("\n===== Step 1: 로그인 페이지 =====")
        await page.goto(LOGIN_URL, timeout=60000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(SCREENSHOTS_DIR / "step1_login_page.png"))
        print(f"  ✓ URL: {page.url}")

        # Step 2: 로그인 — visible email 필드 찾기
        print("\n===== Step 2: 로그인 =====")
        # 모든 input 확인
        await page.wait_for_timeout(1000)
        email_filled = False
        pw_filled = False

        # visible email input 찾기
        email_selectors = [
            'input[name="email"]:visible',
            'input[type="email"]:visible',
            'input[name="mb_id"]:visible',
            'input[placeholder*="Email"]:visible',
            'input[placeholder*="email"]:visible',
        ]
        for sel in email_selectors:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await loc.fill(EMAIL)
                email_filled = True
                print(f"  ✓ 이메일 입력 (selector: {sel})")
                break

        if not email_filled:
            # JavaScript로 직접 입력
            await page.evaluate(f'''
                const inputs = document.querySelectorAll('input');
                for (const input of inputs) {{
                    if (input.type === 'email' || input.name === 'email' || input.name === 'mb_id') {{
                        input.value = "{EMAIL}";
                        input.dispatchEvent(new Event('input', {{bubbles: true}}));
                    }}
                }}
            ''')
            print("  ✓ 이메일 입력 (JS inject)")

        pw_selectors = [
            'input[type="password"]:visible',
            'input[name="mb_password"]:visible',
            'input[name="password"]:visible',
        ]
        for sel in pw_selectors:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await loc.fill(PASSWORD)
                pw_filled = True
                print(f"  ✓ 비밀번호 입력 (selector: {sel})")
                break

        if not pw_filled:
            await page.evaluate(f'''
                const inputs = document.querySelectorAll('input[type="password"]');
                for (const input of inputs) {{
                    input.value = "{PASSWORD}";
                    input.dispatchEvent(new Event('input', {{bubbles: true}}));
                }}
            ''')
            print("  ✓ 비밀번호 입력 (JS inject)")

        await page.screenshot(path=str(SCREENSHOTS_DIR / "step2_form_filled.png"))

        # Submit
        submitted = False
        submit_selectors = [
            'button[type="submit"]:visible',
            'input[type="submit"]:visible',
            'button:has-text("Sign in"):visible',
            'button:has-text("sign in"):visible',
            'button:has-text("Log in"):visible',
            'button:has-text("LOGIN"):visible',
        ]
        for sel in submit_selectors:
            loc = page.locator(sel).first
            if await loc.count() > 0:
                await loc.click()
                submitted = True
                print(f"  ✓ 로그인 버튼 클릭 ({sel})")
                break

        if not submitted:
            await page.keyboard.press("Enter")
            print("  ✓ Enter키로 submit")

        # 로그인 완료 대기
        await page.wait_for_timeout(5000)
        print(f"  ✓ 로그인 후 URL: {page.url}")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "step2_after_login.png"))

        # Step 3: Ambassador 페이지
        print("\n===== Step 3: Ambassador 페이지 =====")
        await page.goto(TARGET_URL, timeout=60000)
        await page.wait_for_timeout(5000)
        await page.screenshot(path=str(SCREENSHOTS_DIR / "step3_ambassador.png"), full_page=True)
        print(f"  ✓ URL: {page.url}")
        print(f"  ✓ Title: {await page.title()}")

        # Step 4: 분석
        print("\n===== Step 4: 페이지 분석 =====")
        headings = await page.locator("h1, h2, h3, h4").all_text_contents()
        print(f"  Headings: {[h.strip() for h in headings if h.strip()][:10]}")

        buttons = await page.locator("button, [class*='btn']").all_text_contents()
        print(f"  Buttons: {[b.strip() for b in buttons if b.strip()][:10]}")

        imgs = await page.locator("img[src]").count()
        print(f"  Images: {imgs}")

        # Full page
        await page.screenshot(path=str(SCREENSHOTS_DIR / "step4_full.png"), full_page=True)

        print(f"\n===== 완료! =====")
        for f in sorted(SCREENSHOTS_DIR.glob("*.png")):
            print(f"  {f.name} ({f.stat().st_size // 1024}KB)")

        await page.wait_for_timeout(2000)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
