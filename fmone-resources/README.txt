In this folder we have the pipelines that can be created with FMone. For a brief explanation of them:

- regional_mongo: params (specific region, nslaves)
It creates a MongoDB instance in the region we specify and spins up nslaves
on that same region that send their metrics. It can also be used to evaluate
the overhead of FMone. This can be compared to an scenario
where there is no monitoring at all to evaluate overhead of FMone
- aggregate: (specific region, nslaves) (Note: This needs a mongoDB instance called mongocloud running)
It has 4 elements. The first 2 are groups of agents that are going to get
metrics at docker and host level. This metrics are going to be sent to the
third element which is going to be RabbitMQ. Then the fourth element is going
to be an fmone agent that is going to pull the messages from the queue and
insert them into mongocloud instance
- central_ycsb: (region_for_mongo, nslaves_for_all_cluster )
This is going to create a mongoDB in one region we specify and agents for host
and docker in all the slaves of the cluster. We need to specify anyway the nslaves.
This is used together with a CassandraDB in the central region for the evaluation
of FMone
- centralycsb_kafka: (nslaves_for_all_cluster)
This is just going to create a series of slaves across the cluster collecting
docker and host metrics and publishing them to a Kafka queue. The kafka
queue is created though the DCOS CLI. This installation will give you
some broker addresses that we have to include in the centralycsb JSON