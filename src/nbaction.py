# src/nbaction.py
import sys
import os
import os.path
import subprocess

NOTEBOOK_EXTN = ".ipynb"
HTML_EXTN = ".html"

def exec_notebook(src, target):
    cmd = ["jupyter", "nbconvert", "--ExecutePreprocessor.timeout=600", "--to",  "notebook", "--execute", "--output=" + target, src ]
    return subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def clean_notebook(src):
    cmd = ["jupyter", "nbconvert", "--ExecutePreprocessor.timeout=600", "--clear-output", src ]
    return subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def publish_notebook(src, target):
    cmd = ["jupyter", "nbconvert", "--ExecutePreprocessor.timeout=600", "--to", "html", "--output=" + target,  src ]
    return subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

# Main
repo_workspace = os.environ.get("GITHUB_WORKSPACE", '.')
sources = os.environ.get("NB_SOURCES", '').split(' ')
target_path = os.path.join(repo_workspace, os.environ.get("NB_TARGET_PATH", 'publish/notebook'))
doc_path = os.path.join(repo_workspace, os.environ.get("NB_DOC_PATH", 'publish/doc'))

all_sources = set([ os.path.join(repo_workspace, f) for f in sources ])
processed = []

for s in all_sources:
    if '.ipynb_checkpoints' in s:
        continue
    basename = os.path.basename(s)
    f, extn = os.path.splitext(basename)

    if extn.lower() != NOTEBOOK_EXTN:
        continue

    ti = os.path.join(repo_workspace, target_path, os.path.dirname(s))
    tif = os.path.join(ti, basename)
    di = os.path.join(repo_workspace, doc_path, os.path.dirname(s))
    dif = os.path.join(di, f + HTML_EXTN)

    os.makedirs(ti, exist_ok=True)
    os.makedirs(di, exist_ok=True)

    result = clean_notebook(s)
    if result.returncode != 0:
        print(f"ERROR: clean_notebook {basename} failed with code {result.returncode}")
    result = exec_notebook(s, tif)
    if result.returncode != 0:
        print(f"ERROR: exec_notebook {basename} -> {tif} failed with code {result.returncode}")
    result = publish_notebook(tif, dif)
    if result.returncode != 0:
        print(f"ERROR: publish_notebook {basename} -> {dif} failed with code {result.returncode}")

    processed.append(s)
    processed.append(tif)
    processed.append(dif)

print("{0}={1}".format("published", ' '.join(processed)), file=sys.stdout)
if "GITHUB_OUTPUT" in os.environ :
    with open(os.environ["GITHUB_OUTPUT"], "a") as f :
        print("{0}={1}".format("published", ' '.join(processed)), file=f)



