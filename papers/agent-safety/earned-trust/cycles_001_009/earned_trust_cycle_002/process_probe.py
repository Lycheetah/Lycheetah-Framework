"""Single-host MULTI-PROCESS SQLite duplicate-effect probe (synthetic)."""
import concurrent.futures
import json
from pathlib import Path
import tempfile
from transactional_provider import ConditionalRefundProvider, Intent


def worker(path: str, intent: Intent) -> str:
    return ConditionalRefundProvider(path).commit(intent).code


def run(rounds=4, workers=8):
    observations=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        for n in range(rounds):
            with tempfile.TemporaryDirectory() as tmp:
                path=str(Path(tmp)/"provider.sqlite")
                intent=Intent(f"effect-{n}",f"approval-{n}","agent","order",1200)
                provider=ConditionalRefundProvider(path)
                provider.seed(intent)
                futures=[pool.submit(worker,path,intent) for _ in range(workers)]
                outcomes=[f.result(timeout=20) for f in futures]
                counts={"COMMITTED":outcomes.count("COMMITTED"),"IDEMPOTENT_REPLAY":outcomes.count("IDEMPOTENT_REPLAY"),"effect_count":provider.effect_count()}
                observations.append({"round":n+1,**counts})
                if counts != {"COMMITTED":1,"IDEMPOTENT_REPLAY":workers-1,"effect_count":1}:
                    raise AssertionError(f"multi-process result not as expected: {counts}")
    return {"status":"SYNTHETIC_LOCAL_MULTIPROCESS", "rounds":rounds,"workers_per_round":workers,
            "observations":observations,"notes":["All processes use one physical host SQLite database per round.",
            "Not a distributed database, service API, model agent, or independent security test."]}

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
