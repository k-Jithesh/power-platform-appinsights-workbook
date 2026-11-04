# Power Platform Application Insights workbook

Azure Monitor workbook for Application Insights telemetry from **Dynamics 365 Customer Engagement (D365 CE)** apps such as Sales, Customer Service and Field Service, other Power Apps **model-driven apps**, **Dataverse** and **Power Pages**. It answers the questions support, delivery and operations teams ask: is Dynamics 365 slow, what is failing, who is affected, and can the data be trusted.

**Version 1.7.2**

There is no custom code to deploy. The queries follow the telemetry schemas published on Microsoft Learn for the Power Platform export to Application Insights.

## Works with

The workbook reads the telemetry that the Power Platform data export sends to Application Insights, so it applies to any app that produces it. Nothing in it is specific to one Dynamics 365 app, apart from the Conversations tab. It reports by app module and by table, so you can see which app is slow.

| Area | What you get | What it needs |
| --- | --- | --- |
| Dynamics 365 Sales, Field Service and other customer engagement apps | Form, view and dashboard load times by table and app module (for example Account, Contact, Lead, Opportunity and Case, wherever they are used), save and update performance, server operations, failures and throttling, plug-ins, and per-user triage | Dataverse diagnostics and performance export |
| Dynamics 365 Customer Service | Everything above, plus the Conversations tab: routing and conversation lifecycle events over time and by queue | Dynamics Customer Service export and conversation diagnostics |
| Custom Power Apps model-driven apps | The same views as the apps above | Dataverse diagnostics and performance export |
| Power Pages | Page views, load time, browsers, locations, calls and JavaScript errors, a visitor funnel and abandoned pages | Application Insights JavaScript snippet on the site; Dataverse export for the server side |
| Power Automate | Cloud flow runs, failures, duration, and failing triggers and actions | Power Automate export |
| Custom integrations | Requests, p95 and failures by service, and outbound calls | Custom telemetry (for example OpenTelemetry) in the same Application Insights resource |

## Questions this answers

- Why is Dynamics 365 slow for some users, and is it only them? See **User triage**.
- Which forms, views and tables are slow to load in a model-driven app? See **Forms & views**.
- Is the slowness in the browser, the network, the server, a plug-in or an integration? See **Pages & browser**, **Plug-ins & dependencies** and **Integrations**.
- Are Dataverse API calls failing or being throttled (HTTP 429), and who is making them? See **Errors & throttling** and **Callers**.
- Is the slowness regional? See the country, state and city view on **Pages & browser**.
- How is a Power Pages portal performing, and where do visitors drop off? See **Power Pages**.
- Which Power Automate cloud flows fail or run slowly? See **Power Automate**.
- Are Customer Service conversations being routed and handled? See **Conversations**.
- Can I trust this data right now? See **Export health**.

## Prerequisites and setup

The workbook only shows what you export, so set up the out-of-the-box Application Insights integrations first. Do this once for each Power Platform environment. The first data can take up to 24 hours to arrive.

| Step | What to do | Where | What you need |
| --- | --- | --- | --- |
| 1 | Create a workspace-based Application Insights resource, one per Power Platform environment | Azure portal | An Azure subscription and permission to create resources |
| 2 | Leave local authentication enabled on that resource | Application Insights resource | Microsoft Learn states the integration requires it |
| 3 | Confirm the environment is a managed environment | Power Platform admin center | The export is supported for managed environments only |
| 4 | Create a **Dataverse diagnostics and performance** export | Power Platform admin center | The admin roles and resource access listed below |
| 5 | Optional: create **Power Automate** and **Dynamics Customer Service** exports | Power Platform admin center | Same as step 4 |
| 6 | Power Pages only: add the Application Insights JavaScript snippet to the site | Power Pages management app | Edit access to the site |
| 7 | Wait up to 24 hours, then open the workbook and check the **Export health** tab | Azure Monitor | Access to the resource, listed below |

### 1. Create the Application Insights resource

