import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router";
import ChatAssistant from "./Components/ChatAssistant";
import logo from "./assets/headphone-user.gif";

const App = () => {
  const { hash } = useParams();

  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");

  const [bot_toggle, setbot_toggle] = useState(false);
  const baseUrl = "http://localhost:8080";
  const token = useMemo(() => localStorage.getItem("token") || "", []);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("hash");
    window.location.href = "/v1/auth";
  };

  const loadTasks = async () => {
    const res = await fetch(`${baseUrl}/tasks/hash/${hash}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    console.log("tasks api response", data);
    const normalized = Array.isArray(data)
      ? data
      : data && typeof data === "object"
      ? Object.values(data)
      : [];
    setTasks(normalized);
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const addTask = async (e) => {
    e.preventDefault();
    const res = await fetch(`${baseUrl}/tasks/hash/${hash}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title, taskDate: date }),
    });
    if (res.ok) {
      setTitle("");
      setDate("");
      loadTasks();
    }
  };

  const updateTask = async (id, next) => {
    const res = await fetch(`${baseUrl}/tasks/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(next),
    });
    if (res.ok) loadTasks();
  };

  const deleteTask = async (id) => {
    const res = await fetch(`${baseUrl}/tasks/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) loadTasks();
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-neutral-800">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">Knot Tasks</h1>
          <div className="flex items-center gap-3">
            <div className="text-sm text-neutral-400">Secure workspace</div>
            <button className="btn-danger" onClick={logout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="card p-4 mb-6">
          <form onSubmit={addTask} className="flex flex-col sm:flex-row gap-3">
            <input
              className="input flex-1"
              placeholder="Task title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <input
              type="date"
              className="input"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
            <button className="btn-primary" type="submit">
              Add
            </button>
          </form>
        </div>

        <div className="card overflow-hidden mb-6">
          <div className="grid grid-cols-12 px-4 py-3 border-b border-neutral-700 text-xs uppercase tracking-wide text-neutral-400 sticky top-0 bg-neutral-900/90 backdrop-blur">
            <div className="col-span-7">Title</div>
            <div className="col-span-3">Date</div>
            <div className="col-span-2 text-right">Actions</div>
          </div>
          <div className="max-h-[60vh] overflow-y-auto">
            {tasks.map((t) => (
              <div
                key={t.id}
                className="grid grid-cols-12 gap-3 px-4 py-3 border-b border-neutral-800 items-center odd:bg-neutral-900/40 even:bg-neutral-950/40"
              >
                <div className="col-span-7">
                  <input
                    className="input w-full"
                    value={t.title}
                    onChange={(e) =>
                      updateTask(t.id, { ...t, title: e.target.value })
                    }
                  />
                </div>
                <div className="col-span-3">
                  <input
                    type="date"
                    className="input w-full"
                    value={t.taskDate || ""}
                    onChange={(e) =>
                      updateTask(t.id, { ...t, taskDate: e.target.value })
                    }
                  />
                </div>
                <div className="col-span-2 flex justify-end">
                  <button
                    className="btn-danger"
                    onClick={() => deleteTask(t.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
            {tasks.length === 0 && (
              <div className="px-4 py-6 text-neutral-400 text-sm">
                No tasks yet. Create your first task above.
              </div>
            )}
          </div>
        </div>
      </main>
      <div
        className="card fixed bottom-5 right-5 bg-white/90 rounded-full w-10 h-10 z-100 overflow-hidden"
        onClick={() => setbot_toggle((prev) => !prev)}
      >
        {bot_toggle ? (
          <ChatAssistant
            bot_toggle={bot_toggle}
            setbot_toggle={setbot_toggle}
          />
        ) : (
          <img src={logo} className="w-full h-full scale-75" />
        )}
      </div>
    </div>
  );
};

export default App;
