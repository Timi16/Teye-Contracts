"""
Teye-Contracts: Soroban Event Poller Example
----------------------------------------------
Polls the Soroban RPC for events emitted by your contract.

Install: pip install stellar-sdk
"""
import time
import pydantic
from requests.exceptions import ConnectionError
from stellar_sdk import SorobanServer
from stellar_sdk.soroban_rpc import EventFilter, EventFilterType
from stellar_sdk.exceptions import SorobanRpcErrorResponse

RPC_URL = "https://soroban-testnet.stellar.org"
CONTRACT_ID = "C..." 
POLL_INTERVAL_SECONDS = 5 

def main():
    server = SorobanServer(RPC_URL)
    
    try:
        start_ledger = server.get_latest_ledger().sequence
    except ConnectionError as e:
        print(f"Network Connection failed: {e}")
        return
        
    # Use the EventFilterType enum instead of a raw string
    contract_filter = EventFilter(type=EventFilterType.CONTRACT, contract_ids=[CONTRACT_ID])
    last_cursor = None

    while True:
        try:
            current_ledger = server.get_latest_ledger().sequence
            if current_ledger >= start_ledger:
                
                fetching_pages = True
                while fetching_pages:
                    # Fix limit syntax and use cursor for pagination
                    response = server.get_events(
                        start_ledger=start_ledger,
                        filters=[contract_filter],
                        limit=100,
                        cursor=last_cursor
                    )
                    
                    if response.events:
                        for event in response.events:
                            print(f"🔔 Processed Event [{event.id}] in Ledger {event.ledger}")
                        
                        # Update the cursor to the final event in this batch
                        last_cursor = response.events[-1].paging_token
                        
                        if len(response.events) < 100:
                            fetching_pages = False
                    else:
                        fetching_pages = False
                        
                # Advance the ledger track after paginating through all events
                start_ledger = current_ledger + 1

        # Targeted Exception Handling
        except SorobanRpcErrorResponse as e:
            print(f"RPC Error: {e}")
        except ConnectionError as e:
            print(f"Network failure: {e}")
        except pydantic.ValidationError as e:
            print(f"Payload validation error: {e}")
        except TypeError as e:
            print(f"Pagination type error: {e}")
        except Exception as e:
            raise e
            
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()