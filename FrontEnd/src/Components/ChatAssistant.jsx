import { useMemo, useRef, useState } from "react";
import logo from "../assets/headphone-user.gif";

const ChatAssistant = ({ token }) => {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi! Ask me about your tasks or say 'summarize'.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef(null);

  const handleSend = async (e) => {
    e?.preventDefault?.();

    const text = input.trim();
   
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    try {
      let reply;
      const AI_BASE_URL =
        import.meta.env?.VITE_AI_BASE_URL || "http://localhost:8000";

      const res = await fetch(`${AI_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({"user_input":text} || {}),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed: ${res.status}`);
      }
      reply = res.text();
      console.log(reply)
      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: Please Try Again Later` },
      ]);
    } finally {
      setLoading(false);
      setTimeout(
        () =>
          listRef.current?.scrollTo({
            top: listRef.current.scrollHeight,
            behavior: "smooth",
          }),
        0
      );
    }
  };

  return (
    <div className="card p-4 flex flex-col h-full max-w-150">
      <div ref={listRef} className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={
              m.role === "assistant" ? "chat-bubble ai" : "chat-bubble user"
            }
          >
            {m.content}
          </div>
        ))}
      </div>
      <form onSubmit={handleSend} className="mt-3 flex gap-2">
        <input
          className="input flex-1"
          placeholder="Ask or say 'summarize' / 'add ...' / 'mark ...'"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default ChatAssistant;
