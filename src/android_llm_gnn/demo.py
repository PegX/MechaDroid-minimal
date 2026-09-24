"""Normalize synthetic method metadata into a small call-graph report."""
import argparse
import json
from pathlib import Path
from .preprocess.method_keys import parse_method_key
from .preprocess.dalvik_normalizer import DalvikNormalizer

def run():
    normalizer=DalvikNormalizer()
    methods=["Ldemo/Main;->start()V","Ldemo/Store;->save(Ljava/lang/String;)V"]
    instruction=normalizer.normalize_instruction("invoke-virtual","v0, v1, Ldemo/Store;->save(Ljava/lang/String;)V")
    return {"project":"MechaDroid","scope":"synthetic preprocessing only; no APK loading or malware verdict", "nodes":[{"id":i,**parse_method_key(key)} for i,key in enumerate(methods)],"edges":[{"source":0,"target":1,"kind":"synthetic_call"}],"instruction":{"opcode":instruction.opcode,"tokens":instruction.tokens}}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path);a=p.parse_args();text=json.dumps(run(),indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+"\n")
    else:print(text)
if __name__ == "__main__":main()
