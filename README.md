# codql_jenkins
 
A helper python script to integrate CodeQL into Jenkins pipelines and output a sarif file.

For example, for this sample C# app:

```powershell
python codeql_jenkins.py "./app" "dotnet build" "codeql-db-app" "csharp" "codeql/csharp-queries" "codeql-results.sarif" 
```

Reach out to @slemos on Slack if help is required.