"""Reproduce crash-before-journal-commit discrepancy: Forge IV vs Forge V.

Both use an identical Git SHA-verified upstream CommitFence. Forge IV has its
own journal DB; Forge V journals in the fence's protected database transaction.
Comparison is intentionally synthetic, not a provider-effect test.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import zipfile

BASE=Path(__file__).resolve().parent
_legacy_temp=None
legacy=BASE.parent/'sovereign_choice_forge_iv'
if not (legacy/'intent_bridge.py').exists():
    # Portable archive: restore the actual prior lineage rather than synthesize it.
    _legacy_temp=TemporaryDirectory()
    with zipfile.ZipFile(BASE/'lineage/FORGE_IV_COMPLETE.zip') as archive:
        archive.extractall(_legacy_temp.name)
    legacy=Path(_legacy_temp.name)/'sovereign_choice_forge_iv'
sys.path[:0]=[str(BASE/'upstream_mirror/papers/agent-safety/frontier-controls'),
             str(BASE/'upstream_mirror/papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7'),
             str(BASE), str(legacy)]
from research_support import Action
from commit_fence import CommitFence
from choice_ledger import AtomicChoiceLedger
from intent_bridge import IntentAuthorityBridge


def action(subject,effect):
    return Action(principal='alice',tool='email',operation='send',
                  object_id='draft',destination='example@example.test',
                  arguments={'subject':subject},effect_id=effect)


def run():
    with TemporaryDirectory() as t:
        old_fence=CommitFence(Path(t)/'old_fence.sqlite')
        old=IntentAuthorityBridge(old_fence,Path(t)/'old_journal.sqlite')
        original=action('first','fx1'); revision=action('second','fx2')
        old.grant('alice','email','original',original)
        before_old=old.current('alice','email')
        orig_log=old._log
        def fail_active(*args, **kwargs):
            if kwargs.get('kind')=='GRANT_ACTIVE':
                raise RuntimeError('simulated crash at final journal write')
            return orig_log(*args, **kwargs)
        old._log=fail_active
        try:
            old.grant('alice','email','revision',revision)
            raise AssertionError('expected synthetic error')
        except RuntimeError as ex:
            assert 'simulated crash' in str(ex)
        old_journal=old.current('alice','email')
        old_authority=old_fence.state('alice','email')
        assert old_journal==before_old
        assert old_authority['generation'] != old_journal.generation
        assert old_authority['active'] is True

        new_fence=CommitFence(Path(t)/'atomic.sqlite')
        new=AtomicChoiceLedger(new_fence)
        new.grant('alice','email','original',original)
        before_new=new.current('alice','email')
        try:
            new.grant('alice','email','revision',revision,inject_failure=True)
            raise AssertionError('expected synthetic error')
        except RuntimeError as ex:
            assert 'injected' in str(ex)
        new_journal=new.current('alice','email')
        new_authority=new_fence.state('alice','email')
        assert new_journal == before_new
        assert new_authority['generation'] == new_journal.generation
        assert new_authority['active'] == new_journal.active

        return {
            'experiment':'Simulated exception after authority update, before journal commit',
            'legacy_split_journal':{
                'journal_version':old_journal.version,
                'journal_generation':old_journal.generation,
                'upstream_generation':old_authority['generation'],
                'generation_mismatch':old_authority['generation']!=old_journal.generation,
                'upstream_active':old_authority['active'],
                'known_boundary':'Wrapper denies mismatched intent, but the separate stores disagree after interruption'},
            'forge_v_atomic':{
                'journal_version':new_journal.version,
                'journal_generation':new_journal.generation,
                'upstream_generation':new_authority['generation'],
                'generation_mismatch':new_authority['generation']!=new_journal.generation,
                'upstream_active':new_authority['active'],
                'known_boundary':'Only local SQLite choice+authority rollback; external provider effects not covered'},
            'real_upstream_commit_fence':True,
            'external_effects':False
        }


if __name__=='__main__':
    result=run()
    print(json.dumps(result,indent=2))
    (BASE/'comparison_results.json').write_text(json.dumps(result,indent=2)+'\n')
