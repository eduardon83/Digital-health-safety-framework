const API = "https://api.example.org";

// Neutral event names only (HDSF CORE-TRK-02); no health values in logs (CORE-DAT-10).
export async function recordEvent(name: "entry_saved" | "summary_viewed") {
  await fetch(`${API}/events`, { method: "POST", body: JSON.stringify({ name }) });
  console.log("event sent", name);
}
