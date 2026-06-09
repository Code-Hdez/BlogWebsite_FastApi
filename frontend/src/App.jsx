import { useState } from "react";

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setData(null);
    setError(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/posts")
      const json = await res.json()
      setData(json)
    }catch(err){
      console.error(err)
      setError("Error de CORS o Conexion. Revisar la consola del navegador")

    }

  };

  return (
    <div style={{ fontFamily: "sans-serif", padding: 30 }}>
      <h1>Demo CORS con FastAPI</h1>
      <p>
        Este ejemplo intenta conectar con la API en <b>http://127.0.0.1:8000</b>
      </p>
      <button
        onClick={fetchData}
        style={{
          background: "#3182ce",
          color: "white",
          padding: "10px 20px",
          border: "none",
          borderRadius: 6,
          cursor: "pointer",
          fontSize: "16px",
        }}
      >
        Probar conexión
      </button>

      {data && (
        <pre
          style={{
            marginTop: 20,
            background: "#1a202c",
            color: "#f7fafc",
            padding: 15,
            borderRadius: 8,
          }}
        >
          {JSON.stringify(data, null, 2)}
        </pre>
      )}

      {error && (
        <pre
          style={{
            marginTop: 20,
            background: "#fed7d7",
            color: "#742a2a",
            padding: 15,
            borderRadius: 8,
          }}
        >
          {error}
        </pre>
      )}
    </div>
  );
}

export default App;