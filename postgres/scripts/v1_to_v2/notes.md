## Old Database

Projects without results:

```
SELECT
    name
    project_id
FROM 
    projects
WHERE
    project_id not in (
        SELECT
            project_id
        FROM
            results
        GROUP BY
            project_id
    );

                           name                           | project_id 
----------------------------------------------------------+------------
 BAD IMAGERY Disease elimination on Bijagos islands 4     |       5873
 ERROR DUPLICATE Disease elimination on Bijagos islands 5 |       6069
 DUPLICATE: THIS ONE IS FALSEEliminate Malaria: Cambodia  |       6494
 Test Project                                             |       7480
 Support demining effort : Chad 4                         |      10464
 BENNI TEST                                               |      10604
 TEST Swipe to help MSF in Douentza, Mali 1               |      13506
 test task, do not activate                               |      13525
 End Malaria: Angola 15X                                  |      13533
 TEST: New import worker                                  |      13539
 TEST: New import worker 2                                |      13541
 Map Philippines 2                                        |      13591
 Map Philippines 3                                        |      13593
 Map Philippines 2                                        |      13595
 Map Philippines 3                                        |      13597
 Colombia RefugeeResponse4                                |      13603
 Colombia RefugeeResponse5                                |      13605
 Colombia RefugeeResponse6                                |      13607
 Colombia RefugeeResponse7                                |      13609
 Colombia RefugeeResponse8                                |      13611
 Map Philippines 8                                        |      13613
 Sur Colombia                                             |      13615
 Sur Colombia 11                                          |      13627
 Map Philippines 16                                       |      13637
 Map Philippines 17                                       |      13639
 Map Philippines 18                                       |      13641
 Map Philippines 16                                       |      13645
 MapPH Bukindon North                                     |      13647
 MapPH Bukindon North                                     |      13649
 MapPH Bukindon Central                                   |      13651
(30 rows)
```



Groups without project

```
SELECT
    count(*) 
FROM
    groups
WHERE
    project_id not in (
        SELECT
            project_id
        FROM
            projects
    )

 count 
-------
  4298
(1 row)
```


Tasks without project

```sql
SELECT
    count(*) 
FROM
    tasks
WHERE
    project_id not in (
        SELECT
            project_id
        FROM
            projects
    )

 count
--------
 914127
(1 row)
```


Results without user

```
SELECT
    count(*)  
FROM 
    results 
WHERE 
    user_id not in ( 
        SELECT 
            user_id 
        FROM 
            users 
    );

 count
-------
 80989
(1 row)
```


Anzahl an Results:

```
select count(*) from results;

  count
----------
 20538723
(1 row
```

---


## New Database

```
SELECT
    name, project_id
FROM
    projects
WHERE
    geom is NULL;

 Missing Maps Malawi       | 798
 Southern Malawi Districts | 922
 Map Philippines 15        | 13635
 Map Philippines 13        | 13631
 (4 rows)
```


Anzahl an Tasks:
37 286 140






114 Results in der Produktion database
