import { OpenRouter } from "@openrouter/sdk";

export async function decide({ state, questions, model = "~typesafe/jev-latest", sessionId, user, apiKey = process.env.OPENROUTER_API_KEY }) {
  if (!apiKey) throw new Error("OPENROUTER_API_KEY not set");
  // SDK expects `questions` as a record keyed by id, not an array
  const questionsRecord = Array.isArray(questions)
    ? Object.fromEntries(questions.map((q) => [q.id, q]))
    : questions;
  const openrouter = new OpenRouter({ apiKey });
  const decision = await openrouter.alpha.decisions.create({
    decisionsRequest: { model, state, questions: questionsRecord, ...(sessionId && { sessionId }), ...(user && { user }) }
  });
  return { answers: decision.answers, id: decision.id, model: decision.model, provider: decision.provider, usage: decision.usage };
}
