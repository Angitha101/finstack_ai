# from sql_connection import client, text
# import re
# from dateutil.relativedelta import relativedelta
# from dateutil import parser
# import calendar
# from langchain.agents import AgentExecutor
# from langchain.agents.agent_toolkits import SQLDatabaseToolkit
# from langchain.agents import create_sql_agent
# from langchain_openai import ChatOpenAI
# from langchain.chains import ConversationChain, LLMChain
# from langchain.prompts import PromptTemplate
# import os
# from langchain.sql_database import SQLDatabase
# from datetime import datetime
# os.environ["OPENAI_API_KEY"] = "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"
# TABLE_NAME="finstack_pnl"
# db = SQLDatabase(client)
# # Create the toolkit for PostgreSQL (pointing to your specific table)

# llm = ChatOpenAI(
#     model="gpt-4",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
# )

# toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# agent_executor = create_sql_agent(
#     llm=llm,
#     toolkit=toolkit,
#     verbose=True,
#     top_k=1000,
# )



# def get_available_months():
#     query = f"""
#     SELECT DISTINCT 
#     TO_CHAR(date, 'YYYY-MM') AS month
#     FROM {TABLE_NAME}  -- Update this table name if needed
#     ORDER BY month DESC
#     """
    
#     with client.connect() as connection:
#         result = connection.execute(text(query))
#         # Collect months into a list and return
#         months = [row[0] for row in result]
#     return months

# # Add this function to determine the valid time range
# def get_valid_time_range(available_months):
#     if not available_months:
#         return None, None
#     available_months_dt = [datetime.strptime(month, '%Y-%m') for month in available_months]

#     latest_month = max(available_months_dt)
#     earliest_month = min(available_months_dt)
#     valid_start = (earliest_month - relativedelta(months=2)).replace(day=1)

#     return valid_start, latest_month



# def extract_time_periods(question):
#     """Extract time periods mentioned in the question."""
#     # Patterns for various time formats
#     year_pattern = r'\b(20\d{2})\b'
#     month_year_pattern = r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})\b'
#     quarter_pattern = r'\b(Q[1-4])\s+(\d{4})\b'

#     time_periods = []

#     # Extract years
#     years = re.findall(year_pattern, question)
#     for year in years:
#         time_periods.append({'type': 'year', 'value': int(year)})

#     # Extract month-year combinations
#     month_years = re.findall(month_year_pattern, question, re.IGNORECASE)
#     for month, year in month_years:
#         date = parser.parse(f"{month} {year}")
#         time_periods.append({'type': 'month', 'value': date})

#     # Extract quarters
#     quarters = re.findall(quarter_pattern, question)
#     for quarter, year in quarters:
#         quarter_num = int(quarter[1])
#         # start_month = (quarter_num - 1) * 3 + 1
#         # time_periods.append(('quarter', parser.parse(f"{year}-{start_month:02d}-01")))
#         time_periods.append({'type': 'quarter', 'year': int(year), 'quarter': quarter_num})


#     return time_periods



# def construct_date_filter(time_periods):
#     date_filter = []

#     for period in time_periods:
#         if isinstance(period, dict):
#             if period['type'] == 'year':
#                 try:
#                     year = int(period['value'])
#                     date_filter.append(f"EXTRACT(MONTH FROM Date) = {year}")
#                 except ValueError:
#                     date_filter.append(f"EXTRACT(YEAR FROM Date) IS NULL")  

#             elif period['type']=='month':
#                 try:
#                     month = period['value'].month
#                     year = period['value'].year
#                 except ValueError:
#                     date_filter.append(f"EXTRACT(MONTH FROM Date) IS NULL")  

#             # Handle quarter filter
#             elif period['type'] == 'quarter':
#                 try:
#                     quarter = period['quarter']
#                     year = period['year']
#                     start_month = (quarter - 1) * 3 + 1
#                     end_month = start_month + 2
#                     date_filter.append(f"(EXTRACT(MONTH FROM Date) BETWEEN {start_month} AND {end_month} AND EXTRACT(YEAR FROM Date) = {year})")
#                 except KeyError:
#                     date_filter.append(f"EXTRACT(YEAR FROM Date) IS NULL") 
#         else:
#             raise TypeError(f"Expected dictionary, got {type(period)}")

