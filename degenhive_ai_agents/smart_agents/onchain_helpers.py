import requests, json, argparse, asyncio
from typing import Union, Tuple
# from pysui.sui.sui_builders.exec_builders import MergeCoin, SplitCoin, ExecuteTransaction
# from pysui.sui.sui_builders.get_builders import GetAllCoinBalances, GetObjectsOwnedByAddress

# from pysui.sui.sui_clients.transaction import SuiTransactionAsync
# from pysui.sui.sui_builders.get_builders import GetCoins
import binascii
from pysui import SyncClient, SuiConfig, handle_result, ObjectID, SuiAddress, AsyncClient
from pysui.sui.sui_txn import SyncTransaction, AsyncTransaction

from pysui.abstracts import SignatureScheme
from pysui.sui.sui_types import bcs
from pysui.sui.sui_utils import partition
from pysui.sui.sui_txresults.single_tx import SuiCoinObjects, SuiCoinObject
from pysui.sui.sui_txresults.complex_tx import TxInspectionResult
from pysui.abstracts import SignatureScheme

import canoser 

from pysui.sui.sui_crypto import (
    SuiAddress,
    as_keystrings,
    create_new_address,
    emphemeral_keys_and_addresses,
    keypair_from_keystring,
    load_keys_and_addresses,
    recover_key_and_address,
    gen_mnemonic_phrase,
)

from pysui.sui.sui_types.scalars import (
    ObjectID,
    SuiBoolean,
    SuiInteger,
    SuiString,
    SuiU128,
    SuiU16,
    SuiU256,
    SuiU32,
    SuiU64,
    SuiU8,
)
from pysui.sui.sui_constants import (
    SUI_BECH32_HRP,
    PRIVATE_KEY_BYTE_LEN,
    SCHEME_PRIVATE_KEY_BYTE_LEN,
    SUI_HEX_ADDRESS_STRING_LEN,
    SUI_KEYPAIR_LEN,
    ED25519_DEFAULT_KEYPATH,
    ED25519_PUBLICKEY_BYTES_LEN,
    SECP256K1_DEFAULT_KEYPATH,
    SECP256K1_PUBLICKEY_BYTES_LEN,
    SECP256R1_DEFAULT_KEYPATH,
)

# Define ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'

CLOCK = "0x6"
SUI_SYSTEM_STATE = "0x5"
SUI_TYPE = "0x2::sui::SUI"



def color_print(text, color_code):
    END_COLOR = '\033[0m'  # Reset color code
    print(color_code + text + END_COLOR)


class HiveChronicleUserInfo(canoser.Struct):
    _fields = [
        ('active_epoch', canoser.Uint64),
        ('max_entropy_for_cur_epoch', canoser.Uint64),
        ('remaining_entropy', canoser.Uint64),
        ('total_hive_gems', canoser.Uint64),
        ('usable_hive_gems', canoser.Uint64),
        ('entropy_inbound', canoser.Uint64),
        ('entropy_outbound', canoser.Uint64),
        ('total_bees_farmed', canoser.Uint64),
        ('simulated_bees_from_entropy', canoser.Uint64),
        ('rebuzzes_count', canoser.Uint64),
        ('noise_buzzes_count', canoser.Uint64),
        ('last_noise_epoch', canoser.Uint64),
        ('noise_count', canoser.Uint64),
        ('chronicle_buzzes_count', canoser.Uint64),
        ('last_chronicle_epoch', canoser.Uint64),
        ('chronicle_count', canoser.Uint64),
        ('buzz_chains_count', canoser.Uint64),
        ('last_buzz_epoch', canoser.Uint64),
        ('buzz_count', canoser.Uint64),
        ('subscribers_only', canoser.Uint8),
        ('infusion_buzzes_count', canoser.Uint64),
        ('infusion_count', canoser.Uint64),        

    ]


class TimeStreamUserInfo(canoser.Struct):
    _fields = [
        ('stream_epoch', canoser.Uint64),
        ('points', canoser.Uint64),
        ('flag', bool),
        ('sui_bidded', canoser.Uint64),
        ('buzz_cost_in_hive', canoser.Uint64),
        ('access_type', canoser.Uint8),
        # ('collection_name', str),
        ('user_total_points', canoser.Uint64),
        ('hive_earned', canoser.Uint64),
        ('bees_earned', canoser.Uint64),
        ('rewards_final', bool),
        ('total_points_sum', canoser.Uint128),
    ]


# 0-------1-------- TIME STREAM GLOBAL STATE INFO ---------1--------0

