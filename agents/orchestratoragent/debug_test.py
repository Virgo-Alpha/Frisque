# agents/orchestratoragent/debug_test.py

# We import the specific function we want to test
from app.agent import company_researcher

# This block allows us to run this file directly as a script
if __name__ == "__main__":
    print("--- Starting direct tool test ---")
    
    # We will call the function directly with a hardcoded value
    company_name = "Figma"
    print(f"Testing the company_researcher tool with input: '{company_name}'")
    
    # Call the function and store the result
    result = company_researcher(company_name)
    
    # Print the final result
    print("\n--- Test Result ---")
    print(result)
    print("--- End of test ---")