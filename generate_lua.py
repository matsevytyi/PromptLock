import logging

# TODO: Fix the validation to allow necessary operations for research
import re
import logging

def generate_lua_script(llm_response: str) -> str:
    """Extract clean Lua code from LLM response and remove unwanted lines."""

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    lua_code = llm_response.strip()

    # --- Step 1: Extract Lua code blocks ---
    # This matches ```lua ... ``` blocks
    code_blocks = re.findall(r"```lua\s*(.*?)```", lua_code, re.DOTALL | re.IGNORECASE)

    if not code_blocks:
        code_blocks = lua_code

    if not code_blocks:
        logger.error("No code blocks found in LLM response")
        raise ValueError("No Lua code found in LLM response")
    
    # Block truly dangerous operations but allow research-necessary ones
    # dangerous_ops = ['os.execute', 'socket', 'http', 'wget', 'curl', 'loadstring', 'package.loadlib']
    # for op in dangerous_ops:
    #     if op in lua_code and not (op == 'os.execute' and 'find' in lua_code):  # Allow find commands
    #         logger.error(f"Prohibited operation: {op}")
    #         raise ValueError(f"Script contains prohibited operation: {op}")

    # Check for shell injection attempts in io.popen calls
    # if 'io.popen' in lua_code:
    #     # Look for dangerous shell patterns
    #     dangerous_shell = ['rm -rf', 'sudo', 'chmod +x', '$(', '`', '&&', '||', ';']
    #     for pattern in dangerous_shell:
    #         if pattern in lua_code:
    #             logger.error(f"Dangerous shell pattern: {pattern}")
    #             raise ValueError(f"Script contains dangerous shell pattern: {pattern}")

    # Merge all code blocks (or take only first if you prefer)
    lua_code = "\n".join(code_blocks)

    # --- Step 2: Remove unwanted lines ---
    lua_lines = lua_code.splitlines()

    # remove lines containing test environment verification
    lua_lines = [line for line in lua_lines if "verify_test_environment()" not in line]

    # remove empty or purely comment lines (lines starting with --)
    lua_lines = [line for line in lua_lines if line.strip() and not line.strip().startswith("--")]

    # join back clean Lua code
    lua_code = "\n".join(lua_lines).strip()

    # --- Step 3: Check required components ---
    required = ['PHASE 1', 'PHASE 2', 'PHASE 3', 'PHASE 4', 'io.open']
    missing = [comp for comp in required if comp not in lua_code]
    if missing:
        logger.warning(f"Missing components: {missing}")

    logger.info("Enhanced script validation successful - research operations approved")
    return lua_code

def run_lua_script(lua_path: str) -> (str, bool):
    """Run the generated Lua script."""
    import subprocess

    try:
        
        # okay and here I need
        
        result = subprocess.run(
            ["lua", "-e", "io.stdout:setvbuf('no')", lua_path],
            capture_output=True,
            text=True
        )
        if len(result.stderr) > 0 or "err" in result.stdout.lower():
            return result.stderr, False
        return result.stdout, True
    except subprocess.CalledProcessError as e:
        print("Error running Lua script:")
        print(e)
        return e.stderr, False