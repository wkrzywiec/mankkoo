```bash
docker cp migration/streams.csv postgres:streams.csv
```


```sql
psql -U postgres -d test
COPY streams FROM '/streams.csv' WITH (FORMAT csv, ESCAPE '\');
```