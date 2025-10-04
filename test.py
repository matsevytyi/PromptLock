from generate_prompt import create_llm_client, generate_prompt, generate_lua_script
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ")

# This should now work
#client = create_llm_client("ollama", model="deepseek-coder:6.7b")
client = create_llm_client("groq", api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")

metadata = {
    "os": "MacOS",
    "arch": "arm64",
    "errors_messages": """ERROR: /Users/andriimatsevytyi/Downloads/phase1.lua:20: attempt to index a nil value (field 'filename'),lua: /Users/andriimatsevytyi/Downloads/phase1.lua:23: attempt to mod a 'string' with a 'nil'
    stack traceback:
	[C]: in metamethod 'mod'
	/Users/andriimatsevytyi/Downloads/phase1.lua:23: in local 'mapDirectory'
	/Users/andriimatsevytyi/Downloads/phase1.lua:65: in upvalue 'phase1'
	/Users/andriimatsevytyi/Downloads/phase1.lua:367: in local 'main'
	/Users/andriimatsevytyi/Downloads/phase1.lua:408: in main chunk
	[C]: in ?
    stack traceback:
	/Users/andriimatsevytyi/Downloads/phase1.lua:20: in local 'walkDirectory'
	/Users/andriimatsevytyi/Downloads/phase1.lua:52: in local 'phase1_directory_recon'
	/Users/andriimatsevytyi/Downloads/phase1.lua:215: in main chunk
	[C]: in ?
    lua: /Users/andriimatsevytyi/Downloads/phase1.lua:10: bad argument #1 to 'for iterator' (table expected, got boolean)
    stack traceback:
	[C]: in function 'next'
	/Users/andriimatsevytyi/Downloads/phase1.lua:10: in local 'phase1_reconnaissance'
	/Users/andriimatsevytyi/Downloads/phase1.lua:36: in main chunk
	[C]: in ?
    lua: /Users/andriimatsevytyi/Downloads/phase1.lua:198: attempt to call a nil value (field 'merge')
    stack traceback:
	/Users/andriimatsevytyi/Downloads/phase1.lua:198: in local 'main'
	/Users/andriimatsevytyi/Downloads/phase1.lua:232: in main chunk
	[C]: in ?
    Phase 1 execution time: 0 seconds
    Phase 1 directories found: 0
    Phase 2 execution time: 0 seconds
    Phase 2 personal data points found: 0
    Phase 3 execution time: 0 seconds
    Phase 3 user intelligence points found: 0
    Phase 4 execution time: 0 seconds
    Phase 4 sensitive documents found: 0
    table: 0x600001898c00
 """
}

prompt = generate_prompt(metadata)



response = client.generate(prompt)

script = generate_lua_script(response["response"])

print("response:", script)
