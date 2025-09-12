import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router";

const App = () => {
  const { [":undefined"]: dynamicSegment } = useParams();
  const emailFromPath = useMemo(() => {
    const path = window.location.pathname;
    return decodeURIComponent(path.slice(1));
  }, []);

  const email = emailFromPath || dynamicSegment;

  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const baseUrl = "http://localhost:8080";

  const loadTasks = async () => {
    const res = await fetch(`${baseUrl}/tasks/${email}`);
    const data = await res.json();
    setTasks(data);
  };

  useEffect(() => {
    if (email) loadTasks();
  }, [email]);

  const addTask = async (e) => {
    e.preventDefault();
    const res = await fetch(`${baseUrl}/tasks/${email}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(next),
    });
    if (res.ok) loadTasks();
  };

  const deleteTask = async (id) => {
    const res = await fetch(`${baseUrl}/tasks/${id}`, { method: "DELETE" });
    if (res.ok) loadTasks();
  };

  return (
    <div className="bg-black min-h-screen text-white p-6">
      <div className="max-w-xl mx-auto">
        <h1 className="text-2xl mb-4">Tasks for {email}</h1>

        <form onSubmit={addTask} className="flex gap-2 mb-6">
          <input
            className="input flex-1"
            placeholder="Title"
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
          <button className="btn-l" type="submit">Add</button>
        </form>

        <ul className="flex flex-col gap-2">
          {tasks.map((t) => (
            <li key={t.id} className="flex items-center gap-2 bg-zinc-900 p-3 rounded">
              <input
                className="input flex-1"
                value={t.title}
                onChange={(e) => updateTask(t.id, { ...t, title: e.target.value })}
              />
              <input
                type="date"
                className="input"
                value={t.taskDate || ""}
                onChange={(e) => updateTask(t.id, { ...t, taskDate: e.target.value })}
              />
              <button className="btn-l" onClick={() => deleteTask(t.id)}>Delete</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default App;