class TimeStreamConfigParams(canoser.Struct):
    _fields = [
        ('are_live', bool),
        ('cur_auction_stream', canoser.Uint64),
        ('stream_init_ms', canoser.Uint64),
        ('first_rank_assets_limit', canoser.Uint64),
        ('second_rank_assets_limit', canoser.Uint64),
        ('third_rank_assets_limit', canoser.Uint64),

        ('max_streams_per_slot', canoser.Uint64),
        ('choosen_buzzes_count', canoser.Uint64),
        ('hive_per_ad_slot', canoser.Uint64),
        ('bees_per_ad_slot', canoser.Uint64),
        ('min_bid_limit', canoser.Uint64),
        ('tax_on_bid', canoser.Uint64),
    ]

class TimeStreamerInfo(canoser.Struct):
    _fields = [
        # ('profileID', canoser.RustOptional(canoser.StrT)),
        # ('streamer_name', canoser.RustOptional(str)),
        ('streams_count', canoser.Uint64),
        ('access_type', canoser.Uint8),
        ('sui_per_buzz', canoser.Uint64),
        ('buzz_cost_in_hive', canoser.Uint64),
        ('remaining_buzzes_count', canoser.Uint64),
        ('engagement_points', canoser.Uint128),
        ('collection_name', str),
    ]


class LeadingBidsInfo(canoser.Struct):
    _fields = [
        ('o_profile_addr', SuiAddress),
        ('o_bid_amt', canoser.Uint64),
        ('s_profile_addr', canoser.Uint64),
        ('s_bid_amt', canoser.Uint64),
        ('t_profile_addr', canoser.Uint64),
        ('t_bid_amt', canoser.Uint64),
    ]

class TimeStreamPolInfo(canoser.Struct):
    _fields = [
        ('bid_pool', canoser.Uint64),
        ('sui_avail_for_pol', canoser.Uint64)
    ]


class TimeStreamEngagementScoresState(canoser.Struct):
    _fields = [
        ('hive_gems_available', canoser.Uint64),
        ('hive_per_ad_slot', canoser.Uint64),
        ('bees_available', canoser.Uint64),
        ('bees_per_ad_slot', canoser.Uint64),
        ('total_sui_bidded', canoser.Uint64),
        ('ongoing_points_sum', canoser.Uint128),
        ('user_points_score', canoser.Uint64),
        ('leading_bid_amt', canoser.Uint64),
        ('points_per_sui_bidded', canoser.Uint128),
    ]

class BeeFarmSnapshotInfo(canoser.Struct):
    _fields = [
        ('epoch', canoser.Uint64),
        ('bees_distributed', canoser.Uint64),
        ('entropy_during_epoch', canoser.Uint64),
        ('bees_per_entropy', SuiU256),
        ('bees_burnt', canoser.Uint64),
    ]



"""
Initialize a new account by generating a mnemonic phrase and recovering the keypair and address
"""
def initialize_new_account(rpc_url):

    mnemonic = gen_mnemonic_phrase(12)
    mnemonic2, keyPair, suiAddress = recover_key_and_address(SignatureScheme.ED25519, mnemonic, ED25519_DEFAULT_KEYPATH)

    private_key_bytes = keyPair.private_key.key_bytes
    private_key_hex_string = binascii.hexlify(private_key_bytes).decode('utf-8')

    color_print("\nInitialized new account with the following details:", GREEN)
    suiClient = SuiConfig.user_config(
            # Required
            rpc_url=rpc_url,
            # rpc_url="https://fullnode.testnet.sui.io:443/",
            # Required. First entry becomes the 'active-address'
            # Must be a valid Sui keystring (i.e. 'key_type_flag | private_key_seed' )
            # prv_keys=["AOvsnh0guUmbheI3MHqWL/nFBABXkamx+UqwsrMRbGMt"],
        ######################################################################################################################################################################################################################################
            prv_keys=[ { 'wallet_key': "0x" + private_key_hex_string, 'key_scheme': SignatureScheme.ED25519}],
        ######################################################################################################################################################################################################################################
        )

    address = suiClient.active_address.owner
    print(f"mnemonic: {mnemonic}")
    print(f"address: {address}")
    print(f"private_key_hex_string: {private_key_hex_string}")

    return mnemonic, private_key_hex_string, address



def getSuiSyncClient(rpc_url, private_key_hex_string ):
    print(f"rpc_url: {rpc_url}")
    suiClient = SyncClient(SuiConfig.user_config(
            rpc_url=rpc_url,
            prv_keys=[{'wallet_key': "0x" + private_key_hex_string, 'key_scheme': SignatureScheme.ED25519}],
        ))
    print(suiClient)
    return suiClient


