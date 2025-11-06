# 🛡️ Advanced Anti-Bot Bypass Roadmap

## Current Status: 7/10

Sistem enterprise-grade mimari ve reliability açısından **10/10**, ancak en güçlü anti-bot sistemlerini aşmak için ek teknikler gerekli.

## Phase 1: CAPTCHA Solving ⚠️ HIGH PRIORITY

### Implementation
```python
# src/infrastructure/captcha/solver.py

class CaptchaSolver:
    """CAPTCHA solving service integration."""

    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> str:
        """Solve reCAPTCHA v2 using 2Captcha/Anti-Captcha."""
        pass

    async def solve_recaptcha_v3(self, site_key: str, page_url: str, action: str) -> str:
        """Solve reCAPTCHA v3."""
        pass

    async def solve_hcaptcha(self, site_key: str, page_url: str) -> str:
        """Solve hCaptcha."""
        pass

    async def solve_cloudflare_turnstile(self, site_key: str, page_url: str) -> str:
        """Solve Cloudflare Turnstile."""
        pass
```

### Required Services
- **2Captcha**: https://2captcha.com/ (1000 captchas = $1-3)
- **Anti-Captcha**: https://anti-captcha.com/
- **CapSolver**: https://www.capsolver.com/
- **CapMonster**: https://capmonster.cloud/

### Cost Estimate
- ~$0.001-0.003 per CAPTCHA
- For 1000 bookings/day: $1-3/day = $30-90/month

## Phase 2: Advanced Fingerprinting Bypass

### 1. Canvas Fingerprinting
```python
# Playwright injection
await page.add_init_script("""
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {
        // Add noise to canvas data
        const context = this.getContext('2d');
        const imageData = context.getImageData(0, 0, this.width, this.height);
        for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] += Math.floor(Math.random() * 10) - 5;
        }
        context.putImageData(imageData, 0, 0);
        return originalToDataURL.apply(this, arguments);
    };
""")
```

### 2. WebGL Fingerprinting
```python
await page.add_init_script("""
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
            return 'Intel Inc.';
        }
        if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.apply(this, arguments);
    };
""")
```

### 3. Audio Context Fingerprinting
```python
await page.add_init_script("""
    const audioContext = AudioContext.prototype.createOscillator;
    AudioContext.prototype.createOscillator = function() {
        const oscillator = audioContext.apply(this, arguments);
        const originalStart = oscillator.start;
        oscillator.start = function() {
            // Add random variation
            this.frequency.value += Math.random() * 0.001;
            return originalStart.apply(this, arguments);
        };
        return oscillator;
    };
""")
```

## Phase 3: Behavioral Simulation

### Human-like Mouse Movements
```python
# src/core/utils/human_simulation.py

import numpy as np
from typing import Tuple, List

class HumanSimulator:
    """Simulate human-like behavior."""

    async def move_mouse_humanlike(
        self,
        page,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int]
    ):
        """Move mouse in natural bezier curve."""
        points = self._generate_bezier_curve(from_pos, to_pos)
        for x, y in points:
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.001, 0.005))

    def _generate_bezier_curve(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Generate bezier curve points."""
        # Add control points with randomness
        control1 = (
            start[0] + random.randint(-100, 100),
            start[1] + random.randint(-100, 100)
        )
        control2 = (
            end[0] + random.randint(-100, 100),
            end[1] + random.randint(-100, 100)
        )

        # Generate curve points
        points = []
        steps = random.randint(50, 100)
        for i in range(steps):
            t = i / steps
            x, y = self._bezier_point(t, start, control1, control2, end)
            points.append((int(x), int(y)))

        return points

    async def type_humanlike(self, page, selector: str, text: str):
        """Type with human-like speed and errors."""
        element = await page.query_selector(selector)
        await element.click()

        for char in text:
            # Random typing speed: 80-200ms per character
            delay = random.uniform(80, 200)

            # 2% chance of typo
            if random.random() < 0.02:
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await element.type(wrong_char, delay=delay)
                await asyncio.sleep(random.uniform(100, 300))
                await page.keyboard.press('Backspace')
                await asyncio.sleep(random.uniform(50, 150))

            await element.type(char, delay=delay)

    async def random_scroll(self, page):
        """Random scroll patterns."""
        # Scroll down in chunks
        viewport_height = await page.evaluate('window.innerHeight')
        scroll_amount = random.randint(100, viewport_height // 2)

        for _ in range(random.randint(2, 5)):
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            await asyncio.sleep(random.uniform(0.5, 2.0))

        # Sometimes scroll back up
        if random.random() < 0.3:
            await page.evaluate(f'window.scrollBy(0, -{scroll_amount // 2})')
            await asyncio.sleep(random.uniform(0.5, 1.5))
```

## Phase 4: Residential Proxy Integration

### Recommended Providers
1. **Bright Data** (formerly Luminati) - Premium, expensive
2. **Smartproxy** - Good balance of price/quality
3. **Oxylabs** - High quality
4. **NetNut** - ISP proxies
5. **SOAX** - Residential + mobile

