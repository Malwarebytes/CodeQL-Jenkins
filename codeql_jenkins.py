import logging
import urllib.request
import tarfile
import sys
import subprocess
import os
import shutil

CODEQL_BUNDLE_URL = "https://github.com/github/codeql-action/releases/download/codeql-bundle-20230304/codeql-bundle-win64.tar.gz"
CODEQL_TAR_FILENAME = "codeql.tar.gz"
CODEQL_PATH = "codeql"
CODEQL_PATH_EXECUTABLE = os.path.join(CODEQL_PATH, "codeql.exe")

logging.getLogger().setLevel(level=logging.INFO)

def retrieve_codeql():
    logging.info("Dowloading codeql")
    urllib.request.urlretrieve(CODEQL_BUNDLE_URL, CODEQL_TAR_FILENAME)
    tar = tarfile.open(CODEQL_TAR_FILENAME)
    logging.info("Extracting codeql")
    tar.extractall()
    tar.close()

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
        logging.info(f"""Example: python codeql_jenkins.py "./app" "dotnet build" "codeql-db-app" "csharp" "codeql/csharp-queries" "codeql-results.sarif" """)
        sys.exit(-1)
    _, source_root, build_command, db_name, language, queries, sarif_output_name = sys.argv
    threads = 8
    retrieve_codeql()
    create_database(build_command, db_name, source_root, threads, language)
    analyze_database(db_name, queries, threads, sarif_output_name)
    logging.info(f"Wrote sarif to {sarif_output_name}")

