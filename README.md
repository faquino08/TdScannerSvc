# TdScannerReader

Flask app that creates an ftp server and exposes an api for reading watchlists exported as `.csv` files and inserting the data into the postgres database.

[Main Repo](https://github.com/faquino08/FinanceDb/blob/main/README.md)

# Docker Reference

The following is a description of each env var key and value:

**Key Name:** PROJECT_ROOT \
**Description:** :warning: DEPRECATED :warning: a string containing the authentication information for the postgres server. DO NOT INCLUDE DATABASE NAME. \
**Values:** <span style="color:#6C8EEF">user:password@host:port</span>

**Key Name:** POSTGRES_DB \
**Description:** a string containing the name of the postgres database for data insertion. \
**Values:** <span style="color:#6C8EEF">\<postgres database name string></span>

**Key Name:** POSTGRES_USER \
**Description:**  a string containing the username the postgres server to use for authentication. \
**Values:** <span style="color:#6C8EEF">\<postgres username string></span>

**Key Name:** POSTGRES_PASSWORD \
**Description:** a string containing the password the postgres user specified. \
**Values:** <span style="color:#6C8EEF">\<postgres password string></span>

**Key Name:** POSTGRES_LOCATION \
**Description:** a string containing the hostname for the postgres server. \
**Values:** <span style="color:#6C8EEF">\<postgres hostname string></span>

**Key Name:** POSTGRES_PORT \
**Description:** a string containing the port for the postgres server. \
**Values:** <span style="color:#6C8EEF">\<postgres port string></span>

**Key Name:** PASV_ADDRESS \
**Description:** a string containing the hostname to return for passive ftp communication. \
**Values:** <span style="color:#6C8EEF">\<hostname string></span>

**Key Name:** API_PORT \
**Description:** a string for defining the port to use for exposing the api. \
**Values:** <span style="color:#6C8EEF">\<port string></span>

**Key Name:** DEBUG_BOOL \
**Description:** a string determining whether logging should include debug level messages. \
**Values:** <span style="color:#6C8EEF">True|False</span>

**Key Name:** APP_NAME \
**Description:** a string assigning an app name to be used when logging workflow runs in the database. \
**Values:** <span style="color:#6C8EEF">\<app name string></span>\
**Default:** **TdReader**

# Api Reference

[comment]: <> (First Command)
### <span style="color:#6C8EEF">**POST**</span> /run-tos-reader?delay=<span style="color:#a29bfe">**:int**</span>
Run workflow for importing `.csv` files exported by the Power Automate Desktop containing: 
* the component stocks for major market indices[^1]
* equities with *options*, *weekly options* and *penny incremented options* 
* listed *Futures* symbols

#### **Arguments:**
- **delay**<span style="color:red">*</span> - integer declaring how many seconds before starting the workflow

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

