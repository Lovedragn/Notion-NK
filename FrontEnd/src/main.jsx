import { createRoot } from "react-dom/client";
import "./index.css";
import { createBrowserRouter, Navigate, RouterProvider } from "react-router";

import App from "./App.jsx";
import Login from "./Auth/Login.jsx";

const token = localStorage.getItem("token");
const hash = localStorage.getItem("hash");

const router = createBrowserRouter([
  { path: "/", element : <Navigate to={ hash ? `/${hash}` : "v1/auth" } replace/> },
  { path: `/:hash`, element: <App /> },
  { path: "/v1/auth", element: <Login /> },
]);

createRoot(document.getElementById("root")).render(
  <RouterProvider router={router} />
);
