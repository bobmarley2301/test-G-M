const puppeteer = require('puppeteer');
const fs = require('fs');
const axios = require('axios');

async function loginToFacebook(page, email, password) {
    try {
        await page.goto('https://www.facebook.com/', { waitUntil: 'networkidle2' });
        console.log('Navigated to Facebook login page.');

        // Введення email та пароля
        await page.type('#email', email, { delay: 50 });
        await page.type('#pass', password, { delay: 50 });

        await new Promise([
            page.click('button[name="login"]'),
            page.waitForNavigation({ waitUntil: 'networkidle2' }),
        ]);
        console.log('Successfully logged in.');
    } catch (error) {
        console.error('Error during login:', error);
        throw error;
    }
}

async function getProfilePicture(page) {
    try {
        
        await page.goto('https://www.facebook.com/me', { waitUntil: 'networkidle2' });
        console.log('Navigated to profile page.');

        const profilePicUrl = await page.$eval(
            'image, img',
            (img) => img.getAttribute('xlink:href') || img.src
        );

        console.log(`Profile picture URL: ${profilePicUrl}`);
        return profilePicUrl;
    } catch (error) {
        console.error('Error while fetching profile picture:', error);
        return null;
    }
}

async function downloadPicture(url, savePath) {
    try {
        const response = await axios({
            method: 'get',
            url: url,
            responseType: 'stream',
        });

        const writer = fs.createWriteStream(savePath);
        response.data.pipe(writer);

        return new Promise((resolve, reject) => {
            writer.on('finish', () => {
                console.log(`Picture downloaded successfully and saved to ${savePath}`);
                resolve();
            });
            writer.on('error', reject);
        });
    } catch (error) {
        console.error('Error while downloading picture:', error);
    }
}

(async () => {
    const email = 'aremcudmitro240@gmail.com';
    const password = 'Dima1234567809';
    const savePath = 'profile_picture.jpg';

    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    try {
        await loginToFacebook(page, email, password);

        // Перевірка CAPTCHA
        if (page.url().includes('captcha')) {
            console.warn('CAPTCHA detected. Manual intervention required.');
            await browser.close();
            return;
        }

        const profilePicUrl = await getProfilePicture(page);
        if (profilePicUrl) {
            await downloadPicture(profilePicUrl, savePath);
        } else {
            console.error('Failed to fetch profile picture.');
        }
    } catch (error) {
        console.error('Error in the main process:', error);
    } finally {
        await browser.close();
    }
})();