async def kraftHiveProfileTx(rpc_url, private_key_hex_string, protocol_config, name, bio) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     

    print(suiClient._config.active_address)
    # return

    txBlock = SyncTransaction(client=suiClient)

    # spendable_sui = await getSpendableSui(suiClient, txBlock, 0)

    spendable_sui = txBlock.move_call(
        target=f"0x2::coin::zero",
        arguments=[],
        type_arguments=[SUI_TYPE],
    )

    txBlock.move_call(
        target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_chronicles::kraft_hive_profile",
        arguments=[
                   ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]),
                   ObjectID(CLOCK),
                   ObjectID(SUI_SYSTEM_STATE),
                   ObjectID(protocol_config["DSUI_VAULT"]),
                   ObjectID(protocol_config["PROFILE_MAPPING_STORE"]),
                   ObjectID(protocol_config["HIVE_MANAGER"]),
                   ObjectID(protocol_config["DSUI_DISPERSER"]),
                   spendable_sui,
                   SuiString(name),
                   SuiString(bio),
            ],
            type_arguments=[],
        )

    # txBlock.transfer_sui(recipient=SuiAddress("0xa23060b3c164838b892eaaea10c41cd95c13c7da32bd8f6b5d584da5251f9b77"), from_coin=ObjectID("0x01fa15f663674dd3a16e897f287098bff1a07b174b5b7245233cecde77faa904"), amount=SuiInteger(10000))
    # txBlock.transfer_objects(recipient=SuiAddress("0xa23060b3c164838b892eaaea10c41cd95c13c7da32bd8f6b5d584da5251f9b77"), transfers=[ObjectID("0x5e8e6e8198d8b203f343b8ef190ccd4621bcf6810b5599e10ff9f3ba887a71f1")])


#   recipient: Union[ObjectID, SuiAddress],
#         from_coin: Union[str, ObjectID, ObjectRead, SuiCoinObject, bcs.Argument],
#         amount: Optional[Union[
    simulation_response, txBlock = simulate_tx(txBlock)

    if (simulation_response):
        print(f"Simulation successful")

        # res = txBlock.execute(gas_budget="10000000")
        # kind = txBlock.raw_kind()
        # print(f"Kind: {kind}")

        exec_result = handle_result(txBlock.execute(gas_budget="100000000" ))
        print(f"Result: {exec_result.to_json()}")
        # print(res.result_string)
        # print(res.result_string.to_dict())
        # print(f"Result: {res.to_json()}")
    
    else: 
        print(f"Simulation failed")



async def getSpendableSui(client: AsyncClient, txBlock: AsyncTransaction, spendableVal):
    objects = (await client.get_objects(fetch_all=True)).result_data.to_dict()["data"]
    # print('got objects')
    # print(objects)
    sui_objects = []

    for obj in objects:
        if obj['type'].startswith('0x2::coin::Coin'):
            identifier = obj['type'][obj['type'].find('<')+1:-1]
            symbol = get_symbol(identifier)
            if symbol == 'SUI':
                sui_objects.append(obj['objectId'])


    if len(sui_objects) == 1:
        print(f"Only one coin Object found")
        print(f"spendableVal: {spendableVal}")
        print((txBlock.gas).to_json())
        return await txBlock.split_coin(coin=txBlock.gas, amounts=[0])
    # else:
    #     print(f"{len(coinVec)} coins of type {type} found")
    #     coin = coinVec[0]
    #     coin_id = coin.object_id
    #     coin_amount = coin.amount
    #     if coin_amount > spendableVal:
    #         await txer.merge_coins(merge_to=coin_id, merge_from=[coin.object_id])
    #         return spendableVal
    #     else:
    #         return coin_amount



async def objects_joined(client: AsyncClient, txb: AsyncTransaction) -> Tuple[AsyncTransaction, dict]:
    # weakness: if a coin identifier is A::B::C, C must be unique for a type of coin (each coin has a different symbol). else this fails.
    objects = (await client.get_objects(fetch_all=True)).result_data.to_dict()["data"]
    print('got objects')
    coin_objects = {}
    join_objects = {}
    for obj in objects:
        if obj['type'].startswith('0x2::coin::Coin'):
            identifier = obj['type'][obj['type'].find('<')+1:-1]
            symbol = get_symbol(identifier)
            if symbol == 'SUI':
                continue
            if symbol in coin_objects:
                join_objects[symbol].append(obj['objectId'])
            else:
                coin_objects[symbol] = obj['objectId']
                join_objects[symbol] = []
    # print(json.dumps(coin_objects, indent=4))
    # print(json.dumps(join_objects, indent=4))

    for key, value in coin_objects.items():
        if len(join_objects[key]) > 0:
            print(f'joining {key} coins')
            await txb.merge_coins(merge_to=value, merge_from=join_objects[key])
    return txb, coin_objects


def get_symbol(identifier):
    if '::LP<' in identifier:
        coins = identifier[identifier.find('::LP<') + 5:-1].split(',')
        coins = [str(coin).strip() for coin in coins]
        symbol = "-".join([get_symbol(coin) for coin in coins])
    else:
        symbol = identifier.split('::')[-1].split('>')[0]

    return symbol


