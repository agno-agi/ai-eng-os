import json
from textwrap import dedent
from typing import Any, Dict, List, Optional

from agno.knowledge.document import Document
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.tools import Toolkit
from agno.utils.log import log_debug, log_error


class KnowledgeTools(Toolkit):
    def __init__(
        self,
        knowledge: Knowledge,
        enable_think: bool = False,
        enable_search: bool = False,
        enable_analyze: bool = False,
        enable_list_content: bool = False,
        enable_add_url_content: bool = False,
        instructions: Optional[str] = None,
        add_instructions: bool = True,
        add_few_shot: bool = False,
        few_shot_examples: Optional[str] = None,
        all: bool = False,
        **kwargs,
    ):
        if knowledge is None:
            raise ValueError("knowledge must be provided when using KnowledgeTools")

        # Store enable flags as instance variables
        self.enable_think = enable_think or all
        self.enable_search = enable_search or all
        self.enable_analyze = enable_analyze or all
        self.enable_list_content = enable_list_content or all
        self.enable_add_url_content = enable_add_url_content or all

        # Add instructions for using this toolkit
        if instructions is None:
            self.instructions = self._get_default_instructions()
            if add_few_shot:
                if few_shot_examples is not None:
                    self.instructions += "\n" + few_shot_examples
                else:
                    self.instructions += "\n" + self.FEW_SHOT_EXAMPLES
        else:
            self.instructions = instructions

        # The knowledge to search
        self.knowledge: Knowledge = knowledge

        tools: List[Any] = []
        if self.enable_think:
            tools.append(self.think)
        if self.enable_search:
            tools.append(self.search_knowledge)
        if self.enable_analyze:
            tools.append(self.analyze)
        if self.enable_list_content:
            tools.append(self.list_knowledge_content)
        if self.enable_add_url_content:
            tools.append(self.add_url_content)
        super().__init__(
            name="knowledge_tools",
            tools=tools,
            instructions=self.instructions,
            add_instructions=add_instructions,
            **kwargs,
        )

    def think(self, session_state: Dict[str, Any], thought: str) -> str:
        """Use this tool as a scratchpad to reason about the question, refine your approach, brainstorm search terms, or revise your plan.

        Call `Think` whenever you need to figure out what to do next, analyze the user's question, or plan your approach.
        You should use this tool as frequently as needed.

        Args:
            thought: Your thought process and reasoning.

        Returns:
            str: The full log of reasoning and the new thought.
        """
        try:
            log_debug(f"Thought: {thought}")

            # Add the thought to the Agent state
            if session_state is None:
                session_state = {}
            if "thoughts" not in session_state:
                session_state["thoughts"] = []
            session_state["thoughts"].append(thought)

            # Return the full log of thoughts and the new thought
            thoughts = "\n".join([f"- {t}" for t in session_state["thoughts"]])
            formatted_thoughts = dedent(
                f"""Thoughts:
                {thoughts}
                """
            ).strip()
            return formatted_thoughts
        except Exception as e:
            log_error(f"Error recording thought: {e}")
            return f"Error recording thought: {e}"

    def search_knowledge(self, session_state: Dict[str, Any], query: str) -> str:
        """Use this tool to search the knowledge base for relevant information.
        After thinking through the question, use this tool as many times as needed to search for relevant information.

        Args:
            query: The query to search the knowledge base for.

        Returns:
            str: A string containing the response from the knowledge base.
        """
        try:
            log_debug(f"Searching knowledge base: {query}")

            # Get the relevant documents from the knowledge base
            relevant_docs: List[Document] = self.knowledge.search(query=query)
            if len(relevant_docs) == 0:
                return "No documents found"
            return json.dumps([doc.to_dict() for doc in relevant_docs])
        except Exception as e:
            log_error(f"Error searching knowledge base: {e}")
            return f"Error searching knowledge base: {e}"

    def analyze(self, session_state: Dict[str, Any], analysis: str) -> str:
        """Use this tool to evaluate whether the returned documents are correct and sufficient.
        If not, go back to "Think" or "Search" with refined queries.

        Args:
            analysis: A thought to think about and log.

        Returns:
            str: The full log of thoughts and the new thought.
        """
        try:
            log_debug(f"Analysis: {analysis}")

            # Add the thought to the Agent state
            if session_state is None:
                session_state = {}
            if "analysis" not in session_state:
                session_state["analysis"] = []
            session_state["analysis"].append(analysis)

            # Return the full log of thoughts and the new thought
            analysis = "\n".join([f"- {a}" for a in session_state["analysis"]])
            formatted_analysis = dedent(
                f"""Analysis:
                {analysis}
                """
            ).strip()
            return formatted_analysis
        except Exception as e:
            log_error(f"Error recording analysis: {e}")
            return f"Error recording analysis: {e}"

    def list_knowledge_content(self) -> list[dict]:
        """Use this tool to list the content in the knowledge base.

        Return a list containing everything that is stored in knowledge.
        Each entry in the returned list contains the name, description, and metadata of a content item,
        allowing you to see what information is available in the knowledge base before searching.

        Returns:
            list[dict]: A list of dictionaries, each containing:
                - name: The name of the content item
                - description: A description of the content item
                - metadata: Additional metadata associated with the content item
        """
        contents, _ = self.knowledge.get_content()
        return [
            {
                "name": content.name,
                "description": content.description,
                "metadata": content.metadata,
            }
            for content in contents
        ]

    def add_url_content(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        url: Optional[str] = None,
    ) -> str:
        """Use this tool to add content from a url to the knowledge base.

        Args:
            name: Optional; The name of the content.
            description: Optional; A short summary of the content.
            metadata: Optional; A dictionary of metadata the content should be indexed with in the knowledge base.
            url: Optional; The url of the content.

        Returns:
            str: A string indicating the status of the addition.
        """
        # if not url.endswith(".pdf"):
        #     url = url + ".pdf"
        print("RECEVIED METADATA: ", metadata)
        if url is not None:
            reader = PDFReader()
            self.knowledge.add_content(
                url=url,
                reader=reader,
                metadata=metadata,
                description=description,
                name=name,
            )

        return "Successfully added content to the knowledge base"

    def _get_default_instructions(self) -> str:
        """Generate default instructions based on which tools are enabled."""
        tool_descriptions = []

        if self.enable_think:
            tool_descriptions.append("Think")
        if self.enable_search:
            tool_descriptions.append("Search")
        if self.enable_analyze:
            tool_descriptions.append("Analyze")
        if self.enable_list_content:
            tool_descriptions.append("List Content")
        if self.enable_add_url_content:
            tool_descriptions.append("Add Content from URL")

        tools_text = ", ".join(tool_descriptions[:-1])
        if len(tool_descriptions) > 1:
            tools_text += f", and {tool_descriptions[-1]}"
        else:
            tools_text = tool_descriptions[0] if tool_descriptions else "tools"

        instructions = f"You have access to the {tools_text} tools that will help you search your knowledge for relevant information. Use these tools as frequently as needed to find the most relevant information.\n\n"

        if (
            self.enable_think
            or self.enable_search
            or self.enable_analyze
            or self.enable_list_content
            or self.enable_add_url_content
        ):
            instructions += "## How to use the available tools:\n\n"

        tool_num = 1
        if self.enable_think:
            think_text = f"""\
                {tool_num}. **Think**
                - Purpose: A scratchpad for planning, brainstorming keywords, and refining your approach. You never reveal your "Think" content to the user.
                - Usage: Call `think` whenever you need to figure out what to do next, analyze your approach, or decide new search terms before (or after) you look up documents.

            """
            instructions += dedent(think_text)
            tool_num += 1

        if self.enable_search:
            search_text = f"""\
                {tool_num}. **Search**
                - Purpose: Executes a query against the knowledge base.
                - Usage: Call `search` with a clear query string whenever you want to retrieve documents or data. You can and should call this tool multiple times in one conversation.
                    - For complex topics, use multiple focused searches rather than one broad search
                    - Try different phrasing and keywords if initial searches don't yield useful results
                    - Use quotes for exact phrases and OR for alternative terms (e.g., "protein synthesis" OR "protein formation")

            """
            instructions += dedent(search_text)
            tool_num += 1

        if self.enable_analyze:
            analyze_text = f"""\
                {tool_num}. **Analyze**
                - Purpose: Evaluate whether the returned documents are correct and sufficient. If not, go back to "Think" or "Search" with refined queries.
                - Usage: Call `analyze` after getting search results to verify the quality and correctness of that information. Consider:
                    - Relevance: Do the documents directly address the user's question?
                    - Completeness: Is there enough information to provide a thorough answer?
                    - Reliability: Are the sources credible and up-to-date?
                    - Consistency: Do the documents agree or contradict each other?

            """
            instructions += dedent(analyze_text)
            tool_num += 1

        if self.enable_list_content:
            list_content_text = f"""\
                {tool_num}. **List Content**
                - Purpose: Returns a list containing indicators of everything that is stored in the knowledge base. Each entry includes the name, description, and metadata of content items.
                - Usage: Call `list_knowledge_content` when you need to see what information is available in the knowledge base before searching, or when the user asks about what content is available.

            """
            instructions += dedent(list_content_text)

        if self.enable_add_url_content:
            add_url_content_text = f"""\
                {tool_num}. **Add Content from URL**
                - Purpose: Adds content from a url to the knowledge base.
                - Usage: Call `add_url_content` with the url of the content to add it to the knowledge base.

            """
            instructions += dedent(add_url_content_text)
            tool_num += 1

        guidelines = []
        if self.enable_think:
            guidelines.append("- Do not include your internal chain-of-thought in direct user responses.")
            guidelines.append('- Use "Think" to reason internally. These notes are never exposed to the user.')

        if self.enable_think and self.enable_search and self.enable_analyze:
            guidelines.append(
                "- Iterate through the cycle (Think → Search → Analyze) as many times as needed until you have a final answer."
            )
        elif self.enable_search and self.enable_analyze:
            guidelines.append(
                "- Iterate through the cycle (Search → Analyze) as many times as needed until you have a final answer."
            )

        guidelines.append("- When you do provide a final answer to the user, be clear, concise, and accurate.")

        if self.enable_search:
            guidelines.append(
                "- If search results are sparse or contradictory, acknowledge limitations in your response."
            )
            guidelines.append(
                "- Synthesize information from multiple sources rather than relying on a single document."
            )

        if guidelines:
            instructions += "**Important Guidelines**:\n"
            for guideline in guidelines:
                instructions += f"    {guideline}\n"

        return instructions.strip()

    FEW_SHOT_EXAMPLES = dedent("""\
        You can refer to the examples below as guidance for how to use each tool.
        ### Examples

        #### Example 1: Multiple Searches and Analysis

        User: What are the recommended dietary guidelines for someone with mild hypertension?
        Think: The user is asking about dietary guidelines for mild hypertension. I'll start broad, then refine if needed.
        Search: "dietary guidelines for mild hypertension", "salt intake recommendations for mild hypertension"
        Analyze: I got one document referencing the DASH diet, but it's quite brief. I might need more info about salt intake recommendations specifically.
        Think: Let me refine my search to see if there are official guidelines from recognized health organizations.
        Search: "WHO or American Heart Association guidelines for hypertension", "fruits and vegetables for mild hypertension"
        Analyze: The new documents mention daily sodium limits, recommended fruit/vegetable intake, and more. This seems thorough. I'm ready to formulate the answer.

        Final Answer: For mild hypertension, the guidelines typically recommend following the DASH diet, which emphasizes ...

        #### Example 2: Invalid or Insufficient Search Results

        User: Do you have any documentation on the 'XYZ Project' from last year?
        Think: I'll try searching for 'XYZ Project last year' but if that fails, I'll look for internal code names or older references.
        Search: "XYZ Project last year"
        Analyze: No relevant documents. Let me refine my search to check for 'XYZ Project' in different date ranges or alternate titles.
        Think: Possibly it's under 'XYZ Initiative' or 'XYZ Rollout.' Let's do a second search.
        Search: "XYZ Initiative OR 'XYZ Rollout' from last year"
        Analyze: Found a relevant archive for 'XYZ Initiative'. Looks correct and references last year's timeline. I'll proceed with that info.

        Final Answer: Yes, we have some archived documentation under the name 'XYZ Initiative.' It includes ...

        #### Example 3: Synthesizing Complex Information

        User: How do quantum computers differ from classical computers in terms of performance?
        Think: This is a technical question requiring clear explanations of quantum vs. classical computing performance characteristics.
        Search: "quantum computing performance vs classical computing"
        Analyze: Found general information but need more specifics on actual performance metrics and use cases.
        Think: Let me search for specific quantum advantages and limitations.
        Search: "quantum supremacy examples", "quantum computing limitations"
        Search: "quantum computing speedup for specific algorithms"
        Analyze: Now I have concrete examples of quantum speedup for certain algorithms, limitations for others, and real-world benchmarks.

        Final Answer: Quantum computers differ from classical computers in three key ways: [synthesized explanation with specific examples]...\
    """)
