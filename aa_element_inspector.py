#!/usr/bin/env python3
"""
AA.com Element Inspector
Simple script to inspect what elements are actually on the AA.com page
This will help us create more accurate selectors for clicking and form filling
"""

import asyncio
from playwright.async_api import async_playwright

async def inspect_aa_elements():
    """
    Inspect all elements on the AA.com homepage to understand the structure
    """
    print("🔍 AA.com Element Inspector")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Keep visible so you can see the page
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        try:
            print("🌐 Loading AA.com homepage...")
            await page.goto("https://www.aa.com/homePage.do", wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            print("✅ Homepage loaded!")
            
            print("\n📊 INSPECTING FORM ELEMENTS:")
            print("-" * 40)
            
            # Inspect all input elements
            inputs = await page.query_selector_all('input')
            print(f"Found {len(inputs)} input elements:")
            
            for i, input_elem in enumerate(inputs):
                try:
                    input_type = await input_elem.get_attribute('type') or 'text'
                    input_name = await input_elem.get_attribute('name') or 'no-name'
                    input_id = await input_elem.get_attribute('id') or 'no-id'
                    input_placeholder = await input_elem.get_attribute('placeholder') or 'no-placeholder'
                    input_class = await input_elem.get_attribute('class') or 'no-class'
                    input_value = await input_elem.get_attribute('value') or 'no-value'
                    
                    print(f"  {i+1:2d}. Type: {input_type:10} | Name: {input_name:15} | ID: {input_id:15} | Placeholder: {input_placeholder:20} | Class: {input_class:30}")
                    
                    # Highlight this element on the page
                    await input_elem.evaluate("element => element.style.border = '3px solid red'")
                    
                except Exception as e:
                    print(f"  {i+1:2d}. Error inspecting input: {str(e)}")
            
            print(f"\n📊 INSPECTING BUTTON ELEMENTS:")
            print("-" * 40)
            
            # Inspect all button elements
            buttons = await page.query_selector_all('button')
            print(f"Found {len(buttons)} button elements:")
            
            for i, button in enumerate(buttons):
                try:
                    button_text = await button.inner_text() or 'no-text'
                    button_type = await button.get_attribute('type') or 'button'
                    button_class = await button.get_attribute('class') or 'no-class'
                    button_id = await button.get_attribute('id') or 'no-id'
                    
                    print(f"  {i+1:2d}. Text: {button_text:20} | Type: {button_type:10} | Class: {button_class:30} | ID: {button_id:15}")
                    
                    # Highlight this element on the page
                    await button.evaluate("element => element.style.border = '3px solid blue'")
                    
                except Exception as e:
                    print(f"  {i+1:2d}. Error inspecting button: {str(e)}")
            
            print(f"\n📊 INSPECTING RADIO BUTTONS:")
            print("-" * 40)
            
            # Inspect all radio buttons
            radios = await page.query_selector_all('input[type="radio"]')
            print(f"Found {len(radios)} radio button elements:")
            
            for i, radio in enumerate(radios):
                try:
                    radio_value = await radio.get_attribute('value') or 'no-value'
                    radio_name = await radio.get_attribute('name') or 'no-name'
                    radio_id = await radio.get_attribute('id') or 'no-id'
                    radio_class = await radio.get_attribute('class') or 'no-class'
                    
                    print(f"  {i+1:2d}. Value: {radio_value:15} | Name: {radio_name:15} | ID: {radio_id:15} | Class: {radio_class:30}")
                    
                    # Highlight this element on the page
                    await radio.evaluate("element => element.style.border = '3px solid green'")
                    
                except Exception as e:
                    print(f"  {i+1:2d}. Error inspecting radio: {str(e)}")
            
            print(f"\n📊 INSPECTING CHECKBOXES:")
            print("-" * 40)
            
            # Inspect all checkboxes
            checkboxes = await page.query_selector_all('input[type="checkbox"]')
            print(f"Found {len(checkboxes)} checkbox elements:")
            
            for i, checkbox in enumerate(checkboxes):
                try:
                    checkbox_name = await checkbox.get_attribute('name') or 'no-name'
                    checkbox_id = await checkbox.get_attribute('id') or 'no-id'
                    checkbox_class = await checkbox.get_attribute('class') or 'no-class'
                    checkbox_value = await checkbox.get_attribute('value') or 'no-value'
                    
                    print(f"  {i+1:2d}. Name: {checkbox_name:15} | ID: {checkbox_id:15} | Class: {checkbox_class:30} | Value: {checkbox_value:15}")
                    
                    # Highlight this element on the page
                    await checkbox.evaluate("element => element.style.border = '3px solid orange'")
                    
                except Exception as e:
                    print(f"  {i+1:2d}. Error inspecting checkbox: {str(e)}")
            
            print(f"\n📊 INSPECTING SELECT ELEMENTS:")
            print("-" * 40)
            
            # Inspect all select elements
            selects = await page.query_selector_all('select')
            print(f"Found {len(selects)} select elements:")
            
            for i, select in enumerate(selects):
                try:
                    select_name = await select.get_attribute('name') or 'no-name'
                    select_id = await select.get_attribute('id') or 'no-id'
                    select_class = await select.get_attribute('class') or 'no-class'
                    
                    print(f"  {i+1:2d}. Name: {select_name:15} | ID: {select_id:15} | Class: {select_class:30}")
                    
                    # Highlight this element on the page
                    await select.evaluate("element => element.style.border = '3px solid purple'")
                    
                except Exception as e:
                    print(f"  {i+1:2d}. Error inspecting select: {str(e)}")
            
            print(f"\n🎯 RECOMMENDED SELECTORS:")
            print("-" * 40)
            print("Based on the inspection above, here are recommended selectors:")
            print()
            print("For One-Way Trip Selection:")
            print("  - Look for radio buttons with value containing 'one' or 'oneway'")
            print("  - Try: input[type='radio'][value*='one']")
            print()
            print("For Origin Airport:")
            print("  - Look for input with placeholder 'From' or name containing 'origin'")
            print("  - Try: input[placeholder*='From'] or input[name*='origin']")
            print()
            print("For Destination Airport:")
            print("  - Look for input with placeholder 'To' or name containing 'destination'")
            print("  - Try: input[placeholder*='To'] or input[name*='destination']")
            print()
            print("For Departure Date:")
            print("  - Look for input with placeholder 'Depart' or name containing 'depart'")
            print("  - Try: input[placeholder*='Depart'] or input[name*='depart']")
            print()
            print("For Search Button:")
            print("  - Look for button with text 'Search' or type 'submit'")
            print("  - Try: button:has-text('Search') or button[type='submit']")
            print()
            print("For Redeem Miles Checkbox:")
            print("  - Look for checkbox with name or id containing 'miles'")
            print("  - Try: input[type='checkbox'][name*='miles']")
            
            print(f"\n⏳ Keeping browser open for 30 seconds so you can inspect the highlighted elements...")
            print("Red borders = Input fields")
            print("Blue borders = Buttons") 
            print("Green borders = Radio buttons")
            print("Orange borders = Checkboxes")
            print("Purple borders = Select dropdowns")
            
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error during inspection: {str(e)}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_aa_elements())
