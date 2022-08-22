# Beholder
Beholder is an open source data observability solution. At the time of writing Beholder only supports AWS, Spark and Hive.

```mermaid
flowchart TD
    %% AWS resources
    subgraph AWS
        S3
        EVENT[EventBridge]
        
        S3 --> |Send Event Notifications| EVENT 
        EVENT --> |Push Filtered Events| SQS
    end
    
    subgraph DP[Data Platform]
        subgraph CATALOG[Catalog]
            HIVE[Hive]
        end
        subgraph COMPUTE[Compute]
            SPARK[Spark]
            PRESTO[Presto/Athena/Trino]
        end
    end
    
    subgraph Beholder
        PSQL[(PostgreSQL DB)]
        TSQL[(Timeseries DB)]
        BACK[Backend Application]
        WEB[Webserver]
    
        BACK --> |Push metrics| TSQL
        BACK <--> |Get & Push rules| PSQL
        WEB --> |Get data, \nsubmit new rules| BACK
        WEB --> TSQL
    end
    AWS --> |Publish notifications to subscribers| BACK
    BACK --> |Get information about notifications, \nlaunch jobs for stats| DP
```

## Components
### Beholder
Beholder is the core application with both a front- and backend. The frontend is responsible for the display of data as
well as allowing users to define rules to be evaluated on datasets, whereas the backend is the center of communication 
between the various services.

#### Metrics
Beholder (will) calculate the following metrics for each event by default:
- Bytes written
- Rows written

In addition, there are extra metrics you can define:
- Aggregations by key
- Cardinality of column(s)
- Null count

#### Alerting
If an anomaly is detected Beholder can dispatch alerts in order to notify users and enable them to proactively investigate.

#### Terraform support
TBD

### PostgreSQL
Postgres is used to store both transactional and time series data .

### AWS
Beholder currently only supports AWS as cloud platform. It requires S3 object notifications to be setup in order to take
and event driven approach in calculating metrics. Without it, beholder can run on a time-based schedule. Though this is
not recommended. You can define filters to determine when you want Beholder to take action.

### Data Catalog
Beholder will leverage a data catalog to enrich the observed data. For instance, if the location of an event is not known
in the catalog it is able to dispatch an alert for this. If you only use schedule based observations, it will use the catalog
to know what to monitor

### Compute
Beholder itself does not compute the metrics, it will rely on other tools to do so, such as Spark or Presto.

## How it works
### Event driven
```mermaid
flowchart TD
    subgraph AWS
        WRITER[Writer]
        S3
        EVENT[EventBridge]
        SQS
        
        WRITER --> |Application writes to a bucket| S3
        S3 --> |Publishes a notification for each file written| EVENT
        EVENT --> |Applies filters defined by user, forwards message| SQS
    end
    
    SQS --> |Polls for new events| BH1
    
    subgraph BEHOLDER[Beholder]
        BH1[Beholder]
        PSQL[PostgreSQL]
        DC[Data Catalog]
        DCEXISTS{Is the location \npresent in the catalog?}
            
        BH1 --> DCEXISTS
        DCEXISTS --> Y1[Yes] --> |Beholder pulls data from catalog| DC --> |Get rules| PSQL
        DCEXISTS --> N1[No] ---> |Get rules| PSQL
    end
    
    PSQL --> |Submit job based on rules| C1
    
    subgraph COMPUTE[Compute]
        C1[Job]
        CSQS[SQS]
        
        C1 --> |Publish job results| CSQS
    end
    
    CSQS --> |Consume job results| BH2
    
    subgraph BEHOLDER2[Beholder]
        BH2[Beholder]
        TSQL[PostgreSQL\nTimeseries tables]
        ALERT{Alert?}
        
        BH2 --> |Push job results| TSQL
        BH2 --> |Evalute results| ALERT
        ALERT --> Y2[Yes] --> AS[Submit Alert]
        ALERT --> N2[No]
    end
```