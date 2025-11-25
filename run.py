# ==================== MAIN EXECUTION ====================
from chatbot import FinancialChatbot

def main():
    print("🚀 THANOS-LEVEL AI AGENT ACTIVATED!")
    print("💎 You have all the infinity stones (APIs + Web Search)")
    print("Type 'quit' to exit\n")
    
    chatbot = FinancialChatbot()
    
    while True:
        user_input = input("\n💬 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            response = chatbot.process_query(user_input)
            print(f"\n🤖 Analyst: {response}")
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()