#     # Join all filters if there are multiple filters
#     return " AND ".join(date_filter) if date_filter else ""




# def find_matching_values(question, llm):
#     # Prompt template to extract relevant entities for filtering
#     prompt = PromptTemplate(
#         input_variables=["question"],
#         template="""You are a financial data analyst. Based on the question, identify relevant 
#         column names and their values from the dataset for filtering. The dataset includes the columns: 
#         PNL Type, Category, realm_id, Account, Account Type, Account Sub Type, Business Unit, 
#         Class, Customer, Vendor, Expense, Revenue, Net Revenue.

#         Respond in this structured format:
#         - PNL Type: [values]
#         - Category: [values]
#         - realm_id: [values]
#         - Account: [values]
#         - Account Type: [values]
#         - Account Sub Type: [values]
#         - Business Unit: [values]
#         - Class: [values]
#         - Customer: [values]
#         - Vendor: [values]

#         Question: {question}
#         """
#     )

#     # Initialize the LLM chain
#     chain = LLMChain(llm=llm, prompt=prompt)
#     extracted_terms = chain.run(question=question)

#     # Parse the response
#     relevant_terms = {
#         'PNL Type': set(),
#         'Category': set(),
#         'realm_id': set(),
#         # 'Date': set(),
#         'Account': set(),
#         'Account Type': set(),
#         'Account Sub Type': set(),
#         'Business Unit': set(),
#         'Class': set(),
#         'Customer': set(),
#         'Vendor': set()
#     }

#     # Populate the relevant_terms dictionary
#     for line in extracted_terms.split("\n"):
#         line = line.strip()
#         for key in relevant_terms.keys():
#             if line.startswith(f"{key}:"):
#                 values = line.replace(f"{key}:", "").strip()
#                 relevant_terms[key].update(value.strip() for value in values.split(",") if value.strip())

#     return relevant_terms






# def construct_filter_clause(matches):
#     clauses = []
#     for key, values in matches.items():
#         if values:
#             # Map keys to your column names
#             column_mapping = {
#                 'PNL Type': 'pnl_type',
#                 'Category': 'category',
#                 'realm_id': 'realm_id',
#                 # 'Date': 'date',
#                 'Account': 'account',
#                 'Account Type': 'account_type',
#                 'Account Sub Type': 'account_sub_type',
#                 'Business Unit': 'business_unit',
#                 'Class': 'class',
#                 'Customer': 'customer',
#                 'Vendor': 'vendor'
#             }
            
#             column = column_mapping.get(key)
            
#             # Special handling for "Date"
#             if key == 'Date':
#                 date_clauses = []
#                 for value in values:
#                     if "-" in value:  # Assuming ranges are in the format "YYYY-MM-DD to YYYY-MM-DD"
#                         start_date, end_date = value.split("to")
#                         date_clauses.append(f"({column} BETWEEN '{start_date.strip()}' AND '{end_date.strip()}')")
#                     elif value.isdigit() and len(value) == 4:  # Assuming year format "YYYY"
#                         date_clauses.append(f"YEAR({column}) = {value.strip()}")
#                     else:
#                         date_clauses.append(f"{column} = '{value.strip()}'")
#                 clauses.append(" OR ".join(date_clauses))
#             else:
#                 # Handle other columns
#                 quoted_values = [f"'{v}'" for v in values]
#                 clauses.append(f"{column} IN ({', '.join(quoted_values)})")
    
#     return " AND ".join(clauses) if clauses else ""





# # use different logic for evaluation
# def evaluate_answer_relevance(question, answer):
#     prompt = PromptTemplate(
#         input_variables=["question", "answer"],
#         template="""Given the following question and answer, evaluate how well the answer addresses the question.
#         Provide a relevance score as a percentage and a brief explanation.

#         Question: {question}

#         Answer: {answer}

#         Relevance Score (0-100%):
#         Explanation:"""
#     )