def simulate_tx(txb: SyncTransaction): 
    simulation = txb.inspect_all()
    simulation = simulation.to_json()    
    simulation_json = json.loads(simulation)

    if simulation_json["effects"]["status"]["status"] == "success":
        print(f"Transaction will be successful")
        return True, txb
    else:
        print(f"Transaction will fail")
        return False, txb


"""
Execute a transaction to like a stream buzz Post
"""
async def like_stream_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, stream_index, stream_inner_index) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
    txBlock = SyncTransaction(client=suiClient)
    txBlock.move_call(
        target=f"{protocol_config["TWO_TOKEN_AMM_PACKAGE"]}::bee_trade::like_stream_buzz",
        arguments=[
                   ObjectID(CLOCK),
                   ObjectID(protocol_config["PROFILE_MAPPING_STORE"]),
                   ObjectID(protocol_config["HIVE_MANAGER"]),
                   ObjectID(protocol_config["HIVE_VAULT"]),
                   ObjectID(protocol_config["BEE_CAP"]),
                   ObjectID(protocol_config["BEE_TOKEN_POLICY"]),
                     ObjectID(user_profile),
                    SuiU64(stream_index),
                    SuiU64(stream_inner_index),
            ],
            type_arguments=[SUI_TYPE],
        )

    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        print(txBlock)
        # res = txBlock.execute(gas_budget="10000000")
        kind = txBlock.raw_kind()
        print(f"Kind: {kind}")

        exec_result = handle_result(txBlock.execute(gas_budget="10000000"))
        print(f"Result: {exec_result.to_json()}")
        # print(res.result_string)
        # print(res.result_string.to_dict())
        # print(f"Result: {res.to_json()}")    
    else: 
        print(f"Simulation failed")


"""
Execute a transaction to upvote a Hive Buzz Post
"""
async def upvote_hive_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, poster_profile, stream_index, stream_inner_index) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
    txBlock = SyncTransaction(client=suiClient)
    txBlock.move_call(
        target=f"{protocol_config["TWO_TOKEN_AMM_PACKAGE"]}::bee_trade::upvote_hive_buzz",
        arguments=[
                     ObjectID(CLOCK),
                        ObjectID(protocol_config["PROFILE_MAPPING_STORE"]),
                        ObjectID(protocol_config["HIVE_MANAGER"]),
                        ObjectID(protocol_config["HIVE_VAULT"]),
                        ObjectID(user_profile),
                        ObjectID(protocol_config["BEE_CAP"]),
                        ObjectID(protocol_config["BEE_TOKEN_POLICY"]),
                        ObjectID(poster_profile),
                        SuiU64(stream_index),
                        SuiU64(stream_inner_index),
            ],
            type_arguments=[SUI_TYPE],
        )

    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        print(txBlock)
        # res = txBlock.execute(gas_budget="10000000")
        kind = txBlock.raw_kind()
        print(f"Kind: {kind}")

        exec_result = handle_result(txBlock.execute(gas_budget="10000000"))
        print(f"Result: {exec_result.to_json()}")
        # print(res.result_string)
        # print(res.result_string.to_dict())
        # print(f"Result: {res.to_json()}")    
    else: 
        print(f"Simulation failed")
    





















 
# async def objects_joined(client: SuiClient, txb: SuiTransactionAsync) -> Tuple[SuiTransactionAsync, dict]:
#     # weakness: if a coin identifier is A::B::C, C must be unique for a type of coin (each coin has a different symbol). else this fails.
#     objects = (await client.get_objects(fetch_all=True)).result_data.to_dict()["data"]
#     print('got objects')
#     coin_objects = {}
#     join_objects = {}
#     for obj in objects:
#         if obj['type'].startswith('0x2::coin::Coin'):
#             identifier = obj['type'][obj['type'].find('<')+1:-1]
#             symbol = get_symbol(identifier)
#             if symbol == 'SUI':
#                 continue
#             if symbol in coin_objects:
#                 join_objects[symbol].append(obj['objectId'])
#             else:
#                 coin_objects[symbol] = obj['objectId']
#                 join_objects[symbol] = []
#     # print(json.dumps(coin_objects, indent=4))
#     # print(json.dumps(join_objects, indent=4))

#     for key, value in coin_objects.items():
#         if len(join_objects[key]) > 0:
#             print(f'joining {key} coins')
#             await txb.merge_coins(merge_to=value, merge_from=join_objects[key])
#     return txb, coin_objects






# --------------------- x -----------------------------------
# --------------------- x -----------------------------------
# --------------------- x -----------------------------------

