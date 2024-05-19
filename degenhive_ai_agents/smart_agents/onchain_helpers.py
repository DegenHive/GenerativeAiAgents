import canoser.str_t
import requests, json, argparse, asyncio
from typing import Union, Tuple
# from pysui.sui.sui_builders.exec_builders import MergeCoin, SplitCoin, ExecuteTransaction
# from pysui.sui.sui_builders.get_builders import GetAllCoinBalances, GetObjectsOwnedByAddress

# from pysui.sui.sui_clients.transaction import SuiTransactionAsync
# from pysui.sui.sui_builders.get_builders import GetCoins
import binascii
from pysui import SyncClient, SuiConfig, handle_result, ObjectID, SuiAddress, AsyncClient
from pysui.sui.sui_bcs import bcs
from pysui.sui.sui_txn import SyncTransaction, AsyncTransaction

from pysui.abstracts import SignatureScheme
from pysui.sui.sui_types import bcs
from pysui.sui.sui_utils import partition
from pysui.sui.sui_txresults.single_tx import SuiCoinObjects, SuiCoinObject
from pysui.sui.sui_txresults.complex_tx import TxInspectionResult
from pysui.abstracts import SignatureScheme
from utils import *
from pysui.sui.sui_types.collections import SuiArray
import canoser 
import time
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
    SuiNullType,
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

_ADDRESS_LENGTH = 32

def color_print(text, color_code):
    END_COLOR = '\033[0m'  # Reset color code
    print(color_code + text + END_COLOR)


class OptionalSuiString(canoser.RustOptional):
    """OptionalU16 Optional assignment of unsigned 16 bit int."""

    _type = canoser.StrT


class HiveProfileOwnerInfo(canoser.Struct):
    _fields = [
        ('owner', canoser.ArrayT(canoser.Uint8, _ADDRESS_LENGTH, False)) # SUI address),
    ]

class HiveProfileIdInfo(canoser.Struct):
    _fields = [
        ('has_profile', canoser.BoolT),
        ('profile_id', canoser.ArrayT(canoser.Uint8, _ADDRESS_LENGTH, False)) # SUI address
    ]


# class OptionalTypeFactory:
#     """Optional Optional assignment of any canoser type."""

#     @classmethod
#     def as_optional(cls, in_type: Any = canoser.Struct) -> canoser.RustOptional:
#         """."""
#         Optional._type = in_type.__class__
#         return Optional(None)
    

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
        ('collection_name', str),
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

class EpochInfo(canoser.Struct):
    _fields = [
        ('epoch', canoser.Uint64),
        ('epoch_timestamp_ms', canoser.Uint64)
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



async def getSuiASyncClient(rpc_url, private_key_hex_string ):
    try:
        async_suiClient = AsyncClient(SuiConfig.user_config(
                rpc_url=rpc_url,
                prv_keys=[{'wallet_key': "0x" + private_key_hex_string, 'key_scheme': SignatureScheme.ED25519}],
            ))
        print(async_suiClient)

        # txBlock = AsyncTransaction(client=async_suiClient)

        objects = await async_suiClient.get_objects(fetch_all=True)
        objects = objects.result_data.to_dict()["data"]
        print(objects)

    # spendableSui, use_gas_object = getSpendableSui(async_suiClient, txBlock, int(1000000000))
    # txBlock.transfer_objects(recipient=SuiAddress(recipient_address), transfers=[spendableSui] )

    # simulation_response, txBlock = simulate_tx(txBlock)
    # if (simulation_response):
    #     print(f"Simulation successful")
    #     if use_gas_object:
    #         exec_result = handle_result(txBlock.execute(gas_budget="10000000", use_gas_object=use_gas_object))
    #     else:
    #         exec_result = handle_result(txBlock.execute(gas_budget="10000000"))
    #     exec_result = exec_result.to_json()
    #     exec_result = json.loads(exec_result)

    #     if (exec_result["effects"]["status"]["status"] == "success"):
    #         color_print(f"SUI transferred successfuly: {exec_result["digest"]}", GREEN)
    #         return exec_result
    #     else:
    #         color_print(f"Error transferring SUI: {exec_result["effects"]["status"]["error"]}", RED)
    #         return False
    # else: 
    #     print(f"Simulation failed")
    #     return False



    except Exception as e:
        send_telegram_message(f"Error getting SUI Sync Client: {e}")
        print(f"Error getting SUI Sync Client: {e}")
        return None




def getSuiSyncClient(rpc_url, private_key_hex_string ):
    try:
        suiClient = SyncClient(SuiConfig.user_config(
                rpc_url=rpc_url,
                prv_keys=[{'wallet_key': "0x" + private_key_hex_string, 'key_scheme': SignatureScheme.ED25519}],
            ))
        return suiClient
    except Exception as e:
        send_telegram_message(f"Error getting SUI Sync Client: {e}")
        print(f"Error getting SUI Sync Client: {e}")
        return None


def kraftHiveProfileTx(rpc_url, private_key_hex_string, protocol_config, address, name, bio) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
    txBlock = SyncTransaction(client=suiClient)

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
    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        exec_result = handle_result(txBlock.execute())
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"Hive Profile Krafted successfuly: {exec_result["digest"]}", GREEN)
            time.sleep(3)
            profileInfo = getHiveProfileIdForUser(rpc_url, private_key_hex_string, protocol_config, address)
            return True, profileInfo
        else:
            color_print(f"Error Krafting Hive Profile: {exec_result["effects"]["status"]["error"]}", RED)
            return False, None
    else: 
        print(f"Simulation failed")
        return False, None
    


