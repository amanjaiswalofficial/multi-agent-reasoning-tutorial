# main.py
import asyncio
import os
from agents.fetch_agent import fetch_articles
from agents.decision_agent import create_decision_agent, PERSONAS
from agents.arbiter_agent import create_arbiter_agent

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def save_article(index, article, decisions, debate_responses, final):
    # Save detailed report
    filename = f"{OUTPUT_DIR}/article_{index+1}.md"
    with open(filename, "w") as f:
        f.write(f"# {article.title}\n")
        f.write(f"{article.url}\n")
        f.write(f"**Word Count:** {article.word_count}\n\n")
        
        f.write("## Article Summary\n")
        f.write(f"{article.summary}\n\n")
        
        f.write("## Stage 1: Initial Agent Decisions\n")
        for name, decision in decisions:
            f.write(f"### {name}\n")
            f.write(f"**Decision:** `{decision.action}` (confidence: {decision.confidence:.2f})\n")
            f.write(f"**Reason:** {decision.reason}\n\n")
            f.write("**Reasoning Chain:**\n")
            for step in decision.reasoning_chain:
                f.write(f"- {step.step}: {step.analysis} (confidence: {step.confidence:.2f})\n")
            f.write(f"\n**Key Factors:** {', '.join(decision.key_factors)}\n\n")
        
        f.write("## Phase 2: Debate Responses\n")
        for resp in debate_responses:
            f.write(f"### {resp.agent_name} Response\n")
            f.write(f"**Responding to:** {resp.response_to}\n")
            f.write(f"**Argument:** {resp.argument}\n")
            f.write(f"**Counter-points:** {', '.join(resp.counter_points)}\n")
            f.write(f"**Final Stance:** {resp.final_stance.action} - {resp.final_stance.reason}\n\n")
        
        f.write("## Phase 3: Final Arbiter Decision\n")
        f.write(f"**Action:** `{final.action}` (confidence: {final.confidence:.2f})\n")
        f.write(f"**Reason:** {final.reason}\n\n")
        f.write("**Arbiter Reasoning Chain:**\n")
        for step in final.reasoning_chain:
            f.write(f"- {step.step}: {step.analysis} (confidence: {step.confidence:.2f})\n")
        f.write(f"\n**Key Factors:** {', '.join(final.key_factors)}\n")

    print(f"Detailed analysis saved to {filename}")

async def process_article(article, index):
    print(f"\nProcessing: {article.title}")
    print(f"Word count: {article.word_count}")
    
    # Stage 1: Initial decisions with reasoning
    print("\nStage 1: Initial agent decisions...")
    decisions = []
    
    for name, prompt in PERSONAS.items():
        agent_run, agent_debate = create_decision_agent(name, prompt)
        result = await agent_run(article)
        decisions.append((name, result))
        print(f"{name}: {result.action} (confidence: {result.confidence:.2f})")

    # Stage 2: Debate round
    print("\nStage 2: Inter-agent debate...")
    debate_responses = []
    
    for name, prompt in PERSONAS.items():
        agent_run, agent_debate = create_decision_agent(name, prompt)
        other_decisions = [(n, d) for n, d in decisions if n != name]
        if other_decisions:
            debate_resp = await agent_debate(article, other_decisions, round_num=1)
            debate_responses.append(debate_resp)
            print(f"  ✓ {name} debated and adjusted stance")

    # Stage 3: Final arbiter decision
    print("\nStage 3: Arbiter final decision...")
    arbiter = create_arbiter_agent()
    final = await arbiter(article, decisions, debate_responses)
    print(f"Final decision: {final.action} (confidence: {final.confidence:.2f})")

    await save_article(index, article, decisions, debate_responses, final)

async def main():
    num_articles = int(input("Enter the number of articles you wish to analyse:"))
    print("Starting Multi-Agent News Analysis with Debate...")
    articles = await fetch_articles(n=num_articles)
    
    print(f"\nFetched {len(articles)} articles")

    for i, article in enumerate(articles):
        await process_article(article, i)
    
    print(f"\nOutput saved at {OUTPUT_DIR}/ directory")

if __name__ == "__main__":
    asyncio.run(main())
