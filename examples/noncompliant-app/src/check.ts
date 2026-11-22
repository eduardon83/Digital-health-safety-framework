import AsyncStorage from "@react-native-async-storage/async-storage";
import analytics from "@react-native-firebase/analytics";

const API = "http://api.symptompal.example";
const OPENAI_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz123456";

export async function saveCheck(symptoms: string[], diagnosis: string) {
  console.log("user symptoms", symptoms, "diagnosis", diagnosis);
  await AsyncStorage.setItem("last_diagnosis", diagnosis);
  await analytics().logEvent("depression_check_done", { score: symptoms.length });
  await fetch(`${API}/checks`, { method: "POST", body: JSON.stringify({ symptoms, diagnosis }) });
}
