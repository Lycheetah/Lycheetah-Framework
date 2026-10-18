"""Browser smoke, explicitly synthetic responses only; never human data."""
import csv,io,sys,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from score_study import parse_csv,summarize
from build_study import ROOT,COHORTS,OPTIONS
KEY={x['id']:x for x in json.loads((ROOT/'researcher'/'ANSWER_KEY_DO_NOT_SHARE.json').read_text())}


def main():
 reports=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path="/usr/bin/chromium",args=["--no-sandbox"])
  for cohort in COHORTS:
   context=browser.new_context(accept_downloads=True)
   page=context.new_page()
   errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
   page.set_content((ROOT/'participants'/f'SXP-L_v2.0_Cohort_{cohort}.html').read_text(encoding='utf8'),wait_until='load')
   page.get_by_role('button',name='Start',exact=True).click()
   assert 'Case 1 of 32' in page.locator('#counter').inner_text()
   for index in range(32):
    case=page.evaluate('cases[idx].id')
    # Choose correct answers for A, unsure for all other cohorts: test both paths.
    answer=KEY[case]['answer'] if cohort=='A' else 'unsure'
    page.locator(f'#options input[value="{answer}"]').check()
    if index<31:page.get_by_role('button',name='Next',exact=True).click()
   with page.expect_download() as event:page.get_by_role('button',name='Export local CSV').click()
   download=event.value
   path=ROOT/'results'/f'SYNTHETIC_BROWSER_QA_COHORT_{cohort}.csv'
   download.save_as(path)
   parsed=parse_csv(path)
   results=summarize(parsed)['arms']
   assert sum(x['correct'] for x in results.values())==(32 if cohort=='A' else 0)
   assert not errs,errs
   if cohort=='A':page.screenshot(path=str(ROOT/'BROWSER_QA_v2.0.png'),full_page=True)
   reports.append({'cohort':cohort,'exports':32,'errors':errs,'correct_synthetic':sum(x['correct'] for x in results.values())})
   context.close()
  browser.close()
 print(json.dumps({'type':'SYNTHETIC_BROWER_QA_NOT_HUMAN','reports':reports},indent=2))
 (ROOT/'results'/'BROWSER_QA_REPORT.json').write_text(json.dumps({'type':'synthetic software QA only','reports':reports},indent=2)+'\n')
if __name__=='__main__':main()
