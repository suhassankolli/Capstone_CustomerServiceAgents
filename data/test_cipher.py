import asyncio
from graphiti_core import Graphiti
from graphiti_core.llm_client import OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

from dotenv import load_dotenv
load_dotenv()
import os
open_api_key = os.getenv("OPENAI_API_KEY")
neo_url=os.getenv("NEO_URI")
neo_pwd= os.getenv("NEO_PWD")

graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    neo_pwd, 
    llm_client=OpenAIClient(),
    embedder=OpenAIEmbedder(
        config=OpenAIEmbedderConfig(embedding_model="text-embedding-3-small")
    )
)
print("Graphiti's good to go!")

async def search_knowledge(query:str):
    results = []

    try:
        await graphiti.build_indices_and_constraints(delete_existing=False)

        _query =  query # "Can you get me all the products and its details from product node for customer CUST0007?"
        results = await graphiti.search(query=_query)
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        #################################################
        # CLEANUP
        #################################################
        # Always close the connection to Neo4j when
        # finished to properly release resources
        #################################################

        # Close the connection
        await graphiti.close()
        print('\nConnection closed')

        return results

        

    ## Query the products associated with customer 
    
  


async def main():
    search_results = await search_knowledge("Can you get me all the products and its details from product node for customer CUST0007?")
    print(" Search results ")
    for result in search_results:
        print(f"{result.source.name} {result.edge_type} {result.target.name}")


if __name__ == "__main__":
    asyncio.run(main())


