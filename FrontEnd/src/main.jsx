import { createRoot } from "react-dom/client";
import "./index.css";
import { createBrowserRouter, Navigate, RouterProvider } from "react-router";

import App from "./App.jsx";

const VITE_APP_GOOGLE_CLIENT_ID = import.meta.env.VITE_APP_GOOGLE_CLIENT_ID;

const storedUser = localStorage.getItem("user");
const user = storedUser ? JSON.parse(storedUser) : {};
const { address } = user;

const router = createBrowserRouter([
  { path: "/", element : <Navigate to={"auth/v1/google"} replace/> },
  { path: `/:${address}`, element: <App /> },
  { path: "/auth/v1/google", element: <Login /> },
]);

createRoot(document.getElementById("root")).render(
  <RouterProvider router={router} />
);
