const puppeteer = require('puppeteer');
const { Blocker } = require('./Blocker');
const fs = require('fs').promises;


(async () => {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--window-size=1024,768', '--js-flags=--print-bytecode'],
        executablePath: "/path/to/instrumented-chromium",
        timeout: 120000,
        dumpio: true,
        ignoreHTTPSErrors: true,
        pipe: true
    });
    try {
        const client = new Blocker({
            adRules: ['./lists/easylist.txt'],
            trackingRules: [
                './lists/easyprivacy.txt',
                './lists/enhancedstats-addon.txt']
        })
        const main_url = process.argv[2]
        console.log(`[INFO] Visiting ${main_url}`);
        const scriptsArray = [];
        const seen = new Set();

        const page = await browser.newPage();
        await page.setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36");
        page.on('requestfinished', request => {
            try {
                const response = request.response();
                if (request.resourceType() == 'script' && response.ok() && !seen.has(`${main_url},${request.url()}`)) {
                    scriptsArray.push({ 'main_url': main_url, 'script_url': request.url()})
                    seen.add(`${main_url},${request.url()}`)
                }
            } catch (err) {
                console.error("[Error Listening Req]: " + err.message);
            }
        })

        try {
            await page.goto(main_url, { waitUntil: ['load', 'domcontentloaded', 'networkidle0'], timeout: 30000 });
            await new Promise(r => setTimeout(r, 2000));
        } catch(e) {
            console.log(e.message)
        }
        const output = scriptsArray.map(item => {
            const { matched, category } = client.check({ script_url: item.script_url, main_url: item.main_url, resource_type: 'script' })
            return {...item, label: matched}
        })

        const formattedData = output.map(item => JSON.stringify(item)).join('\n');
        await fs.writeFile(`./temp/puppeteer_links.log`, formattedData);


    } catch (e) {
        console.log(e.message)
    } finally {
        await browser.close()
    }

})()

