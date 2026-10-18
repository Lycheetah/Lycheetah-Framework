"""Differential regression tests: independent SQL query logic vs ledger.

Synthetic inputs created in this repo; independence is of *algorithm*, not gold.
"""
import random
import unittest
from datetime import datetime, timedelta, timezone
from hybrid_gateway.core import HybridGateway, SourceDocument, ClaimProposal
from hybrid_gateway.sql_temporal_baseline import SQLTemporalBaseline
from demo_sql_comparison import build, run


def ts(days):
    return (datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(days=days)).isoformat().replace('+00:00','Z')


def row(g, sql, *, tenant='t', subject='refunds', predicate='window_days',
        scope='online', effective=10, known=15):
    kw=dict(tenant=tenant,subject=subject,predicate=predicate,scope=scope,
            effective_at=ts(effective),known_at=ts(known))
    a=g.query(**kw);b=sql.query(**kw)
    return (a.disposition,a.value,tuple(x['claim_id'] for x in a.citations)),(b.disposition,b.value,b.claim_ids)


def add(g, cid, val, valid, known, *, tenant='t', scope='online',
        until=None, supersedes=()):
    source=SourceDocument('s'+cid,tenant,'urn:'+cid,
                          f'Refunds allowed within {val} days.')
    g.register_source(source)
    claim=ClaimProposal(cid,tenant,'refunds','window_days',scope,str(val),
                        ts(valid),source.source_id,source.body,
                        valid_until=ts(until) if until is not None else None,
                        supersedes=tuple(supersedes))
    d=g.ingest(claim,recorded_at=ts(known),reviewer_approved=True)
    assert d.disposition=='ALLOW',d


class SQLBaselineTests(unittest.TestCase):
    def test_four_case_result_and_no_advantage(self):
        x=run(verbose=False)
        self.assertEqual(x['counts'], {'naive_latest_known':2, 'sql_temporal':4, 'gateway':4})

    def test_exact_scope_and_tenant(self):
        g=HybridGateway();add(g,'a',14,0,1,tenant='A',scope='web')
        add(g,'b',30,0,2,tenant='B',scope='web')
        add(g,'c',45,0,3,tenant='A',scope='store')
        with SQLTemporalBaseline(g.events) as s:
            for tenant,scope in [('A','web'),('A','store'),('B','web'),('B','store')]:
                self.assertEqual(*row(g,s,tenant=tenant,scope=scope))

    def test_transitive_supersession_with_intermediate_withdrawn(self):
        g=HybridGateway()
        add(g,'a',14,0,1)
        add(g,'b',30,5,6,supersedes=('a',))
        add(g,'c',45,9,10,supersedes=('b',))
        self.assertEqual(g.withdraw('b',effective_from=ts(8),recorded_at=ts(11),reviewer_approved=True).disposition,'ALLOW')
        with SQLTemporalBaseline(g.events) as s:
            for eff in [-1,0,3,5,8,9,20]:
                for known in [0,1,5,6,9,10,11,20]:
                    self.assertEqual(*row(g,s,effective=eff,known=known),f'eff={eff} known={known}')

    def test_expiry_and_knowledge_time_boundary(self):
        g=HybridGateway();add(g,'a',14,0,2,until=6);add(g,'b',30,6,10)
        with SQLTemporalBaseline(g.events) as s:
            for eff in [0,5,6,7,10]:
                for known in [0,2,5,10]:
                    self.assertEqual(*row(g,s,effective=eff,known=known))

    def test_equal_values_with_multiple_citations(self):
        g=HybridGateway();add(g,'a',14,0,1);add(g,'b',14,0,2)
        with SQLTemporalBaseline(g.events) as s:
            a,b=row(g,s);self.assertEqual(a,b)
            self.assertEqual(a,('ANSWER','14',('a','b')))

    def test_batch_admission_together(self):
        g=HybridGateway();props=[]
        for cid,value in [('a',14),('b',30)]:
            src=SourceDocument('s'+cid,'t','urn:'+cid,f'Refunds allowed within {value} days.')
            g.register_source(src)
            props.append(ClaimProposal(cid,'t','refunds','window_days','online',str(value),ts(0),src.source_id,src.body))
        self.assertEqual(g.ingest_batch(props,recorded_at=ts(4),reviewer_approved=True).disposition,'ALLOW')
        with SQLTemporalBaseline(g.events) as s:
            self.assertEqual(*row(g,s,effective=10,known=4))
            self.assertEqual(*row(g,s,effective=10,known=3))

    def test_unsupported_event_rejected(self):
        with self.assertRaises(ValueError):
            SQLTemporalBaseline([{'kind':'FANTASY','at':ts(0),'payload':{}}])

    def test_randomized_seeded_differential_1200_queries(self):
        rng=random.Random(20261018)
        # 30 distinct append-only histories, 40 queries each. This establishes
        # consistency on generated legal cases, NOT accuracy vs outside gold.
        for trial in range(30):
            g=HybridGateway();known=0
            by_key={('A','web'):[],('A','store'):[],('B','web'):[],('B','store'):[]}
            for n in range(18):
                tenant,scope=rng.choice(list(by_key))
                known+=rng.randrange(1,4)
                parent=rng.choice(by_key[(tenant,scope)]) if by_key[(tenant,scope)] and rng.random()<.45 else None
                valid=rng.randint(-3,known+5)
                if parent: valid=max(valid,int((datetime.fromisoformat(g.claims[parent].valid_from.replace('Z','+00:00'))-datetime(2026,1,1,tzinfo=timezone.utc)).days))
                until=valid+rng.randint(1,12) if rng.random()<.35 else None
                cid=f'c{trial}_{n}'
                add(g,cid,rng.choice((14,30,45,60)),valid,known,tenant=tenant,scope=scope,
                    until=until,supersedes=((parent,) if parent else ()))
                by_key[(tenant,scope)].append(cid)
                if rng.random()<.2:
                    target=rng.choice(by_key[(tenant,scope)])
                    known+=1
                    d=g.withdraw(target,effective_from=ts(rng.randint(-3,known+5)),
                                 recorded_at=ts(known),reviewer_approved=True)
                    self.assertEqual(d.disposition,'ALLOW')
            self.assertTrue(g.verify_chain(anchored_head=g.head_digest))
            with SQLTemporalBaseline(g.events) as s:
                for _ in range(40):
                    tenant,scope=rng.choice([('A','web'),('A','store'),('B','web'),('B','store'),('X','web')])
                    eff=rng.randint(-5,known+12);k=rng.randint(-5,known+12)
                    self.assertEqual(*row(g,s,tenant=tenant,scope=scope,effective=eff,known=k),
                                     f'trial={trial} effective={eff} known={k} tenant={tenant} scope={scope}')

if __name__=='__main__':unittest.main()
