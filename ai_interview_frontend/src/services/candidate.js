import axios from "axios";

const BASE_URL = "http://localhost:8000/candidate";

export const getCandidateSessionAPI = async (sessionId) => {
  try {
    const response = await axios.get(`${BASE_URL}/session/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching candidate session:", error);
    return null;
  }
};
