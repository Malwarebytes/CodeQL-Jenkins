import logging
import urllib.request
import sys
import subprocess
import os
import tarfile

logging.getLogger().setLevel(level=logging.INFO)


class Scan:
    DEFAULT_PATH = os.path.expanduser("~")
    PROGRAM_FILES = os.environ["ProgramFiles"]
    IS_WINDOWS = os.name == "nt"
    THREADS = 8
    CODEQL_BUNDLE_URL = (
        f"https://github.com/github/codeql-action/releases/download/codeql-bundle-20230304/codeql-bundle-"
        + ("win64" if IS_WINDOWS else "linux64")
        + ".tar.gz"
    )
    CODEQL_TAR_FILENAME = "codeql.tar.gz"

    def __init__(self):
        self.DEFAULT_CODEQL_PATH = "codeql"

    def retrieve_codeql(self):
        logging.info("Looking for CodeQL")
        codeql_path = self.DEFAULT_CODEQL_PATH
        if not os.path.exists(self.DEFAULT_CODEQL_PATH):
            logging.info(f"Didn't find CodeQL in {self.DEFAULT_CODEQL_PATH}")
            codeql_path = os.path.join(Scan.DEFAULT_PATH, "codeql")
        if not os.path.exists(codeql_path) and Scan.IS_WINDOWS:
            logging.info(f"Didn't find CodeQL in {codeql_path}")
            codeql_path = os.path.join(Scan.PROGRAM_FILES, "codeql")
        if not os.path.exists(codeql_path):
            logging.info(f"Didn't find CodeQL in {codeql_path}")
            logging.info("Dowloading codeql")
            urllib.request.urlretrieve(Scan.CODEQL_BUNDLE_URL, Scan.CODEQL_TAR_FILENAME)
            logging.info("Extracting codeql")
            with tarfile.open(Scan.CODEQL_TAR_FILENAME, "r") as tar:
                tar.extractall()
            codeql_path = self.DEFAULT_CODEQL_PATH
        self.codeql_path_executable = os.path.abspath(
            os.path.join(codeql_path, "codeql.cmd")
        )
        logging.info(f"Using CodeQL from {self.codeql_path_executable}")

    def create_database(self, build_command, db_name, source_root, language):
        logging.info("Creating database")
        subprocess.run(
            [
                self.codeql_path_executable,
                "database",
                "create",
                "-v",
                db_name,
                "--threads",
                str(Scan.THREADS),
                "--language",
                language,
                "--command",
                build_command,
                "--source-root",
                source_root,
            ]
        )

    def analyze_database(self, db_name, queries, sarif_output_name):
        logging.info("Analyzing database")
        subprocess.run(
            [
                self.codeql_path_executable,
                "database",
                "analyze",
                "-v",
                db_name,
                queries,
                "--threads",
                str(Scan.THREADS),
                "--format=sarif-latest",
                "--output",
                sarif_output_name,
            ]
        )


def test():
    source_root = "./app"
    build_command = "dotnet clean && dotnet build"
    db_name = "codeql-db"
    language = "csharp"
    queries = "codeql/csharp"
    sarif_output_name = "codeql-results.sarif"
    scan = Scan()
    scan.retrieve_codeql()
    scan.create_database(build_command, db_name, source_root, language)
    scan.analyze_database(db_name, queries, sarif_output_name)


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) != 7:
        logging.error(
            f"""Usage: codeql_jenkins.py "source_root" "build_command" "codeql_db_name" "language" "queries" "sarif-output" """
        )
        logging.info(
            f"""Example: python codeql_jenkins.py "./app" "dotnet build" "codeql-db-app" "csharp" "codeql/csharp-all" "codeql-results.sarif" """
        )
        sys.exit(-1)
    (
        _,
        source_root,
        build_command,
        db_name,
        language,
        queries,
        sarif_output_name,
    ) = sys.argv
    scan = Scan()
    scan.retrieve_codeql()
    scan.create_database(build_command, db_name, source_root, language)
    scan.analyze_database(db_name, queries, sarif_output_name)
    logging.info(f"Wrote sarif to {sarif_output_name}")
