#clusterdeploy
###shell+fabric+python

##文件说明
conf/blockchain-nodes                           为集群节点的信息，每行一条。格式: user@host:port  password
script/fabfile.py                               读取host信息与用户指定参数，进行集群、节点行为控制。
script/hostlist.py                              生成可读取的hostlist
script/create_rethinkdb_conf.py                 生成rethinkdb配置
conf/template/rethinkdb.conf.template           rethinkdb配置模板
script/write_keypairs_file.py                   生成一套密钥
script/clusterize_confiles.py                   生成一套集群的unichain配置

###综合脚本
script/first_setup.sh $NUM_NODES                初次安装部署启动
script/update.sh $NUM_NODES                     更新 [重新分配密钥drop table] TODO:轻量级update ??密钥变了额

###部署脚本
script/install_base_software.sh                 安装依赖
script/install_rethinkdb.sh                     安装rethinkdb
script/configure_rethinkdb.sh                   配置rethinkdb
script/install_unichain_from_git_archive.sh     安装unichain
script/configure_unichain.sh $NUM_NODES         配置unichain

###控制脚本
script/clustercontrol.sh                        集群控制

./clustercontrol.sh  start                      启动整个集群
./clustercontrol.sh  stop                       关闭整个集群

目前unichain没有提供service，stop和restart command也在TODO#357.
脚本采用screen和kill来达到start和stop，若未正常启动可多次运行[关闭-启动]脚本

startnode.sh & stopnode.sh                      单节点控制

./startnode.sh -h user@host -p password   [ -r ]  [ -u ]   启动指定的节点。 -r 启动 该节点上的rethinkdb ，-u 启动该节点上的unichain

./stopnode.sh  -h user@host -p password   [ -r ]  [ -u ]   关闭指定的节点。 -r 关闭 该节点上的rethinkdb ，-u 关闭该节点上的unichain
