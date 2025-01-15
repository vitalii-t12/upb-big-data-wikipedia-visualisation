#!/bin/bash

# Format HDFS
if [ ! -d "/hadoop/dfs/name" ]; then
    echo "Formatting HDFS..."
    $HADOOP_HOME/bin/hdfs namenode -format
fi

# Start Namenode and Datanode
$HADOOP_HOME/sbin/start-dfs.sh

# Keep container running
tail -f /dev/null
