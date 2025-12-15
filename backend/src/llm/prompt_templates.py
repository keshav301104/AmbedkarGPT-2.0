class PromptTemplates:
    @staticmethod
    def get_summary_prompt(text_content):
        return f"""
        You are an expert researcher analyzing the works of Dr. B.R. Ambedkar.
        Read the following text segments and identify the central theme.
        Write a concise summary (2-3 sentences) explaining what this group of text discusses.
        
        TEXT:
        {text_content}
        
        SUMMARY:
        """

    @staticmethod
    def get_answer_prompt(context, query):
        return f"""
        You are an AI assistant named AmbedkarGPT. You answer questions based STRICTLY on the provided context from Dr. B.R. Ambedkar's book.
        
        --- CONTEXT ---
        {context}
        ---------------
        
        USER QUESTION:
        {query}
        
        INSTRUCTIONS:
        1. Answer the question directly using the information in the Context.
        2. If the context contains the answer (even partially), DO NOT start with "I cannot find information". Just give the answer.
        3. Only say "I cannot find information about this" if the context is completely unrelated or empty.
        4. CITATION RULE: You MUST cite your sources using the bracketed numbers like [1], [2] at the end of sentences.
        
        ANSWER (Direct and cited):
        """