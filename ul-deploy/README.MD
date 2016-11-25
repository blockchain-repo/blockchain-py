#clusterdeploy
###shell+fabric3+python3


##部署统一入口
bash build.sh $1
Options:
    h|-h|help|-help usage help
    env_check       before setup, check tools already in env
    first_setup     first setup:install base tools|depends libs|rethinkdb|bigchaindb|unichain
    server_check    after setup|update, check servers in cluster nodes are running
    
    update          updte setup:update unichain
    configure       rethinkdb|bigchaindb|unichain, start cluster nodes server
    reconfigure     rethinkdb|bigchaindb|unichain, restart cluster nodes server
    start_all       start all cluster nodes
    stop_all        stop  sll cluster nodes
    start_node      start signal cluster node, params same as start_node.sh
    stop_node       stop  signal cluster node, params same as stop_node.sh


##文件说明
conf/blockchain-nodes                           为集群节点的信息，每行一条。格式: user@host:port  password
script/fabfile.py                               读取host信息与用户指定参数，进行集群、节点行为控制。
script/hostlist.py                              生成可读取的hostlist
script/create_rethinkdb_conf.py                 生成rethinkdb配置
conf/template/rethinkdb.conf.template           rethinkdb配置模板
script/write_keypairs_file.py                   生成一套密钥
script/clusterize_confiles.py                   生成一套集群的unichain配置

###综合脚本
script/run_init_env.sh                          初始化中控机,检查并安装python3|fabric3
script/run_first_setup.sh                       初次安装部署启动, node个数从配置文件中读取
script/run_update.sh                            更新 [重新分配密钥drop table], node个数从配置文件中读取
                                                TODO:轻量级update ??密钥变了额
script/run_env_check.sh                         安装前检查环境是否可用
script/run_server_check.sh                      安装后检查安装服务是否正常

###部署脚本
script/blockchain_nodes_conf_util.sh            blockchain_nodes配置文件校验\读取
check_tools_util.sh                             基础工具检查公用方法
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
