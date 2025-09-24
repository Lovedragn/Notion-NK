import { useMemo, useRef, useState } from "react";
import aiClient from "../api/aiClient";
import logo from "../assets/headphone-user.gif";

const ChatAssistant = ({ userId, hash, token, bot_toggle , setbot_toggle }) => {
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
      if (text.toLowerCase() === "summarize") {
        const res = await aiClient.summarize(userId, hash, token);
        reply = res.summary || JSON.stringify(res);
      } else if (
        text.toLowerCase().startsWith("add ") ||
        text.toLowerCase().startsWith("create ")
      ) {
        const res = await aiClient.createTask(text, userId, hash, token);
        reply = res.message || "Task created.";
      } else if (
        text.toLowerCase().startsWith("update ") ||
        text.toLowerCase().startsWith("mark ")
      ) {
        const res = await aiClient.updateTask(text, userId, hash, token);
        reply = res.message || "Task updated.";
      } else {
        const res = await aiClient.ask(text, userId, hash, token);
        reply = res.answer || JSON.stringify(res);
      }
      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: ${err.message}` },
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
      <div
        className="card fixed bottom-5 right-5 bg-white/90 rounded-full w-10 h-10 z-100 overflow-hidden"
        onClick={() => setbot_toggle(prev => !prev)}
      />
      
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