#     chain = LLMChain(llm=llm, prompt=prompt)
#     response = chain.run(question=question, answer=answer)
#     return response



# def ask_question(question, context=""):
#     time_periods = extract_time_periods(question)
#     print(f"time_periods, {time_periods}")
#     answer=""
#     date_filter = construct_date_filter(time_periods)
#     print(f"Date filter: {date_filter}")

#     matches = find_matching_values(question, llm)
#     print(f"matches, {matches}")

#     filter_clause = construct_filter_clause(matches)
#     print(f"filter clause {filter_clause}")


#     if date_filter:
#             filter_clause = f"{filter_clause} AND {date_filter}" if filter_clause else date_filter
        
#             print(f"filter_clause, {filter_clause}")
#     instruction = f"""You are a knowledgeable finance data analyst working for Rittman Analytics.
#     Use the `{TABLE_NAME}` table to answer this question.
#     Use the following SQL filter clause in your query: {filter_clause}, if the value is not null.
#     When calculating revenue or any other financial metrics, make sure to aggregate the values for the entire time period(s) mentioned in the question (which may be months, quarters, or years).
#     If no specific time period is mentioned, provide an overview of all available data.
#     If multiple time periods are mentioned, provide a comparison between them.
#     Please construct and execute a SQL query to answer the question, making sure to include the filter clause.
#     Do not include markdown-style triple backticks in the SQL you generate and try to use or validate.


#     Question is: {question}
#     """

#     answer = agent_executor.run(instruction)

#     relevance_evaluation = evaluate_answer_relevance(question, answer)

#     return f"{answer}\n\nRelevance Evaluation:\n{relevance_evaluation}"





# def ask_question_with_feedback_and_learning(question: str, max_iterations: int = 3) -> str:
#     iteration = 0
#     while iteration < max_iterations:
#         # # Retrieve similar Q&A pairs
#         # similar_qa = get_similar_qa(question)

#         # # Prepare the context with similar Q&A pairs
#         # context = format_similar_qa(similar_qa)

#         # Use the modified ask_question function with context
#         answer = ask_question(question)
#         print(f"\nAnswer (Iteration {iteration + 1}):\n{answer}")

#         user_satisfied = input("\nDid this answer your question sufficiently? (yes/no): ").lower().strip()

#         if user_satisfied == 'yes':
#             # Store the successful Q&A pair
#             # store_successful_qa(question, answer)
#             return answer

#         feedback = input("Please provide feedback on how the answer could be improved: ")

#         # Use LLM to analyze feedback and improve the question
#         improve_prompt = PromptTemplate(
#             input_variables=["original_question", "answer", "feedback", "context"],
#             template="""Given the original question, the provided answer, user feedback, and similar Q&A pairs from past interactions,
#             please suggest an improved version of the question that addresses the user's concerns.

#             Original Question: {original_question}

#             Provided Answer: {answer}

#             User Feedback: {feedback}

#             {context}

#             Improved Question:"""
#         )

#         improve_chain = LLMChain(llm=llm, prompt=improve_prompt)
#         improved_question = improve_chain.run(
#             original_question=question,
#             answer=answer,
#             feedback=feedback,
#             # context=context
#         )

#         print(f"\nImproved question based on feedback: {improved_question}")

#         question = improved_question  # Update the question for the next iteration
#         iteration += 1

#     return "I apologize, but I couldn't provide a satisfactory answer within the maximum number of iterations. Please try rephrasing your question or contact support for further assistance."




# def main():
#     global valid_time_range

#     # Determine available months and valid time range
#     available_months = get_available_months()
#     valid_time_range = get_valid_time_range(available_months)

#     print("Hi! Ask me a question about our company's profit and loss data")
#     while True:
#         question = input("\nYour question (or type 'QUIT' to exit): ")
#         if question.lower() == 'quit':
#             break

#         final_answer = ask_question_with_feedback_and_learning(question)
        
#         print(f"\nFinal Answer: {final_answer}")
#         print("\n---")

# if __name__ == "__main__":
#     main() 