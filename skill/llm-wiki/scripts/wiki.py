#!/usr/bin/env python3
"""Portable, project-scoped helpers. Semantic knowledge compilation remains an agent task."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = ".wiki-schema.md"
REGISTRY = "llm-wiki-aliases.json"
TEMPLATES = Path(__file__).resolve().parents[1] / "templates"

def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))

def require_write():
    if os.environ.get("WIKI_WRITE_CONFIRM") != "yes":
        raise ValueError("Write denied: obtain current user authorization, then set WIKI_WRITE_CONFIRM=yes for this command only")

def within(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False

def project():
    explicit = os.environ.get("FRAMEWORK_PROJECT_ROOT")
    cwd = Path.cwd().resolve()
    if explicit:
        root = Path(explicit).resolve(strict=True)
        if not root.is_dir() or not within(cwd, root):
            raise ValueError("Explicit project root must contain current directory")
        return root
    for folder in (cwd, *cwd.parents):
        if (folder / ".git").exists() or (folder / "framework-project.json").exists():
            return folder
        if (folder / REGISTRY).exists():
            return folder
    return None

def validate_alias(alias):
    if not alias.strip() or alias in ('.', '..') or '/' in alias or '\\' in alias or any(ord(c) < 32 for c in alias):
        raise ValueError('Alias must be a nonempty name, not a path')

def registry():
    root = project()
    if root is None or not (root / REGISTRY).is_file():
        return root, {}
    file = root / REGISTRY
    if file.is_symlink():
        raise ValueError("Registry must not be a symlink")
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in data.items()):
        raise ValueError("Registry must map strings to paths")
    for alias in data:
        validate_alias(alias)
    return root, data

def validate(path):
    path = path.resolve(strict=True)
    if not path.is_dir() or not (path / SCHEMA).is_file():
        raise ValueError("Not a knowledge root: " + str(path))
    if (path / SCHEMA).is_symlink():
        raise ValueError("Schema must not be a symlink")
    return path

def resolve(target):
    if target in (".", "..") or Path(target).is_absolute() or "/" in target or "\\" in target:
        return validate(Path(target).expanduser())
    root, data = registry()
    if target not in data:
        raise ValueError("Unknown alias; no current-KB or global fallback: " + target)
    raw = Path(data[target])
    path = (root / raw).resolve()
    if raw.is_absolute() or not within(path, root):
        raise ValueError("Alias must be a project-relative path inside project")
    return validate(path)

def safe_file(root, relative):
    candidate = root / relative
    if not within(candidate, root):
        raise ValueError("Path escapes root")
    # No symlink components for writes or recursive data operations.
    current = root
    for component in Path(relative).parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("Symlink path rejected")
    return candidate

def pages(root):
    folder = safe_file(root,"wiki")
    result = []
    if folder.is_dir():
        for p in sorted(folder.rglob("*.md")):
            safe_file(root,p.relative_to(root))
            if p.is_file():
                result.append(p)
    return result

def read_text(p):
    return p.read_text(encoding="utf-8")

def metadata(root):
    text = read_text(root / SCHEMA)
    def value(labels, default):
        m = re.search(r"(?m)^\s*(?:-\s*)?(?:" + labels + r"):\s*(.+)$", text)
        return m.group(1).strip() if m else default
    return {"topic":value("Topic|主题","untitled"),"language":value("Language|语言","zh")}

def find_matches(root, topic):
    terms = re.findall(r"\w+", topic.casefold())
    results = []
    for f in pages(root):
        body = read_text(f).casefold()
        hits = sum(body.count(t) for t in terms)
        if hits:
            results.append({"page":f.relative_to(root).as_posix(),"matches":hits})
    return sorted(results,key=lambda r:(-r["matches"],r["page"]))[:10]

def register(alias, target):
    require_write()
    validate_alias(alias)
    root, data = registry()
    if root is None:
        raise ValueError("Set FRAMEWORK_PROJECT_ROOT or create a project marker before registration")
    destination = validate(Path(target))
    if not within(destination,root):
        raise ValueError("KB must be inside project")
    relative = destination.relative_to(root).as_posix()
    if alias in data and data[alias] != relative:
        raise ValueError("Alias conflict: existing mapping preserved")
    data[alias] = relative
    output = root / REGISTRY
    temp = root / (REGISTRY + ".new")
    with temp.open("x",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write("\n")
    os.replace(temp,output)
    emit({"status":"REGISTERED","alias":alias,"path":relative})

def initialize(target, topic, language):
    require_write()
    if language not in ("zh","en"):
        raise ValueError("Language must be zh or en")
    dest = Path(target).expanduser().absolute()
    if dest.is_symlink() or (dest.exists() and (not dest.is_dir() or any(dest.iterdir()))):
        raise ValueError("Target exists and is not an empty ordinary directory")
    for parent in dest.parents:
        if parent.is_symlink():
            raise ValueError("Symlink parent rejected")
    suffix = "-en" if language=="en" else ""
    rendered = {}
    values={"TOPIC":topic,"DATE":dt.date.today().isoformat(),"WIKI_ROOT":".","LANG":language}
    for name,output in [("schema",SCHEMA),("purpose","purpose.md"),("index","index.md"),("log","log.md"),("overview","overview.md")]:
        text = read_text(TEMPLATES / (name + suffix + "-template.md"))
        for key,value in values.items():
            text = text.replace("{{"+key+"}}",value)
        rendered[output]=text
    dest.mkdir(parents=True,exist_ok=True)
    for d in ["raw/articles","raw/notes","raw/pdfs","raw/assets",*["wiki/"+x for x in ["entities","topics","sources","comparisons","synthesis","queries"]]]:
        (dest / d).mkdir(parents=True,exist_ok=True)
    for name,text in rendered.items():
        with (dest/name).open("x",encoding="utf-8") as f:
            f.write(text)
    emit({"status":"INITIALIZED","root":str(dest.resolve()),"registered":False,"pending":["purpose review","separate alias registration","content ingestion"]})

def prepare(root, source):
    require_write()
    src = Path(source)
    if src.is_symlink() or not src.is_file():
        raise ValueError("Source must be an ordinary file")
    content=src.read_bytes()
    digest=hashlib.sha256(content).hexdigest()[:12]
    target=safe_file(root,"raw/notes/"+dt.date.today().isoformat()+"-"+digest+"-"+src.name)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("xb") as f:
        f.write(content)
    return {"status":"PREPARED","raw":target.relative_to(root).as_posix(),"pending":["agent reads schema and source","source/entity/topic pages","index and log","source/link verification"]}

def lint(root, strict):
    all_pages=pages(root)
    errors=[]
    for f in all_pages:
        body=read_text(f)
        fm=re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)",body,re.S)
        if strict and (not fm or any(not re.search(r"(?m)^"+key+r":\s*\S",fm.group(1)) for key in ["type","created"])):
            errors.append({"page":f.relative_to(root).as_posix(),"error":"missing frontmatter/type/created"})
        for link in re.findall(r"\[\[([^\]]+)\]\]",body):
            key=link.split("|")[0].split("#")[0].strip()
            if not key:
                continue
            linked_root=root
            if ":" in key:
                alias,key=key.split(":",1)
                try:
                    linked_root=resolve(alias.strip())
                except (ValueError,OSError):
                    errors.append({"page":f.name,"error":"unresolved cross-KB alias"})
                    continue
                key=key.strip()
            matches=[p for p in pages(linked_root) if p.stem==key or p.relative_to(linked_root/"wiki").with_suffix("").as_posix()==key]
            if len(matches)!=1:
                errors.append({"page":f.relative_to(root).as_posix(),"error":"missing or ambiguous link","link":key})
    emit({"checked":len(all_pages),"errors":errors,"scope":"structural only; agent must verify semantic accuracy, provenance and schema-specific requirements"})
    return 1 if errors else 0

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["resolve","list-kb","add-alias","detect-lang","read-schema","init","query","ingest","batch-ingest","status","lint","graph","digest","delete","crystallize"])
    parser.add_argument("args",nargs=argparse.REMAINDER)
    ns=parser.parse_args()
    cmd,args=ns.command,ns.args
    def need(n):
        if len(args)<n:
            raise ValueError("Not enough arguments for "+cmd)
    if cmd=="init":
        need(2);initialize(args[0],args[1],args[2] if len(args)>2 else "zh");return 0
    if cmd=="list-kb":
        root,data=registry();emit({"status":"CONFIGURED" if data else "NOT_CONFIGURED","aliases":data});return 0
    if cmd=="add-alias":
        need(2);register(args[0],args[1]);return 0
    if cmd=="query" and args and args[0]=="--all":
        need(2);root,data=registry()
        if not data:
            emit({"status":"NOT_CONFIGURED","results":[]});return 0
        results=[];failed=[]
        for alias in sorted(data):
            try:results.append({"alias":alias,"results":find_matches(resolve(alias),args[1])})
            except (ValueError,OSError) as e:failed.append({"alias":alias,"error":str(e)})
        emit({"results":results,"failed":failed});return 1 if failed else 0
    need(1);root=resolve(args[0])
    if cmd=="resolve": print(root)
    elif cmd=="detect-lang": print(metadata(root)["language"])
    elif cmd=="read-schema": emit(metadata(root))
    elif cmd=="query":
        need(2);emit({"root":str(root),"results":find_matches(root,args[1])})
    elif cmd=="status":
        emit({"root":str(root),**metadata(root),"pages":len(pages(root))})
    elif cmd=="lint":
        return lint(root,"--strict" in args)
    elif cmd=="ingest":
        need(2);emit(prepare(root,args[1]))
    elif cmd=="batch-ingest":
        require_write()
        folder=Path(args[1]) if len(args)>1 else safe_file(root,"raw")
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError("Batch source must be an ordinary directory")
        targets=sorted(folder.rglob("*.md"))
        prepared=[];failed=[]
        for source in targets:
            try:
                if any(parent.is_symlink() for parent in [source,*source.parents]):
                    raise ValueError("Symlink source rejected")
                prepared.append(prepare(root,source))
            except (OSError,ValueError) as e: failed.append({"source":str(source),"error":str(e)})
        emit({"status":"PARTIAL" if failed else "PREPARED","prepared":prepared,"failed":failed,"pending":"Agent must compile and verify knowledge pages"})
        return 1 if failed else 0
    elif cmd=="graph":
        emit({"nodes":[p.relative_to(root).as_posix() for p in pages(root)],"edges":[{"source":p.relative_to(root).as_posix(),"target":x} for p in pages(root) for x in re.findall(r"\[\[([^\]]+)\]\]",read_text(p))],"mode":"read-only"})
    elif cmd=="digest":
        need(2);emit({"status":"PLAN_ONLY","topic":args[1],"sources":find_matches(root,args[1]),"template":"synthesis-template.md","pending":["agent synthesis","provenance verification","index/log updates"]})
    elif cmd=="crystallize":
        need(2)
        content=sys.stdin.read() if args[1]=="-" else read_text(Path(args[1]))
        emit({"status":"PLAN_ONLY","confidence":"INFERRED","topic":args[2] if len(args)>2 else "session","characters":len(content),"pending":["authorized agent synthesis","source retention","index/log and validation"]})
    elif cmd=="delete":
        need(2);target=safe_file(root,"raw/"+args[1])
        if not target.is_file(): raise ValueError("Exact raw-relative file does not exist")
        refs=[p.relative_to(root).as_posix() for p in pages(root) if target.name in read_text(p)]
        emit({"status":"PLAN_ONLY","target":target.relative_to(root).as_posix(),"references":refs,"pending":["explicit scope confirmation","recoverable removal by agent","repair references and index/log","validate"],"deleted":False})
    return 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except (ValueError,OSError,json.JSONDecodeError) as error:
        print("ERROR: "+str(error),file=sys.stderr)
        sys.exit(1)