"""
Transfer Tokens (non SUI) from one address to another
"""
def transferTokens(rpc_url, private_key_hex_string, type_, from_address, recipient_address, amount):
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
    txBlock = SyncTransaction(client=suiClient)

    objects = suiClient._get_coins_for_type(address= from_address, coin_type=type_)
    objects = objects.result_data.to_dict()["data"]
    coinObjectIds = []
    
    avail_balance = 0
    for obj in objects:
        avail_balance += int(obj["balance"])
        coinObjectIds.append(obj["coinObjectId"])
    
    if avail_balance < amount:
        send_telegram_message(f"Insufficient balance for token type ${type_}: {avail_balance} < {amount} \
                              \nFrom: {from_address} \nTo: {recipient_address} \nAmount: {amount}")
    
    if len(objects) > 1:
        merge_coins = [coin for coin in objects[1:]]  
        txBlock.merge_coins(merge_to=coinObjectIds[0], merge_from=merge_coins)
    
    transferObject = txBlock.split_coin(coin=coinObjectIds[0], amounts=[amount])
    txBlock.transfer_objects(recipient=SuiAddress(recipient_address), transfers=[transferObject] )

    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        exec_result = handle_result(txBlock.execute())
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"Tokens transferred successfuly: {exec_result["digest"]}", GREEN)
            return True
        else:
            color_print(f"Error transferring Tokens: {exec_result["effects"]["status"]["error"]}", RED)
            return False
    else:
        print(f"Simulation failed")
        return False



def transferSui(rpc_url, private_key_hex_string, recipient_address, amount):
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
    txBlock = SyncTransaction(client=suiClient)


    spendableSui, use_gas_object = getSpendableSui(suiClient, txBlock, int(amount))
    txBlock.transfer_objects(recipient=SuiAddress(recipient_address), transfers=[spendableSui] )

    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        if use_gas_object:
            exec_result = handle_result(txBlock.execute(gas_budget="10000000", use_gas_object=use_gas_object))
        else:
            exec_result = handle_result(txBlock.execute(gas_budget="10000000"))
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)

        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"SUI transferred successfuly: {exec_result["digest"]}", GREEN)
            return exec_result
        else:
            color_print(f"Error transferring SUI: {exec_result["effects"]["status"]["error"]}", RED)
            return False
    else: 
        print(f"Simulation failed")
        return False
    

def getSuiBalanceForAddress(rpc_url, private_key_hex_string, user_address):
    try: 
        print(f"Getting SUI balance for address: {user_address}")
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)    
        sui_objs = suiClient.get_gas(address=user_address)
        sui_objs = sui_objs.result_data.to_dict()["data"]
        total_balance = 0
        for obj in sui_objs:
            total_balance += int(obj["balance"])
        return total_balance
    except Exception as e:
        print(f"Error getting SUI balance: {e}")
        return None


"""
Deposit HIVE in a Hive Profile
"""
def depositHiveInProfile(rpc_url, private_key_hex_string, protocol_config, type_, userAddress, userProfileID, amount):
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
    txBlock = SyncTransaction(client=suiClient)

    objects = suiClient._get_coins_for_type(address= userAddress, coin_type=type_)
    objects = objects.result_data.to_dict()["data"]
    coinObjectIds = []
    
    avail_balance = 0
    for obj in objects:
        avail_balance += int(obj["balance"])
        coinObjectIds.append(obj["coinObjectId"])
    
    if avail_balance < amount:
        amount = avail_balance

    if len(objects) > 1:
        merge_coins = [coin for coin in coinObjectIds[1:]]  
        txBlock.merge_coins(merge_to=coinObjectIds[0], merge_from=merge_coins)
    
    if amount == 0:
        color_print(f"Zero balance for token type {type_}: Unable to deposit HIVE in Profile ${userProfileID} | userAddress = ${userAddress}", RED)
        return False
        
    txBlock.move_call(
        target=f"{protocol_config["HIVE_PACKAGE"]}::hive::burn_hive_for_gems",
        arguments=[
                   ObjectID(protocol_config["HIVE_VAULT"]),
                   ObjectID(userProfileID),
                    ObjectID(coinObjectIds[0]),
                    SuiU64(amount),
            ],
        )
 
    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        exec_result = handle_result(txBlock.execute())
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"HIVE deposited successfuly: {exec_result["digest"]}", GREEN)
            return True
        else:
            color_print(f"Error depositing HIVE: {exec_result["effects"]["status"]["error"]}", RED)
            return False
    else:
        print(f"Simulation failed")
        return False




"""
Used to get SUI coin to be spent, 

Returns - 
- spendableSui: SUI coin to be spent
- CoinID: CoinID of the SUI coin to be used for covering gas fees
"""
def getSpendableSui(client: SyncClient, txBlock: SyncTransaction, spendableVal):
    objects = client.get_objects(fetch_all=True)
    objects = objects.result_data.to_dict()["data"]
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
        return txBlock.split_coin(coin=txBlock.gas, amounts=[spendableVal]), None
    else:
        print(f"{len(sui_objects)} coins of type SUI found")
        # for obj in sui_objects:
        #     print(obj)
        sui_coin_id = sui_objects[0]
        merge_coins = [coin for coin in sui_objects[1:]]  
        txBlock.merge_coins(merge_to=txBlock.gas, merge_from=merge_coins)
        return txBlock.split_coin(coin=txBlock.gas, amounts=[spendableVal]), sui_coin_id



async def objects_joined(client: SyncClient, txb: SyncTransaction) -> Tuple[SyncTransaction, dict]:
    # weakness: if a coin identifier is A::B::C, C must be unique for a type of coin (each coin has a different symbol). else this fails.
    objects = client.get_objects(fetch_all=True)
    objects = objects.result_data.to_dict()["data"]

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
    try:
        simulation = txb.inspect_all()
        simulation = simulation.to_json()    
        simulation_json = json.loads(simulation)

        if simulation_json["effects"]["status"]["status"] == "success":
            print(f"Transaction will be successful")
            return True, txb
        else:
            print(f"Transaction will fail - Error")
            print(simulation_json["effects"]["status"]["error"])
            return False, simulation_json["effects"]["status"]["error"]
    except Exception as e:
        print(f"Error simulating transaction: {e}")
        return False, e


############### --- ############### --- ############### --- ###############
############### --- --- --- NOISE   FUNCTIONS  --- --- --- --- ############
############### --- ############### --- ############### --- ###############

