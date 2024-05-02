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

from canoser import Struct, Uint8, Uint64

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


class HiveChronicleState(Struct):
    _fields = [
        ('active_epoch', Uint64),
        ('max_entropy_for_cur_epoch', Uint64),
        ('remaining_entropy', Uint64),
        ('total_hive_gems', Uint64),
        ('usable_hive_gems', Uint64),
        ('entropy_inbound', Uint64),
        ('entropy_outbound', Uint64),
        ('total_bees_farmed', Uint64),
        ('simulated_bees_from_entropy', Uint64),
        ('rebuzzes_count', Uint64),
        ('noise_buzzes_count', Uint64),
        ('last_noise_epoch', Uint64),
        ('noise_count', Uint64),
        ('chronicle_buzzes_count', Uint64),
        ('last_chronicle_epoch', Uint64),
        ('chronicle_count', Uint64),
        ('buzz_chains_count', Uint64),
        ('last_buzz_epoch', Uint64),
        ('buzz_count', Uint64),
        ('subscribers_only', Uint8),
        ('infusion_buzzes_count', Uint64),
        ('infusion_count', Uint64),

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

def getHiveChronicleInfo(rpc_url, private_key_hex_string, protocol_config, user_profile) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)

    print(f"HIVE_MANAGER: {protocol_config["HIVE_MANAGER"]}")
    print(f"HIVE_CHRONICLES_VAULT: {protocol_config["HIVE_CHRONICLES_VAULT"]}")
    print(f"user_profile: {user_profile}")


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
    print(simulation_json["results"][0]["returnValues"][0] )

    obj = HiveChronicleState.deserialize(simulation_json["results"][0]["returnValues"][0])
    print(obj)

    # user_hive_chronicle = {}
    # user_hive_chronicle.active_epoch = bcs.
    




# [{'mutableReferenceOutputs': [[{'Input': 2}, [168, 3, 51, 152, 207, 32, 37, 186, 184, 170, 189, 207, 9, 218, 235, 147, 23, 158, 234, 155, 245, 181, 236, 176, 165, 221, 103, 59, 172, 170, 186, 162, 162, 148, 255, 234, 76, 211, 30, 169, 186, 241, 66, 24, 176, 73, 56, 33, 231, 195, 33, 60, 225, 3, 33, 15, 7, 129, 83, 216, 251, 229, 49, 174, 100, 113, 145, 199, 25, 241, 71, 10, 53, 90, 32, 230, 16, 250, 128, 12, 118, 18, 94, 50, 221, 55, 143, 247, 30, 17, 99, 188, 134, 220, 243, 186, 14, 72, 105, 118, 101, 67, 104, 114, 111, 110, 105, 99, 108, 101, 115, 1, 0, 1, 159, 58, 168, 170, 42, 159, 176, 127, 68, 111, 145, 141, 197, 43, 116, 29, 200, 153, 173, 240, 244, 27, 84, 80, 229, 124, 125, 49, 195, 151, 12, 102, 16, 67, 69, 76, 69, 83, 84, 73, 65, 76, 95, 66, 69, 73, 78, 71, 83, 53, 98, 175, 185, 166, 204, 49, 28, 224, 203, 193, 112, 105, 80, 252, 178, 143, 156, 57, 138, 85, 71, 74, 210, 168, 253, 224, 163, 48, 173, 132, 67, 12, 86, 65, 77, 80, 73, 82, 69, 83, 95, 68, 69, 78, 73, 64, 205, 157, 8, 17, 166, 251, 188, 116, 237, 200, 47, 243, 210, 138, 109, 155, 98, 110, 18, 208, 244, 84, 154, 93, 46, 116, 150, 226, 18, 140, 15, 66, 69, 69, 95, 72, 73, 86, 69, 95, 83, 84, 82, 69, 65, 77, 24, 0, 0, 0, 0, 0, 0, 0, 24, 0, 0, 0, 0, 0, 0, 0, 24, 0, 0, 0, 0, 0, 0, 0, 24, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 64, 150, 54, 225, 86, 214, 48, 66, 200, 151, 35, 33, 46, 62, 252, 107, 24, 64, 234, 33, 6, 218, 249, 74, 79, 91, 251, 53, 215, 88, 88, 136, 20, 0, 0, 0, 0, 0, 0, 0, 1, 24, 73, 78, 73, 84, 73, 65, 76, 73, 90, 69, 95, 65, 73, 82, 68, 82, 79, 80, 95, 86, 65, 85, 76, 84, 1, 22, 67, 76, 65, 73, 77, 95, 73, 78, 70, 85, 83, 73, 79, 78, 95, 82, 69, 87, 65, 82, 68, 83, 18, 173, 142, 216, 228, 99, 236, 109, 111, 254, 155, 194, 133, 109, 208, 3, 97, 187, 218, 123, 89, 25, 145, 158, 128, 250, 10, 149, 240, 47, 247, 146, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 203, 68, 98, 19, 202, 82, 29, 189, 95, 52, 74, 103, 166, 112, 31, 186, 143, 18, 162, 116, 227, 184, 185, 89, 14, 151, 129, 55, 39, 162, 142, 88, 9, 0, 0, 0, 0, 0, 0, 0, 1, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 49, 1, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 57, 9, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 49, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 50, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 51, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 52, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 53, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 54, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 55, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 56, 14, 87, 69, 76, 67, 79, 77, 69, 95, 66, 85, 90, 90, 95, 57, 202, 22, 253, 52, 251, 156, 0, 0, 99, 1, 0, 0, 0, 0, 0, 0, 238, 92, 84, 188, 83, 52, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 72, 176, 71, 156, 73, 41, 49, 229, 209, 205, 191, 144, 173, 181, 186, 157, 118, 115, 192, 70, 66, 142, 231, 71, 230, 137, 157, 213, 218, 173, 69, 216, 3, 0, 0, 0, 0, 0, 0, 0, 1, 96, 1, 0, 0, 0, 0, 0, 0, 1, 98, 1, 0, 0, 0, 0, 0, 0], '0xcbdb23195ae9d63a492d0257ea32e707973db35eebf09b3f6e9388414a8b39a::hive_chronicles::HiveChroniclesVault']], 
#   'returnValues': [[[99, 1, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[1, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[99, 1, 0, 0, 0, 0, 0, 0], 'u64'], [[1, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[1, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[99, 1, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[99, 1, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0], 'u8'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64'], [[0, 0, 0, 0, 0, 0, 0, 0], 'u64']]}]






