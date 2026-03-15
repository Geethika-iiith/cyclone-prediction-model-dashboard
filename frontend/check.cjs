const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR:', err.message));
    try {
        await page.goto('http://localhost:5173', {waitUntil: 'networkidle2'});
        await page.waitForTimeout(2000);
        console.log("Page loaded.");
        const html = await page.content();
        if (html.includes('Acquiring Meteorological Data')) {
            console.log("Stuck on loading state.");
        } else if (html.includes('Next-Generation Disaster')) {
            console.log("On welcome screen. Selecting city Mumbai...");
            await page.select('select', 'Mumbai');
            await page.waitForTimeout(3000);
            const mHtml = await page.content();
            if (mHtml.includes('Projected Precipitation')) {
                 console.log("Successfully loaded dashboard!");
            } else {
                 console.log("Failed to load dashboard after selecting city.");
            }
        } else {
             console.log("Unknown state.");
        }
    } catch (e) {
        console.log("Puppeteer Error:", e.message);
    }
    await browser.close();
})();
