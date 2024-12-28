---
title: Mitohondrion database stats
---

<table border="3" style="width:100%">
 <tr>
    <td>
        Mutations: <Value data = {variants_count} column = count_result />
    </td>
    <td>
        Samples: <Value data = {sample_count} column = count_result />
    </td>
 </tr>
  <tr>
    <td>
        Min GC (%): <Value data = {min_gc} column = gc_content />
    </td>
    <td>
        Max GC (%): <Value data = {max_gc} column = gc_content />
    </td>
 </tr>
   <tr>
    <td>
        Samples with total length and N50 difference: <Value data = {diff} column = diff />
    </td>
 </tr>
</table>

<Dropdown name=quantity>
    <DropdownOption value=10 valueLabel="10"/>
    <DropdownOption value=20/>
    <DropdownOption value=50/>
    <DropdownOption value=100/>
</Dropdown>

<BarChart
    data={top_mutations}
    title="Top mutations"
    x=allele
    y=count
/>

<table border="3" style="width:100%">
 <tr>
    <td style="width:50%">
        Search sample
    </td>
    <td>
        Last uploaded
    </td>
 </tr>
  <tr>
    <td>
        <TextInput
            name=sample_name
            title=""/>
    </td>
    <td>
        <Value data = {last_name} column = name />
    </td>
 </tr>
 <tr>
    <td>
Found <Value data = {sample_mutations} column = mutation_count /> mutations
    </td>
    <td>
Found <Value data = {last_sample_mutations} column = mutation_count /> mutations
    </td>
 </tr>
 <tr>
    <td>
Dangerous: <Value data = {sample_danger} column = associateddiseases emptySet = pass emptyMessage = "no" />
    </td>
    <td>
Dangerous: <Value data = {last_sample_danger} column = associateddiseases emptySet = pass emptyMessage = "no" />
    </td>
 </tr>
 <tr>
    <td>
<DataTable data={sample_mutations_list}/>
    </td>
    <td>
<DataTable data={last_sample_mutations_list}/>
    </td>
 </tr>
</table>

```sql variants_count
  select
      count(*) as count_result
  from mutations.mutations;
```

```sql sample_count
  select
      COUNT(DISTINCT name)  as count_result
  from mutations.samples;
```

```sql min_gc
SELECT MIN(gc_content) AS gc_content FROM mutations.quast;
```

```sql max_gc
SELECT MAX(gc_content) AS gc_content FROM mutations.quast;
```

```sql diff
  select
      count(*) as diff
  from mutations.quast
  where not total_length == n50;
```

```sql n_mutations
  select
      count(*)
  from mutations.mutations
  where allele like '%N%';
```

```sql top_mutations
  select 
      count,
      allele
  from mutations.mutations
  order by count desc
  limit ${inputs.quantity.value}
```


```sql sample_mutations
SELECT COUNT(mutation) AS mutation_count FROM mutations.samples WHERE name = (SELECT name FROM samples WHERE name like '${inputs.sample_name}%' LIMIT 1);
```

```sql sample_danger
SELECT * FROM mutations JOIN samples ON mutations.id = samples.mutation WHERE samples.name = (SELECT name FROM samples WHERE name like '${inputs.sample_name}%' LIMIT 1) AND associateddiseases IS NOT NULL;
```

```sql sample_mutations_list
SELECT allele FROM mutations JOIN samples ON mutations.id = samples.mutation WHERE samples.name = (SELECT name FROM samples WHERE name like '${inputs.sample_name}%' LIMIT 1);
```

```sql last_name
SELECT name FROM mutations.samples ORDER BY id DESC LIMIT 1;
```

```sql last_sample_mutations
SELECT COUNT(mutation) AS mutation_count FROM mutations.samples WHERE name = (SELECT name FROM samples ORDER BY id DESC LIMIT 1);
```

```sql last_sample_danger
SELECT * FROM mutations JOIN samples ON mutations.id = samples.mutation WHERE samples.name = (SELECT name FROM samples ORDER BY id DESC LIMIT 1) AND associateddiseases IS NOT NULL;
```

```sql last_sample_mutations_list
SELECT allele FROM mutations JOIN samples ON mutations.id = samples.mutation WHERE samples.name = (SELECT name FROM samples ORDER BY id DESC LIMIT 1);
```
