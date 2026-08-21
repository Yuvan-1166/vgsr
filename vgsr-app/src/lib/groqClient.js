import Groq from "groq-sdk";

let groqClient = null;

function getClient() {
  const apiKey = import.meta.env.VITE_GROQ_API_KEY;
  if (!apiKey) {
    throw new Error("Missing VITE_GROQ_API_KEY in .env file");
  }
  if (!groqClient) {
    groqClient = new Groq({ apiKey, dangerouslyAllowBrowser: true });
  }
  return groqClient;
}

const SYSTEM_PROMPT = `You are an expert SQL query generator. You convert natural language questions into accurate, optimized SQL queries.

RULES:
1. Return ONLY valid SQL for the given database schema.
2. Use proper SQL syntax (ANSI SQL compatible with PostgreSQL/MySQL).
3. Use appropriate JOINs when querying across tables.
4. Use meaningful aliases for tables.
5. Include comments in the SQL when the logic is complex.
6. If the question is ambiguous, make reasonable assumptions and note them.
7. Use aggregate functions (COUNT, SUM, AVG, etc.) when appropriate.
8. Handle NULL values properly.
9. Use LIMIT for potentially large result sets.
10. Format the SQL cleanly with proper indentation.

You MUST respond in this exact JSON format (no markdown, no code blocks):
{
  "sql": "the SQL query here",
  "explanation": "brief explanation of what the query does and any assumptions made"
}`;

export async function generateSQL(schemaText, question) {
  const client = getClient();

  const response = await client.chat.completions.create({
    model: "openai/gpt-oss-20b",
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      {
        role: "user",
        content: `DATABASE SCHEMA:\n${schemaText}\n\nQUESTION: ${question}\n\nGenerate the SQL query for this question.`,
      },
    ],
    temperature: 0.1,
    max_tokens: 2048,
    response_format: { type: "json_object" },
  });

  const content = response.choices[0]?.message?.content;
  if (!content) throw new Error("No response from Groq API");

  try {
    const parsed = JSON.parse(content);
    if (!parsed.sql) throw new Error("Response missing SQL field");
    return {
      sql: parsed.sql.trim(),
      explanation: parsed.explanation || "",
    };
  } catch {
    // Try to extract SQL from non-JSON response
    const sqlMatch = content.match(/```sql\n([\s\S]*?)```/);
    if (sqlMatch) {
      return { sql: sqlMatch[1].trim(), explanation: "" };
    }
    throw new Error("Failed to parse Groq API response");
  }
}
