# codql_jenkins
 
A helper python script to integrate CodeQL into Jenkins pipelines and output a sarif file.

The script can download CodeQL if it's not found. By default it looks for codeql `./codeql`, `~/codeql` and `C:/Program Files/codeql`.

For example, for this sample C# app:

```powershell
python codeql_jenkins.py "./app" "dotnet clean && dotnet build" "codeql-db-app" "csharp" "codeql/csharp-all" "codeql-results.sarif" 
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

Reach out to @slemos on Slack if help is required.