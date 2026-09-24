import json
from android_llm_gnn.demo import run

def test_demo_is_repeatable_and_serializable():
    a=run();b=run()
    assert a == b
    assert a["project"] == "MechaDroid"
    json.dumps(a,allow_nan=False)
