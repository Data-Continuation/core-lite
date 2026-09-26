#!/usr/bin/env python3
"""Bounded non-authorizing source inventory for exact SDK-pinned Core-Lite."""
import argparse, ast, hashlib, json, re, subprocess, sys, tomllib
from pathlib import Path
PIN = "72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8"
def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout
def source_imports(raw):
    try:
        tree=ast.parse(raw.decode("utf-8-sig"))
    except (UnicodeError,SyntaxError):
        return {"status":"UNPARSEABLE","modules":[],"dynamic":[]}
    roots=set(); dynamic=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node,ast.ImportFrom) and node.level==0 and node.module:
            roots.add(node.module.split(".")[0])
        elif isinstance(node,ast.Call):
            fn=node.func
            name=fn.id if isinstance(fn,ast.Name) else (fn.attr if isinstance(fn,ast.Attribute) else "")
            if name in ("__import__","import_module","exec","eval"):
                dynamic.append({"line":node.lineno,"call":name})
    return {"status":"PARSED","modules":sorted(roots),"dynamic":dynamic}
def audit(pin=PIN):
    paths=git("ls-tree","-r","--name-only",pin).decode().splitlines()
    p=tomllib.loads(git("show",pin+":pyproject.toml").decode())
    imports=set(); files=[]; dynamic_count=0
    for path in paths:
        raw=git("show",pin+":"+path)
        item={"path":path,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
        if path.endswith(".py"):
            scan=source_imports(raw);item["python"]=scan
            imports.update(scan["modules"]);dynamic_count+=len(scan["dynamic"])
        header=raw[:1500].decode("utf-8","replace").splitlines()[:35]
        markers=[x.strip()[:200] for x in header if re.search("SPDX-License-Identifier|Copyright",x,re.I)]
        if markers:item["observed_header_markers_not_title_proof"]=markers[:8]
        files.append(item)
    log=git("log","--format=%H%x1f%an%x1f%ae%x1f%B%x00",pin).decode("utf-8","replace")
    commits=[x for x in log.split("\0") if "\x1f" in x]
    authors={}; coauthors=set()
    for commit in commits:
        cols=commit.strip().split("\x1f",3)
        if len(cols)!=4:continue
        who=cols[1]+" <"+cols[2]+">"
        authors[who]=authors.get(who,0)+1
        coauthors.update(re.findall(r"(?im)^Co-authored-by:\s*(.+)$",cols[3]))
    return {"schema":"stegverse.core-lite.pinned-source-candidate/v1",
        "goal_task_id":"ECOSYSTEM-OPEN-SOURCE-STRATEGY-001","source_pin":pin,
        "classification":"SOURCE_INVENTORY_NOT_COMPLETE_SBOM_OR_RIGHTS_CLEARANCE",
        "publication_allowed":False,"rights_holder_grant":"NOT_PROVIDED",
        "project":{"name":p["project"]["name"],"version":p["project"]["version"],
            "requires_python":p["project"].get("requires-python"),
            "license_field_present":"license" in p["project"],
            "runtime_dependencies":p["project"].get("dependencies",[]),
            "build_dependencies":p.get("build-system",{}).get("requires",[])},
        "tracked_blob_count":len(paths),"python_file_count":sum(path.endswith(".py") for path in paths),
        "observed_import_roots":sorted(imports),
        "unresolved_import_names_not_package_mappings":sorted(imports-sys.stdlib_module_names-{"core_lite"}),
        "dynamic_import_or_exec_calls":dynamic_count,
        "reachable_commit_records":len(commits),
        "git_author_attributions_not_copyright_title":authors,
        "coauthor_trailers_not_permissions":sorted(coauthors),"files":files,
        "evidence_gaps":["Original per-file grants and legal ownership not independently attested",
            "Static Python imports do not cover arbitrary runtime, subprocess or installation behavior",
            "Import roots are not complete version-pinned dependency distributions",
            "Full reproducible consumer build and SDK optional Python matrix unverified"]}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",default="reports/core_lite_pinned_sbom_candidate.json")
    args=p.parse_args();result=audit()
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"source_pin":PIN,"tracked_blobs":result["tracked_blob_count"],
         "python_files":result["python_file_count"],"commits":result["reachable_commit_records"],
         "publication_allowed":False}))
