# codeql_jenkins
 
A helper python library to integrate CodeQL into Jenkins pipelines and output a sarif file.

The library can download CodeQL if it's not found. By default it looks for codeql `./codeql`, `~/codeql` and `C:/Program Files/codeql`. It runs on both Python 2.7 and 3.x.

For example, for a sample C# app located in `C:/app`:

```python
from codeql_jenkins import Scan
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
```

```
INFO:root:Looking for CodeQL
INFO:root:Didn't find CodeQL in codeql
INFO:root:Didn't find CodeQL in C:\Users\slemos\codeql
INFO:root:Didn't find CodeQL in C:\Program Files\codeql
INFO:root:Dowloading codeql
INFO:root:Extracting codeql
INFO:root:Using CodeQL from C:\Sources\codeql_jenkins\codql_jenkins\codeql\codeql.cmd
INFO:root:Creating database
...
INFO:root:Wrote sarif to codeql-results.sarif
```

This repository is provided as-is and isn't bound to Malwarebytes' SLA.
