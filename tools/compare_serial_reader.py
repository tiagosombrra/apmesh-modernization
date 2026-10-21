#!/usr/bin/env python3
"""Compare actual serial interning, directions, controls and evaluated scalar bits."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from audit_serial_reader import audit
from qualify_serial_reader import fixtures


def compare(original, candidate, original_root, candidate_root, output):
    output=output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    paths,_=fixtures(output)
    cases=[]
    counts={key:0 for key in ["patch_records","control_records","incidence_records","scalar_records"]}
    for shape,path in enumerate(paths):
        for seed in range(2):
            records={}; observations={}
            for name,executable in [("original",original),("candidate",candidate)]:
                argv=[str(executable.resolve()),f"trace-1-{seed}",str(path)]
                process=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
                log=output/f"{shape}-{seed}-{name}.log"
                log.write_bytes(process.stdout)
                if process.returncode!=0:
                    raise ValueError("Live numerical trace failed: "+str(argv))
                records[name]={"argv":argv,"exit_code":process.returncode,"log":log.name,
                               "sha256":hashlib.sha256(process.stdout).hexdigest()}
                observations[name]=[line for line in process.stdout.decode().splitlines()
                                    if line.startswith(("serial_geometry=","serial_control=","serial_incidence=","serial_value="))]
            if not observations["original"] or observations["original"]!=observations["candidate"]:
                raise ValueError("Actual nonempty serial trace differs")
            count=(1 if shape<2 else 3)*(1+seed)
            lines=observations["candidate"]
            required={"patch_records":count,"control_records":16*count,"incidence_records":4*count,"scalar_records":144*count}
            for key,prefix in [("control_records","serial_control="),("incidence_records","serial_incidence="),("scalar_records","serial_value=")]:
                if sum(line.startswith(prefix) for line in lines)!=required[key]:
                    raise ValueError("Trace observation inventory differs: "+key)
            for key,value in required.items(): counts[key]+=value
            cases.append({"shape":shape,"seed":seed,"invocations":records,
                          "observations_sha256":hashlib.sha256(json.dumps(lines).encode()).hexdigest()})
    result={"status":"passed","paired_traces":len(cases),**counts,"cases":cases,
            "preservation":audit(candidate_root,original_root),
            "scope":"Eight actual C++17 trace pairs, four bounded shapes, empty/seeded Geometry; exact control coordinates/IDs, ordered curve incidence/directions and Parameterize/Qu/Qv bits. Not a broader model or whole-process qualification."}
    (output/"report.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ["original","candidate","original-root","candidate-root","output"]:
        parser.add_argument("--"+name,type=Path,required=True)
    args=parser.parse_args()
    result=compare(args.original,args.candidate,args.original_root,args.candidate_root,args.output)
    print(json.dumps({k:result[k] for k in ["status","paired_traces","patch_records","control_records","incidence_records","scalar_records"]}))
