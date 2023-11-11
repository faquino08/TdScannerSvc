# TdScannerReader

Flask app that creates an ftp server and exposes an api for reading watchlists exported as `.csv` files and inserting the data into the postgres database.

# Api Reference

[comment]: <> (First Command)
### <span style="color:#6C8EEF">**POST**</span> /run-tos-reader?delay=<span style="color:#a29bfe">**:int**</span>
Run workflow for importing `.csv` files exported by the Power Automate Desktop containing: 
* the component stocks for major market indices[^1]
* equities with *options*, *weekly options* and *penny incremented options* 
* listed *Futures* symbols

#### **Arguments:**
- **delay**<span style="color:red">*</span> - integer showing how many seconds before starting the 

[comment]: <> (Second Command)
### <span style="color:#6C8EEF">**POST**</span> /run-sector-reader?delay=<span style="color:#a29bfe">**:int**</span>&calcTdEquity=<span style="color:#a29bfe">**:boolean**</span>
Run workflow for importing `.csv` files listing equities according to Sector classification. Each `.csv` file represents a single sector. 
#### **Arguments:**
- **delay**<span style="color:red">*</span> - integer declaring how many seconds before starting the workflow
- **calcTdEquity** - whether or not to run the workflow for updating the table of all currently listed equities. *Default:* ***False***

[comment]: <> (Third Command)
### <span style="color:#6C8EEF">**POST**</span> /run-calendar-reader?delay=<span style="color:#a29bfe">**:int**</span>
Run workflow for importing `.csv` file containing dates listed in this years economic calendar (includes earnings announcements, conference calls, and economic indicator announcements such as the jobs report).
#### **Arguments:**
- **delay**<span style="color:red">*</span> - integer declaring how many seconds before starting the workflow

<span style="color:red">*</span> - required argument
[^1]: Indices include DJI, Nasdaq100, Russell2000, SP400, & SP500

