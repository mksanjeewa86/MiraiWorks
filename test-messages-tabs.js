// Simple test to verify the messages page tab functionality
// Run this with: node test-messages-tabs.js

const { chromium } = require('playwright');

async function testMessagesTabs() {
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();
    
    try {
        console.log('Navigating to messages page...');
        await page.goto('http://localhost:3000/messages');
        
        // Wait for the page to load
        await page.waitForTimeout(2000);
        
        console.log('Taking screenshot...');
        await page.screenshot({ path: 'messages-page.png', fullPage: true });
        
        // Check if tab navigation exists
        const tabNav = await page.$('div.flex.bg-gray-100');
        console.log('Tab navigation found:', tabNav !== null);
        
        // Check for tab buttons
        const conversationsTab = await page.$('button:has-text("Conversations")');
        const contactsTab = await page.$('button:has-text("Contacts")');
        
        console.log('Conversations tab found:', conversationsTab !== null);
        console.log('Contacts tab found:', contactsTab !== null);
        
        // Check the debug text
        const activeTabText = await page.textContent('p:has-text("Active tab:")');
        console.log('Active tab debug text:', activeTabText);
        
        if (contactsTab) {
            console.log('Clicking Contacts tab...');
            await contactsTab.click();
            await page.waitForTimeout(500);
            
            const updatedActiveTabText = await page.textContent('p:has-text("Active tab:")');
            console.log('Active tab after click:', updatedActiveTabText);
        }
        
        // Get page content for debugging
        const pageContent = await page.content();
        console.log('Page contains "Tab Navigation":', pageContent.includes('Tab Navigation'));
        
        console.log('Test completed. Check messages-page.png for visual confirmation.');
        
    } catch (error) {
        console.error('Test failed:', error);
    } finally {
        await browser.close();
    }
}

testMessagesTabs();