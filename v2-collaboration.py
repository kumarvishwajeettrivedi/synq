import model_interface as models

def get_consensus(prompt, gemini_resp, groq_resp, openrouter_resp):
    consensus_prompt = f"""
    You are a wise judge and synthesizer. You have received three different answers to the same user prompt.
    
    USER PROMPT: {prompt}
    
    ANSWER 1 (Gemini):
    {gemini_resp}
    
    ANSWER 2 (Groq):
    {groq_resp}
    
    ANSWER 3 (OpenRouter/Llama):
    {openrouter_resp}
    
    Your task is to:
    1. Analyze the three answers.
    2. Identify the common points and any contradictions.
    3. Synthesize the best possible final answer that combines the strengths of all three.
    4. If there are disagreements, explain them and provide the most accurate information.
    
    Provide your response in a clear, structured format.
    """
    return models.query_gemini(consensus_prompt)

def main():
    prompt = input("Enter your problem: ")
    
    print("\n Fetching responses from models...\n")
    
    gemini_resp = models.query_gemini(prompt)
    print(" Gemini received")
    
    groq_resp = models.query_groq(prompt)
    print(" Groq received")
    
    openrouter_resp = models.query_openrouter(prompt)
    print(" OpenRouter received")
    
    print("\n Building Consensus...\n")
    consensus = get_consensus(prompt, gemini_resp, groq_resp, openrouter_resp)
    
    final_output = f"""
======================
     MULTI-LLM OUTPUT
======================

 GEMINI:
{gemini_resp}

 GROQ:
{groq_resp}

 OPENROUTER (Llama-3.1):
{openrouter_resp}

======================
  FINAL CONSENSUS
======================
{consensus}
"""
    print(final_output)

if __name__ == "__main__":
    main()