"""
Execute a transaction to make a Noise Post
"""
def make_noise_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, noise, gen_ai) :
    print(f"make_noise_buzzTx: user_profile = {user_profile}, noise = {noise}, gen_ai = {gen_ai}")
    try: 
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_chronicles::make_some_noise",
            arguments=[
                    ObjectID(CLOCK),
                    ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]),
                    ObjectID(user_profile),
                    SuiString(noise),
                    SuiString([gen_ai])
                ],
                type_arguments=[],
            )
        simulation_response, txBlock = simulate_tx(txBlock)
        if (simulation_response):
            print(f"Simulation successful")
            exec_result = handle_result(txBlock.execute())
            exec_result = exec_result.to_json()
            exec_result = json.loads(exec_result)
            if (exec_result["effects"]["status"]["status"] == "success"):
                color_print(f"Noise Buzz made successfuly: {exec_result["digest"]}", GREEN)
                return True
            else:
                color_print(f"Error making Noise Buzz: {exec_result["effects"]["status"]["error"]}", RED)
                send_telegram_message(f"Error making Noise Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
                return False
        else: 
            print(f"Simulation failed")
            send_telegram_message(f"Simulation -- Error making Noise Buzz: {txBlock}")
            return False
    except Exception as e:
        print(f"Error making Noise Buzz: {e}")
        return False



############### --- ############### --- ############### --- ###############
############### --- --- --- LIKE FUNCTIONS  --- --- --- --- ###############
############### --- ############### --- ############### --- ###############

"""
Execute a transaction to like a HiveChronicle Post
"""
def like_hiveChronicle_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, poster_profile, buzz_type, buzz_index, thread_index) :
    # print(f"rpc_url: {rpc_url}, private_key_hex_string: {private_key_hex_string}")
    print(f"like_hiveChronicle_buzzTx: user_profile = {user_profile}, poster_profile = {poster_profile}, buzz_type = {buzz_type}, buzz_index = {buzz_index}, thread_index = {thread_index}")
    try: 
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
        print(suiClient)
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_chronicles::add_like_to_buzz",
            arguments=[
                    ObjectID(CLOCK),
                    ObjectID(protocol_config["HIVE_MANAGER"]),
                    ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]),
                    ObjectID(user_profile),
                    ObjectID(poster_profile),
                    SuiU8(buzz_type),
                    SuiU64(buzz_index),
                    SuiU64(thread_index),
                ],
                type_arguments=[],
            )
        simulation_response, txBlock = simulate_tx(txBlock)
        if (simulation_response):
            print(f"Simulation successful")
            exec_result = handle_result(txBlock.execute())
            exec_result = exec_result.to_json()
            exec_result = json.loads(exec_result)
            if (exec_result["effects"]["status"]["status"] == "success"):
                color_print(f"HiveChronicle Buzz Liked successfuly: {exec_result["digest"]}", GREEN)
                return True
            else:
                color_print(f"Error Liking HiveChronicle Buzz: {exec_result["effects"]["status"]["error"]}", RED)
                send_telegram_message(f"Error Liking HiveChronicle Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
                return False
        else: 
            print(f"Simulation failed")
            send_telegram_message(f"Simulation -- Error Liking HiveChronicle Buzz: {simulation_response}")
            return False
    except Exception as e:
        print(f"Error Liking HiveChronicle Buzz: {e}")
        return False


"""
Execute a transaction to like a DexDao Governor Post
"""
def like_dexDaoGovernor_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, governor_post_index) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_chronicles::entry_like_governor_buzz",
            arguments=[
                    ObjectID(CLOCK),
                    ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]),
                    ObjectID(protocol_config["HIVE_MANAGER"]),
                    ObjectID(protocol_config["POOLS_GOVERNOR"]),
                    ObjectID(user_profile),
                    SuiU64(governor_post_index),
                ],
                type_arguments=[],
            )
        
        simulation_response, txBlock = simulate_tx(txBlock)
        if (simulation_response):
            print(f"Simulation successful")
            exec_result = handle_result(txBlock.execute())
            exec_result = exec_result.to_json()
            exec_result = json.loads(exec_result)
            if (exec_result["effects"]["status"]["status"] == "success"):
                color_print(f"DexDao Governor Buzz Liked successfuly: {exec_result["digest"]}", GREEN)
                return True
            else:
                color_print(f"Error Liking DexDao Governor Buzz: {exec_result["effects"]["status"]["error"]}", RED)
                send_telegram_message(f"Error Liking DexDao Governor Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
                return False
        else: 
            print(f"Simulation failed")
            send_telegram_message(f"Simulation -- Error Liking DexDao Governor Buzz: {txBlock}")
            return False
    except Exception as e:
        print(f"Error Liking DexDao Governor Buzz: {e}")
        return False


"""
Execute a transaction to like a HiveDao Governor Post
"""
def like_HiveDaoGovernor_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, governor_post_index) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVE_DAO_PACKAGE"]}::hive_dao::like_governor_buzz",
            arguments=[
                    ObjectID(CLOCK),
                    ObjectID(protocol_config["POOLS_GOVERNOR"]),
                    ObjectID(user_profile),
                        SuiU64(governor_post_index),
                ],
                type_arguments=[],
            )
        simulation_response, txBlock = simulate_tx(txBlock)
        if (simulation_response):
            print(f"Simulation successful")
            exec_result = handle_result(txBlock.execute())
            exec_result = exec_result.to_json()
            exec_result = json.loads(exec_result)
            if (exec_result["effects"]["status"]["status"] == "success"):
                color_print(f"HiveDao Governor Buzz Liked successfuly: {exec_result["digest"]}", GREEN)
                return True
            else:
                color_print(f"Error Liking HiveDao Governor Buzz: {exec_result["effects"]["status"]["error"]}", RED)
                send_telegram_message(f"Error Liking HiveDao Governor Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
                return False
        else: 
            print(f"Simulation failed")
            send_telegram_message(f"Simulation -- Error Liking HiveDao Governor Buzz: {txBlock}")
            return False
    except Exception as e:
        print(f"Error Liking HiveDao Governor Buzz: {e}")
        return False

"""
Execute a transaction to like a stream buzz Post
"""
def like_stream_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, stream_index, stream_inner_index) :
    try:
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
            exec_result = handle_result(txBlock.execute())
            exec_result = exec_result.to_json()
            exec_result = json.loads(exec_result)
            if (exec_result["effects"]["status"]["status"] == "success"):
                color_print(f"Stream Buzz Liked successfuly: {exec_result["digest"]}", GREEN)
                return True
            else:
                color_print(f"Error Liking Stream Buzz: {exec_result["effects"]["status"]["error"]}", RED)
                send_telegram_message(f"Error Liking Stream Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
                return False
        else: 
            print(f"Simulation failed")
            send_telegram_message(f"Simulation -- Error Liking Stream Buzz: {txBlock}")
            return False
    except Exception as e:
        print(f"Error Liking Stream Buzz: {e}")
        return False

############### --- ############### --- ############### --- ###############
############### --- --- --- COMMENT FUNCTIONS  --- --- --- --- ############
############### --- ############### --- ############### --- ###############

"""
Execute a transaction to comment on a HiveChronicle Post
"""
def comment_on_hiveChronicle_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, poster_profile, buzz_type, buzz_index, thread_index, dialogue_index, dialogue_content, to_remove) :
    try: 
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_chronicles::update_dialogue_to_buzz",
            arguments=[
                    ObjectID(CLOCK),
                    ObjectID(protocol_config["HIVE_MANAGER"]),
                    ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]),
                    ObjectID(user_profile),
                    ObjectID(poster_profile),
                    SuiU8(buzz_type),
                        SuiU64(buzz_index),
                        SuiU64(thread_index),
                        SuiU64(dialogue_index),
                        SuiString(dialogue_content),
                        SuiBoolean(to_remove),
                ],
                type_arguments=[],
            )

        simulation_response, txBlock = simulate_tx(txBlock)
        if (simulation_response):
            print(f"Simulation successful")
            exec_result = handle_result(txBlock.execute())
            exec_result = exec_result.to_json()
            exec_result = json.loads(exec_result)
            if (exec_result["effects"]["status"]["status"] == "success"):
                color_print(f"HiveChronicle Buzz Liked successfuly: {exec_result["digest"]}", GREEN)
                return True
            else:
                color_print(f"Error Commenting HiveChronicle Buzz: {exec_result["effects"]["status"]["error"]}", RED)
                send_telegram_message(f"Error Commenting HiveChronicle Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
                return False
        else: 
            print(f"Simulation failed")
            send_telegram_message(f"Simulation -- Error Commenting HiveChronicle Buzz: {txBlock}")
            return False
    except Exception as e:
        print(f"Error Commenting HiveChronicle Buzz: {e}")
        return False


"""
Execute a transaction to comment on a DexDao Governor Post
"""
def comment_on_dexDaoGovernor_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, governor_post_index, comment_index, comment) :
    try: 
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["DEX_DAO_PACKAGE"]}::dex_dao::interact_with_governance_buzz",
            arguments=[
                    ObjectID(CLOCK),
                    ObjectID(protocol_config["HIVE_MANAGER"]),
                    ObjectID(protocol_config["POOLS_GOVERNOR"]),
                    ObjectID(user_profile),
                        SuiU64(governor_post_index),
                        SuiU64(comment_index),
                        SuiU64(comment)
                ],
                type_arguments=[],
            )

        simulation_response, txBlock = simulate_tx(txBlock)
        if (simulation_response):
            print(f"Simulation successful")
            exec_result = handle_result(txBlock.execute())
            exec_result = exec_result.to_json()
            exec_result = json.loads(exec_result)
            if (exec_result["effects"]["status"]["status"] == "success"):
                color_print(f"DexDao Governor Buzz Liked successfuly: {exec_result["digest"]}", GREEN)
                return True
            else:
                color_print(f"Error Commenting DexDao Governor Buzz: {exec_result["effects"]["status"]["error"]}", RED)
                send_telegram_message(f"Error Commenting DexDao Governor Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
                return False
        else: 
            print(f"Simulation failed")
            send_telegram_message(f"Simulation -- Error Commenting DexDao Governor Buzz: {txBlock}")
            return False
    except Exception as e:
        print(f"Error Commenting DexDao Governor Buzz: {e}")
        return False

"""
Execute a transaction to comment on a HiveDao Governor Post
"""
def comment_on_HiveDaoGovernor_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, governor_post_index, comment_index, comment) :
    try: 
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["DEX_DAO_PACKAGE"]}::dex_dao::interact_with_governance_buzz",
            arguments=[
                    ObjectID(CLOCK),
                    ObjectID(protocol_config["HIVE_MANAGER"]),
                    ObjectID(protocol_config["POOLS_GOVERNOR"]),
                    ObjectID(user_profile),
                        SuiU64(governor_post_index),
                        SuiU64(comment_index),
                        SuiU64(comment)
                ],
                type_arguments=[],
            )

        simulation_response, txBlock = simulate_tx(txBlock)
        if (simulation_response):
            print(f"Simulation successful")
            exec_result = handle_result(txBlock.execute())
            exec_result = exec_result.to_json()
            exec_result = json.loads(exec_result)
            if (exec_result["effects"]["status"]["status"] == "success"):
                color_print(f"DexDao Governor Buzz Liked successfuly: {exec_result["digest"]}", GREEN)
                return True
            else:
                color_print(f"Error Commenting DexDao Governor Buzz: {exec_result["effects"]["status"]["error"]}", RED)
                send_telegram_message(f"Error Commenting DexDao Governor Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
                return False
        else: 
            print(f"Simulation failed")
            send_telegram_message(f"Simulation -- Error Commenting DexDao Governor Buzz: {txBlock}")
            return False
    except Exception as e:
        print(f"Error Commenting DexDao Governor Buzz: {e}")
        return False

"""
Execute a transaction to comment on a stream buzz Post
"""
def interact_with_stream_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, streamer_profile, stream_index, stream_inner_index, user_buzz, n_gen_ai_url) :
    print(f"Interacting with Stream Buzz Tx")
    # print(f"n_gen_ai_url: {n_gen_ai_url}")
    # print(f"user_profile: {user_profile}")
    # print(f"streamer_profile: {streamer_profile}")
    # print(f"stream_index: {stream_index}")
    # print(f"stream_inner_index: {stream_inner_index}")
    # print(f"user_buzz: {user_buzz}")
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
    txBlock = SyncTransaction(client=suiClient)
    txBlock.move_call(
        target=f"{protocol_config["TWO_TOKEN_AMM_PACKAGE"]}::bee_trade::interact_with_stream_buzz",
        arguments=[
                   ObjectID(CLOCK),
                   ObjectID(protocol_config["PROFILE_MAPPING_STORE"]),
                   ObjectID(protocol_config["HIVE_MANAGER"]),
                   ObjectID(protocol_config["HIVE_VAULT"]),
                   ObjectID(protocol_config["BEE_CAP"]),
                   ObjectID(protocol_config["BEE_TOKEN_POLICY"]),
                   ObjectID(protocol_config["HIVE_DISPERSER"]),
                   ObjectID(user_profile), ObjectID(streamer_profile),
                    SuiU64(stream_index),
                    SuiU64(stream_inner_index),
                    SuiString(user_buzz),
                    SuiString([n_gen_ai_url])
            ],
            type_arguments=[SUI_TYPE],
        )
    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        exec_result = handle_result(txBlock.execute())
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"Commented on Stream Buzz successfuly: {exec_result["digest"]}", GREEN)
            return True
        else:
            color_print(f"Error commenting on Stream Buzz: {exec_result["effects"]["status"]["error"]}", RED)
            send_telegram_message(f"Error commenting on Stream Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
            return False
    else: 
        print(f"Simulation failed")
        send_telegram_message(f"Simulation -- Error commenting on Stream Buzz: {txBlock}")
        return False



"""
Execute a transaction to upvote a Hive Buzz Post
"""
def upvote_hive_buzzTx(rpc_url, private_key_hex_string, protocol_config, user_profile, poster_profile, stream_index, stream_inner_index) :
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
        exec_result = handle_result(txBlock.execute())
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"Hive Buzz Upvoted successfuly: {exec_result["digest"]}", GREEN)
            return True
        else:
            color_print(f"Error Upvoting Hive Buzz: {exec_result["effects"]["status"]["error"]}", RED)
            send_telegram_message(f"Error Upvoting Hive Buzz: {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
            return False
    else:
        print(f"Simulation failed")
        send_telegram_message(f"Simulation -- Error Upvoting Hive Buzz: {txBlock}")
        return False
    

#  ---------------- UPDATE GLOBAL CYCLIC FUNCTIONS ----------------
# ---------------- UPDATE GLOBAL CYCLIC FUNCTIONS ----------------


"""
Execute a transaction to stake all SUI etc for degenSUI
"""
def handle_liquid_staking_functions(rpc_url, private_key_hex_string, protocol_config) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
    txBlock = SyncTransaction(client=suiClient)
    txBlock.move_call(
        target=f"{protocol_config["DSUIVAULT_PACKAGE"]}::hsui_vault::process_unstake_sui_requests",
        arguments=[ ObjectID(SUI_SYSTEM_STATE),   ObjectID(protocol_config["DSUI_VAULT"]) ],
        )
    txBlock.move_call(
        target=f"{protocol_config["DSUIVAULT_PACKAGE"]}::hsui_vault::update_calculated_accrued_rewards",
        arguments=[ ObjectID(SUI_SYSTEM_STATE),   ObjectID(protocol_config["DSUI_VAULT"]) ],
        )    
    txBlock.move_call(
        target=f"{protocol_config["DSUIVAULT_PACKAGE"]}::hsui_vault::process_stake_sui_requests",
        arguments=[ ObjectID(SUI_SYSTEM_STATE),   ObjectID(protocol_config["DSUI_VAULT"]) ],
        )    
    if "HIVE_DAO_GOVERNOR" in protocol_config:
        txBlock.move_call(
            target=f"{protocol_config["HIVE_DAO_PACKAGE"]}::hive_dao::claim_collected_degensui",
            arguments=[ ObjectID(SUI_SYSTEM_STATE),   ObjectID(protocol_config["HIVE_DAO_GOVERNOR"]) 
                       ,   ObjectID(protocol_config["DSUI_VAULT"]),   ObjectID(protocol_config["TREASURY_DSUI"])
                        ,   ObjectID(protocol_config["DSUI_DISPERSER"]) ]
            )            
    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        exec_result = handle_result(txBlock.execute(gas_budget="10000000"))
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"LSD FUNCTIONS executed successfuly: {exec_result["digest"]}", GREEN)
            send_telegram_message(f"LSD FUNCTIONS executed  successfuly: <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
            return True, None
        else:
            color_print(f"Error  executing LSD functions: {exec_result["effects"]["status"]["error"]}", RED)
            send_telegram_message(f"Error executing LSD functions : {exec_result["effects"]["status"]["error"]}")
            return False, None
    else: 
        print(f"Simulation failed")
        send_telegram_message(f"Simulation -- Error  executing LSD functions : {txBlock}")
        return False

  

"""
Execute a transaction to increment the BEE farm epoch in HiveChronicle APP
"""
def increment_bee_farm_epoch(rpc_url, private_key_hex_string, protocol_config) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
    txBlock = SyncTransaction(client=suiClient)
    txBlock.move_call(
        target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_chronicles::increment_bee_farm_epoch",
        arguments=[
                        ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]),
                        ObjectID(protocol_config["HIVE_MANAGER"]),
                        ObjectID(protocol_config["BEE_TOKEN_POLICY"]),
                        ObjectID(protocol_config["BEE_CAP"]),
            ],
            type_arguments=[SUI_TYPE],
        )
    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        exec_result = handle_result(txBlock.execute(gas_budget="10000000"))
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"BEE-Farm Epoch Incremented successfuly: {exec_result["digest"]}", GREEN)
            send_telegram_message(f"BEE-Farm Epoch Incremented successfuly: <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
            return True, None
        else:
            color_print(f"Error Incrementing BEE-Farm Epoch: {exec_result["effects"]["status"]["error"]}", RED)
            send_telegram_message(f"Error Incrementing BEE-Farm Epoch : {exec_result["effects"]["status"]["error"]}")
            return False, None
    else: 
        print(f"Simulation failed")
        send_telegram_message(f"Simulation -- Error Incrementing BEE-Farm Epoch : {txBlock}")
        return False
    
    

"""
Execute a transaction to increment the Time-Stream Cycle (first half)
"""
def increment_timeStream_part_1(rpc_url, private_key_hex_string, protocol_config, prev_streamer_rank1_profile, prev_streamer_rank2_profile, prev_streamer_rank3_profile) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
    txBlock = SyncTransaction(client=suiClient)
    txBlock.move_call(
        target=f"{protocol_config["HIVE_PACKAGE"]}::hive::increment_stream_part_1",
        arguments=[     ObjectID(CLOCK),
                        ObjectID(protocol_config["PROFILE_MAPPING_STORE"]),
                        ObjectID(protocol_config["HIVE_VAULT"]),
                        ObjectID(prev_streamer_rank1_profile),
                        ObjectID(prev_streamer_rank2_profile),
                        ObjectID(prev_streamer_rank3_profile),
            ],
            type_arguments=[SUI_TYPE],
        )
    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        exec_result = handle_result(txBlock.execute())
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"Time-Stream Cycle Incremented successfuly (part 1): {exec_result["digest"]}", GREEN)
            send_telegram_message(f"Time-Stream Cycle Incremented successfuly (part 1): <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
            return True
        else:
            color_print(f"Error Incrementing Time-Stream Cycle (part 1): {exec_result["effects"]["status"]["error"]}", RED)
            send_telegram_message(f"Error Incrementing Time-Stream Cycle (part 1): {exec_result["effects"]["status"]["error"]} \nTxhash - <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
            return False
    else: 
        print(f"Simulation failed")
        send_telegram_message(f"Simulation -- Error Incrementing Time-Stream Cycle (part 1): {txBlock}")
        return False

"""
Execute a transaction to increment the Time-Stream Cycle (2nd half)
"""
def increment_timeStream_part_2(rpc_url, private_key_hex_string, protocol_config, new_streamer_rank1, new_streamer_rank2, new_streamer_rank3) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
    txBlock = SyncTransaction(client=suiClient)
    txBlock.move_call(
        target=f"{protocol_config["TWO_TOKEN_AMM_PACKAGE"]}::bee_trade::increment_stream_part_2",
        arguments=[     ObjectID(CLOCK),
                        ObjectID(protocol_config["PROFILE_MAPPING_STORE"]),
                        ObjectID(protocol_config["HIVE_VAULT"]),
                        ObjectID(new_streamer_rank1),
                        ObjectID(new_streamer_rank2),
                        ObjectID(new_streamer_rank3),
                        ObjectID(protocol_config["BEE_CAP"]),                        
                        ObjectID(protocol_config["BEE_TOKEN_POLICY"])
            ],
            type_arguments=[SUI_TYPE],
        )
    simulation_response, txBlock = simulate_tx(txBlock)
    if (simulation_response):
        print(f"Simulation successful")
        exec_result = handle_result(txBlock.execute(gas_budget="10000000"))
        exec_result = exec_result.to_json()
        exec_result = json.loads(exec_result)
        if (exec_result["effects"]["status"]["status"] == "success"):
            color_print(f"Time-Stream Cycle Incremented successfuly (part 2): {exec_result["digest"]}", GREEN)
            send_telegram_message(f"Time-Stream Cycle Incremented successfuly (part 2): <a href='https://testnet.suivision.xyz/txblock/{exec_result["digest"]}>{exec_result["digest"]}</a>")
            return True
        else:
            color_print(f"Error Incrementing Time-Stream Cycle (part 2): {exec_result["effects"]["status"]["error"]}", RED)
            send_telegram_message(f"Error Incrementing Time-Stream Cycle (part 2): {exec_result["effects"]["status"]["error"]}")
            return False
    else: 
        print(f"Simulation failed")
        send_telegram_message(f"Simulation -- Error Incrementing Time-Stream Cycle (part 2): {txBlock}")
        return False





 
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
def getOwnerForHiveProfile(rpc_url, private_key_hex_string, protocol_config, hiveProfileID) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVEPROFILE_PACKAGE"]}::hive_profile::get_profile_owner",
            arguments=[ ObjectID(hiveProfileID) ],  type_arguments=[], )
        simulation = txBlock.inspect_all()
        simulation_json = json.loads(simulation.to_json())
        hive_profile_owner = HiveProfileOwnerInfo.deserialize( simulation_json["results"][0]["returnValues"][0][0]) 
        hive_profile_owner = json.loads(hive_profile_owner.to_json())
        return "0x" + hive_profile_owner["owner"]
    except Exception as e:
        color_print(f"onchain_helpers/getOwnerForHiveProfile: Error -  {e}", RED)
        return None



  


"""
Fetch HiveChronicle state information for a user profile from chain 
"""
def getHiveProfileIdForUser(rpc_url, private_key_hex_string, protocol_config, user_address) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVEPROFILE_PACKAGE"]}::hive_profile::does_user_own_profile",
            arguments=[  ObjectID(protocol_config["PROFILE_MAPPING_STORE"]),  SuiAddress(user_address) ],
                type_arguments=[],
            )
        simulation = txBlock.inspect_all()
        simulation_json = json.loads(simulation.to_json())
        hive_profile_info = HiveProfileIdInfo.deserialize( simulation_json["results"][0]["returnValues"][0][0] + simulation_json["results"][0]["returnValues"][1][0] ) 
        hive_profile_info = json.loads(hive_profile_info.to_json())
        return "0x" + hive_profile_info["profile_id"]
    except Exception as e:
        color_print(f"onchain_helpers/getHiveProfileIdForUser: Error -  {e}", RED)
        return None



  

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
        return json.loads(hive_chronicle_info.to_json())
    except Exception as e:
        color_print(f"onchain_helpers/getHiveChronicleInfo: Error -  {e}", RED)
        return None

