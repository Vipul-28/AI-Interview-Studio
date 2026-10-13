import axios from "axios";

const BASE_URL = "http://localhost:8000/recruiter";

export const createInterviewAPI = async (formData) => {
  try {
    const response = await axios.post(`${BASE_URL}/create-interview`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error creating interview:", error);
    throw error;
  }
};

export const getInterviewsAPI = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/interviews`);
    return response.data;
  } catch (error) {
    console.error("Error fetching interviews:", error);
    return [];
  }
};

export const getInterviewDetailAPI = async (sessionId) => {
  try {
    const response = await axios.get(`${BASE_URL}/interview/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching interview detail:", error);
    return null;
  }
};

export const resendInviteAPI = async (sessionId) => {
  try {
    const response = await axios.post(`${BASE_URL}/send-invite/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error("Error sending invite email:", error);
    throw error;
  }
};

export const sendReportEmailAPI = async (sessionId) => {
  try {
    const response = await axios.post(`${BASE_URL}/send-report/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error("Error emailing report:", error);
    throw error;
  }
};