1. Sign in to the [Azure portal](https://portal.azure.com), select **Create a resource**, then **Monitoring & Diagnostics**, then **Application Insights**.
2. Fill in the details and select **Review + create**. Use a workspace-based resource (classic resources are retired). If you do not choose a Log Analytics workspace, one is created for you.
3. Use a separate resource for each Power Platform environment. Microsoft Learn warns that the out-of-the-box reports do not work correctly when one resource holds data from several environments.
4. Leave local authentication enabled. Microsoft Learn states the integration requires it.

Data ingestion and retention are billed through the Log Analytics workspace. See [Azure Monitor pricing](https://azure.microsoft.com/pricing/details/monitor/) before you turn on large exports.

### 2. Create the exports in the Power Platform admin center

1. Sign in to the [Power Platform admin center](https://admin.powerplatform.microsoft.com).
2. Select **Manage**, then **Data export**, then the **App Insights** tab, then **New data export**.
3. Enter a friendly name and select the data type from the table below. For **Power Automate**, choose whether to export cloud flow runs, triggers or actions. Select all three to fill the Power Automate tab.
4. Choose the environment to export from, then **Next**.
5. Choose the Azure subscription, resource group and Application Insights resource to export to, then **Next**.
6. Review the details and select **Create**. Data starts arriving within 24 hours.

| Export data type | Feeds these tabs |
| --- | --- |
| Dataverse diagnostics and performance | Overview, User triage, Forms & views, Pages & browser, Server operations, Callers, Errors & throttling, Plug-ins & dependencies, Export health, and the server side of Power Pages |
| Power Automate | Power Automate |
| Dynamics Customer Service | Conversations. You can create only one Customer Service export per environment. Also configure [conversation diagnostics](https://learn.microsoft.com/dynamics365/customer-service/administer/configure-conversation-diagnostics). |
| Copilot Studio | Not used by this workbook |

**Who can set this up.** Microsoft Learn lists these requirements. Without them the integration does not work.

- The Power Platform administrator or Dynamics 365 administrator role at tenant level in Microsoft Entra ID, and the environment administrator or system administrator role in the Dataverse environment.
- Contributor or Owner access to the Application Insights resource you export to.
- A managed environment. For the Customer Service export, Learn also lists a Power Apps, Power Automate or Dynamics 365 licence with premium use rights.

At the time of writing, Learn documents the Power Automate and Dynamics Customer Service exports as preview and not available in sovereign clouds (GCC, GCC High, DoD, 21Vianet). Check [Export data to Application Insights](https://learn.microsoft.com/power-platform/admin/set-up-export-application-insights) for the current position.

### 3. Power Pages: add the Application Insights snippet

Power Pages browser telemetry does not come from the export. It comes from a JavaScript snippet on the site.

1. Copy the **JavaScript (Web) SDK Loader Script** from [Application Insights JavaScript SDK setup](https://learn.microsoft.com/azure/azure-monitor/app/javascript-sdk). Replace `YOUR_CONNECTION_STRING` with the connection string from your Application Insights resource's **Overview** pane.
2. Open the [Power Pages management app](https://learn.microsoft.com/power-pages/configure/portal-management-app) and go to **Content Snippets**.
3. Create a content snippet named **Tracking Code** with **Type** set to **Text** and the language left blank. Paste the script into **Value**.
4. On sites that use the standard data model, use **Enable Traffic Analysis** in the Portal Management app instead. It creates the same **Tracking Code** snippet.

The site can send this telemetry to the same Application Insights resource or a different one. The Power Pages tab lets you pick which. See [Set up telemetry monitoring](https://learn.microsoft.com/power-pages/go-live/telemetry-monitoring).

### 4. Check that data is arriving

- Open the workbook and look at the **Export health** tab. It shows delivery lag and whether each feed is Current, Delayed or Stale.
- Or run these in the Application Insights **Logs** pane. Page loads from model-driven apps appear in `pageViews` and Dataverse requests in `requests`.

```kusto
pageViews | where timestamp > ago(1d) | summarize count()
requests | where timestamp > ago(1d) | summarize count()
```

If nothing appears after 24 hours, check the following. A common cause is missing permissions when the export was set up.

- The person who created the export had the roles listed above.
- The export points at the Application Insights resource you are querying.

### 5. Access to the workbook

- **View:** Reader on the subscription and on the Application Insights resource, so the pickers and queries work.
- **Save a copy:** you also need permission to write workbooks in the resource group, for example Workbook Contributor or Monitoring Contributor.

## Deploy

| Option | Steps |
| --- | --- |
| Quickest | Azure Monitor, Workbooks, New, Advanced editor, paste `power-platform-appinsights-workbook.json`, Apply, Save. Then pick the Subscription, Resource group and Application Insights resource. |
| Repeatable | Deploy `power-platform-appinsights-workbook.arm.json` to a resource group. |
| Alerts (optional) | Deploy `power-platform-appinsights-alerts.arm.json` with the Application Insights resource ID and an optional action group. Workbooks cannot create alerts themselves. |

To update an existing workbook, open it, select Advanced editor, paste the new JSON, then Apply and Save.

## What each tab does

| Tab | Question it answers | What it shows | Needs |
| --- | --- | --- | --- |
| **Overview** | Is Dataverse healthy, is it getting better or worse, and can I trust the data? | Latest period against the previous period with a Better or Worse assessment; health tiles (requests, success rate, p95, throttling, exceptions, page load); requests, failures and duration over time; data freshness. | Dataverse diagnostics and performance export |
| **User triage** | A user says it is slow. What happened to them, and is it only them? | A searchable list of users with loads, slow loads, API requests, failures and throttling, worst first. Click a user to compare them with everyone else on the same table and operation, and to see their timeline, slowest loads and calls, failures, exceptions, device and location. | Dataverse diagnostics and performance export |
| **Forms & views** | Which tables are slow to open, save or update? | Form and view load Apdex by table, form ID and view ID (Satisfied, Tolerating, Frustrated); most-used tables; save and update performance by table as a server-side proxy; custom plug-in time per table. | Dataverse diagnostics and performance export |
| **Pages & browser** | Is it slow in the browser or on the server? | Page load over time, browser request timing (time to first byte, stall, download), slowest pages by app and table, and load time and network latency by country with a drill-down to states and cities, and maps of network latency by country and by state or city. | Dataverse diagnostics and performance export |
| **Server operations** | Which Dataverse operations are slow? | Performance-style grid (p50, p95, p99, count, failures); duration distribution; busiest operations over time; filter by operation name. | Dataverse diagnostics and performance export |
| **Callers** | Who is calling Dataverse, and who is behind the failures and throttling? | Requests, failures and HTTP 429 by caller type (browser, Power Automate, Power Pages, Postman, integrations) from the user agent; failing operations and top users per caller. | Dataverse diagnostics and performance export |
| **Errors & throttling** | What is failing, how often, and why? | Failures-style grid; failures by response code; top failing operations over time; what drives failures; HTTP 429 throttling; exceptions; suggested alerts. | Dataverse diagnostics and performance export |
| **Plug-ins & dependencies** | Are custom plug-ins or outbound calls slowing requests? | Custom plug-in execution time and failures; Dataverse SDK calls and external HTTP calls ranked by duration. | Dataverse diagnostics and performance export |
| **Integrations** | How are our own integration APIs performing? | Requests, p95 and failures by service name; per-operation figures; outbound calls to third-party APIs. | Custom telemetry (for example OpenTelemetry) in the same Application Insights resource |
| **Power Pages** | How is the portal performing, and where do visitors drop off? | Page views, users, sessions, load time by page title, browsers, locations, calls made by pages, JavaScript errors; a funnel with completion rate and the top 5 abandoned pages; portal calls into Dataverse. Page titles that differ only in capital letters are combined. | Application Insights JavaScript snippet on the site; Dataverse export (server side) |
| **Power Automate** | Which cloud flows are failing or slow? | Flow runs, success rate and failed runs; run duration; flows by volume and failures; failing triggers and actions. | Power Automate export |
| **Conversations** | Are Customer Service conversations being routed and handled? | Conversation diagnostics events over time; conversations routed by queue; event types. | Dynamics Customer Service export and conversation diagnostics |
| **Export health** | Can the data be trusted right now? | Delivery lag against the 24-hour SLA; freshness by feed and signal (Current, Delayed, Stale); ingestion volume by feed; gaps in the Dataverse export. | Any of the exports |

## Drill-down: click a row

Ten grids are clickable. Clicking a row opens a detail panel directly below the grid, with the selected item in its header. Select another row to switch. The location drill-down has no header, because the selected country stays highlighted in the grid above it. On the operation and failing-operation grids, click the Overall row to hide the panel.

| Tab | Click | Panel shows |
| --- | --- | --- |
| User triage | A user row | Selected user and totals; load time against everyone else over time; load time by table and API duration by operation against everyone else; activity timeline; slowest loads and calls; what ran inside the slowest requests; failures; exceptions; device and location. |
| Forms & views | A table row in the form or view grid | Forms and views by ID with Apdex, apps, locations, users with the most frustrating loads, the slowest loads. |
| Forms & views | A row in the save and update grid | Trend by action, operations, response codes, users with the slowest saves, the slowest saves and what ran inside them. |
| Pages & browser | A country row | The states and cities in that country (the 100 busiest, each with at least 5 loads from at least 3 users) with median, average and p95 load time and network latency, and the country's p95 load time over time against the rest of the world. A State filter above the grid narrows it to chosen states. A map of its states or cities comes first (see Map view). A ranking at the end shows the median network latency at the 15 busiest places, banded fast, moderate or slow, against the typical latency for the whole country. |
| Pages & browser | A state and city row in that grid | The state's p95 load time over time against the rest of the country, and the city's against the rest of the state. |
| Server operations | An operation row | Requests and duration trend, response codes, callers, users, the slowest requests and what ran inside them. |
| Callers | A caller row | Trend, operations the caller uses, response codes, users, the raw user agent strings. |
| Errors & throttling | A failing operation row | Failure trend and rate, response codes, callers and users affected, failed dependencies and exceptions inside the failed requests, the latest failures. |
| Power Pages | A page row | Views and load trend, where the load time goes, browsers, locations, previous and next page, calls and JavaScript errors from the page, the slowest loads. |
| Power Pages | A row in either abandonment grid | Where visitors came from, whether the page was slower when they left, failed calls and JavaScript errors in those sessions, the most recent abandoned sessions. |

**Tracing a single request or visit:** the panels list Operation IDs (Dataverse requests) and Session IDs (Power Pages visits). Copy one into Application Insights, Transaction search or Logs, to see the end-to-end detail.

## Using User triage

1. Set the **Time range** picker (choose Custom) to the minutes the user reported. The list and the panel follow it.
2. Find the user. The list shows up to 3,000 users, worst experience first (slow loads, then failures). To go straight to one person, copy their Dataverse user ID into **Find a user**: the system user ID in model-driven apps, or the contact ID in Power Pages. Open the user or contact record in Dataverse and copy the ID from the page address (the `id=` value). Part of an ID or name is enough.
3. Optional: add names in **Optional names**, as pairs such as `0000-aaaa=Jane Citizen; 1111-bbbb=Pat Lee`. The export has no names, only Dataverse record IDs. The same box can name form and view IDs. Names cannot contain `;` or a double quote.
4. Click the user's row. Read **Is it only this user?** first. It compares the user with everyone else on the same table or operation. A ratio near 1 means everyone is equally slow, so look at the platform. A high ratio points to something specific to the user: device, network, location, security roles or data volume.
5. Use the activity timeline and the slowest loads and calls to find the moment they reported. Copy an Operation ID into Application Insights to see the end-to-end transaction.

**Slow load threshold** (default 6 seconds) sets what counts as a slow load on this tab. Page-load telemetry has no save event, so saves appear in the timeline as create and update calls.

## Location view: what is and is not available

Location comes from the visitor's IP address when the telemetry arrives. Application Insights keeps the country, state and city, then discards the address (it stores `0.0.0.0`). So:

- **City is the finest level.** There is no suburb or postcode, and location is not stored against a user.
- People on a corporate network or VPN show as the city the network exits from, and some loads have no city.
- Storing IP addresses (`DisableIpMasking`) would not add a postcode. It would still be an estimate, and Microsoft recommends against it for privacy reasons.
- If you need a site, suburb or postcode, it has to come from Dataverse, because the telemetry user ID is the Dataverse user or contact ID. That means joining a user-to-site list into the queries, which this workbook does not do.

**Network latency ranking:** at the end of the country drill-down, a grid ranks the 15 busiest places (at least 5 loads from at least 3 users each, following the State filter). It shows the median network latency, which is the typical value and is not pulled up by a few very slow loads, as a bar with a band: **Fast** under 40 ms, **Moderate** 40 to 59 ms, **Slow** 60 ms or more. The first row is the typical latency for the whole country, as a reference. Only loads with a latency reading are counted, because not every page load reports one, so the load count can be lower than in the grid above. **p95_latency_ms** beside it shows the slow tail, and the band uses the median only. The median is the better measure of a place's connection, because the latency Dataverse reports for each load is already a typical estimate, while the p95 of a small place is close to its single worst load. Use p95 for page load time, where the slow tail is what users notice. The bands are set in the query and the grid colours, so edit both to change them.

**Filtering and sharing:** every grid has a download to Excel button, which exports the visible columns (hidden key columns are left out). Workbooks have no CSV option of their own, so save the Excel file as CSV from Excel if you need CSV. The States and cities grid also has a State filter (multi-select, most loads first), a search box and an Open in Logs button, where Export offers CSV. That grid lists the 100 busiest places, each with at least 5 loads from at least 3 users, so its export holds only those rows.

**Reading the comparison charts:** each point is the p95 for one time bucket (one hour on a 24-hour range). A small city may have only a few loads in an hour, so its p95 is effectively its slowest single load and can spike without pointing to a wider problem. Check the Loads column or widen the time range before acting on a spike.

## Map view

Two maps show where in the world the network is slow. Bubble size is page loads and colour is the median network latency, green for low and red for high.

- **World map:** above the country grid. It uses the built-in country map, so it needs nothing extra.
- **State or city map:** at the top of the country drill-down, with a **Map detail** switch for states or cities.

Application Insights does not record coordinates, so the state and city map looks each place up by name in a public place file, [`data/place-coordinates.csv`](data/place-coordinates.csv). The file has about 194,000 places with at least 500 people, built from [GeoNames](https://www.geonames.org/) (Creative Commons Attribution 4.0) by `tools/build_place_coordinates.py`. The query:

1. matches the city name, using the state name as well when it matches, so the right Richmond or Quincy is chosen;
2. falls back to the most populous place with that city name when the state is spelled differently;
3. draws a state at the middle of its matched cities, which is usually its busiest city;
4. reports **Placed %**, the share of that place's loads whose city could be found.

What to expect:

- **It is an approximation.** On a sample of real place names from the Application Insights demo instance, about three quarters of distinct places and states could be placed, and 30 of 31 Australian and New Zealand places. Names that differ from GeoNames, small suburbs of very large cities, and loads with no city are not drawn. They still count in the grids.
- **Places with fewer than 5 loads or fewer than 3 users are hidden,** and the State filter does not apply to the map.
- **Country names:** a few names that Application Insights uses differ from the place file (for example Russian Federation and Korea (South)). The query maps the common ones. To add more, edit the alias list at the top of the map query.
- **No data leaves your environment.** The query only reads the CSV file from its address. Nothing from your telemetry is sent to the file's host.
- **Host your own copy for production.** The default address is this repository. Copy `data/place-coordinates.csv` to storage you control and paste its address into **Place coordinates file**. Azure Monitor reads it from the service, so the address must be reachable from the public internet without a firewall, and Microsoft documents a limit of 100 MB for this operator.
- **The map cannot zoom.** Workbooks have no zoom or centre setting for maps, so the map always shows the whole world and a single country looks small. Microsoft documents pan and zoom, including zooming to the data by default, only for its Workbooks preview experience, which opens dashboard-style workbooks. To look closer, use the **Places on the map** table under the map. It lists each placed place with its latitude and longitude, and its download to Excel button gives a file that Excel 3D Maps or Power BI can zoom into.
- **Map rendering needs Azure Maps support** in your cloud and tenant.

Place coordinates are derived from GeoNames data under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). To refresh the file, run `python tools/build_place_coordinates.py`.

## Alert rules in the optional template

| Rule | Fires when | Default |
| --- | --- | --- |
| Dataverse throttling (HTTP 429) | HTTP 429 responses reach the threshold in 15 minutes | 10 in 15 min |
| Dataverse failure rate | Failure rate reaches the threshold, with enough requests to be meaningful | 10% and 200 requests |
| Dataverse slow responses | p95 server duration reaches the threshold over 30 minutes | 3,000 ms and 200 requests |
| Dataverse export silent | No Dataverse export requests for the set number of hours | 6 hours |

## Read before sharing figures

- **Delivery delay:** the export has a 24-hour delivery SLA and is not lossless, so recent hours can be incomplete. Use the Export health tab first.
- **Trends, not exact counts:** use the data for trends and comparisons. Use flow run history and Dataverse itself for exact counts.
- **Save and command buttons:** page-load telemetry covers form, view and dashboard loads only. Save and update performance is a server-side proxy, based on the create, update and delete calls.
- **Apdex bands:** set to Satisfied under 6T and Tolerating from 6T to 12T. The standard Apdex definition uses T and 4T, so confirm before comparing with other Apdex reports.
- **Abandonment:** a session is abandoned when it did not view a page matching the success-page text. It needs the success page to be a separate page view, and it excludes search engine bots by default.
- **Latency charts:** the totals row under latency, rate and lag charts is hidden, because a sum of latencies means nothing. Charts that count things keep it.
- **Personal data:** user IDs are Dataverse record IDs (the system user ID in model-driven apps, the contact ID in Power Pages). User triage shows individual activity, and names typed into Optional names stay in the browser session. Do not save or share the workbook with names filled in, and aggregate before sharing outside the support team.

## Validation status

**Checked**
- All 177 queries parse and run against Microsoft's public Application Insights demo instance.
- The drill-down panels were run with real selections on that data. The demo has no Dataverse form-load telemetry, so the load-based panels (User triage, location, forms) were tested on constructed sample rows with known answers.
- The comparison, save and update, table, caller mapping, funnel, Power Pages page and abandonment, page-title merging and location logic were tested the same way, including the three location comparison charts against an independent calculation.
- A pilot against a real export confirmed that states and cities are recorded and that the location grid, drill-down and comparison charts load in the portal.
- The workbook structure was checked: every clickable grid exports a hidden key, has matching detail items that stay hidden until a row is clicked, and every one of them uses the selection. The ARM template carries the same content as the workbook.

**Not yet checked**
- Which ID each export feed records. Microsoft Learn describes the user ID differently on different pages, and the User triage list combines page loads and API requests by ID. If the two feeds use different IDs, the same person appears twice.
- That the totals row is hidden on the 25 latency charts, that the state and city selection and the State filter reset when another country is chosen (if not, the charts ask for a new row and the grid can show nothing until you pick All), that the download to Excel button appears on every grid and Open in Logs on the States and cities grid, how the latency ranking's bars and band colours render, how the two maps render in the portal (bubble size, the green to red colour scale and Azure Maps availability), and that Azure Monitor can read the place coordinates file from your tenant.
- The Power Pages tab against a real site, and deployment of the alerts template.
- Each Dynamics 365 app (Sales, Customer Service, Field Service) against its own real export. The workbook reads telemetry shared by all model-driven apps, so it should apply, but this has not been confirmed app by app.

## Maintaining this repository

`power-platform-appinsights-workbook.arm.json` embeds the workbook as a JSON string, so it must be regenerated whenever the workbook changes. Edit the workbook JSON, then run this from the repository root:

```python
import json

VERSION = "1.7.2"  # also update the version text inside the workbook JSON
WB = "power-platform-appinsights-workbook.json"
ARM = "power-platform-appinsights-workbook.arm.json"

wb = json.load(open(WB, encoding="utf-8"))
arm = json.load(open(ARM, encoding="utf-8"))
res = next(r for r in arm["resources"] if r.get("properties", {}).get("serializedData"))
old = json.loads(res["properties"]["serializedData"])
for key in ("isLocked", "fallbackResourceIds"):  # wrapper keys kept from the existing template
    if key in old:
        wb[key] = old[key]
res["properties"]["serializedData"] = json.dumps(wb, separators=(",", ":"), ensure_ascii=False)
res["tags"]["workbookVersion"] = VERSION
with open(ARM, "w", encoding="utf-8") as f:
    json.dump(arm, f, indent=2, ensure_ascii=False)
```

Version numbers follow major.minor.patch: a new tab or section raises the minor number, and a query fix raises the patch number.

## Version history

- **1.7.2:** Pages & browser: a p95 network latency column beside the median in the latency ranking and in the **Places on the map** table. Bands and map colours stay on the median.
- **1.7.1:** Pages & browser: smaller, slightly transparent bubbles on the state or city map, a **Places on the map** table with latitude, longitude and download to Excel, and a note that workbook maps cannot zoom.
- **1.7.0:** Pages & browser: a world map of network latency by country, and a state or city map at the top of the country drill-down. The state and city map looks places up in a new place coordinates file (`data/place-coordinates.csv`, built from GeoNames under CC BY 4.0).
- **1.6.0:** Pages & browser: a ranking of the median network latency at the busiest places in the selected country, with fast, moderate and slow bands and a typical row for the whole country. A download to Excel button on every grid (102 grids).
- **1.5.0:** Pages & browser: a State filter above the States and cities grid, and download to Excel and Open in Logs buttons on that grid so it can be shared for investigation.
- **1.4.4:** Pages & browser: the location drill-down no longer repeats the selected country in its own heading and table. The states and cities grid and the charts sit directly under the country grid and appear when a country is clicked.
- **1.4.3:** Naming only. The "proof of concept" label is removed from the workbook title, the About text, the ARM template's default display name and this README. The validation status below still lists what has not been checked.
- **1.4.2:** Naming only. The workbook title, the ARM template's default display name and the alerts template description now say Power Platform Application Insights instead of D365 Observability. The alerts template version label is aligned with the workbook (it still said 1.2.0).
- **1.4.1:** The location comparison charts plot p95 load time instead of the median. The totals row under 25 latency, rate and lag charts is hidden. The ARM template version tag is corrected.
- **1.4.0:** Pages & browser: the states and cities grid is clickable, with charts comparing the chosen state and city with the rest of the country and state.
- **1.3.0 and 1.3.1:** Pages & browser: the location grid has one row per country, and clicking a country opens its states and cities. Cities are the finest level Application Insights records.
- **1.2.2:** Wording only. User IDs are described as Dataverse record IDs, and examples are generic.
- **1.2.1:** Power Pages tab: page titles that differ only in capital letters are combined into one row.
- **1.2.0:** New User triage tab: a searchable user list and a click-through panel that compares one user with everyone else.
- **1.1.0:** Click-through drill-down on seven grids. Operation IDs and session IDs are shown so a single request or visit can be traced.
- **1.0.0:** First numbered release. Adds Callers, Export health, the Power Pages tab with funnel and top abandoned pages, previous-period comparison, save and update performance by table, and an alerts template.

## License

GPL-3.0. See [LICENSE](LICENSE). The place coordinates file in `data/` is derived from [GeoNames](https://www.geonames.org/) data and is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