"""
Fetch a profile's Time-Stream state information from chain 
"""
def getTimeStreamStateForProfileInfo(rpc_url, private_key_hex_string, protocol_config, user_profile) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"{protocol_config["HIVE_PACKAGE"]}::hive::get_state_for_profile",
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
                                                    + simulation_json["results"][0]["returnValues"][10][0]  + simulation_json["results"][0]["returnValues"][11][0]
                                                ) 
        return json.loads(time_stream_state_info.to_json())
    except Exception as e:
        color_print(f"onchain_helpers/getTimeStreamStateForProfileInfo: Error -  {e}", RED)
        return None
     
# --------------------- x -----------------------------------
# --------------------- x -----------------------------------
# --------------------- x -----------------------------------

"""
Get current epoch
"""
def getEpochInfo(rpc_url, private_key_hex_string):
    try: 
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        txBlock = SyncTransaction(client=suiClient)
        txBlock.move_call(
            target=f"0x2::tx_context::epoch",
            arguments=[],
            type_arguments=[],
        )
        txBlock.move_call(
            target=f"0x2::tx_context::epoch_timestamp_ms",
            arguments=[],
            type_arguments=[],
        )
        simulation = txBlock.inspect_all()
        simulation_json = json.loads(simulation.to_json())
        current_epochInfo = EpochInfo.deserialize( simulation_json["results"][0]["returnValues"][0][0] + simulation_json["results"][1]["returnValues"][0][0] )
        return json.loads(current_epochInfo.to_json())
    except Exception as e:
        color_print(f"onchain_helpers/getEpochInfo: Error -  {e}", RED)
        return None

