import logging
import urllib.request
import sys
import subprocess
import os
import zipfile

DOWNLOAD_CODEQL = False
IS_WINDOWS = os.name == "nt"
CODEQL_BUNDLE_URL = f"https://github.com/github/codeql-cli-binaries/releases/download/v2.12.4/codeql-" + ("win64" if IS_WINDOWS else "linux64") + ".zip"
CODEQL_ZIP_FILENAME = "codeql.zip"
CODEQL_PATH = "codeql" if DOWNLOAD_CODEQL else os.path.join(os.environ["ProgramFiles"] if IS_WINDOWS else os.path.expanduser("~"), "codeql", "codeql")
CODEQL_PATH_EXECUTABLE = os.path.abspath(os.path.join(CODEQL_PATH, "codeql.cmd"))
logging.getLogger().setLevel(level=logging.INFO)

def retrieve_codeql():
    if not DOWNLOAD_CODEQL:
        logging.info(f"Skipping download and using {CODEQL_PATH_EXECUTABLE}")
        return
    logging.info("Dowloading codeql")
    urllib.request.urlretrieve(CODEQL_BUNDLE_URL, CODEQL_ZIP_FILENAME)
    logging.info("Extracting codeql")
    with zipfile.ZipFile(CODEQL_ZIP_FILENAME, 'r') as zip_ref:
        zip_ref.extractall()

# /codeql/codeql database create -v /tmp/mblinux-codeql-db --threads=8 --language=cpp --command=${WORKSPACE}/Scripts/buildit.sh --source-root=${WORKSPACE}
def create_database(build_command, db_name, source_root, threads, language):
    logging.info("Creating database")
    subprocess.run([CODEQL_PATH_EXECUTABLE, "database", "create", "-v", db_name, "--threads", str(threads), "--language",  language, "--command", build_command, "--source-root", source_root])

#  ../codeql/codeql database analyze /tmp/mblinux-codeql-db codeql/cpp-queries --threads=8 --format=sarif-latest --output=/tmp/codeql-results-mblinux.sarif"
def analyze_database(db_name, queries, threads, sarif_output_name):
    logging.info("Analyzing database")
    subprocess.run([CODEQL_PATH_EXECUTABLE, "database", "analyze", "-v", db_name, queries, "--threads", str(threads), "--format=sarif-latest",  "--output", sarif_output_name])

def test():
    source_root = "./app"
    build_command = "dotnet build"
    db_name = "codeql-db"
    language = "csharp"
    queries = "codeql/csharp-queries"
    sarif_output_name="codeql-results.sarif"
    threads = 8
    retrieve_codeql()
    create_database(build_command, db_name, source_root, threads, language)
    analyze_database(db_name, queries, threads, sarif_output_name)

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) != 7:
        logging.error(f"""Usage: codeql_jenkins.py "source_root" "build_command" "codeql_db_name" "language" "queries" "sarif-output" """)
        logging.info(f"""Example: python codeql_jenkins.py "./app" "dotnet build" "codeql-db-app" "csharp" "codeql/csharp" "codeql-results.sarif" """)
        sys.exit(-1)
    _, source_root, build_command, db_name, language, queries, sarif_output_name = sys.argv
    threads = 8
    retrieve_codeql()
    create_database(build_command, db_name, source_root, threads, language)
    analyze_database(db_name, queries, threads, sarif_output_name)
    logging.info(f"Wrote sarif to {sarif_output_name}")

