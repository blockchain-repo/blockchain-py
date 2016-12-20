"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/http-client-server-api.html
"""
from flask import current_app, request, Blueprint, make_response
from flask_restful import Resource, Api
from extend.localdb.restore.api.views.base import make_error
from extend.localdb.restore.utils import leveldb_utils, rethinkdb_utils
from extend.localdb.restore.utils.common_utils import deal_response, decode_data
from bigchaindb import config
node_collect = Blueprint('node_collect', __name__)
node_collect_api = Api(node_collect)

import rapidjson

ldb = leveldb_utils.LocaldbUtils()
rdb = rethinkdb_utils.RethinkdbUtils()

# Unfortunately I cannot find a reference to this decorator.
# This answer on SO is quite useful tho:
# - http://stackoverflow.com/a/13432373/597097


class NodeLocaldbCheck(Resource):

    def post(self):
        """API endpoint to check the Federation localdb.

        Return:
            A ``json stream``
        """

        req = request.get_json(force=True)
        if not req:
            return make_error(400, 'Invalid parameters')
        target = req['target']
        if target and target == 'check':
            can_access = ldb.check_conn_free(close_flag=True)
            response = {
                "free": True,
                "desc": 'can access the node localdb data.'
            }
            if not can_access:
                response['free'] = False
                response['desc'] = 'node localdb dirs is busy or not exist!'
            compress = config['restore_server']['compress']
            if compress:
                print("node check response {}".format(response))
            response = deal_response(response, make_response, compress=compress)
            return response
        else:
            return make_error(400, 'Invalid parameters')


class NodeBaseInfoApi(Resource):
    def post(self):
        """API endpoint to get the Federation local db info.

        Return:
            A ``json stream``
        """

        req = request.get_json(force=True)
        if not req:
            return make_error(400, 'Invalid parameters')

        target = req['target']

        if target and target == 'node':
            compress = config['restore_server']['compress']
            response = ldb.get_restore_node_info()
            if compress:
                print("node info response {}".format(response))
            response = deal_response(response, make_response, compress=compress)
            return response
        else:
            return make_error(400, 'Invalid parameters')


class NodeBlockVotes(Resource):
    def post(self):
        """API endpoint to get the Federation local db info.

        Return:
            A ``json stream``
        """

        req = request.get_json(force=True)
        if not req:
            return make_error(400, 'Invalid parameters')

        current_block_num = req['current_block_num']
        if not isinstance(current_block_num,int):
            return make_error(400, 'Invalid parameters')

        response = ldb.get_restore_block_info(current_block_num)
        compress = config['restore_server']['compress']
        response = deal_response(response, make_response, compress=compress)
        if compress:
            print("block num={:<5} {}".format(current_block_num,response))
        return response


class NodeRreRestore(Resource):
    def post(self):
        """API endpoint to init the Federation rethinkdb.

        Return:
            A ``json stream``
        """
        req = request.get_json(force=True)
        if not req:
            return make_error(400, 'Invalid parameters')

        target = req['target']
        exist_db = False
        need_init = True
        reset_sent = False
        records_count = 0
        desc = ""
        if target and target == 'pre_restore':
            have_send_num = req['sent_num']
            db_name = req['db']
            clear = req['clear']
            fore_clear = req['fore_clear']
            exist_db = rdb.exists_database(db_name)
            if exist_db:
                records_count = rdb.get_count(table='bigchain', dbname=db_name)
                last_block_id = rdb.get_last_before_block_id(dbname=db_name)
                if have_send_num == records_count:
                    need_init = False
                    desc = "Cluster can go on recovering!"
                elif records_count == 0:
                    need_init = False
                    reset_sent = True
                    desc = "Cluster data is blank, will reset sent_num and go on recovering!"
                else:
                    # if !=, must init rethinkdb and central restore_header
                    sent_id = req['sent_id']
                    # avoid the interpurt, cause the lose one write records
                    if have_send_num >= 1 and have_send_num + 1 == records_count \
                            and sent_id == last_block_id:
                        need_init = False
                        desc = "Central sent records is ok and will go on!"
                    else:
                        need_init = True
                        desc = "Cluster db need init first!"
                    if clear:
                        rdb.clear(dbname=db_name)
                        reset_sent = True
                        need_init = False
                        desc = "Cluster db clear data and central need reset restore_header!"

                if fore_clear:
                    rdb.clear(dbname=db_name)
                    reset_sent = True
                    desc = "Cluster db fore clear!"

        response = {
            "exist_db": exist_db,
            "records_count": records_count,
            "need_init": need_init,  # init and clear, use fab init_unichain
            "reset_sent":reset_sent,
            "desc": desc
        }
        compress = config['restore_server']['compress']
        response = deal_response(response, make_response, compress=compress)
        return response


class NodeWriteRethinkdb(Resource):
    def post(self):
        """API endpoint to write the central localdb data to Federation rethinkdb.

        Return:
            A ``json stream``
        """

        req = request.data
        # b'' <==> len(req) == 0 <==> not req
        if not req:
            return make_error(400, 'Invalid parameters')

        req = decode_data(req, compress=True)

        insert_flag = True
        fail_msg = None
        target = req['target']
        if target and target == 'rethinkdb':
            block = req['block']
            votes = req['votes']
            if block:
                insert_block_result = rdb.write_block(block)
                if 'first_error' in insert_block_result.keys():
                    fail_msg = insert_block_result['first_error'][:30]
                    insert_block_result['first_error'] = None
                # {'replaced': 0, 'first_error': None, 'inserted': 0, 'unchanged': 0, 'deleted': 0, 'skipped': 0, 'errors': 1}
                if insert_block_result['inserted'] == 0:
                    print("The block\tid={} insert fail, may be Duplicate primary key or other".format(block['id']))
                    insert_flag = False
                # avoid lose data, single check
                if votes:
                    for (key, vote_val) in votes.items():
                        if not isinstance(vote_val, list):
                            votes = [vote_val]
                        for vote in votes:
                            insert_vote_result = rdb.write_vote(vote)
                            if insert_vote_result['inserted'] == 0:
                                print("The vote \tid={}insert fail, may be Duplicate primary key or other".format(vote['id']))
                                insert_flag = False
                            break
            else:
                insert_flag = False
        else:
            insert_flag = False

        response = {
            "op":'insert',
            "success":insert_flag,
            "msg":fail_msg
        }
        compress = config['restore_server']['compress']
        response = deal_response(response, make_response, compress=compress)
        return response


node_collect_api.add_resource(NodeLocaldbCheck,
                             '/check',
                             strict_slashes=False)
node_collect_api.add_resource(NodeBaseInfoApi,
                             '/node',
                             strict_slashes=False)
node_collect_api.add_resource(NodeBlockVotes,
                             '/block',
                             strict_slashes=False)
node_collect_api.add_resource(NodeRreRestore,
                             '/pre_restore',
                             strict_slashes=False)
node_collect_api.add_resource(NodeWriteRethinkdb,
                             '/rethinkdb',
                             strict_slashes=False)
