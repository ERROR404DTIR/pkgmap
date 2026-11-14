#!/usr/bin/env python3
"""Map installed Python distribution dependencies without third-party packages."""
import argparse,json,re
from pathlib import Path
from importlib import metadata
def norm(name):return re.sub(r"[-_.]+","-",name).lower()
def build_graph(distributions):
 installed={norm(d["name"]):d for d in distributions};graph={k:[] for k in installed};missing={}
 for key,d in installed.items():
  for req in d.get("requires",[]) or []:
   match=re.match(r"\s*([A-Za-z0-9_.-]+)",req)
   if not match:continue
   dep=norm(match.group(1))
   if dep in installed:graph[key].append(dep)
   else:missing.setdefault(key,[]).append(dep)
  graph[key]=sorted(set(graph[key]))
 return {"graph":graph,"missing":missing,"count":len(installed)}
def collect():
 rows=[]
 for d in metadata.distributions():
  name=d.metadata.get("Name")
  if name:rows.append({"name":name,"version":d.version,"requires":d.requires or []})
 return rows
def tree(data,root):
 graph=data["graph"];seen=set();lines=[]
 def walk(node,depth):
  lines.append("  "*depth+node)
  if node in seen:lines[-1]+=" (already shown)";return
  seen.add(node)
  for child in graph.get(node,[]):walk(child,depth+1)
 key=norm(root)
 if key not in graph:raise KeyError(root)
 walk(key,0);return "\n".join(lines)
def mermaid(data):
 lines=["graph TD"]
 for src,deps in data["graph"].items():
  for dep in deps:lines.append(f'  "{src}" --> "{dep}"')
 return "\n".join(lines)+"\n"
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--json",action="store_true");p.add_argument("--mermaid");p.add_argument("--tree");a=p.parse_args()
 data=build_graph(collect())
 if a.mermaid:Path(a.mermaid).write_text(mermaid(data),encoding="utf-8")
 if a.tree:
  try:print(tree(data,a.tree))
  except KeyError:p.error("package is not installed: "+a.tree)
  return
 if a.json:print(json.dumps(data,indent=2));return
 edges=sum(map(len,data["graph"].values()))
 print(f"Distributions: {data['count']} · dependency edges: {edges} · missing requirements: {sum(map(len,data['missing'].values()))}")
 for pkg,deps in sorted(data["missing"].items()):print("MISSING:",pkg,"->",", ".join(deps))
if __name__=="__main__":main()
