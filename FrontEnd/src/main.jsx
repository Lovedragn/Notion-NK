import { createRoot } from "react-dom/client";
import "./index.css";
import { createBrowserRouter, Navigate, RouterProvider } from "react-router";

import App from "./App.jsx";
import Login from "./Auth/Login.jsx";

const storedUser = localStorage.getItem("user");
const user = storedUser ? JSON.parse(storedUser) : {};
const { email } = user;

const router = createBrowserRouter([
  { path: "/", element : <Navigate to={"v1/auth"} replace/> },
  { path: `/:${email || 'email'}`, element: <App /> },
  { path: "/v1/auth", element: <Login /> },
]);

createRoot(document.getElementById("root")).render(
  <RouterProvider router={router} />
);