"""
Get HiveProfile Info
"""
def getHiveProfileInfo(rpc_url, private_key_hex_string, hiveProfileID ) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        hiveProfile = (suiClient.get_object(hiveProfileID))
        hiveProfile = hiveProfile.result_data.to_dict()["content"]["fields"]
        print(f"hiveProfile username: {hiveProfile["username"] }")
        print(f"hiveProfile bio: {hiveProfile["bio"] }")
        return hiveProfile
    except Exception as e:
        color_print(f"onchain_helpers/getHiveProfileInfo: Error -  {e}", RED)
        return None


"""
Get GLobal TimeStream Info
"""
def getTimeStreamInfo(rpc_url, private_key_hex_string, protocol_config) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)

        StreamerBuzzObject = (suiClient.get_object(protocol_config["STREAMER_BUZZ_OBJECT"]))
        StreamerBuzzObject = StreamerBuzzObject.result_data.to_dict()["content"]["fields"]

        # Current streamers
        streamerProfile1 = StreamerBuzzObject["streamers_info"]["fields"]["rank1_profile"]
        streamerProfile2 = StreamerBuzzObject["streamers_info"]["fields"]["rank2_profile"]
        streamerProfile3 = StreamerBuzzObject["streamers_info"]["fields"]["rank3_profile"]

        # Current leading bids
        leadingBidsInfo = {
            "o_profile_addr": StreamerBuzzObject["leading_bids"]["fields"]["o_profile_addr"],
            "o_bid_amt": StreamerBuzzObject["leading_bids"]["fields"]["o_bid_amt"],
            "s_profile_addr": StreamerBuzzObject["leading_bids"]["fields"]["s_profile_addr"],
            "s_bid_amt": StreamerBuzzObject["leading_bids"]["fields"]["s_bid_amt"],
            "t_profile_addr": StreamerBuzzObject["leading_bids"]["fields"]["t_profile_addr"],
            "t_bid_amt": StreamerBuzzObject["leading_bids"]["fields"]["t_bid_amt"],
        }

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
        # print(simulation_json)
        
        time_stream_config_params = TimeStreamConfigParams.deserialize( simulation_json["results"][0]["returnValues"][0][0] + simulation_json["results"][0]["returnValues"][1][0]
                                            + simulation_json["results"][0]["returnValues"][2][0] + simulation_json["results"][0]["returnValues"][3][0]
                                                + simulation_json["results"][0]["returnValues"][4][0] + simulation_json["results"][0]["returnValues"][5][0]
                                                    + simulation_json["results"][0]["returnValues"][6][0] + simulation_json["results"][0]["returnValues"][7][0]
                                                    + simulation_json["results"][0]["returnValues"][8][0] + simulation_json["results"][0]["returnValues"][9][0]
                                                    + simulation_json["results"][0]["returnValues"][10][0] + simulation_json["results"][0]["returnValues"][11][0]
                                                )
        # print(f"time_stream_config_params: {time_stream_config_params}")
        
        time_streamer1_info = TimeStreamerInfo.deserialize(# simulation_json["results"][1]["returnValues"][0][0] + simulation_json["results"][1]["returnValues"][1][0]
                                            simulation_json["results"][1]["returnValues"][2][0] + simulation_json["results"][1]["returnValues"][3][0]
                                                + simulation_json["results"][1]["returnValues"][4][0] + simulation_json["results"][1]["returnValues"][5][0]
                                                    + simulation_json["results"][1]["returnValues"][6][0] + simulation_json["results"][1]["returnValues"][7][0]
                                                    + simulation_json["results"][1]["returnValues"][8][0] )
        time_streamer1_info = json.loads(time_streamer1_info.to_json())
        time_streamer1_info["profile_addr"] = streamerProfile1

        time_streamer2_info = TimeStreamerInfo.deserialize( # simulation_json["results"][2]["returnValues"][0][0] + simulation_json["results"][2]["returnValues"][1][0]
                                                simulation_json["results"][2]["returnValues"][2][0] + simulation_json["results"][2]["returnValues"][3][0]
                                                + simulation_json["results"][2]["returnValues"][4][0] + simulation_json["results"][2]["returnValues"][5][0]
                                                    + simulation_json["results"][2]["returnValues"][6][0] + simulation_json["results"][2]["returnValues"][7][0]
                                                    + simulation_json["results"][2]["returnValues"][8][0] )
        time_streamer2_info = json.loads(time_streamer2_info.to_json())
        time_streamer2_info["profile_addr"] = streamerProfile2

        time_streamer3_info = TimeStreamerInfo.deserialize( # simulation_json["results"][3]["returnValues"][0][0] + simulation_json["results"][3]["returnValues"][1][0]
                                                simulation_json["results"][3]["returnValues"][2][0] + simulation_json["results"][3]["returnValues"][3][0]
                                                + simulation_json["results"][3]["returnValues"][4][0] + simulation_json["results"][3]["returnValues"][5][0]
                                                    + simulation_json["results"][3]["returnValues"][6][0] + simulation_json["results"][3]["returnValues"][7][0]
                                                    + simulation_json["results"][3]["returnValues"][8][0] )
        time_streamer3_info = json.loads(time_streamer3_info.to_json())
        time_streamer3_info["profile_addr"] = streamerProfile3
        
        leading_bids_info = LeadingBidsInfo.deserialize( simulation_json["results"][4]["returnValues"][0][0] + simulation_json["results"][4]["returnValues"][1][0], 
                                            + simulation_json["results"][4]["returnValues"][2][0] + simulation_json["results"][4]["returnValues"][3][0]
                                                + simulation_json["results"][4]["returnValues"][4][0] + simulation_json["results"][4]["returnValues"][5][0] )

        time_stream_pol_info = TimeStreamPolInfo.deserialize( simulation_json["results"][5]["returnValues"][0][0] + simulation_json["results"][5]["returnValues"][1][0] )
        # print(f"time_stream_pol_info: {time_stream_pol_info}")

        time_stream_engagement_scores_state = TimeStreamEngagementScoresState.deserialize( simulation_json["results"][6]["returnValues"][0][0] + simulation_json["results"][6]["returnValues"][1][0]
                                            + simulation_json["results"][6]["returnValues"][2][0] + simulation_json["results"][6]["returnValues"][3][0]
                                                + simulation_json["results"][6]["returnValues"][4][0] + simulation_json["results"][6]["returnValues"][5][0]
                                                    + simulation_json["results"][6]["returnValues"][6][0] + simulation_json["results"][6]["returnValues"][7][0]
                                                    + simulation_json["results"][6]["returnValues"][8][0] )
        # print(f"time_stream_engagement_scores_state: {time_stream_engagement_scores_state}")

        return {
            "config_params": json.loads(time_stream_config_params.to_json()),
            "streamer1_info": time_streamer1_info, 
            "streamer2_info": time_streamer2_info,
            "streamer3_info": time_streamer3_info,
            "leading_bids_info": leadingBidsInfo,
            "pol_info": json.loads(time_stream_pol_info.to_json()),
            "engagement_state": json.loads(time_stream_engagement_scores_state.to_json()),
        }

    except Exception as e:
        color_print(f"onchain_helpers/getTimeStreamInfo: Error -  {e}", RED)
        return None
 