"""
Fetch HiveChronicle state information for a user profile from chain 
"""
def getHiveChronicleInfo(rpc_url, private_key_hex_string, protocol_config, user_profile) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_chronicles::get_hive_chronicle_for_profile",
            arguments=[
                        ObjectID(CLOCK),
                            ObjectID(protocol_config["HIVE_MANAGER"]),
                            ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]),
                            ObjectID(user_profile),
                ],
                type_arguments=[],
            )
        simulation = txBlock.inspect_all()
        simulation_json = json.loads(simulation.to_json())
        hive_chronicle_info = HiveChronicleUserInfo.deserialize( simulation_json["results"][0]["returnValues"][0][0] + simulation_json["results"][0]["returnValues"][1][0]
                                            + simulation_json["results"][0]["returnValues"][2][0] + simulation_json["results"][0]["returnValues"][3][0]
                                                + simulation_json["results"][0]["returnValues"][4][0] + simulation_json["results"][0]["returnValues"][5][0]
                                                    + simulation_json["results"][0]["returnValues"][6][0] + simulation_json["results"][0]["returnValues"][7][0]
                                                    + simulation_json["results"][0]["returnValues"][8][0] + simulation_json["results"][0]["returnValues"][9][0]
                                                    + simulation_json["results"][0]["returnValues"][10][0] + simulation_json["results"][0]["returnValues"][11][0]
                                                    + simulation_json["results"][0]["returnValues"][12][0] + simulation_json["results"][0]["returnValues"][13][0]
                                                    + simulation_json["results"][0]["returnValues"][14][0] + simulation_json["results"][0]["returnValues"][15][0]
                                                    + simulation_json["results"][0]["returnValues"][16][0] + simulation_json["results"][0]["returnValues"][17][0]
                                                    + simulation_json["results"][0]["returnValues"][18][0] + simulation_json["results"][0]["returnValues"][19][0]
                                                    + simulation_json["results"][0]["returnValues"][20][0] + simulation_json["results"][0]["returnValues"][21][0]
                                                ) 
        return hive_chronicle_info
    except Exception as e:
        color_print(f"onchain_helpers/getHiveChronicleInfo: Error -  {e}", RED)
        return None

"""
Fetch a profile's Time-Stream state information from chain 
"""
def getTimeStreamStateForProfileInfo(rpc_url, private_key_hex_string, protocol_config, user_profile) :
    user_profile = "0xe24e9496973e907453b308b940015a269ff16da0d720342e967aab6d8600f4dc"
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_points_for_profile",
            arguments=[    ObjectID(protocol_config["HIVE_VAULT"]),
                            SuiAddress(user_profile),
                ],
                type_arguments=[SUI_TYPE],
            )
        simulation = txBlock.inspect_all()
        simulation_json = json.loads(simulation.to_json())
        time_stream_state_info = TimeStreamUserInfo.deserialize( simulation_json["results"][0]["returnValues"][0][0] + simulation_json["results"][0]["returnValues"][1][0]
                                            + simulation_json["results"][0]["returnValues"][2][0] + simulation_json["results"][0]["returnValues"][3][0]
                                                + simulation_json["results"][0]["returnValues"][4][0] + simulation_json["results"][0]["returnValues"][5][0]
                                                    + simulation_json["results"][0]["returnValues"][6][0] + simulation_json["results"][0]["returnValues"][7][0]
                                                    + simulation_json["results"][0]["returnValues"][8][0] + simulation_json["results"][0]["returnValues"][9][0]
                                                    + simulation_json["results"][0]["returnValues"][10][0] # + simulation_json["results"][0]["returnValues"][11][0]
                                                ) 
        return time_stream_state_info
    except Exception as e:
        color_print(f"onchain_helpers/getTimeStreamStateForProfileInfo: Error -  {e}", RED)
        return None
    

# --------------------- x -----------------------------------
# --------------------- x -----------------------------------
# --------------------- x -----------------------------------