#     let user_hive_chronicle: any = {};
#     user_hive_chronicle.active_epoch = deserializeValue(0, BCS.U64, resp);
#     user_hive_chronicle.max_entropy_for_cur_epoch = deserializeValue(
#       1,
#       BCS.U64,
#       resp
#     );
#     user_hive_chronicle.remaining_entropy = deserializeValue(2, BCS.U64, resp);
#     user_hive_chronicle.total_hive_gems = deserializeValue(3, BCS.U64, resp);
#     user_hive_chronicle.usable_hive_gems = deserializeValue(4, BCS.U64, resp);

#     user_hive_chronicle.entropy_inbound = deserializeValue(5, BCS.U64, resp);
#     user_hive_chronicle.entropy_outbound = deserializeValue(6, BCS.U64, resp);

#     user_hive_chronicle.total_bees_farmed = deserializeValue(7, BCS.U64, resp);

#     user_hive_chronicle.simulated_bees_from_entropy = deserializeValue(
#       8,
#       BCS.U64,
#       resp
#     );
#     user_hive_chronicle.rebuzzes_count = deserializeValue(9, BCS.U64, resp);

#     user_hive_chronicle.noise_buzzes_count = deserializeValue(
#       10,
#       BCS.U64,
#       resp
#     );
#     user_hive_chronicle.last_noise_epoch = deserializeValue(11, BCS.U64, resp);
#     user_hive_chronicle.noise_count = deserializeValue(12, BCS.U64, resp);
#     user_hive_chronicle.chronicle_buzzes_count = deserializeValue(
#       13,
#       BCS.U64,
#       resp
#     );
#     user_hive_chronicle.last_chronicle_epoch = deserializeValue(
#       14,
#       BCS.U64,
#       resp
#     );

#     user_hive_chronicle.chronicle_count = deserializeValue(15, BCS.U64, resp);

#     user_hive_chronicle.buzz_chains_count = deserializeValue(16, BCS.U64, resp);
#     user_hive_chronicle.last_buzz_epoch = deserializeValue(17, BCS.U64, resp);
#     user_hive_chronicle.buzz_count = deserializeValue(18, BCS.U64, resp);
#     user_hive_chronicle.subscribers_only = deserializeValue(19, BCS.U8, resp);
#     user_hive_chronicle.infusion_buzzes_count = deserializeValue(
#       20,
#       BCS.U64,
#       resp
#     );
#     user_hive_chronicle.infusion_count = deserializeValue(21, BCS.U64, resp);

#     return user_hive_chronicle;
#   } catch (e) {
#     console.log("Error in sui_get_hive_chronicle_info");
#     console.log(e);
#     return {
#       active_epoch: 0,
#       max_entropy_for_cur_epoch: 0,
#       remaining_entropy: 0,
#       total_hive_gems: 0,
#       usable_hive_gems: 0,

#       entropy_inbound: 0,
#       entropy_outbound: 0,
#       total_bees_farmed: 0,

#       simulated_bees_from_entropy: 0,
#       rebuzzes_count: 0,

#       noise_buzzes_count: 0,
#       last_noise_epoch: 0,
#       noise_count: 0,
#       chronicle_buzzes_count: 0,
#       last_chronicle_epoch: 0,
#       chronicle_count: 0,
#       buzz_chains_count: 0,
#       last_buzz_epoch: 0,
#       buzz_count: 0,
#       subscribers_only: 0,
#       infusion_buzzes_count: 0,
#       infusion_count: 0,
#     };
#   }
# }













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