"""
Get Global HiveChronicle Info
"""
def getGlobalHiveChronicleInfo(rpc_url, private_key_hex_string, protocol_config, epoch) :
    try:
        suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)
        
        
        hiveChronicleVault = (suiClient.get_object(protocol_config["HIVE_CHRONICLES_VAULT"]))
        hiveChronicleVault = hiveChronicleVault.result_data.to_dict()["content"]["fields"]
        hiveChronicleVaultToReturn = { 
            "bee_farm_info": hiveChronicleVault["bee_farm_info"]["fields"],
            "config_params": hiveChronicleVault["config_params"]["fields"],
            "total_bees_available": hiveChronicleVault["total_bees_available"],
            "welcome_buzzes_count" : hiveChronicleVault["welcome_buzzes"]["fields"]["size"],
            "system_infusion_buzzes_count" : hiveChronicleVault["system_infusion_buzzes"]["fields"]["size"],
            "lockdrop_vault_dof_manager_cap": { "name" : hiveChronicleVault["lockdrop_vault_dof_manager_cap"]["fields"]["app_name"] , "id": hiveChronicleVault["lockdrop_vault_dof_manager_cap"]["fields"]["id"]["id"] },
            "infusion_vault_dof_manager_cap": { "name" : hiveChronicleVault["infusion_vault_dof_manager_cap"]["fields"]["app_name"] , "id": hiveChronicleVault["infusion_vault_dof_manager_cap"]["fields"]["id"]["id"] },
            "hive_entry_capID": hiveChronicleVault["hive_entry_cap"]["fields"]["id"]["id"],
            "hive_chronicle_dof_cap":  { "name" : hiveChronicleVault["hive_chronicle_dof_cap"]["fields"]["app_name"] , "id": hiveChronicleVault["hive_chronicle_dof_cap"]["fields"]["id"]["id"] },
        }
        # print(hiveChronicleVaultToReturn)
                
        # if (epoch > 0):
            # txBlock = SyncTransaction(client=suiClient)
        #     txBlock.move_call( target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_entry::query_bees_farming_snampshot",
        #                         arguments=[    ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]), SuiU64(epoch) ],
        #                         type_arguments=[])                
        #     simulation = txBlock.inspect_all()
        #     simulation_json = json.loads(simulation.to_json())
        #     print(simulation_json)
        #     bee_farm_snapshot_info = BeeFarmSnapshotInfo.deserialize( simulation_json["results"][0]["returnValues"][0][0] + simulation_json["results"][0]["returnValues"][1][0]
        #                                     + simulation_json["results"][0]["returnValues"][2][0] + simulation_json["results"][0]["returnValues"][3][0]
        #                                         + simulation_json["results"][0]["returnValues"][4][0] )
        #     print(f"bee_farm_snapshot_info: {bee_farm_snapshot_info}")
        #     hiveChronicleVault["bee_farm_snapshot_info"] = bee_farm_snapshot_info
       
        return hiveChronicleVaultToReturn, None

    except Exception as e:
        color_print(f"onchain_helpers/getGlobalHiveChronicleInfo: Error -  {e}", RED)
        return None, None
 





















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