def getTimeStreamInfo(rpc_url, private_key_hex_string, protocol_config) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call( target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_streamer_buzzes_params",
                            arguments=[    ObjectID(protocol_config["HIVE_VAULT"]) ],
                            type_arguments=[SUI_TYPE])
        txBlock.move_call( target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_streamer_info",
                            arguments=[    ObjectID(protocol_config["HIVE_VAULT"]), SuiU64(0) ],
                            type_arguments=[SUI_TYPE])
        txBlock.move_call( target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_streamer_info",
                            arguments=[    ObjectID(protocol_config["HIVE_VAULT"]), SuiU64(1) ],
                            type_arguments=[SUI_TYPE])
        txBlock.move_call( target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_streamer_info",
                            arguments=[    ObjectID(protocol_config["HIVE_VAULT"]), SuiU64(2) ],
                            type_arguments=[SUI_TYPE])
        txBlock.move_call( target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_leading_bids_info",
                            arguments=[    ObjectID(protocol_config["HIVE_VAULT"])  ],
                            type_arguments=[SUI_TYPE])
        txBlock.move_call( target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_streamer_pol_info",
                            arguments=[    ObjectID(protocol_config["HIVE_VAULT"])  ],
                            type_arguments=[SUI_TYPE])
        txBlock.move_call( target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_engagement_scores_state",
                            arguments=[    ObjectID(protocol_config["HIVE_VAULT"])  ],
                            type_arguments=[SUI_TYPE])
                
        simulation = txBlock.inspect_all()
        simulation_json = json.loads(simulation.to_json())
        print(simulation_json)
        
        time_stream_config_params = TimeStreamConfigParams.deserialize( simulation_json["results"][0]["returnValues"][0][0] + simulation_json["results"][0]["returnValues"][1][0]
                                            + simulation_json["results"][0]["returnValues"][2][0] + simulation_json["results"][0]["returnValues"][3][0]
                                                + simulation_json["results"][0]["returnValues"][4][0] + simulation_json["results"][0]["returnValues"][5][0]
                                                    + simulation_json["results"][0]["returnValues"][6][0] + simulation_json["results"][0]["returnValues"][7][0]
                                                    + simulation_json["results"][0]["returnValues"][8][0] + simulation_json["results"][0]["returnValues"][9][0]
                                                    + simulation_json["results"][0]["returnValues"][10][0] + simulation_json["results"][0]["returnValues"][11][0]
                                                )
        print(f"time_stream_config_params: {time_stream_config_params}")
        
        time_streamer1_info = TimeStreamerInfo.deserialize(# simulation_json["results"][1]["returnValues"][0][0] + simulation_json["results"][1]["returnValues"][1][0]
                                            simulation_json["results"][1]["returnValues"][2][0] + simulation_json["results"][1]["returnValues"][3][0]
                                                + simulation_json["results"][1]["returnValues"][4][0] + simulation_json["results"][1]["returnValues"][5][0]
                                                    + simulation_json["results"][1]["returnValues"][6][0] + simulation_json["results"][1]["returnValues"][7][0]
                                                    + simulation_json["results"][1]["returnValues"][8][0] )
        print(f"time_streamer1_info: {time_streamer1_info}")

        time_streamer2_info = TimeStreamerInfo.deserialize( # simulation_json["results"][2]["returnValues"][0][0] + simulation_json["results"][2]["returnValues"][1][0]
                                                simulation_json["results"][2]["returnValues"][2][0] + simulation_json["results"][2]["returnValues"][3][0]
                                                + simulation_json["results"][2]["returnValues"][4][0] + simulation_json["results"][2]["returnValues"][5][0]
                                                    + simulation_json["results"][2]["returnValues"][6][0] + simulation_json["results"][2]["returnValues"][7][0]
                                                    + simulation_json["results"][2]["returnValues"][8][0] )
        print(f"time_streamer2_info: {time_streamer2_info}")

        time_streamer3_info = TimeStreamerInfo.deserialize( # simulation_json["results"][3]["returnValues"][0][0] + simulation_json["results"][3]["returnValues"][1][0]
                                                simulation_json["results"][3]["returnValues"][2][0] + simulation_json["results"][3]["returnValues"][3][0]
                                                + simulation_json["results"][3]["returnValues"][4][0] + simulation_json["results"][3]["returnValues"][5][0]
                                                    + simulation_json["results"][3]["returnValues"][6][0] + simulation_json["results"][3]["returnValues"][7][0]
                                                    + simulation_json["results"][3]["returnValues"][8][0] )
        print(f"time_streamer3_info: {time_streamer3_info}")
        
        # leading_bids_info = LeadingBidsInfo.deserialize( simulation_json["results"][4]["returnValues"][0][0] + simulation_json["results"][4]["returnValues"][1][0], 
        #                                     + simulation_json["results"][4]["returnValues"][2][0] + simulation_json["results"][4]["returnValues"][3][0]
        #                                         + simulation_json["results"][4]["returnValues"][4][0] + simulation_json["results"][4]["returnValues"][5][0] )

        time_stream_pol_info = TimeStreamPolInfo.deserialize( simulation_json["results"][5]["returnValues"][0][0] + simulation_json["results"][5]["returnValues"][1][0] )
        print(f"time_stream_pol_info: {time_stream_pol_info}")

        time_stream_engagement_scores_state = TimeStreamEngagementScoresState.deserialize( simulation_json["results"][6]["returnValues"][0][0] + simulation_json["results"][6]["returnValues"][1][0]
                                            + simulation_json["results"][6]["returnValues"][2][0] + simulation_json["results"][6]["returnValues"][3][0]
                                                + simulation_json["results"][6]["returnValues"][4][0] + simulation_json["results"][6]["returnValues"][5][0]
                                                    + simulation_json["results"][6]["returnValues"][6][0] + simulation_json["results"][6]["returnValues"][7][0]
                                                    + simulation_json["results"][6]["returnValues"][8][0] )
        print(f"time_stream_engagement_scores_state: {time_stream_engagement_scores_state}")

        return {
            "config_params": time_stream_config_params,
            "streamer1_info": time_streamer1_info,
            "streamer2_info": time_streamer2_info,
            "streamer3_info": time_streamer3_info,
            # "leading_bids_info": leading_bids_info,
            "pol_info": time_stream_pol_info,
            "engagement_state": time_stream_engagement_scores_state
        }

    except Exception as e:
        color_print(f"onchain_helpers/getTimeStreamInfo: Error -  {e}", RED)
        return None
 

