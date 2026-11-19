import React from "react";

export default function Home() {
  const backendOrigin = process.env.OLIVE_STAFF_ORIGIN ?? "http://localhost:8000";

  return (
    <main>
      <h1>Olive Branch Hotel</h1>
      <a href={new URL("/staff/login/", backendOrigin).href}>Staff sign in</a>
    </main>
  );
}
