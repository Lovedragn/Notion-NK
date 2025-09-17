const AI_BASE_URL = import.meta.env?.VITE_AI_BASE_URL || "http://localhost:8000";

async function postJson(path, body) {
	const res = await fetch(`${AI_BASE_URL}${path}`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(body || {}),
	});
	if (!res.ok) {
		const text = await res.text();
		throw new Error(text || `Request failed: ${res.status}`);
	}
	return res.json();
}

export const aiClient = {
	ask: (query, userId, token) => postJson("/ask", { query, userId, token }),
	summarize: (userId, token) => postJson("/summarize", { userId, token }),
	createTask: (prompt, userId, hash, token) => postJson("/create-task", { prompt, userId, hash, token }),
	updateTask: (prompt, userId, token) => postJson("/update-task", { prompt, userId, token }),
};

export default aiClient;