def getHiveChronicleInfo(rpc_url, private_key_hex_string, protocol_config, epoch) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        txBlock = SyncTransaction(client=suiClient)
        
        hiveChronicleVault = (suiClient.get_object(id))
        hiveChronicleVault = hiveChronicleVault.result_data.to_dict()["content"]["fields"]
        

        if (epoch > 0):
            txBlock.move_call( target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_entry::query_bees_farming_snampshot",
                                arguments=[    ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]), SuiU64(epoch) ],
                                type_arguments=[])                
            simulation = txBlock.inspect_all()
            simulation_json = json.loads(simulation.to_json())
            print(simulation_json)
            bee_farm_snapshot_info = BeeFarmSnapshotInfo.deserialize( simulation_json["results"][0]["returnValues"][0][0] + simulation_json["results"][0]["returnValues"][1][0]
                                            + simulation_json["results"][0]["returnValues"][2][0] + simulation_json["results"][0]["returnValues"][3][0]
                                                + simulation_json["results"][0]["returnValues"][4][0] )
            print(f"bee_farm_snapshot_info: {bee_farm_snapshot_info}")
            hiveChronicleVault["bee_farm_snapshot_info"] = bee_farm_snapshot_info
       

        return hiveChronicleVault

    except Exception as e:
        color_print(f"onchain_helpers/getTimeStreamInfo: Error -  {e}", RED)
        return None
 





















# async def get_pool_info(client: SuiClient, id: str) -> dict:
#     obj = (await client.get_object(id)).result_data.to_dict()["content"]["fields"]
#     return obj

# async def get_remove_strategy(client: SuiClient, pool_id, coin_x: int = 0, coin_y: int = 0 ) -> Tuple[int, int, int]:
#     # returns the lp tokens to do balanced exit
#     # and amount of other coin to add back
#     pool = await get_pool_info(client=client, id=pool_id)
#     total_x = int(pool["coin_x_reserve"])
#     total_y = int(pool["coin_y_reserve"])
#     lp_tokens = int(pool["lp_supply"]["fields"]["value"])
#     if coin_x > total_x or coin_y > total_y:
#         raise Exception("Coin amount is greater than total pool amount")
#     # print(f"total_x: {total_x}, total_y: {total_y}, lp_tokens: {lp_tokens}")
#     if coin_x == 0:
#         lp = int(lp_tokens * coin_y / total_y)
#         coin_x = int(total_x * lp / lp_tokens)
#         return lp, coin_x, 0
#     elif coin_y == 0:
#         lp = int(lp_tokens * coin_x / total_x)
#         coin_y = int(total_y * lp / lp_tokens)
#         return lp, 0, coin_y
#     else:
#         if (total_x / coin_x) > (total_y / coin_y):
#             # means (coin_y / total_y) is greater
#             # implying we should remove according to coin_y value, and add back x
#             lp, coin_xr, _ = await get_remove_strategy(client=client, coin_y=coin_y)
#             return lp, coin_xr - coin_x, 0
#         else:
#             lp, _, coin_yr = await get_remove_strategy(client=client, coin_x=coin_x)
#             return lp, 0, coin_yr - coin_y


# async def exec_add(client: SuiClient, add: dict, scripts_package: str, pool_id: str, type_array: list):
#     txer = SuiTransactionAsync(client)

#     txer, coin_objects = await objects_joined(client, txer)

#     if add["amount_a"] == "0": # no ETH
#         # provide x
#         print("Providing USDC")
#         await txer.move_call(
#             target=f"{scripts_package}::hive_scripts::add_liquidity_to_2pool_only_x",
#             arguments=[
#                 ObjectID("0x6"),
#                 ObjectID(pool_id),
#                 ObjectID(coin_objects["USDC"]),
#                 SuiU64(int(add["amount_b"])),
#             ],
#             type_arguments=type_array,
#         )
#     elif add["amount_b"] == "0": # no USDT
#         # provide y
#         print("Providing DETH")
#         await txer.move_call(
#             target=f"{scripts_package}::hive_scripts::add_liquidity_to_2pool_only_y",
#             arguments=[
#                 ObjectID("0x6"),
#                 ObjectID(pool_id),
#                 ObjectID(coin_objects["DETH"]),
#                 SuiU64(int(add["amount_a"])),
#             ],
#             type_arguments=type_array,
#         )
#     else:
#         # provide x and y
#         print("Providing DETH and USDC")
#         await txer.move_call(
#             target=f"{scripts_package}::hive_scripts::add_liquidity_to_2pool",
#             arguments=[
#                 ObjectID("0x6"),
#                 ObjectID(pool_id),
#                 ObjectID(coin_objects["USDC"]),
#                 SuiU64(int(add["amount_b"])),
#                 ObjectID(coin_objects["DETH"]),
#                 SuiU64(int(add["amount_a"])),
#             ],
#             type_arguments=type_array,
#         )

