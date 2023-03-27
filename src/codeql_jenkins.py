import logging
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
        "https://github.com/github/codeql-action/releases/download/codeql-bundle-20230304/codeql-bundle-"
        + ("win64" if IS_WINDOWS else "linux64")
        + ".tar.gz"
    )
    CODEQL_TAR_FILENAME = "codeql.tar.gz"

    def __init__(self):
        self.DEFAULT_CODEQL_PATH = "codeql"

    def install_corepack(self, corepack_path):
        logging.info("Enabling drivers corepack")
        subprocess.call([self.codeql_path_executable, "pack", "install", corepack_path])
        logging.info("Windows Driver Developer Supplemental Tools installed")

    def retrieve_codeql(self, extra_corepacks=[]):
        logging.info("Looking for CodeQL")
        codeql_path = self.DEFAULT_CODEQL_PATH
        if not os.path.exists(self.DEFAULT_CODEQL_PATH):
            logging.info("Didn't find CodeQL in {}".format(self.DEFAULT_CODEQL_PATH))
            codeql_path = os.path.join(Scan.DEFAULT_PATH, "codeql")
        if not os.path.exists(codeql_path) and Scan.IS_WINDOWS:
            logging.info("Didn't find CodeQL in {}".format(codeql_path))
            codeql_path = os.path.join(Scan.PROGRAM_FILES, "codeql")
        if not os.path.exists(codeql_path):
            logging.info("Didn't find CodeQL in {}".format(codeql_path))
            logging.info("Dowloading codeql")
            if sys.version_info[0] <= 2:
                import urllib

                urllib.urlretrieve(Scan.CODEQL_BUNDLE_URL, Scan.CODEQL_TAR_FILENAME)
            elif sys.version_info[0] <= 3:
                import urllib.request

                urllib.request.urlretrieve(
                    Scan.CODEQL_BUNDLE_URL, Scan.CODEQL_TAR_FILENAME
                )
            logging.info("Extracting codeql")
            with tarfile.open(Scan.CODEQL_TAR_FILENAME, "r") as tar:
                tar.extractall()
            codeql_path = self.DEFAULT_CODEQL_PATH
        self.codeql_path_executable = os.path.abspath(
            os.path.join(codeql_path, "codeql.cmd")
        )
        logging.info("Using CodeQL from {}".format(self.codeql_path_executable))
        if "WINDOWS_DRIVER" in extra_corepacks:
            driver_corepack_path = os.path.abspath(os.path.join(__file__, "../../", "Windows-Driver-Developer-Supplemental-Tools", "src"))
            self.install_corepack(driver_corepack_path)

    def create_database(self, build_command, db_name, source_root, language):
        logging.info("Creating database")
        subprocess.call(
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
                "--overwrite",
            ]
        )

    def analyze_database(self, db_name, queries, sarif_output_name):
        logging.info("Analyzing database")
        subprocess.call(
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