### Implementation
```python
# src/infrastructure/proxy/residential_proxy_manager.py

class ResidentialProxyManager:
    """Manage residential proxy rotation."""

    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        self.proxies = []

    async def get_proxy(self, country: str = None, city: str = None) -> str:
        """Get residential proxy with geo-targeting."""
        if self.provider == "brightdata":
            return self._get_brightdata_proxy(country, city)
        elif self.provider == "smartproxy":
            return self._get_smartproxy_proxy(country, city)

    def _get_brightdata_proxy(self, country: str, city: str) -> str:
        """
        Format: http://username-country-{country}:password@proxy.brightdata.com:port
        """
        username = f"{self.api_key}-country-{country or 'us'}"
        return f"http://{username}:password@brd.superproxy.io:22225"
```

### Cost Estimate
- **Residential Proxies**: $5-15 per GB
- **ISP Proxies**: $3-8 per IP/month
- Typical usage: 10-50GB/month = $50-750/month

## Phase 5: TLS Fingerprinting Bypass

### JA3 Fingerprint Spoofing
```python
# Use curl_cffi or httpx with custom TLS config

from curl_cffi import requests as curl_requests

class StealthHTTPClient:
    """HTTP client with TLS fingerprint spoofing."""

    async def get(self, url: str, **kwargs):
        """Make request with Chrome TLS fingerprint."""
        return curl_requests.get(
            url,
            impersonate="chrome110",  # Mimic Chrome 110 TLS
            **kwargs
        )
```

### Dependencies
```bash
pip install curl_cffi
pip install pycurl
```

## Phase 6: Playwright Undetected Mode

### Enhanced Stealth Configuration
```python
# src/infrastructure/browser/stealth_browser.py

class StealthBrowser:
    """Ultra-stealthy browser configuration."""

    async def launch_stealth_browser(self):
        """Launch browser with all anti-detection measures."""
        browser = await self.playwright.chromium.launch(
            headless=False,  # Headless is more detectable
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-blink-features',
                '--disable-automation',
                '--disable-infobars',
                '--window-size=1920,1080',
                '--start-maximized',
                # Spoof WebRTC
                '--enable-webrtc-hide-local-ips-with-mdns',
                # Hardware acceleration
                '--enable-accelerated-2d-canvas',
                '--enable-gpu-rasterization',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self._get_random_user_agent(),
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation'],
            color_scheme='light',
            device_scale_factor=1,
        )

        # Inject all stealth scripts
        await self._inject_stealth_scripts(context)

        return context

    async def _inject_stealth_scripts(self, context):
        """Inject comprehensive stealth scripts."""
        # Remove webdriver flag
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Chrome runtime
        await context.add_init_script("""
            window.chrome = {
                runtime: {}
            };
        """)

        # Permissions
        await context.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        # Plugin array
        await context.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        # Languages
        await context.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
```

## Phase 7: ML-Based Detection Evasion

### Behavioral Analytics Bypass
```python
class BehavioralAnalyticsEvader:
    """Evade ML-based behavioral analysis."""

    async def simulate_human_session(self, page):
        """Full human session simulation."""
        # 1. Natural page loading wait
        await asyncio.sleep(random.uniform(1.5, 3.5))

        # 2. Random page interactions
        await self._random_page_interactions(page)

        # 3. Mouse movements
        await self._simulate_mouse_movements(page)

        # 4. Reading time simulation
        await self._simulate_reading_time(page)

        # 5. Natural navigation
        await self._simulate_natural_navigation(page)

    async def _random_page_interactions(self, page):
        """Random clicks, hovers, scrolls."""
        actions = [
            self._random_hover,
            self._random_scroll,
            self._random_click,
        ]

        for _ in range(random.randint(3, 7)):
            action = random.choice(actions)
            await action(page)
            await asyncio.sleep(random.uniform(0.5, 2.0))
```

## Implementation Priority

### Must Have (High Priority)
1. ✅ **CAPTCHA Solving** - Blocker for most sites
2. ✅ **Residential Proxies** - Essential for high-volume
3. ✅ **Behavioral Simulation** - Defeats ML detection

### Should Have (Medium Priority)
4. ⚠️ **Advanced Fingerprinting Bypass** - For sophisticated sites
5. ⚠️ **TLS Fingerprinting** - For CDN protection

### Nice to Have (Low Priority)
6. 📋 **ML Evasion** - For cutting-edge detection

## Cost Analysis

### Monthly Costs for Production
- **CAPTCHA Solving**: $30-100/month (1000-3000 captchas)
- **Residential Proxies**: $50-500/month (depending on volume)
- **Total**: $80-600/month for advanced bypass

### ROI Calculation
If booking success rate increases from 70% → 95%:
- 25% more successful bookings
- Reduced retry costs
- Better client satisfaction

## Ethical & Legal Considerations

⚠️ **Important**:
- These techniques are for **authorized penetration testing** or **legitimate automation with site permission**
- Bypassing anti-bot measures without permission may violate Terms of Service
- Some jurisdictions have laws against unauthorized access (CFAA in US, etc.)
- Always get written permission before deployment

## Next Steps

To implement these:

```bash
# 1. Choose CAPTCHA service and get API key
# 2. Select residential proxy provider
# 3. Implement Phase 1 (CAPTCHA)
# 4. Add behavioral simulation
# 5. Test and iterate
```

Would you like me to implement any of these phases?
