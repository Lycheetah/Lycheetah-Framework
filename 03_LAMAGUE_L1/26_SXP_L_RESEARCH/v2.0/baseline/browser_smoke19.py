"""Offline Chromium verification of interactive v1.9 teaching subset."""
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).parent
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1120,'height':850},accept_downloads=True)
    errors=[]; page.on('pageerror',lambda error:errors.append(str(error)))
    page.set_content((root/'NATURAL_REFERENCE_LAB_v1.9.html').read_text(encoding='utf8'))
    assert 'soraviko' in page.locator('#native').inner_text()
    assert 'Maka' in page.locator('#english').inner_text() or 'maka' in page.locator('#english').inner_text()
    assert 'Maka misses Nara' in page.locator('#english').inner_text()
    page.locator('#current').click()
    assert 'Nara misses Maka' in page.locator('#english').inner_text()
    page.locator('#subject').select_option('ti')
    assert 'Maka misses Maka' in page.locator('#english').inner_text()
    page.locator('#subject').select_option('mi')
    page.locator('#verb').select_option('rava')
    assert 'reconnects with' in page.locator('#english').inner_text()
    page.locator('#verb').select_option('luma')
    page.locator('[data-answer="right"]').click()
    assert 'Correct.' in page.locator('#result').inner_text()
    with page.expect_download() as info: page.locator('#download').click()
    info.value.save_as(root/'examples/BROWSER_SAVED.sxp19')
    assert 'tumerako' in (root/'examples/BROWSER_SAVED.sxp19').read_text()
    page.locator('#source').click()
    page.screenshot(path=str(root/'BROWSER_QA_v1.9.png'),full_page=True)
    assert not errors,errors
    print('PASS: source/current selection, subject/verb updates, quiz, offline .sxp19 export and no browser errors')
    browser.close()
