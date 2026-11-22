import * as SecureStore from "expo-secure-store";

// Health values are kept in encrypted storage only (HDSF CORE-DAT-12).
export async function saveSleepHours(day: string, hours: number) {
  await SecureStore.setItemAsync(`sleep.${day}`, String(hours));
}

export async function saveTheme(theme: "light" | "dark") {
  localStorage.setItem("ui.theme", theme);
}
