"""Human-readable demonstration of a revised instruction; zero external effects."""
from pathlib import Path
from tempfile import TemporaryDirectory
from choice_fence import Action, ChoiceFence


if __name__ == '__main__':
    with TemporaryDirectory() as tmp:
        f = ChoiceFence(Path(tmp) / 'demo.sqlite3', key=b'local-demo-not-a-real-auth-key',
                        clock=lambda: 1_800_000_000)
        f.register('person')
        original = Action('person', 'assistant', 'send_email',
                          'colleague@example.test', 'draft-message-001',
                          'Hello, here is the original message.')
        f.issue('old-ticket', original, expires_at=1_800_000_100,
                explicit_human_approval=True)
        print('Original instruction: send this exact sample message.')
        print('Initial precheck:', f.precheck('old-ticket', original))
        f.revise('person', reason='I changed my mind; prepare, do not send.')
        print('New human direction: do not send; prepare a draft instead.')
        print('Previously approved send:', f.commit('old-ticket', original).reason)
        updated = Action('person', 'assistant', 'prepare_draft', 'local-draft',
                         'draft-message-002', 'Here is the draft, awaiting further human choice.')
        f.issue('new-ticket', updated, expires_at=1_800_000_100,
                explicit_human_approval=False)
        result = f.commit('new-ticket', updated)
        print('New local draft:', result.reason)
        print('Protected local effects:', f.effect_count(), '(one simulated draft; zero emails sent)')
        print('Audit valid:', f.audit_ok())