#     txr = await txer.execute(gas_budget="2000000")
#     return txr.result_data.to_dict()


# async def exec_swap(client: SuiClient, swap: dict, scripts_package: str, pool_id: str, type_array: list):
#     txer = SuiTransactionAsync(client)

#     txer, coin_objects = await objects_joined(client, txer)

#     if swap["atob"]:
#         # provide y
#         print("Providing DETH")
#         await txer.move_call(
#             target=f"{scripts_package}::hive_scripts::swap2pool_provide_y",
#             arguments=[
#                 ObjectID("0x6"),
#                 ObjectID(pool_id),
#                 SuiU64(1),
#                 ObjectID(coin_objects["DETH"]),
#                 SuiU64(int(swap["amount_in"])),
#                 SuiBoolean(True),
#             ],
#             type_arguments=type_array,
#         )
#     else:
#         # provide x
#         print("Providing USDC")
#         await txer.move_call(
#             target=f"{scripts_package}::hive_scripts::swap2pool_provide_x",
#             arguments=[
#                 ObjectID("0x6"),
#                 ObjectID(pool_id),
#                 ObjectID(coin_objects["USDC"]),
#                 SuiU64(int(swap["amount_in"])),
#                 SuiU64(1),
#                 SuiBoolean(True),
#             ],
#             type_arguments=type_array,
#         )

#     txr = await txer.execute(gas_budget="2000000")
#     return txr.result_data.to_dict()



# async def exec_remove(client, remove, scripts_package, pool_id, type_array):
#     txer = SuiTransactionAsync(client)

#     txer, coin_objects = await objects_joined(client, txer)

#     amount_x = int(remove["amount_b"])
#     amount_y = int(remove["amount_a"])

#     lp, coin_x, coin_y = await get_remove_strategy(client=client, coin_x=amount_x, coin_y=amount_y)
#     print(f"Removing {lp} LP, Adding {coin_x} USDC, {coin_y} DETH")

#     await txer.move_call(
#         target=f"{scripts_package}::hive_scripts::remove_liquidity_from_2pool",
#         arguments=[
#             ObjectID("0x6"),
#             ObjectID(pool_id),
#             ObjectID(coin_objects["USDC-DETH-Curved"]),
#             SuiU64(lp),
#             SuiU64(int(0)),
#             SuiU64(int(0)),
#         ],
#         type_arguments=type_array,
#     )

#     if coin_x > 0:
#         print("rem: Adding USDC")
#         await txer.move_call(
#             target=f"{scripts_package}::hive_scripts::add_liquidity_to_2pool_only_x",
#             arguments=[
#                 ObjectID("0x6"),
#                 ObjectID(pool_id),
#                 ObjectID(coin_objects["USDC"]),
#                 SuiU64(coin_x),
#             ],
#             type_arguments=type_array,
#         )
#     elif coin_y > 0:
#         print("rem: Adding DETH")
#         await txer.move_call(
#             target=f"{scripts_package}::hive_scripts::add_liquidity_to_2pool_only_y",
#             arguments=[
#                 ObjectID("0x6"),
#                 ObjectID(pool_id),
#                 ObjectID(coin_objects["DETH"]),
#                 SuiU64(coin_y),
#             ],
#             type_arguments=type_array,
#         )

#     txr = await txer.execute(gas_budget="2000000")
#     return txr.result_data.to_dict()

# async def do_tx(client: SuiClient, event: dict, index: int, pool_id: str):
#     if event["type"] == "add":
#         print("Adding liquidity")
#         res = await exec_add(client, event)
#         print("Added")
#         return {
#             "add_result": res,
#             "pool_info": await get_pool_info(client, pool_id),
#             "original_event": event,
#             "index": index,
#         }
#     elif event["type"] == "swap":
#         print("Swapping")
#         res = await exec_swap(client, event)
#         print("Swapped")
#         return {
#             "swap_result": res,
#             "pool_info": await get_pool_info(client, pool_id),
#             "original_event": event,
#             "index": index,
#         }
#     elif event["type"] == "remove":
#         print("Removing liquidity")
#         res = await exec_remove(client, event)
#         print("Removed")
#         return {
#             "remove_result": res,
#             "pool_info": await get_pool_info(client, pool_id),
#             "original_event": event,
#             "index": index,
#         }
#     else:
#         raise Exception("Unknown event type")
