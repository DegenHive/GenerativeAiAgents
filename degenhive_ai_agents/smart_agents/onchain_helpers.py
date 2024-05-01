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
            prv_keys=[ {'wallet_key': "0x" + private_key_hex_string, 'key_scheme': SignatureScheme.ED25519}],
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
            prv_keys=[ {'wallet_key': "0x" + private_key_hex_string, 'key_scheme': SignatureScheme.ED25519}],
        ))
    print(suiClient)
    return suiClient


async def kraftHiveProfileTx(rpc_url, private_key_hex_string, protocol_config, name, bio) :
    suiClient = getSuiSyncClient(rpc_url, private_key_hex_string)     
    txBlock = SyncTransaction(client=suiClient)

    # spendable_sui = await getSpendableSui(suiClient, txBlock, 0)

    # spendable_sui = txBlock.move_call(
    #     target=f"0x2::coin::zero",
    #     arguments=[],
    #     type_arguments=[SUI_TYPE],
    # )

    # txBlock.move_call(
    #     target=f"{protocol_config["HIVE_ENTRY_PACKAGE"]}::hive_chronicles::kraft_hive_profile",
    #     arguments=[
    #                ObjectID(protocol_config["HIVE_CHRONICLES_VAULT"]),
    #                ObjectID(CLOCK),
    #                ObjectID(SUI_SYSTEM_STATE),
    #                ObjectID(protocol_config["DSUI_VAULT"]),
    #                ObjectID(protocol_config["PROFILE_MAPPING_STORE"]),
    #                ObjectID(protocol_config["HIVE_MANAGER"]),
    #                ObjectID(protocol_config["DSUI_DISPERSER"]),
    #                spendable_sui,
    #                SuiString(name),
    #                SuiString(bio),
    #         ],
    #         type_arguments=[],
    #     )

    txBlock.transfer_sui(recipient=SuiAddress("0xd13648ab4f9eecac1daec0b6a6316320237102362a5595838bbac9409c984bfd"), from_coin=ObjectID("0x630738e1189f0c7d3261869b6c4da3c42666a20f12bf9afcb18161679f3d5421"), amount=SuiInteger(1000000))


#   recipient: Union[ObjectID, SuiAddress],
#         from_coin: Union[str, ObjectID, ObjectRead, SuiCoinObject, bcs.Argument],
#         amount: Optional[Union[
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
