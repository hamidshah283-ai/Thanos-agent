# ==================== ENHANCED CHATBOT INTERFACE ====================
from orchestrator import MasterOrchestrator

class FinancialChatbot:
    def __init__(self):
        self.orchestrator = MasterOrchestrator()
    
    def process_query(self, user_input: str) -> str:
        """Main method to process user queries"""
        print(f"🔍 Analyzing: {user_input}")
        
        try:
            # Step 1: Analyze intent
            intent_analysis = self.orchestrator.analyze_intent(user_input)
            print(f"🎯 Intent: {intent_analysis['primary_intent']}")
            print(f"💼 Financial: {intent_analysis.get('is_financial_query', False)}")
            print(f"🌐 Web Search: {intent_analysis.get('needs_web_search', False)}")
            
            # Step 2: Execute appropriate agents
            agent_results = self.orchestrator.execute_agents(intent_analysis)
            print(f"📊 Agent results collected")
            
            # Step 3: Synthesize final response
            final_response = self.orchestrator.synthesize_response(user_input, agent_results, intent_analysis)
            
            return final_response
            
        except Exception as e:
            error_msg = f"❌ System error: {str(e)}"
            print(error_msg)
            return f"I encountered a system error. Please try again with a simpler query."

